#!/usr/bin/env python3
"""Runner dos evals do agente da skill nesma-apf-estimator.

Uma tarefa por chamada. Tarefas que consomem cota: executor (Claude) e juiz (Codex).
O orquestrador lê a cota antes de cada uma e só então chama `executar`.

    python3 evals/agente/runner.py preparar <rodada> {sondas|calibracao|curta|completa}
    python3 evals/agente/runner.py proxima  <rodada>          # próxima tarefa pendente (JSON)
    python3 evals/agente/runner.py executar <rodada> <tarefa> # roda UMA tarefa
    python3 evals/agente/runner.py status   <rodada>          # resumo
    python3 evals/agente/runner.py comparar <rodada>          # relações metamórficas (sem cota)

Resultados em evals/agente/resultados/<rodada>/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SKILL = RAIZ / "nesma-apf-estimator"
GABARITOS = RAIZ / "evals" / "gabaritos-iniciais.md"
RESULTADOS = AQUI / "resultados"
BASE_WS = Path("/tmp/apf-evals")

sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(SKILL / "scripts"))
import apf  # noqa: E402  (cópia confiável, do repositório)
import calibracao  # noqa: E402
import casos as C  # noqa: E402

CONFIG = {
    "executor": {
        "cmd": "claude",
        "modelo": "claude-sonnet-5-5",
        "esforco": "high",
        # Perfil a validar pela sondagem. Se a sondagem mostrar que a skill não é descoberta em
        # --restricted, o perfil muda por decisão registrada, não por fallback automático.
        "perfil": ["--restricted", "--strict-mcp-config",
                   "--tools", "Read,Write,Edit,Glob,Grep,Bash,Skill",
                   "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash,Skill",
                   "--permission-prompts", "none"],
        "timeout_s": 1200,
    },
    "juiz": {
        "cmd": "codex",
        "modelo": "gpt-6.1-sol",
        "esforco": "high",
        "timeout_s": 900,
    },
}


# --------------------------------------------------------------------------- utilidades

def agora() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def sha_arvore(raiz: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(raiz.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(raiz)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def sha_arquivos(*caminhos: Path) -> str:
    h = hashlib.sha256()
    for p in caminhos:
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def config_hash() -> str:
    h = hashlib.sha256()
    h.update(sha_arvore(SKILL).encode())
    h.update(sha_arquivos(AQUI / "casos.py", AQUI / "calibracao.py", AQUI / "runner.py",
                          AQUI / "veredito.schema.json", GABARITOS).encode())
    h.update(json.dumps(CONFIG, sort_keys=True).encode())
    return h.hexdigest()[:16]


def dir_rodada(rodada: str) -> Path:
    return RESULTADOS / rodada


def carregar_estado(rodada: str) -> Dict[str, Any]:
    with open(dir_rodada(rodada) / "estado.json", encoding="utf-8") as fh:
        return json.load(fh)


def salvar_estado(rodada: str, estado: Dict[str, Any]) -> None:
    p = dir_rodada(rodada) / "estado.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def registrar(rodada: str, linha: Dict[str, Any]) -> None:
    with open(dir_rodada(rodada) / "resultados.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")


def versoes() -> Dict[str, str]:
    out = {}
    for nome, cmd in (("claude", ["claude", "--version"]), ("codex", ["codex", "--version"])):
        try:
            out[nome] = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception as e:  # pragma: no cover
            out[nome] = f"erro: {e}"
    return out


# --------------------------------------------------------------------------- preparação

def preparar(rodada: str, tipo: str, reps: int, so: Optional[List[str]]) -> None:
    d = dir_rodada(rodada)
    if (d / "estado.json").exists():
        sys.exit(f"rodada '{rodada}' já existe; use outro nome ou continue com 'proxima'")
    d.mkdir(parents=True)
    tarefas: Dict[str, Dict[str, Any]] = {}
    if tipo == "sondas":
        tarefas["sonda-exec-skill"] = {"tipo": "sonda-exec", "variante": "skill", "consome": "claude"}
        tarefas["sonda-exec-contexto"] = {"tipo": "sonda-exec", "variante": "contexto", "consome": "claude"}
        tarefas["sonda-juiz"] = {"tipo": "sonda-juiz", "consome": "codex"}
    elif tipo == "calibracao":
        for did, caso, _, alvo in calibracao.dossies():
            tarefas[f"calib-{did}"] = {"tipo": "calib", "dossie": did, "caso": caso, "alvo": alvo, "consome": "codex"}
    else:
        ids = so or list(C.CASOS)
        for r in range(1, reps + 1):
            for cid in ids:
                tarefas[f"exec-{cid}-r{r}"] = {"tipo": "exec", "caso": cid, "rep": r, "consome": "claude"}
                c = C.CASOS[cid]
                if c["tipo"] == "contagem" and not c.get("sem_juiz"):
                    tarefas[f"juiz-{cid}-r{r}"] = {"tipo": "juiz", "caso": cid, "rep": r, "consome": "codex",
                                                   "depende": f"exec-{cid}-r{r}"}
    for t in tarefas.values():
        t["fase"] = "pendente"
    estado = {"rodada": rodada, "tipo": tipo, "criada": agora(), "config_hash": config_hash(),
              "config": CONFIG, "versoes": versoes(), "tarefas": tarefas}
    salvar_estado(rodada, estado)
    print(json.dumps({"rodada": rodada, "tarefas": len(tarefas), "config_hash": estado["config_hash"]}, ensure_ascii=False))


def proxima(rodada: str) -> Dict[str, Any]:
    estado = carregar_estado(rodada)
    if estado["config_hash"] != config_hash():
        return {"erro": "configuração mudou desde a preparação da rodada; prepare uma rodada nova"}
    for tid, t in estado["tarefas"].items():
        if t["fase"] != "pendente":
            continue
        dep = t.get("depende")
        if dep:
            fd = estado["tarefas"][dep]["fase"]
            if fd == "pendente":
                continue
            if fd == "invalido" or not estado["tarefas"][dep].get("tem_json"):
                t["fase"] = "pulado"
                t["motivo"] = f"dependência {dep} sem resultado julgável ({fd})"
                salvar_estado(rodada, estado)
                continue
        return {"tarefa": tid, "consome": t["consome"], "tipo": t["tipo"]}
    return {"fim": True}


# --------------------------------------------------------------------------- executor

def montar_invocacao(c: Dict[str, Any]) -> Tuple[str, bool]:
    """(prompt, precisa_arquivo_pedido)."""
    t = c["tipo"]
    if t in ("nl_confirma", "nl_executa"):
        return c["prosa"], c.get("subsidio") is not None
    if c.get("arquivo_inexistente"):
        return f"/nesma-apf-estimator -- {c['arquivo_inexistente']}", False
    args = c.get("args")
    if c.get("inline"):
        if args is None:
            return f"/nesma-apf-estimator {c['subsidio']}", False
        return f"/nesma-apf-estimator {args} -- {c['subsidio']}".replace("  ", " "), False
    if args is None:
        return "/nesma-apf-estimator ./pedido.md", True
    if c.get("sem_delimitador"):
        return f"/nesma-apf-estimator {args} ./pedido.md", True
    return f"/nesma-apf-estimator {args} -- ./pedido.md", True


def preparar_ws(nome: str, subsidio: Optional[str]) -> Path:
    BASE_WS.mkdir(parents=True, exist_ok=True)
    ws = Path(tempfile.mkdtemp(prefix=f"{nome}-", dir=BASE_WS)).resolve()
    shutil.copytree(SKILL, ws / ".claude" / "skills" / "nesma-apf-estimator",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (ws / "tmp").mkdir()
    if subsidio is not None:
        (ws / "pedido.md").write_text(subsidio, encoding="utf-8")
    return ws


def rodar_claude(ws: Path, prompt: str, saida: Path) -> Dict[str, Any]:
    cfg = CONFIG["executor"]
    cmd = [cfg["cmd"], "-p", prompt, "--model", cfg["modelo"], "--effort", cfg["esforco"],
           "--output-format", "stream-json", "--verbose", "--no-session-persistence"] + cfg["perfil"]
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


def ler_trace(caminho: Path) -> Dict[str, Any]:
    eventos = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            eventos.append(json.loads(linha))
        except json.JSONDecodeError:
            pass
    init = next((e for e in eventos if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    ferramentas, textos = [], []
    for e in eventos:
        if e.get("type") == "assistant":
            for bloco in (e.get("message") or {}).get("content") or []:
                if isinstance(bloco, dict) and bloco.get("type") == "tool_use":
                    ferramentas.append({"nome": bloco.get("name"), "entrada": bloco.get("input") or {}})
                elif isinstance(bloco, dict) and bloco.get("type") == "text" and (bloco.get("text") or "").strip():
                    textos.append(bloco["text"])
    final = result.get("result") if isinstance(result.get("result"), str) else ""
    if final and (not textos or textos[-1].strip() != final.strip()):
        textos.append(final)
    # texto_final: tudo o que o agente escreveu ao usuário, na ordem (a tabela pode vir antes da exportação).
    return {"init": init, "result": result, "ferramentas": ferramentas, "texto_final": "\n\n".join(textos)}


PERMITIDOS_ABS = ("/usr/bin/", "/bin/", "/usr/local/bin/", "/opt/homebrew/bin/", "/dev/null", "/usr/sbin/")
REDE = re.compile(r"\b(curl|wget|nc|ssh|scp|rsync|ftp)\b|https?://", re.I)


def auditar(ferramentas: List[Dict[str, Any]], ws: Path) -> List[str]:
    """Acessos observáveis fora do diretório da execução."""
    raizes = {str(ws), str(ws).replace("/private/tmp/", "/tmp/"), str(ws).replace("/tmp/", "/private/tmp/")}
    problemas = []

    def dentro(p: str) -> bool:
        return any(p == r or p.startswith(r + "/") for r in raizes)

    for f in ferramentas:
        nome, ent = f["nome"], f["entrada"]
        if nome in ("WebFetch", "WebSearch"):
            problemas.append(f"{nome}: acesso à rede")
        if nome in ("Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit"):
            for chave in ("file_path", "path", "notebook_path"):
                v = ent.get(chave)
                if isinstance(v, str) and v:
                    p = v if v.startswith("/") else str((ws / v))
                    if ".." in Path(v).parts or not dentro(os.path.normpath(p)):
                        problemas.append(f"{nome} fora do diretório: {v}")
        if nome == "Bash":
            cmd = ent.get("command") or ""
            if REDE.search(cmd):
                problemas.append(f"Bash com rede: {cmd[:120]}")
            if re.search(r"(^|[\s'\"=(])~(/|\s|$)", cmd):
                problemas.append(f"Bash com ~: {cmd[:120]}")
            if re.search(r"(^|[\s'\"=/])\.\.(/|\s|$)", cmd):
                problemas.append(f"Bash com '..': {cmd[:120]}")
            for m in re.finditer(r"(?<![\w.$}])(/[\w.@+\-]+(?:/[\w.@+\-]*)*)", cmd):
                p = m.group(1)
                if dentro(p) or p.startswith(PERMITIDOS_ABS) or p in ("/", "/tmp"):
                    continue
                problemas.append(f"Bash fora do diretório: {p}")
    return problemas


def arquivos_criados(ws: Path) -> List[str]:
    out = []
    for p in ws.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ws)
        if rel.parts[0] == ".claude" or str(rel) == "pedido.md":
            continue
        out.append(str(rel))
    return sorted(out)


def achar_json(ws: Path) -> Optional[Path]:
    candidatos = []
    for p in ws.rglob("*.json"):
        if ".claude" in p.relative_to(ws).parts:
            continue
        try:
            dados = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(dados, dict) and dados.get("versao_esquema") == 1:
            candidatos.append(p)
    if not candidatos:
        return None
    return max(candidatos, key=lambda p: p.stat().st_mtime)


def normalizar(texto: str) -> str:
    return "\n".join(l.rstrip() for l in texto.replace("\r\n", "\n").split("\n")).strip()


def comeca_com_alerta(texto: str) -> bool:
    linhas = [l.strip() for l in texto.strip().splitlines() if l.strip() and not l.strip().startswith("```")]
    return bool(linhas) and linhas[0].upper().startswith("ALERTA")


def tem_contagem(texto: str) -> bool:
    return bool(re.search(r"\d+(,\d+)?\s*(PF|PFM)\b", texto)) or texto.count("|") >= 6


def chamadas_apf(ferramentas: List[Dict[str, Any]]) -> List[str]:
    return [f["entrada"].get("command", "") for f in ferramentas
            if f["nome"] == "Bash" and "apf.py" in (f["entrada"].get("command") or "")]


def toca_pedido(ferramentas: List[Dict[str, Any]]) -> bool:
    return any("pedido.md" in json.dumps(f["entrada"], ensure_ascii=False) for f in ferramentas)


def multiconjunto(est: Dict[str, Any]) -> List[Tuple[str, Optional[str]]]:
    return sorted(((f["tipo"], f.get("operacao")) for f in est["funcoes"]), key=lambda x: (x[0], x[1] or ""))


def conteudo_xlsx(dados: bytes) -> Dict[str, bytes]:
    with zipfile.ZipFile(__import__("io").BytesIO(dados)) as z:
        return {n: z.read(n) for n in z.namelist() if n.startswith("xl/")}


def verificar(c: Dict[str, Any], ws: Path, tr: Dict[str, Any], hash_antes: str) -> Dict[str, Any]:
    v: Dict[str, Any] = {"criterios": {}, "invalido": None}
    crit = v["criterios"]
    if not tr["result"] or tr["result"].get("is_error"):
        v["invalido"] = "execução sem resultado (erro, autenticação ou timeout)"
        return v
    if sha_arvore(ws / ".claude" / "skills" / "nesma-apf-estimator") != hash_antes:
        v["invalido"] = "a cópia da skill foi modificada durante a execução"
        return v
    acessos = auditar(tr["ferramentas"], ws)
    if acessos:
        v["invalido"] = "contaminada: " + "; ".join(acessos[:5])
        return v

    texto = tr["texto_final"]
    criados = arquivos_criados(ws)
    apf_cmds = chamadas_apf(tr["ferramentas"])
    t = c["tipo"]

    if t in ("alerta1", "alerta2"):
        crit["K1"] = {
            "alerta": comeca_com_alerta(texto),
            "sem_script": not apf_cmds,
            "sem_arquivos": not criados,
            "sem_contagem": not tem_contagem(texto),
        }
        if t == "alerta1":
            crit["K1"]["sem_acesso_ao_subsidio"] = not toca_pedido(tr["ferramentas"])
        crit["K1"]["ok"] = all(crit["K1"].values())
        return v

    if t == "nl_confirma":
        crit["K1"] = {
            "sem_script": not apf_cmds,
            "sem_arquivos": not criados,
            "mostra_invocacao": c["espera_invocacao"] in texto,
            "pede_confirmacao": "?" in texto,
            "sem_contagem": not tem_contagem(texto),
        }
        crit["K1"]["ok"] = all(crit["K1"].values())
        return v

    # Execução esperada (contagem, valido, nl_executa)
    k1 = {"sem_alerta": not comeca_com_alerta(texto),
          "check": any(" check " in f" {x} " for x in apf_cmds),
          "render": any(" render " in f" {x} " for x in apf_cmds)}
    k1["ok"] = all(k1.values())
    crit["K1"] = k1
    caminho_json = achar_json(ws)
    v["tem_json"] = caminho_json is not None
    if caminho_json is None:
        crit["K2"] = {"ok": False, "motivo": "JSON canônico não encontrado"}
        return v
    est = json.loads(caminho_json.read_text(encoding="utf-8"))
    v["json"] = str(caminho_json.relative_to(ws))
    erros = apf.validar(est)
    if erros:
        crit["K2"] = {"ok": False, "motivo": "JSON inválido: " + "; ".join(erros[:5])}
        return v
    calc = apf.calcular(est)
    md = apf.render_md(est, calc)
    k2 = {"bloco_literal": normalizar(md) in normalizar(texto)}
    exporta = c.get("exporta")
    exportados = [p for p in criados if Path(p).suffix in (".md", ".txt", ".xlsx") and not p.startswith("tmp/")]
    if exporta:
        alvo = [p for p in exportados if p.endswith("." + exporta)]
        k2["exportou"] = len(alvo) == 1
        if alvo:
            dados = (ws / alvo[0]).read_bytes()
            if exporta == "xlsx":
                k2["exportacao_identica"] = conteudo_xlsx(dados) == conteudo_xlsx(apf.gerar_xlsx(est, calc))
            else:
                confiavel = md if exporta == "md" else apf.render_txt(est, calc)
                k2["exportacao_identica"] = normalizar(dados.decode("utf-8")) == normalizar(confiavel)
    else:
        k2["nada_exportado"] = not exportados
    if c.get("pergunta_formato") or (t == "contagem" and not exporta):
        k2["perguntou_formato"] = bool(re.search(r"export", texto, re.I))
    k2["ok"] = all(x for x in k2.values() if isinstance(x, bool))
    crit["K2"] = k2

    if t in ("valido", "nl_executa"):
        esp = c.get("espera", {})
        crit["config"] = {k: est.get(k) == val for k, val in esp.items()}
        crit["config"]["ok"] = all(crit["config"].values())
        return v

    # contagem
    unidade = c.get("unidade")
    if unidade:
        crit["K4"] = {"ok": calc["unidade"] == unidade, "obtido": calc["unidade"]}
    if c.get("cobertura"):
        crit["cobertura"] = {"ok": calc["cobertura"] == c["cobertura"], "obtido": calc["cobertura"]}
    if c.get("tipos"):
        obtido = multiconjunto(est)
        crit["S1_prefiltro"] = {"ok": obtido == c["tipos"], "obtido": Counter(f"{a}/{b}" for a, b in obtido),
                                "esperado": Counter(f"{a}/{b}" for a, b in c["tipos"])}
    if c.get("totais"):
        par = (calc["total_min"], calc["total_max"])
        crit["S2"] = {"ok": par in c["totais"], "obtido": [str(x) for x in par]}
    return v


def executar_exec(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    c = C.resolver(t["caso"])
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    prompt, precisa_arquivo = montar_invocacao(c)
    ws = preparar_ws(tid, c["subsidio"] if precisa_arquivo else None)
    hash_antes = sha_arvore(ws / ".claude" / "skills" / "nesma-apf-estimator")
    t.update({"ws": str(ws), "prompt": prompt, "inicio": agora()})
    r = rodar_claude(ws, prompt, saida)
    t.update({"fase": "executado", "codigo": r["codigo"], "segundos": r["segundos"]})
    tr = ler_trace(saida / "trace.jsonl")
    (saida / "resposta_final.md").write_text(tr["texto_final"] or "", encoding="utf-8")
    v = verificar(c, ws, tr, hash_antes)
    if v.get("json"):
        shutil.copy(ws / v["json"], saida / "estimativa.json")
    for rel in arquivos_criados(ws):
        destino = saida / "ws" / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ws / rel, destino)
    uso = tr["result"].get("usage") if tr["result"] else None
    t.update({"fase": "invalido" if v["invalido"] else "verificado", "motivo": v["invalido"],
              "tem_json": bool(v.get("tem_json")), "criterios": v["criterios"],
              "custo_usd": (tr["result"] or {}).get("total_cost_usd"), "uso": uso,
              "init": {k: tr["init"].get(k) for k in ("model", "apiKeySource", "permissionMode", "tools", "skills", "slash_commands", "cwd")}})
    return t


# --------------------------------------------------------------------------- sondas

def executar_sonda_exec(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    if t["variante"] == "skill":
        ws = preparar_ws(tid, C.CURTO)
        prompt = "/nesma-apf-estimator modo=detalhada -- ./pedido.md"
    else:
        ws = preparar_ws(tid, None)
        prompt = ("Responda só com uma lista. 1) Quais arquivos de instrução (CLAUDE.md, AGENTS.md ou semelhantes) ou "
                  "memórias foram carregados no seu contexto? Dê os caminhos ou diga 'nenhum'. 2) Quais skills estão "
                  "disponíveis? 3) Quais ferramentas você tem? Não use nenhuma ferramenta.")
    r = rodar_claude(ws, prompt, saida)
    tr = ler_trace(saida / "trace.jsonl")
    (saida / "resposta_final.md").write_text(tr["texto_final"] or "", encoding="utf-8")
    t.update({"fase": "verificado" if tr["result"] and not tr["result"].get("is_error") else "invalido",
              "codigo": r["codigo"], "ws": str(ws), "prompt": prompt,
              "init": tr["init"], "resposta": tr["texto_final"][:3000], "ferramentas_usadas": tr["ferramentas"],
              "custo_usd": (tr["result"] or {}).get("total_cost_usd"), "uso": (tr["result"] or {}).get("usage"),
              "stderr": (saida / "stderr.txt").read_text(encoding="utf-8")[:2000]})
    return t


# --------------------------------------------------------------------------- juiz

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
    cfg = CONFIG["juiz"]
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


def executar_juiz(rodada: str, tid: str, t: Dict[str, Any], estado: Dict[str, Any]) -> Dict[str, Any]:
    dep = estado["tarefas"][t["depende"]]
    pasta_exec = dir_rodada(rodada) / t["depende"]
    est = json.loads((pasta_exec / "estimativa.json").read_text(encoding="utf-8"))
    resposta = (pasta_exec / "resposta_final.md").read_text(encoding="utf-8")
    c = C.CASOS[t["caso"]]
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    dossie = montar_dossie(t["caso"], dep["prompt"], c["subsidio"], est, resposta, c.get("nota_juiz", ""))
    r = rodar_codex(dossie, saida)
    v = interpretar_veredito(r["texto"])
    if r["acoes"]:
        t.update({"fase": "invalido", "motivo": "juiz usou ferramentas: " + ", ".join(sorted(set(r["acoes"])))})
    elif v is None:
        t.update({"fase": "invalido", "motivo": f"veredito ilegível (código {r['codigo']}): {r['stderr'][-300:]}"})
    else:
        t.update({"fase": "julgado", "veredito": v})
    return t


def executar_calib(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    dossies = {d[0]: d for d in calibracao.dossies()}
    _, caso, est, alvo = dossies[t["dossie"]]
    erros = apf.validar(est)
    if erros:
        t.update({"fase": "invalido", "motivo": "dossiê de calibração inválido: " + "; ".join(erros)})
        return t
    resposta = apf.render_md(est, apf.calcular(est))
    c = C.CASOS[caso]
    prompt, _ = montar_invocacao(c)
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    r = rodar_codex(montar_dossie(caso, prompt, c["subsidio"], est, resposta), saida)
    v = interpretar_veredito(r["texto"])
    if r["acoes"]:
        t.update({"fase": "invalido", "motivo": "juiz usou ferramentas"})
    elif v is None:
        t.update({"fase": "invalido", "motivo": f"veredito ilegível (código {r['codigo']}): {r['stderr'][-300:]}"})
    else:
        reprovados = sorted(k for k in ("K3", "S1", "S3", "S4", "S5") if not v[k]["ok"])
        acertou = (not alvo and not reprovados) or (alvo and all(a in reprovados for a in alvo))
        t.update({"fase": "julgado", "veredito": v, "reprovados": reprovados, "acertou": acertou})
    return t


def executar_sonda_juiz(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    r = rodar_codex("Responda apenas com a palavra OK. Não use ferramentas.", saida, com_schema=False)
    ok = r["codigo"] == 0 and "OK" in r["texto"].upper()
    t.update({"fase": "verificado" if ok else "invalido", "codigo": r["codigo"], "resposta": r["texto"][:200],
              "stderr": r["stderr"], "acoes": r["acoes"]})
    return t


# --------------------------------------------------------------------------- comandos

def executar(rodada: str, tid: str) -> None:
    estado = carregar_estado(rodada)
    if estado["config_hash"] != config_hash():
        sys.exit("configuração mudou desde a preparação da rodada; prepare uma rodada nova")
    t = estado["tarefas"].get(tid)
    if t is None:
        sys.exit(f"tarefa inexistente: {tid}")
    if t["fase"] != "pendente":
        sys.exit(f"tarefa {tid} já está em '{t['fase']}'")
    t["inicio"] = agora()
    try:
        if t["tipo"] == "exec":
            executar_exec(rodada, tid, t)
        elif t["tipo"] == "juiz":
            executar_juiz(rodada, tid, t, estado)
        elif t["tipo"] == "calib":
            executar_calib(rodada, tid, t)
        elif t["tipo"] == "sonda-exec":
            executar_sonda_exec(rodada, tid, t)
        elif t["tipo"] == "sonda-juiz":
            executar_sonda_juiz(rodada, tid, t)
    except Exception as e:  # falha operacional: registrada, nunca aprovação
        t.update({"fase": "invalido", "motivo": f"erro do runner: {type(e).__name__}: {e}"})
    t["fim"] = agora()
    salvar_estado(rodada, estado)
    registrar(rodada, {"tarefa": tid, **{k: v for k, v in t.items() if k not in ("init", "ferramentas_usadas")}})
    print(json.dumps(resumo_tarefa(tid, t), ensure_ascii=False, default=str))


def resumo_tarefa(tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    r = {"tarefa": tid, "fase": t["fase"]}
    if t.get("motivo"):
        r["motivo"] = t["motivo"]
    if "criterios" in t:
        r["criterios"] = {k: v.get("ok") for k, v in t["criterios"].items()}
    if "veredito" in t:
        r["juiz"] = {k: t["veredito"][k]["ok"] for k in ("K3", "S1", "S3", "S4", "S5")}
    if "acertou" in t:
        r["acertou"] = t["acertou"]
    if t.get("custo_usd") is not None:
        r["custo_usd"] = t["custo_usd"]
    return r


def status(rodada: str) -> None:
    estado = carregar_estado(rodada)
    fases = Counter(t["fase"] for t in estado["tarefas"].values())
    print(json.dumps({"rodada": rodada, "config_hash": estado["config_hash"],
                      "config_atual_igual": estado["config_hash"] == config_hash(),
                      "fases": fases,
                      "tarefas": [resumo_tarefa(tid, t) for tid, t in estado["tarefas"].items() if t["fase"] != "pendente"]},
                     ensure_ascii=False, indent=1, default=str))


def comparar(rodada: str) -> None:
    estado = carregar_estado(rodada)
    out = {}
    for nome, (a, b, rel) in C.PARES.items():
        for r in sorted({t["rep"] for t in estado["tarefas"].values() if t["tipo"] == "exec"}):
            pa, pb = dir_rodada(rodada) / f"exec-{a}-r{r}" / "estimativa.json", dir_rodada(rodada) / f"exec-{b}-r{r}" / "estimativa.json"
            if not (pa.exists() and pb.exists()):
                out[f"{nome}-r{r}"] = {"ok": None, "motivo": "faltam resultados"}
                continue
            ea, eb = json.loads(pa.read_text()), json.loads(pb.read_text())
            ca, cb = apf.calcular(ea), apf.calcular(eb)
            ma, mb = multiconjunto(ea), multiconjunto(eb)
            if nome == "M05":
                esperado_b = sorted(ma + [("EE", "A")], key=lambda x: (x[0], x[1] or ""))
                ok = (mb == esperado_b and (ca["total_min"], ca["total_max"]) == (Decimal(20), Decimal(20))
                      and (cb["total_min"], cb["total_max"]) == (Decimal("14.75"), Decimal("14.75")))
            else:
                ok = ma == mb and (ca["total_min"], ca["total_max"]) == (cb["total_min"], cb["total_max"])
            out[f"{nome}-r{r}"] = {"ok": ok, "relacao": rel,
                                   "a": [str(ca["total_min"]), str(ca["total_max"])], "b": [str(cb["total_min"]), str(cb["total_max"])]}
    (dir_rodada(rodada) / "metamorficos.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("preparar")
    sp.add_argument("rodada")
    sp.add_argument("tipo", choices=("sondas", "calibracao", "curta", "completa"))
    sp.add_argument("--casos", help="lista separada por vírgula")
    for nome in ("proxima", "status", "comparar"):
        sub.add_parser(nome).add_argument("rodada")
    sp = sub.add_parser("executar")
    sp.add_argument("rodada")
    sp.add_argument("tarefa")
    a = ap.parse_args()
    if a.cmd == "preparar":
        reps = 5 if a.tipo == "completa" else 1
        preparar(a.rodada, a.tipo, reps, a.casos.split(",") if a.casos else None)
    elif a.cmd == "proxima":
        print(json.dumps(proxima(a.rodada), ensure_ascii=False))
    elif a.cmd == "executar":
        executar(a.rodada, a.tarefa)
    elif a.cmd == "status":
        status(a.rodada)
    elif a.cmd == "comparar":
        comparar(a.rodada)


if __name__ == "__main__":
    main()
