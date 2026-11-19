#!/usr/bin/env python3
"""Runner dos evals do agente da skill trese-apf-aproximacao.

Comandos a partir de trese-apf-skills/dev/trese-apf-aproximacao/.

Uma tarefa por chamada. Tarefas que consomem cota: executor (Claude) e juiz (Codex).
O orquestrador lê a cota antes de cada uma e só então chama `executar`.

    python3 evals/agente/runner.py preparar <rodada> {sondas|calibracao|curta|completa}
    python3 evals/agente/runner.py proxima  <rodada>          # próxima tarefa pendente (JSON)
    python3 evals/agente/runner.py executar <rodada> <tarefa> # roda UMA tarefa
    python3 evals/agente/runner.py status   <rodada>          # resumo
    python3 evals/agente/runner.py comparar <rodada>          # relações metamórficas e de diálogo (sem cota)
    python3 evals/agente/runner.py preparar <rodada> dialogo [--casos D2a,...] [--reps N]   # camada 2
    python3 evals/agente/runner.py limpar-sessoes <rodada>    # camada 2: guarda e apaga as sessões do Claude

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
import uuid
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent                            # trese-apf-skills/dev/<skill> (desenvolvimento)
SKILL = RAIZ.parent.parent / "skills" / RAIZ.name     # trese-apf-skills/skills/<skill> (distribuída)
GABARITOS = RAIZ / "evals" / "gabaritos-iniciais.md"
RESULTADOS = AQUI / "resultados"
BASE_WS = Path("/tmp/apf-evals")

sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(SKILL / "scripts"))
import apf  # noqa: E402  (cópia confiável, do repositório)
import calibracao  # noqa: E402
import casos as C  # noqa: E402

import execucao as E  # noqa: E402
import juiz as J  # noqa: E402
from execucao import montar_invocacao, preparar_ws, rodar_claude  # noqa: E402,F401
from juiz import interpretar_veredito, montar_dossie, rodar_codex, secao_gabarito  # noqa: E402,F401

CONFIG = {"executor": E.CONFIG, "juiz": J.CONFIG}


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


def hash_execucao() -> str:
    """O que determina o pedido e o ambiente do executor: skill, casos, runner e perfil."""
    h = hashlib.sha256()
    h.update(sha_arvore(SKILL).encode())
    h.update(sha_arquivos(AQUI / "casos.py", AQUI / "execucao.py").encode())
    return h.hexdigest()[:16]


def hash_juiz() -> str:
    """O que determina o pedido ao juiz, além do dossiê de cada tarefa (registrado por tarefa)."""
    h = hashlib.sha256()
    h.update(sha_arquivos(AQUI / "juiz.py", AQUI / "calibracao.py", AQUI / "veredito.schema.json",
                          AQUI / "veredito-previa.schema.json", GABARITOS).encode())
    return h.hexdigest()[:16]


def config_hash() -> str:
    """Identificador combinado (compatibilidade e exibição)."""
    return hashlib.sha256((hash_execucao() + hash_juiz()).encode()).hexdigest()[:16]


def hashes_compativeis(estado: Dict[str, Any], tarefa: Dict[str, Any]) -> Optional[str]:
    if "hash_execucao" not in estado:
        return "rodada no formato antigo; rode 'reverificar --migrar-de <commit>' antes de continuar"
    if tarefa["consome"] == "claude" and estado["hash_execucao"] != hash_execucao():
        return "a configuração de EXECUÇÃO mudou desde a preparação; prepare uma rodada nova"
    if tarefa["consome"] == "codex" and estado["hash_juiz"] != hash_juiz():
        return "a configuração do JUIZ mudou desde a preparação; prepare uma rodada nova"
    return None


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
    elif tipo == "dialogo":
        for r in range(1, reps + 1):
            for did in so or list(C.DIALOGOS):
                d = C.DIALOGOS[did]
                sessao = str(uuid.uuid4())
                anterior = None
                for k in range(1, len(d["turnos"]) + 2):
                    tid = f"exec-{did}-r{r}-t{k}"
                    tarefas[tid] = {"tipo": "exec", "caso": did, "dialogo": did, "turno": k, "rep": r,
                                    "sessao": sessao, "consome": "claude"}
                    if anterior:
                        tarefas[tid]["depende"] = anterior
                    if k > 1 and d["turnos"][k - 2].get("juiz"):
                        tarefas[f"juiz-{did}-r{r}-t{k}"] = {"tipo": "juiz", "caso": did, "dialogo": did, "turno": k,
                                                            "rep": r, "consome": "codex", "depende": tid}
                    anterior = tid
    elif tipo == "calibracao":
        for did, caso, _, alvo in calibracao.dossies():
            if so and did not in so:
                continue
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
              "hash_execucao": hash_execucao(), "hash_juiz": hash_juiz(), "hash_verificador": hash_verificador(),
              "config": CONFIG, "versoes": versoes(), "tarefas": tarefas}
    salvar_estado(rodada, estado)
    print(json.dumps({"rodada": rodada, "tarefas": len(tarefas), "config_hash": estado["config_hash"]}, ensure_ascii=False))


def proxima(rodada: str) -> Dict[str, Any]:
    estado = carregar_estado(rodada)
    for tid, t in estado["tarefas"].items():
        if t["fase"] != "pendente":
            continue
        erro = hashes_compativeis(estado, t)
        if erro:
            return {"erro": erro, "tarefa": tid}
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

from verificador import (chamadas_apf, congelar, hash_verificador, ler_trace, multiconjunto,  # noqa: E402
                         relacao_correcao, relacao_preservacao, relacao_segundo_lote, sha_arquivo,
                         verificar_snapshot)


def caso_da_tarefa(t: Dict[str, Any]) -> Dict[str, Any]:
    return C.caso_do_turno(t["dialogo"], t["turno"]) if t.get("dialogo") else C.resolver(t["caso"])


def herdados_do_dialogo(rodada: str, estado: Dict[str, Any], t: Dict[str, Any]) -> List[str]:
    """Temporários criados nos turnos anteriores do mesmo diálogo (continuam permitidos e são recopiados)."""
    out: List[str] = []
    for k in range(1, t["turno"]):
        m = dir_rodada(rodada) / f"exec-{t['dialogo']}-r{t['rep']}-t{k}" / "snapshot" / "manifesto.json"
        if m.exists():
            for p in json.loads(m.read_text(encoding="utf-8"))["temporarios"].values():
                if p not in out:
                    out.append(p)
    return out


def executar_exec(rodada: str, tid: str, t: Dict[str, Any], estado: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = caso_da_tarefa(t)
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    herdados: List[str] = []
    if t.get("dialogo") and t["turno"] > 1:  # camada 2: mesmo workspace e mesma sessão do turno anterior
        anterior = estado["tarefas"][t["depende"]]
        ws = Path(anterior["ws"])
        prompt = C.DIALOGOS[t["dialogo"]]["turnos"][t["turno"] - 2]["msg"]
        herdados = herdados_do_dialogo(rodada, estado, t)
    else:
        prompt, precisa_arquivo = montar_invocacao(c)
        ws = preparar_ws(tid, c["subsidio"] if precisa_arquivo else None)
    hash_antes = sha_arvore(ws / ".claude" / "skills" / "trese-apf-aproximacao")
    desde = dt.datetime.now().timestamp() - 1
    t.update({"ws": str(ws), "prompt": prompt, "inicio": agora(), "hash_skill": hash_antes})
    if t.get("dialogo"):
        r = rodar_claude(ws, prompt, saida, sessao=t["sessao"], retomar=t["turno"] > 1)
    else:
        r = rodar_claude(ws, prompt, saida)
    ate = dt.datetime.now().timestamp() + 1
    t.update({"fase": "executado", "codigo": r["codigo"], "segundos": r["segundos"], "janela": [desde, ate]})
    tr = ler_trace(saida / "trace.jsonl")
    (saida / "resposta_final.md").write_text(tr["texto_final"] or "", encoding="utf-8")
    congelar(ws, saida, desde, ate, hash_antes, herdados)
    if t.get("dialogo") and (tr["init"] or {}).get("session_id") not in (None, t["sessao"]):
        t["sessao_observada"] = tr["init"].get("session_id")
    aplicar_verificacao(c, saida, t)
    t.update({"custo_usd": (tr["result"] or {}).get("total_cost_usd"), "uso": (tr["result"] or {}).get("usage"),
              "init": {k: tr["init"].get(k) for k in ("model", "apiKeySource", "permissionMode", "tools", "skills", "cwd")}})
    return t


def aplicar_verificacao(c: Dict[str, Any], saida: Path, t: Dict[str, Any]) -> None:
    v = verificar_snapshot(c, saida)
    if "criterios" in t or t.get("motivo"):
        t.setdefault("historico_verificacao", []).append(
            {k: t.get(k) for k in ("fase", "motivo", "criterios", "verificador", "tem_json")})
    t.update({"fase": "invalido" if v["invalido"] else "verificado", "motivo": v["invalido"],
              "tem_json": bool(v.get("tem_json")), "criterios": v["criterios"], "verificador": v["verificador"],
              "procedencia": v.get("procedencia")})
    if v.get("json"):
        shutil.copy(saida / "snapshot" / v["json"], saida / "estimativa.json")
    elif (saida / "estimativa.json").exists():
        (saida / "estimativa.json").unlink()


# --------------------------------------------------------------------------- sondas

def executar_sonda_exec(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    if t["variante"] == "skill":
        ws = preparar_ws(tid, C.CURTO)
        prompt = E.PROMPT_SONDA_SKILL
    else:
        ws = preparar_ws(tid, None)
        prompt = E.PROMPT_SONDA_CONTEXTO
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

def mensagens_do_dialogo(did: str, ate_turno: int) -> Tuple[str, List[str]]:
    """(invocação do turno 1, mensagens do analista nos turnos 2..ate_turno)."""
    d = C.DIALOGOS[did]
    invocacao, _ = montar_invocacao(C.resolver(d["base"]))
    return invocacao, [d["turnos"][k - 2]["msg"] for k in range(2, ate_turno + 1)]


def dossie_da_tarefa(rodada: str, t: Dict[str, Any], estado: Dict[str, Any]) -> str:
    dep = estado["tarefas"][t["depende"]]
    pasta_exec = dir_rodada(rodada) / t["depende"]
    est = json.loads((pasta_exec / "estimativa.json").read_text(encoding="utf-8"))
    resposta = (pasta_exec / "resposta_final.md").read_text(encoding="utf-8")
    if t.get("dialogo"):
        d = C.DIALOGOS[t["dialogo"]]
        invocacao, mensagens = mensagens_do_dialogo(t["dialogo"], t["turno"])
        cfg = d["turnos"][t["turno"] - 2]["juiz"]
        return J.montar_dossie_dialogo(invocacao, C.CASOS[d["base"]]["subsidio"], mensagens, cfg["secao"],
                                       est, resposta, cfg.get("nota", ""))
    c = C.CASOS[t["caso"]]
    return montar_dossie(t["caso"], dep["prompt"], c["subsidio"], est, resposta, c.get("nota_juiz", ""))


def executar_juiz(rodada: str, tid: str, t: Dict[str, Any], estado: Dict[str, Any]) -> Dict[str, Any]:
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    dossie = dossie_da_tarefa(rodada, t, estado)
    t["hash_dossie"] = hashlib.sha256(dossie.encode()).hexdigest()[:16]
    previa = False if t.get("dialogo") else J.e_previa(t["caso"])
    r = rodar_codex(dossie, saida, schema=J.schema_de(None if t.get("dialogo") else t["caso"]))
    v = interpretar_veredito(r["texto"], previa=previa)
    if r["acoes"]:
        t.update({"fase": "invalido", "motivo": "juiz usou ferramentas: " + ", ".join(sorted(set(r["acoes"])))})
    elif v is None:
        t.update({"fase": "invalido", "motivo": f"veredito ilegível (código {r['codigo']}): {r['stderr'][-300:]}"})
    else:
        t.update({"fase": "julgado", "veredito": v})
    return t


def executar_calib_dialogo(rodada: str, tid: str, t: Dict[str, Any], did: str, est: Dict[str, Any],
                           alvo: List[str]) -> Dict[str, Any]:
    """Calibração do juiz final em diálogo: dossiê do primeiro turno com juiz do diálogo."""
    erros = apf.validar(est) or apf.validar_final(est)
    if erros:
        t.update({"fase": "invalido", "motivo": "dossiê de calibração inválido: " + "; ".join(erros)})
        return t
    d = C.DIALOGOS[did]
    k = next(i + 2 for i, x in enumerate(d["turnos"]) if x.get("juiz"))
    invocacao, mensagens = mensagens_do_dialogo(did, k)
    cfg = d["turnos"][k - 2]["juiz"]
    resposta = apf.render_md(est, apf.calcular(est), "chat")
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    r = rodar_codex(J.montar_dossie_dialogo(invocacao, C.CASOS[d["base"]]["subsidio"], mensagens, cfg["secao"],
                                            est, resposta, cfg.get("nota", "")), saida, schema=J.schema_de(None))
    v = interpretar_veredito(r["texto"], previa=False)
    if r["acoes"]:
        t.update({"fase": "invalido", "motivo": "juiz usou ferramentas: " + ", ".join(sorted(set(r["acoes"])))})
    elif v is None:
        t.update({"fase": "invalido", "motivo": f"veredito ilegível (código {r['codigo']}): {r['stderr'][-300:]}"})
    else:
        reprovados = reprovados_do_veredito(v, False)
        t.update({"fase": "julgado", "veredito": v, "reprovados": reprovados,
                  "acertou": sorted(reprovados) == sorted(alvo)})
    return t


def executar_calib(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    dossies = {d[0]: d for d in calibracao.dossies()}
    _, caso, est, alvo = dossies[t["dossie"]]
    if caso in C.DIALOGOS:
        return executar_calib_dialogo(rodada, tid, t, caso, est, alvo)
    previa = J.e_previa(caso)
    erros = apf.validar(est) or (apf.validar_previa(est) if previa else apf.validar_final(est))
    if erros:
        t.update({"fase": "invalido", "motivo": "dossiê de calibração inválido: " + "; ".join(erros)})
        return t
    resposta = apf.render_previa(est) if previa else apf.render_md(est, apf.calcular(est))
    c = C.CASOS[caso]
    prompt, _ = montar_invocacao(c)
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    r = rodar_codex(montar_dossie(caso, prompt, c["subsidio"], est, resposta, c.get("nota_juiz", "")), saida,
                    schema=J.schema_de(caso))
    v = interpretar_veredito(r["texto"], previa=previa)
    if r["acoes"]:
        t.update({"fase": "invalido", "motivo": "juiz usou ferramentas"})
    elif v is None:
        t.update({"fase": "invalido", "motivo": f"veredito ilegível (código {r['codigo']}): {r['stderr'][-300:]}"})
    else:
        reprovados = reprovados_do_veredito(v, previa)
        if t["dossie"] in calibracao.CALIBRACAO_EXATA:
            acertou = sorted(reprovados) == sorted(alvo)
        else:
            acertou = (not alvo and not reprovados) or (alvo and all(a in reprovados for a in alvo))
        t.update({"fase": "julgado", "veredito": v, "reprovados": reprovados, "acertou": acertou})
    return t


def reprovados_do_veredito(v: Dict[str, Any], previa: bool) -> List[str]:
    """Critérios reprovados. Na prévia inclui R; S4_antigo aparece só para conferência da calibração."""
    crit = J.CRITERIOS_PREVIA if previa else J.CRITERIOS
    out = [k for k in crit if not v[k]["ok"]]
    if previa and isinstance(v.get("S4_antigo"), dict) and not v["S4_antigo"]["ok"]:
        out.append("S4_antigo")
    return sorted(out)


def executar_sonda_juiz(rodada: str, tid: str, t: Dict[str, Any]) -> Dict[str, Any]:
    saida = dir_rodada(rodada) / tid
    saida.mkdir(exist_ok=True)
    r = rodar_codex(J.PROMPT_SONDA, saida, com_schema=False)
    ok = r["codigo"] == 0 and "OK" in r["texto"].upper()
    t.update({"fase": "verificado" if ok else "invalido", "codigo": r["codigo"], "resposta": r["texto"][:200],
              "stderr": r["stderr"], "acoes": r["acoes"]})
    return t


# --------------------------------------------------------------------------- comandos

def executar(rodada: str, tid: str) -> None:
    estado = carregar_estado(rodada)
    t = estado["tarefas"].get(tid)
    if t is None:
        sys.exit(f"tarefa inexistente: {tid}")
    erro = hashes_compativeis(estado, t)
    if erro:
        sys.exit(erro)
    if t["fase"] != "pendente":
        sys.exit(f"tarefa {tid} já está em '{t['fase']}'")
    t["inicio"] = agora()
    try:
        if t["tipo"] == "exec":
            executar_exec(rodada, tid, t, estado)
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
        v = t["veredito"]
        r["juiz"] = {k: v[k]["ok"] for k in J.CRITERIOS_PREVIA if isinstance(v.get(k), dict)}
        if isinstance(v.get("S4_antigo"), dict):
            r["juiz"]["S4_antigo (fora da aprovação)"] = v["S4_antigo"]["ok"]
        if "R" in r["juiz"]:
            r["juiz"]["S4+R"] = r["juiz"]["S4"] and r["juiz"]["R"]
        if isinstance(v.get("medidas"), dict):
            r["medidas"] = v["medidas"]
    if "acertou" in t:
        r["acertou"] = t["acertou"]
    if t.get("custo_usd") is not None:
        r["custo_usd"] = t["custo_usd"]
    return r


# execucao.py e juiz.py NÃO entram: mudá-los altera o que executor e juiz recebem (rodada nova).
# (Na migração da curta-3 eles foram aceitos uma única vez, por serem extração idêntica do runner; ver PLANO.md.)
# Caminhos relativos a RAIZ (dev/<skill>); terminados em "/" valem para o diretório inteiro. O diff é feito no
# repositório inteiro (D73): qualquer outro arquivo mudado, inclusive a skill distribuída em skills/<skill>/, recusa.
PERMITIDOS_NA_MIGRACAO = ("evals/agente/runner.py", "evals/agente/verificador.py", "evals/unit/", "PLANO.md",
                          "evals/README.md", "HANDOFF.md", "evals/.gitignore")
PERMITIDOS_NA_MIGRACAO_RAIZ_GIT = (".gitignore",)


def raiz_git(cwd: Path = RAIZ) -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True,
                               check=True).stdout.strip()).resolve()


def mudados_desde(commit: str, topo: Path) -> List[str]:
    """Arquivos mudados (ou novos, não ignorados) no repositório inteiro desde o commit, relativos à raiz do Git."""
    # --no-renames: um rename lista origem e destino (sem isso, mover um arquivo protegido para um caminho
    # permitido apareceria só pelo destino). -z: nomes com espaço ou acento chegam intactos.
    mudados = subprocess.run(["git", "diff", "--name-only", "--no-renames", "-z", commit], cwd=topo,
                             capture_output=True, text=True, check=True).stdout.split("\0")
    mudados += subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=topo,
                              capture_output=True, text=True, check=True).stdout.split("\0")
    return [m for m in mudados if m]


def proibidos_na_migracao(mudados: List[str], prefixo_dev: str) -> List[str]:
    """prefixo_dev: RAIZ relativo à raiz do Git, em formato posix (ex.: trese-apf-skills/dev/trese-apf-aproximacao)."""
    arquivos = {f"{prefixo_dev}/{p}" for p in PERMITIDOS_NA_MIGRACAO if not p.endswith("/")}
    arquivos |= set(PERMITIDOS_NA_MIGRACAO_RAIZ_GIT)
    dirs = tuple(f"{prefixo_dev}/{p}" for p in PERMITIDOS_NA_MIGRACAO if p.endswith("/"))
    return [m for m in mudados if m not in arquivos and not m.startswith(dirs)]


def reverificar(rodada: str, migrar_de: Optional[str]) -> None:
    """Reavalia, sem consumo de cota, todas as execuções já feitas com o verificador atual."""
    estado = carregar_estado(rodada)
    precisa_migrar = ("hash_execucao" not in estado or estado["hash_execucao"] != hash_execucao()
                      or estado["hash_juiz"] != hash_juiz())
    if precisa_migrar or migrar_de:
        if not migrar_de:
            sys.exit("os hashes de execução/juiz mudaram: informe --migrar-de <commit>; a migração só é aceita "
                     "se, desde esse commit, mudaram apenas arquivos que não afetam executor nem juiz")
        topo = raiz_git()
        mudados = mudados_desde(migrar_de, topo)
        proibidos = proibidos_na_migracao(mudados, RAIZ.relative_to(topo).as_posix())
        if proibidos:
            sys.exit("migração recusada: mudaram arquivos que afetam execução ou juiz: " + ", ".join(proibidos))
        estado.setdefault("migracoes", []).append({"de_commit": migrar_de, "config_hash_antigo": estado["config_hash"],
                                                   "hash_execucao_antigo": estado.get("hash_execucao"),
                                                   "hash_juiz_antigo": estado.get("hash_juiz"), "em": agora(),
                                                   "mudados": sorted(set(mudados))})
        estado.update({"hash_execucao": hash_execucao(), "hash_juiz": hash_juiz(), "config_hash": config_hash()})
    relatorio = {}
    for tid, t in estado["tarefas"].items():
        if t["tipo"] != "exec" or t["fase"] == "pendente":
            continue
        saida = dir_rodada(rodada) / tid
        if not (saida / "snapshot" / "manifesto.json").exists():
            ws = Path(t["ws"])
            if not ws.exists():
                relatorio[tid] = "sem snapshot e sem diretório da execução"
                continue
            ini = dt.datetime.fromisoformat(t["inicio"]).timestamp() - 2
            fim = dt.datetime.fromisoformat(t["fim"]).timestamp() + 2
            congelar(ws, saida, ini, fim, t.get("hash_skill") or sha_arvore(SKILL),
                     herdados_do_dialogo(rodada, estado, t) if t.get("dialogo") else None)
        antes = (t["fase"], t.get("tem_json"))
        aplicar_verificacao(caso_da_tarefa(t), saida, t)
        relatorio[tid] = {"antes": antes[0], "depois": t["fase"], "criterios": {k: x.get("ok") for k, x in t["criterios"].items()}}
    for tid, t in estado["tarefas"].items():
        if t["tipo"] != "juiz":
            continue
        dep = estado["tarefas"][t["depende"]]
        if t["fase"] == "pulado" and dep.get("tem_json"):
            novo = hashlib.sha256(dossie_da_tarefa(rodada, t, estado).encode()).hexdigest()[:16]
            hist = [h for h in t.get("historico_julgamento", []) if h.get("hash_dossie") == novo]
            antigo_txt = dir_rodada(rodada) / tid / "juiz_dossie.md"
            if not hist and antigo_txt.exists() and hashlib.sha256(antigo_txt.read_text(encoding="utf-8").encode()).hexdigest()[:16] == novo:
                hist = [h for h in t.get("historico_julgamento", []) if h.get("veredito")]
            if hist:
                t.update({"fase": "julgado", "motivo": None, "veredito": hist[-1]["veredito"], "hash_dossie": novo})
                relatorio[tid] = "veredito restaurado do histórico (dossiê idêntico)"
            else:
                t["fase"], t["motivo"] = "pendente", None
                relatorio[tid] = "volta a pendente (a execução passou a ter JSON)"
        elif t["fase"] == "julgado":
            if not dep.get("tem_json"):
                t.setdefault("historico_julgamento", []).append({"veredito": t.pop("veredito"), "hash_dossie": t.get("hash_dossie")})
                t["fase"], t["motivo"] = "pulado", "a execução deixou de ter JSON"
                relatorio[tid] = "pulado"
                continue
            novo = hashlib.sha256(dossie_da_tarefa(rodada, t, estado).encode()).hexdigest()[:16]
            antigo_txt = dir_rodada(rodada) / tid / "juiz_dossie.md"
            antigo = t.get("hash_dossie") or (hashlib.sha256(antigo_txt.read_text(encoding="utf-8").encode()).hexdigest()[:16]
                                               if antigo_txt.exists() else None)
            if novo == antigo:
                t["hash_dossie"] = novo
                relatorio[tid] = "veredito mantido (dossiê idêntico)"
            else:
                t.setdefault("historico_julgamento", []).append({"veredito": t.pop("veredito"), "hash_dossie": antigo})
                t["fase"] = "pendente"
                relatorio[tid] = "volta a pendente (dossiê mudou)"
    estado.setdefault("historico_verificador", []).append({"em": agora(), "verificador": hash_verificador()})
    estado["hash_verificador"] = hash_verificador()
    salvar_estado(rodada, estado)
    print(json.dumps(relatorio, ensure_ascii=False, indent=1, default=str))


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
        for r in sorted({t["rep"] for t in estado["tarefas"].values() if t["tipo"] == "exec" and not t.get("dialogo")}):
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
    out.update(comparar_dialogos(rodada, estado))
    (dir_rodada(rodada) / "metamorficos.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))

RELACOES_DIALOGO = {  # relação -> (turno A, turno B, função)
    "preservacao": (1, 2, relacao_preservacao),
    "segundo_lote": (1, 2, relacao_segundo_lote),
    "correcao": (2, 3, relacao_correcao),
}


def comparar_dialogos(rodada: str, estado: Dict[str, Any]) -> Dict[str, Any]:
    """Relações entre turnos da camada 2, sobre os JSONs congelados de cada turno (sem cota)."""
    out: Dict[str, Any] = {}
    reps = sorted({(t["dialogo"], t["rep"]) for t in estado["tarefas"].values() if t.get("dialogo")})
    for did, r in reps:
        nome = C.DIALOGOS[did]["relacao"]
        ka, kb, f = RELACOES_DIALOGO[nome]
        pa = dir_rodada(rodada) / f"exec-{did}-r{r}-t{ka}" / "estimativa.json"
        pb = dir_rodada(rodada) / f"exec-{did}-r{r}-t{kb}" / "estimativa.json"
        if not (pa.exists() and pb.exists()):
            out[f"{did}-r{r}"] = {"ok": None, "relacao": nome, "motivo": "faltam resultados"}
            continue
        out[f"{did}-r{r}"] = {"relacao": nome, **f(json.loads(pa.read_text()), json.loads(pb.read_text()))}
    return out


def repetir(rodada: str, tid: str) -> None:
    """Repete uma execução inválida numa repetição nova do mesmo caso (README: inválidas são
    relatadas à parte e repetidas). A inválida fica no estado, marcada com quem a repete."""
    estado = carregar_estado(rodada)
    t = estado["tarefas"].get(tid)
    if t is None:
        sys.exit(f"tarefa inexistente: {tid}")
    if t["tipo"] != "exec" or t["fase"] != "invalido":
        sys.exit(f"só se repete execução inválida; {tid} é '{t['tipo']}' em '{t['fase']}'")
    if t.get("repetida_por"):
        sys.exit(f"{tid} já foi repetida por {t['repetida_por']}")
    if t.get("dialogo"):
        sys.exit("turno de diálogo não se repete (retomaria uma sessão já avançada); registre a inválida e "
                 "prepare uma repetição nova do diálogo inteiro")
    cid = t["caso"]
    r = 1 + max(x["rep"] for x in estado["tarefas"].values() if x["tipo"] == "exec" and x.get("caso") == cid)
    novo = f"exec-{cid}-r{r}"
    estado["tarefas"][novo] = {"tipo": "exec", "caso": cid, "rep": r, "consome": "claude", "repete": tid, "fase": "pendente"}
    c = C.CASOS[cid]
    if c["tipo"] == "contagem" and not c.get("sem_juiz"):
        estado["tarefas"][f"juiz-{cid}-r{r}"] = {"tipo": "juiz", "caso": cid, "rep": r, "consome": "codex",
                                                 "depende": novo, "fase": "pendente"}
    t["repetida_por"] = novo
    salvar_estado(rodada, estado)
    print(json.dumps({"repete": tid, "nova": novo}, ensure_ascii=False))


def limpar_sessoes(rodada: str) -> None:
    """Camada 2: guarda no último turno de cada diálogo a transcrição da sessão do Claude (evidência) e apaga só as
    sessões desta rodada em ~/.claude/projects. Rode depois de todos os turnos e de `comparar`."""
    estado = carregar_estado(rodada)
    projetos = Path.home() / ".claude" / "projects"
    ultimos: Dict[str, str] = {}
    for tid, t in estado["tarefas"].items():
        if t.get("dialogo") and t["tipo"] == "exec" and t["fase"] != "pendente":
            if t["sessao"] not in ultimos or t["turno"] > estado["tarefas"][ultimos[t["sessao"]]]["turno"]:
                ultimos[t["sessao"]] = tid
    relatorio = {}
    for sessao, tid in ultimos.items():
        achados = list(projetos.glob(f"*/{sessao}.jsonl")) + [p for p in projetos.glob(f"*/{sessao}") if p.is_dir()]
        for p in achados:
            destino = dir_rodada(rodada) / tid / ("sessao.jsonl" if p.is_file() else "sessao")
            if p.is_file():
                shutil.copy2(p, destino)
                p.unlink()
            else:
                shutil.copytree(p, destino, dirs_exist_ok=True)
                shutil.rmtree(p)
        for pasta in {p.parent for p in achados}:  # o Claude Code deixa uma pasta `memory` vazia por projeto
            try:
                (pasta / "memory").rmdir()
            except OSError:
                pass
            try:
                pasta.rmdir()
            except OSError:
                pass
        relatorio[sessao] = {"turno_final": tid, "removidos": [str(p) for p in achados]}
    print(json.dumps(relatorio, ensure_ascii=False, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("preparar")
    sp.add_argument("rodada")
    sp.add_argument("tipo", choices=("sondas", "calibracao", "curta", "completa", "dialogo"))
    sp.add_argument("--casos", help="lista separada por vírgula")
    sp.add_argument("--reps", type=int, help="repetições (padrão: 5 na completa, 1 nas demais)")
    for nome in ("proxima", "status", "comparar", "limpar-sessoes"):
        sub.add_parser(nome).add_argument("rodada")
    sp = sub.add_parser("reverificar")
    sp.add_argument("rodada")
    sp.add_argument("--migrar-de", help="commit em que a rodada (formato antigo) foi preparada")
    sp = sub.add_parser("executar")
    sp.add_argument("rodada")
    sp.add_argument("tarefa")
    sp = sub.add_parser("repetir")
    sp.add_argument("rodada")
    sp.add_argument("tarefa")
    a = ap.parse_args()
    if a.cmd == "preparar":
        reps = a.reps or (5 if a.tipo == "completa" else 1)
        preparar(a.rodada, a.tipo, reps, a.casos.split(",") if a.casos else None)
    elif a.cmd == "proxima":
        print(json.dumps(proxima(a.rodada), ensure_ascii=False))
    elif a.cmd == "executar":
        executar(a.rodada, a.tarefa)
    elif a.cmd == "repetir":
        repetir(a.rodada, a.tarefa)
    elif a.cmd == "status":
        status(a.rodada)
    elif a.cmd == "comparar":
        comparar(a.rodada)
    elif a.cmd == "limpar-sessoes":
        limpar_sessoes(a.rodada)
    elif a.cmd == "reverificar":
        reverificar(a.rodada, a.migrar_de)


if __name__ == "__main__":
    main()
