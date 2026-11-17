"""Verificação automática das execuções do executor (sem consumo de cota).

Separado do runner (consulta 7 ao popper): o hash deste arquivo identifica o VERIFICADOR, e
mudar só este arquivo não invalida execuções já feitas; elas são reavaliadas com `reverificar`
a partir de snapshots congelados.

Fluxo: `congelar` (logo após a execução) copia o diretório da execução e os temporários
criados por ela para `<saida>/snapshot/`, com manifesto de hashes. `verificar_snapshot`
avalia só a partir do snapshot e do trace guardado.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AQUI = Path(__file__).resolve().parent
SKILL = AQUI.parent.parent / "nesma-apf-estimator"
sys.path.insert(0, str(SKILL / "scripts"))
import apf  # noqa: E402  (cópia confiável, do repositório)

BASE_WS = Path("/tmp/apf-evals")
LIMITE_COPIA = 5 * 1024 * 1024


# --------------------------------------------------------------------------- trace

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
    resultados: Dict[str, str] = {}
    for e in eventos:
        if e.get("type") == "user":
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    if isinstance(c, list):
                        c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                    resultados[b.get("tool_use_id")] = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    ferramentas, textos = [], []
    for e in eventos:
        if e.get("type") == "assistant":
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    ferramentas.append({"nome": b.get("name"), "entrada": b.get("input") or {},
                                        "saida": resultados.get(b.get("id"), "")})
                elif isinstance(b, dict) and b.get("type") == "text" and (b.get("text") or "").strip():
                    textos.append(b["text"])
    final = result.get("result") if isinstance(result.get("result"), str) else ""
    if final and (not textos or textos[-1].strip() != final.strip()):
        textos.append(final)
    # texto_final: tudo o que o agente escreveu ao usuário, na ordem (a tabela pode vir antes da exportação).
    return {"init": init, "result": result, "ferramentas": ferramentas,
            "saidas": [f["saida"] for f in ferramentas], "texto_final": "\n\n".join(textos)}


# --------------------------------------------------------------------------- utilidades

def sha_arvore(raiz: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(raiz.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(raiz)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def sha_arquivo(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hash_verificador() -> str:
    return sha_arquivo(Path(__file__))[:16]


def compacto(texto: str) -> str:
    """Toda sequência de espaço ou quebra de linha vira um espaço (quebras suaves do Markdown)."""
    return re.sub(r"\s+", " ", texto).strip()


def normalizar(texto: str) -> str:
    return "\n".join(l.rstrip() for l in texto.replace("\r\n", "\n").split("\n")).strip()


def bloco_presente(md: str, resposta: str) -> bool:
    """O render confiável está na resposta: prosa igual a menos de espaços, e cada linha de tabela idêntica,
    na mesma ordem (impede linhas fundidas, omitidas ou reordenadas)."""
    if compacto(md) not in compacto(resposta):
        return False
    tabela_md = [l.strip() for l in md.splitlines() if l.strip().startswith("|")]
    tabela_resp = [l.strip() for l in resposta.splitlines() if l.strip().startswith("|")]
    it = iter(tabela_resp)
    return all(any(l == r for r in it) for l in tabela_md)


def comeca_com_alerta(texto: str) -> bool:
    linhas = [l.strip() for l in texto.strip().splitlines() if l.strip() and not l.strip().startswith("```")]
    return bool(linhas) and linhas[0].upper().startswith("ALERTA")


def tem_contagem(texto: str) -> bool:
    return bool(re.search(r"\d+(,\d+)?\s*(PF|PFM)\b", texto)) or texto.count("|") >= 6


def chamadas_apf(ferramentas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [f for f in ferramentas if f["nome"] == "Bash" and "apf.py" in (f["entrada"].get("command") or "")]


def toca_pedido(ferramentas: List[Dict[str, Any]]) -> bool:
    return any("pedido.md" in json.dumps(f["entrada"], ensure_ascii=False) for f in ferramentas)


def multiconjunto(est: Dict[str, Any]) -> List[Tuple[str, Optional[str]]]:
    return sorted(((f["tipo"], f.get("operacao")) for f in est["funcoes"]), key=lambda x: (x[0], x[1] or ""))


def conteudo_xlsx(dados: bytes) -> Dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        return {n: z.read(n) for n in z.namelist() if n.startswith("xl/")}


# --------------------------------------------------------------------------- temporários e auditoria

def raiz_temporaria(p: str) -> Optional[Path]:
    """Primeiro nível de um caminho em /tmp ou no TMPDIR do sistema (/var/folders/.../T)."""
    q = p[len("/private"):] if p.startswith("/private/") else p
    m = re.match(r"^(/tmp/[^/]+|/var/folders/[^/]+/[^/]+/T/[^/]+)", q)
    return Path(m.group(1)) if m else None


def temporarios_novos(desde: float, ate: Optional[float] = None) -> List[Path]:
    """Entradas de primeiro nível em /tmp e no TMPDIR do sistema criadas na janela da execução.
    Servem só para LOCALIZAR candidatos; a procedência do JSON é decidida pelo conteúdo."""
    out: List[Path] = []
    for base in {Path("/private/tmp"), Path(tempfile.gettempdir()).resolve()}:
        try:
            filhos = list(base.iterdir())
        except OSError:
            continue
        for f in filhos:
            try:
                st = f.stat()
            except OSError:
                continue
            nasc = getattr(st, "st_birthtime", st.st_ctime)
            if nasc >= desde and (ate is None or nasc <= ate) and not str(f.resolve()).startswith(str(BASE_WS.resolve())):
                out.append(f)
    return out


def _formas(p: str) -> List[str]:
    q = p[len("/private"):] if p.startswith("/private/") else p
    return [q, "/private" + q]


PERMITIDOS_ABS = ("/usr/bin/", "/bin/", "/usr/local/bin/", "/opt/homebrew/bin/", "/dev/null", "/usr/sbin/")
REDE = re.compile(r"\b(curl|wget|nc|ssh|scp|rsync|ftp)\b|https?://", re.I)


def auditar(ferramentas: List[Dict[str, Any]], ws: Path, temporarios_permitidos: List[str]) -> List[str]:
    """Acessos observáveis fora do diretório da execução. Permitidos: o próprio diretório e os
    temporários criados durante a execução (lista congelada no manifesto)."""
    raizes = set(_formas(str(ws)))
    for t in temporarios_permitidos:
        raizes.update(_formas(t))
    problemas = []

    def dentro(p: str) -> bool:
        if any(p == r or p.startswith(r + "/") for r in raizes):
            return True
        r = raiz_temporaria(p)
        return r is not None and "XXX" in r.name  # modelo do mktemp ainda não resolvido

    for f in ferramentas:
        nome, ent = f["nome"], f["entrada"]
        if nome in ("WebFetch", "WebSearch"):
            problemas.append(f"{nome}: acesso à rede")
        if nome in ("Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit"):
            for chave in ("file_path", "path", "notebook_path"):
                v = ent.get(chave)
                if isinstance(v, str) and v:
                    p = v if v.startswith("/") else str(ws / v)
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


def arquivos_criados(arquivos: Path) -> List[str]:
    out = []
    for p in arquivos.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(arquivos)
        if rel.parts[0] == ".claude" or str(rel) == "pedido.md":
            continue
        out.append(str(rel))
    return sorted(out)


# --------------------------------------------------------------------------- snapshot

def congelar(ws: Path, saida: Path, desde: float, ate: float, hash_skill_antes: str) -> Dict[str, Any]:
    """Copia o diretório da execução (sem a skill) e os temporários criados na janela para o snapshot."""
    snap = saida / "snapshot"
    if snap.exists():
        shutil.rmtree(snap)
    (snap / "ws").mkdir(parents=True)
    manifesto: Dict[str, Any] = {"ws_original": str(ws), "desde": desde, "ate": ate, "arquivos": {},
                                 "temporarios": {}, "skill_intacta": None}
    skill = ws / ".claude" / "skills" / "nesma-apf-estimator"
    manifesto["skill_intacta"] = skill.exists() and sha_arvore(skill) == hash_skill_antes
    for p in ws.rglob("*"):
        rel = p.relative_to(ws)
        if not p.is_file() or rel.parts[0] == ".claude" or p.stat().st_size > LIMITE_COPIA:
            continue
        destino = snap / "ws" / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, destino)
        manifesto["arquivos"][f"ws/{rel}"] = sha_arquivo(destino)
    alvo_saida = str(saida.resolve())
    novos = [t for t in temporarios_novos(desde, ate)
             if not (alvo_saida + "/").startswith(str(t.resolve()) + "/")]  # nunca a própria pasta de saída
    for i, t in enumerate(sorted(novos, key=str)):
        destino = snap / "tmp" / str(i)
        manifesto["temporarios"][str(i)] = str(t)
        if t.is_dir():
            for p in t.rglob("*"):
                if p.is_file() and p.stat().st_size <= LIMITE_COPIA:
                    d = destino / p.relative_to(t)
                    d.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, d)
                    manifesto["arquivos"][f"tmp/{i}/{p.relative_to(t)}"] = sha_arquivo(d)
        elif t.is_file() and t.stat().st_size <= LIMITE_COPIA:
            destino.mkdir(parents=True)
            shutil.copy2(t, destino / t.name)
            manifesto["arquivos"][f"tmp/{i}/{t.name}"] = sha_arquivo(destino / t.name)
    (snap / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifesto


def snapshot_integro(snap: Path) -> bool:
    m = json.loads((snap / "manifesto.json").read_text(encoding="utf-8"))
    return all((snap / rel).is_file() and sha_arquivo(snap / rel) == h for rel, h in m["arquivos"].items())


# --------------------------------------------------------------------------- procedência do JSON

def recuperar_json(snap: Path, tr: Dict[str, Any]) -> Tuple[Optional[Path], str]:
    """Escolhe o JSON canônico pelo CONTEÚDO: o render confiável dele precisa ser igual à saída do
    `apf.py render --format md` registrada no trace. Ambiguidade (dois JSONs diferentes que batem) para."""
    renders = [f["saida"] for f in chamadas_apf(tr["ferramentas"])
               if " render " in f" {f['entrada'].get('command', '')} " and "--format md" in f["entrada"].get("command", "")]
    # A saída pode vir precedida por outros comandos encadeados (echo, check): exige-se CONTER o render.
    renders = [compacto(r) for r in renders if r and "# Estimativa de tamanho funcional" in r]
    if not renders:
        return None, "o trace não tem saída de 'apf.py render --format md'"
    alvo = renders[-1]
    candidatos = []
    for p in sorted(snap.rglob("*.json")):
        if p.name == "manifesto.json":
            continue
        try:
            est = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(est, dict) or est.get("versao_esquema") != apf.VERSAO_ESQUEMA or apf.validar(est):
            continue
        calc = apf.calcular(est)
        if any(compacto(apf.render_md(est, calc, perfil)) in alvo for perfil in ("chat", "arquivo")):
            candidatos.append(p)
    conteudos = {p.read_bytes() for p in candidatos}
    if not candidatos:
        return None, "nenhum JSON do snapshot corresponde à saída do render registrada no trace"
    if len(conteudos) > 1:
        return None, "procedência ambígua: JSONs diferentes correspondem ao render"
    return candidatos[-1], "corresponde à saída do render no trace"


# --------------------------------------------------------------------------- verificação

def verificar_snapshot(c: Dict[str, Any], saida: Path) -> Dict[str, Any]:
    snap = saida / "snapshot"
    v: Dict[str, Any] = {"criterios": {}, "invalido": None, "verificador": hash_verificador()}
    crit = v["criterios"]
    if not (snap / "manifesto.json").exists() or not snapshot_integro(snap):
        v["invalido"] = "snapshot ausente ou alterado"
        return v
    m = json.loads((snap / "manifesto.json").read_text(encoding="utf-8"))
    tr = ler_trace(saida / "trace.jsonl")
    if not tr["result"] or tr["result"].get("is_error"):
        v["invalido"] = "execução sem resultado (erro, autenticação ou timeout)"
        return v
    if not m["skill_intacta"]:
        v["invalido"] = "a cópia da skill foi modificada durante a execução"
        return v
    acessos = auditar(tr["ferramentas"], Path(m["ws_original"]), list(m["temporarios"].values()))
    if acessos:
        v["invalido"] = "contaminada: " + "; ".join(acessos[:5])
        return v

    arquivos = snap / "ws"
    texto = tr["texto_final"]
    # Temporário conta como criado pelo agente se o trace o cita, ou se o agente usou mktemp
    # (aí o caminho real não aparece). Temporário de outro processo, sem evidência, não conta.
    comandos = " ".join(f["entrada"].get("command") or "" for f in tr["ferramentas"] if f["nome"] == "Bash")
    citado = comandos + " " + " ".join(tr["saidas"])
    usou_mktemp = "mktemp" in comandos
    autorizados = {i for i, orig in m["temporarios"].items()
                   if usou_mktemp or any(f in citado for f in _formas(orig)) or Path(orig).name in citado}
    criados = arquivos_criados(arquivos) + [rel for rel in m["arquivos"]
                                            if rel.startswith("tmp/") and rel.split("/")[1] in autorizados]
    apf_cmds = chamadas_apf(tr["ferramentas"])
    t = c["tipo"]

    if t in ("alerta1", "alerta2"):
        crit["K1"] = {"alerta": comeca_com_alerta(texto), "sem_script": not apf_cmds,
                      "sem_arquivos": not criados, "sem_contagem": not tem_contagem(texto)}
        if t == "alerta1":
            crit["K1"]["sem_acesso_ao_subsidio"] = not toca_pedido(tr["ferramentas"])
        crit["K1"]["ok"] = all(crit["K1"].values())
        return v

    if t == "nl_confirma":
        crit["K1"] = {"sem_script": not apf_cmds, "sem_arquivos": not criados,
                      "mostra_invocacao": c["espera_invocacao"] in texto, "pede_confirmacao": "?" in texto,
                      "sem_contagem": not tem_contagem(texto)}
        crit["K1"]["ok"] = all(crit["K1"].values())
        return v

    cmds = [f["entrada"].get("command", "") for f in apf_cmds]
    k1 = {"sem_alerta": not comeca_com_alerta(texto),
          "check": any(" check " in f" {x} " for x in cmds),
          "render": any(" render " in f" {x} " for x in cmds)}
    k1["ok"] = all(k1.values())
    crit["K1"] = k1
    caminho_json, procedencia = recuperar_json(snap, tr)
    v["tem_json"] = caminho_json is not None
    v["procedencia"] = procedencia
    if caminho_json is None:
        crit["K2"] = {"ok": False, "motivo": procedencia}
        return v
    v["json"] = str(caminho_json.relative_to(snap))
    est = json.loads(caminho_json.read_text(encoding="utf-8"))
    calc = apf.calcular(est)
    md = apf.render_md(est, calc, "chat")  # o que o agente deve mostrar na resposta
    k2: Dict[str, Any] = {"bloco_literal": bloco_presente(md, texto)}
    exporta = c.get("exporta")
    exportados = [p for p in arquivos_criados(arquivos) if Path(p).suffix in (".md", ".txt", ".xlsx") and not p.startswith("tmp/")]
    if exporta:
        alvo = [p for p in exportados if p.endswith("." + exporta)]
        k2["exportou"] = len(alvo) == 1
        if alvo:
            dados = (arquivos / alvo[0]).read_bytes()
            if exporta == "xlsx":
                k2["exportacao_identica"] = conteudo_xlsx(dados) == conteudo_xlsx(apf.gerar_xlsx(est, calc))
            else:  # arquivos escritos pelo script: comparação estrita (sem relaxar espaços)
                confiavel = apf.render_md(est, calc, "arquivo") if exporta == "md" else apf.render_txt(est, calc, "arquivo")
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

    unidade = c.get("unidade")
    if unidade:
        crit["K4"] = {"ok": calc["unidade"] == unidade, "obtido": calc["unidade"]}
    if c.get("cobertura"):
        crit["cobertura"] = {"ok": calc["cobertura"] == c["cobertura"], "obtido": calc["cobertura"]}
    if c.get("tipos"):
        obtido = multiconjunto(est)
        crit["S1_prefiltro"] = {"ok": obtido == c["tipos"], "obtido": dict(Counter(f"{a}/{b}" for a, b in obtido)),
                                "esperado": dict(Counter(f"{a}/{b}" for a, b in c["tipos"]))}
    if c.get("totais"):
        par = (calc["total_min"], calc["total_max"])
        crit["S2"] = {"ok": par in c["totais"], "obtido": [str(x) for x in par]}
    return v
