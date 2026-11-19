"""Tudo o que determina o que o EXECUTOR recebe: perfil do CLI, invocação e ambiente.
Entra no hash de execução (com a skill e os casos). Mudar este arquivo exige rodada nova."""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

AQUI = Path(__file__).resolve().parent
DEV = AQUI.parent.parent                             # trese-apf-skills/dev/<skill>
SKILL = DEV.parent.parent / "skills" / DEV.name       # trese-apf-skills/skills/<skill>
BASE_WS = Path("/tmp/apf-evals")

CONFIG = {
    "cmd": "claude",
    "modelo": "claude-sonnet-5-5",
    "esforco": "high",
    # Perfil validado por sondagem. A sondagem sondas-1 mostrou que --restricted não descobre
    # .claude/skills do projeto; por decisão registrada (PLANO.md, D30), o isolamento das configurações
    # do usuário fica com --setting-sources project e o confinamento com a auditoria do trace.
    "perfil": ["--setting-sources", "project", "--strict-mcp-config",
               "--tools", "Read,Write,Edit,Glob,Grep,Bash,Skill",
               "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash,Skill",
               "--permission-prompts", "none"],
    "timeout_s": 1200,
}

PROMPT_SONDA_SKILL = "/trese-apf-aproximacao modo=detalhada -- ./pedido.md"
PROMPT_SONDA_CONTEXTO = ("Responda só com uma lista. 1) Quais arquivos de instrução (CLAUDE.md, AGENTS.md ou semelhantes) ou "
                         "memórias foram carregados no seu contexto? Dê os caminhos ou diga 'nenhum'. 2) Quais skills estão "
                         "disponíveis? 3) Quais ferramentas você tem? Não use nenhuma ferramenta.")


def montar_invocacao(c: Dict[str, Any]) -> Tuple[str, bool]:
    """(prompt, precisa_arquivo_pedido)."""
    t = c["tipo"]
    if t in ("nl_confirma", "nl_executa"):
        return c["prosa"], c.get("subsidio") is not None
    if c.get("arquivo_inexistente"):
        return f"/trese-apf-aproximacao -- {c['arquivo_inexistente']}", False
    args = c.get("args")
    if c.get("inline"):
        if args is None:
            return f"/trese-apf-aproximacao {c['subsidio']}", False
        return f"/trese-apf-aproximacao {args} -- {c['subsidio']}".replace("  ", " "), False
    if args is None:
        return "/trese-apf-aproximacao ./pedido.md", True
    if c.get("sem_delimitador"):
        return f"/trese-apf-aproximacao {args} ./pedido.md", True
    return f"/trese-apf-aproximacao {args} -- ./pedido.md", True


def preparar_ws(nome: str, subsidio: Optional[str]) -> Path:
    BASE_WS.mkdir(parents=True, exist_ok=True)
    ws = Path(tempfile.mkdtemp(prefix=f"{nome}-", dir=BASE_WS)).resolve()
    shutil.copytree(SKILL, ws / ".claude" / "skills" / "trese-apf-aproximacao",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (ws / "tmp").mkdir()
    if subsidio is not None:
        (ws / "pedido.md").write_text(subsidio, encoding="utf-8")
    return ws


def rodar_claude(ws: Path, prompt: str, saida: Path, sessao: Optional[str] = None, retomar: bool = False) -> Dict[str, Any]:
    """Um turno do executor. Sem `sessao`, execução isolada e sem persistência. Com `sessao` (camada 2): o primeiro
    turno cria a sessão com esse UUID (`--session-id`) e os seguintes a retomam (`--resume`); a persistência é
    necessária para retomar."""
    cfg = CONFIG
    if sessao is None:
        persistencia = ["--no-session-persistence"]
    else:
        persistencia = ["--resume", sessao] if retomar else ["--session-id", sessao]
    cmd = [cfg["cmd"], "-p", prompt, "--model", cfg["modelo"], "--effort", cfg["esforco"],
           "--output-format", "stream-json", "--verbose"] + persistencia + cfg["perfil"]
    env = dict(os.environ, TMPDIR=str(ws / "tmp"))
    inicio = dt.datetime.now()
    try:
        r = subprocess.run(cmd, cwd=ws, env=env, capture_output=True, text=True, timeout=cfg["timeout_s"])
        codigo, stdout, stderr = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        parcial = e.stdout or ""
        codigo, stdout, stderr = "timeout", parcial.decode() if isinstance(parcial, bytes) else parcial, "timeout"
    (saida / "trace.jsonl").write_text(stdout, encoding="utf-8")
    (saida / "stderr.txt").write_text(stderr or "", encoding="utf-8")
    (saida / "comando.json").write_text(json.dumps({"cmd": cmd, "cwd": str(ws)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"codigo": codigo, "segundos": (dt.datetime.now() - inicio).total_seconds()}
