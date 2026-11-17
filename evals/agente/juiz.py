"""Tudo o que determina o que o JUIZ recebe: instruções, dossiê, CLI e modelo.
Entra no hash do juiz (com calibração, schema e gabaritos); cada julgamento registra também o hash do dossiê."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import casos as C

AQUI = Path(__file__).resolve().parent
GABARITOS = AQUI.parent / "gabaritos-iniciais.md"
BASE_WS = Path("/tmp/apf-evals")

CONFIG = {
    "cmd": "codex",
    "modelo": "gpt-6.1-sol",
    "esforco": "high",
    "timeout_s": 900,
}

PROMPT_SONDA = "Responda apenas com a palavra OK. Não use ferramentas."


INSTRUCOES_JUIZ = """Você é o juiz de uma avaliação. Um agente executou a skill `nesma-apf-estimator` (estimativa de pontos de função NESMA) sobre o subsídio abaixo. Avalie o resultado dele contra o gabarito aprovado e as convenções. Não use ferramentas, não leia arquivos e não execute comandos: tudo o que você precisa está neste texto.

Critérios (responda um booleano para cada, com justificativa curta e uma citação literal do JSON ou da resposta que sustente o veredito; se não houver o que citar, use ""):
- K3: nenhuma função listada como PROIBIDA no gabarito foi contada (em `funcoes`), nem com outro nome.
- S1: as funções obrigatórias do gabarito estão presentes com o tipo correto (e, em melhoria, a operação correta), correspondendo NOME A NOME e PELO SIGNIFICADO, não só pela contagem de tipos. Uma função trocada por outra do mesmo tipo reprova. Nos casos avaliados por rubrica, aplique a rubrica do gabarito.
- S3: hipóteses e cenários coerentes: toda hipótese que muda o total está registrada com o efeito; alternativas que se excluem estão no mesmo grupo; nenhum cenário (mínimo ou máximo) descreve uma aplicação impossível, como contar a mesma entidade como ALI e AIE ao mesmo tempo, ou um arquivo sem processo que o mantenha ou leia. Se não houver hipóteses e o gabarito não exigir, aprove.
- S4: todas as pendências obrigatórias do gabarito aparecem (com estas ou outras palavras) em `pendencias`. Se o gabarito não exigir pendências, aprove.
- S5: rastreabilidade: o campo `requisito` de cada função cita ou parafraseia fielmente um trecho que EXISTE no subsídio, ou a função está ligada a uma hipótese cujo trecho existe. Compare com o subsídio original; trecho inventado ou distorcido reprova.
Em `observacoes`, registre qualquer outro problema relevante que você notar (não afeta os critérios).
"""


def secao_gabarito(nome: str) -> str:
    texto = GABARITOS.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(nome)} ·.*?(?=^## |\Z)", texto, re.S | re.M)
    return m.group(0).strip() if m else ""


def secao_convencoes() -> str:
    texto = GABARITOS.read_text(encoding="utf-8")
    m = re.search(r"^## Convenções usadas nos gabaritos.*?(?=^## )", texto, re.S | re.M)
    return m.group(0).strip() if m else ""


def montar_dossie(caso_id: str, invocacao: str, subsidio: str, est: Dict[str, Any], resposta: str, nota: str = "") -> str:
    c = C.CASOS[caso_id]
    partes = [INSTRUCOES_JUIZ,
              "## Invocação exata\n\n" + invocacao,
              "## Subsídio completo (fonte da verdade para S5)\n\n" + subsidio,
              "## Gabarito do caso\n\n" + secao_gabarito(c.get("secao", caso_id))]
    if nota:
        partes.append("## Nota sobre esta variante\n\n" + nota)
    partes += ["## Convenções\n\n" + secao_convencoes(),
               "## JSON canônico produzido pelo agente\n\n```json\n" + json.dumps(est, ensure_ascii=False, indent=2) + "\n```",
               "## Resposta final do agente\n\n" + resposta]
    return "\n\n".join(partes)


def rodar_codex(prompt: str, saida: Path, com_schema: bool = True) -> Dict[str, Any]:
    cfg = CONFIG
    vazio = Path(tempfile.mkdtemp(prefix="juiz-", dir=BASE_WS if BASE_WS.exists() else None))
    ultimo = saida / "veredito_bruto.txt"
    cmd = [cfg["cmd"], "exec", "-m", cfg["modelo"], "-c", f'model_reasoning_effort="{cfg["esforco"]}"',
           "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json",
           "-C", str(vazio), "-o", str(ultimo)]
    if com_schema:
        cmd += ["--output-schema", str(AQUI / "veredito.schema.json")]
    cmd.append("-")
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=cfg["timeout_s"])
        codigo, stdout, stderr = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        codigo, stdout, stderr = "timeout", "", "timeout"
    (saida / "juiz_trace.jsonl").write_text(stdout or "", encoding="utf-8")
    (saida / "juiz_stderr.txt").write_text(stderr or "", encoding="utf-8")
    (saida / "juiz_dossie.md").write_text(prompt, encoding="utf-8")
    acoes = []
    for linha in (stdout or "").splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        item = ev.get("item") or {}
        if item.get("type") in ("command_execution", "file_change", "mcp_tool_call", "web_search"):
            acoes.append(item.get("type"))
    texto = ultimo.read_text(encoding="utf-8") if ultimo.exists() else ""
    return {"codigo": codigo, "texto": texto, "acoes": acoes, "stderr": (stderr or "")[-2000:]}


def interpretar_veredito(texto: str) -> Optional[Dict[str, Any]]:
    try:
        v = json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texto, re.S)
        if not m:
            return None
        try:
            v = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    if not all(isinstance(v.get(k), dict) and isinstance(v[k].get("ok"), bool) for k in ("K3", "S1", "S3", "S4", "S5")):
        return None
    return v
