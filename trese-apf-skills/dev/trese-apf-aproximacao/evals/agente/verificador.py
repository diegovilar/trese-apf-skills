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
DEV = AQUI.parent.parent                             # trese-apf-skills/dev/<skill>
SKILL = DEV.parent.parent / "skills" / DEV.name       # trese-apf-skills/skills/<skill>
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


# K2 por categorias (D67, consulta 43): conteúdo técnico e avisos obrigatórios exigem cópia literal; as frases
# fixas de orientação de uso (como responder, como pedir correção) exigem presença com o sentido correto: a frase
# literal, ou, no trecho da resposta depois do último bloco de conteúdo, os termos que carregam o sentido (cada grupo:
# alguma das alternativas). Introdução redundante não existe mais no script. Vale para frente; reprovações
# anteriores continuam reprovações.
ORIENTACAO = {
    apf.FECHO_CORRECAO: (("recálcul", "recalcul", "corrig", "correç"), ("export",)),
    apf.PREVIA_FECHO_PERGUNTAS: (("não sei",), ("calcular",)),
    apf.PREVIA_FECHO_FERRAMENTA: (("não sei",), ("calcular",)),
    apf.PREVIA_FECHO_SEM_PERGUNTAS: (("confirm",),),
}


def k2_por_categorias(render: str, resposta: str) -> Dict[str, Any]:
    linhas = render.splitlines()
    orientacao = [l.strip() for l in linhas if l.strip() in ORIENTACAO]
    conteudo = "\n".join(l for l in linhas if l.strip() not in ORIENTACAO)
    r: Dict[str, Any] = {"conteudo_literal": bloco_presente(conteudo, resposta)}
    ultima = next((l for l in reversed(conteudo.splitlines()) if l.strip()), "")
    cr, cu = compacto(resposta), compacto(ultima)
    i = cr.rfind(cu) if cu else -1
    cauda = (cr[i + len(cu):] if i >= 0 else "").casefold()
    detalhe = {}
    for frase in orientacao:
        literal = compacto(frase) in cr
        sentido = all(any(k in cauda for k in grupo) for grupo in ORIENTACAO[frase])
        detalhe[frase[:40]] = "literal" if literal else ("sentido" if sentido else "ausente")
    r["orientacao"] = all(v != "ausente" for v in detalhe.values())
    r["orientacao_detalhe"] = detalhe
    return r


def comeca_com_alerta(texto: str) -> bool:
    linhas = [l.strip() for l in texto.strip().splitlines() if l.strip() and not l.strip().startswith("```")]
    return bool(linhas) and linhas[0].upper().startswith("ALERTA")


def tem_contagem(texto: str) -> bool:
    """Números de PF ou alguma linha de tabela Markdown (não conta barras soltas, como em 'interativo=sim|nao')."""
    tabela = any(re.match(r"^\s*\|.*\|\s*$", l) for l in texto.splitlines())
    return bool(re.search(r"\d+(,\d+)?\s*(PF|PFM)\b", texto)) or tabela


def chamadas_apf(ferramentas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [f for f in ferramentas if f["nome"] == "Bash" and "apf.py" in (f["entrada"].get("command") or "")]


def toca_pedido(ferramentas: List[Dict[str, Any]]) -> bool:
    return any("pedido.md" in json.dumps(f["entrada"], ensure_ascii=False) for f in ferramentas)


def multiconjunto(est: Dict[str, Any]) -> List[Tuple[str, Optional[str]]]:
    return sorted(((f["tipo"], f.get("operacao")) for f in est["funcoes"]), key=lambda x: (x[0], x[1] or ""))


def conteudo_xlsx(dados: bytes) -> Optional[Dict[str, bytes]]:
    """Partes xl/ do pacote; None se o arquivo não for um zip legível."""
    try:
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            return {n: z.read(n) for n in z.namelist() if n.startswith("xl/")}
    except (zipfile.BadZipFile, KeyError, OSError, EOFError):
        return None


def conteudo_docx(dados: bytes) -> Optional[Dict[str, bytes]]:
    """Todas as partes do pacote (modelo e corpo), sem as datas do zip; None se ilegível."""
    try:
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            return {n: z.read(n) for n in z.namelist()}
    except (zipfile.BadZipFile, KeyError, OSError, EOFError):
        return None


EXTENSOES_EXPORTADAS = (".md", ".txt", ".xlsx", ".docx")


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

def congelar(ws: Path, saida: Path, desde: float, ate: float, hash_skill_antes: str,
             herdados: Optional[List[str]] = None) -> Dict[str, Any]:
    """Copia o diretório da execução (sem a skill) e os temporários criados na janela para o snapshot.
    `herdados` (camada 2): temporários criados em turnos anteriores do mesmo diálogo; são copiados de novo no estado
    deste turno e continuam permitidos na auditoria."""
    snap = saida / "snapshot"
    if snap.exists():
        shutil.rmtree(snap)
    (snap / "ws").mkdir(parents=True)
    manifesto: Dict[str, Any] = {"ws_original": str(ws), "desde": desde, "ate": ate, "arquivos": {},
                                 "temporarios": {}, "skill_intacta": None}
    skill = ws / ".claude" / "skills" / "trese-apf-aproximacao"
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
    vistos = {str(t) for t in novos}
    for h in herdados or []:
        if h not in vistos and Path(h).exists():
            novos.append(Path(h))
            vistos.add(h)
    manifesto["herdados"] = list(herdados or [])
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

def recuperar_json(snap: Path, tr: Dict[str, Any], formato: str = "md") -> Tuple[Optional[Path], str]:
    """Escolhe o JSON canônico pelo CONTEÚDO: o render confiável dele precisa ser igual à saída do
    `apf.py render --format md` (ou `--format previa`) registrada no trace. Ambiguidade (dois JSONs
    diferentes que batem) para."""
    # Só o título atual (D74): execuções anteriores se reverificam no checkout correspondente, porque o render
    # comparado abaixo também é o atual.
    titulos = ("# Prévia da estimativa",) if formato == "previa" else ("# " + apf.TITULO_DOCUMENTO,)
    renders = [f["saida"] for f in chamadas_apf(tr["ferramentas"])
               if " render " in f" {f['entrada'].get('command', '')} " and f"--format {formato}" in f["entrada"].get("command", "")]
    # A saída pode vir precedida por outros comandos encadeados (echo, check): exige-se CONTER o render.
    renders = [compacto(r) for r in renders if r and any(t in r for t in titulos)]
    if not renders:
        return None, f"o trace não tem saída de 'apf.py render --format {formato}'"
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
        if formato == "previa":
            if apf.validar_previa(est) or compacto(apf.render_previa(est)) not in alvo:
                continue
            candidatos.append(p)
            continue
        if apf.validar_final(est):
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
    if c.get("previa"):
        return _verificar_previa(c, v, snap, tr, texto, cmds, arquivos)
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
    k2: Dict[str, Any] = k2_por_categorias(md, texto)
    exporta = c.get("exporta")
    exportados = [p for p in arquivos_criados(arquivos) if Path(p).suffix in EXTENSOES_EXPORTADAS and not p.startswith("tmp/")]
    if exporta:
        alvo = [p for p in exportados if p.endswith("." + exporta)]
        k2["exportou"] = len(alvo) == 1
        if alvo:
            dados = (arquivos / alvo[0]).read_bytes()
            if exporta in ("xlsx", "docx"):
                ler, gerar = (conteudo_xlsx, apf.gerar_xlsx) if exporta == "xlsx" else (conteudo_docx, apf.gerar_docx)
                obtido = ler(dados)
                k2["exportacao_identica"] = obtido is not None and obtido == ler(gerar(est, calc))
                if obtido is None:
                    k2["motivo_exportacao"] = f"o .{exporta} exportado não é um pacote zip legível"
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


def _verificar_previa(c: Dict[str, Any], v: Dict[str, Any], snap: Path, tr: Dict[str, Any], texto: str,
                      cmds: List[str], arquivos: Path) -> Dict[str, Any]:
    """Execução com interativo=sim que deve terminar na prévia (D51, D52): JSON válido, prévia do script
    copiada literalmente, nenhum resultado numérico e nada exportado antes da confirmação."""
    crit = v["criterios"]
    finais = [x for x in cmds if " render " in f" {x} " and re.search(r"--format\s+(md|txt|xlsx|docx)\b", x)]
    exportados = [p for p in arquivos_criados(arquivos) if Path(p).suffix in EXTENSOES_EXPORTADAS]
    k1 = {"sem_alerta": not comeca_com_alerta(texto),
          "check": any(" check " in f" {x} " for x in cmds),
          "previa": any(" render " in f" {x} " and "--format previa" in x for x in cmds),
          "sem_render_final": not finais,
          "sem_exportacao": not exportados,
          "sem_pf_na_resposta": not re.search(r"\d+(,\d+)?\s*(PF|PFM)\b", texto)}
    k1["ok"] = all(k1.values())
    crit["K1"] = k1
    caminho_json, procedencia = recuperar_json(snap, tr, "previa")
    v["tem_json"] = caminho_json is not None
    v["procedencia"] = procedencia
    if caminho_json is None:
        crit["K2"] = {"ok": False, "motivo": procedencia}
        return v
    v["json"] = str(caminho_json.relative_to(snap))
    est = json.loads(caminho_json.read_text(encoding="utf-8"))
    crit["K2"] = k2_por_categorias(apf.render_previa(est), texto)
    crit["K2"]["ok"] = crit["K2"]["conteudo_literal"] and crit["K2"]["orientacao"]
    esp = c.get("espera", {})
    if esp:
        crit["config"] = {k: est.get(k) == val for k, val in esp.items()}
        crit["config"]["ok"] = all(crit["config"].values())
    n, perguntas, abertas = apf.lote_atual(est)
    v["lote"] = {"numero": n, "perguntas": len(perguntas), "abertas_restantes": abertas,
                 "pendencias": len(est.get("pendencias", []))}
    return v


# --------------------------------------------------------------------------- camada 2: relações entre turnos

def _norm(t: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (t or "").casefold()).strip()


def _modelo(est: Dict[str, Any]) -> Dict[str, Any]:
    """Modelo funcional independente de IDs: funções por (tipo, operação, nome) com a hipótese de que dependem
    (pela descrição), e hipóteses por descrição, com grupo e exigências também pela descrição."""
    hip = {h["id"]: h for h in est.get("hipoteses", [])}
    desc = {hid: _norm(h.get("descricao")) for hid, h in hip.items()}
    funcoes = sorted((f["tipo"], f.get("operacao") or "", _norm(f["nome"]), desc.get(f.get("hipotese"), ""))
                     for f in est["funcoes"])
    hipoteses = sorted((desc[hid], _norm(h.get("grupo")), tuple(sorted(desc.get(r, r) for r in h.get("requer") or [])))
                       for hid, h in hip.items())
    return {"funcoes": funcoes, "hipoteses": hipoteses}


def relacao_preservacao(previa: Dict[str, Any], final: Dict[str, Any]) -> Dict[str, Any]:
    """D2a: depois de "não sei" em tudo, o resultado final tem o mesmo modelo da prévia (mesmas funções, hipóteses,
    vínculos, cenários e cobertura), tolerando renumeração; as perguntas do lote viram `sem-resposta`."""
    mp, mf = _modelo(previa), _modelo(final)
    cp, cf = apf.calcular(previa), apf.calcular(final)
    lote = {p["id"] for p in previa.get("pendencias", []) if p.get("situacao") == "perguntada"}
    situacao_final = {p["id"]: p.get("situacao") for p in final.get("pendencias", [])}
    r = {"funcoes_iguais": mp["funcoes"] == mf["funcoes"],
         "hipoteses_iguais": mp["hipoteses"] == mf["hipoteses"],
         "totais_iguais": (cp["total_min"], cp["total_max"]) == (cf["total_min"], cf["total_max"]),
         "cobertura_igual": previa["cobertura"].get("status") == final["cobertura"].get("status"),
         "lote_sem_resposta": all(situacao_final.get(pid) == "sem-resposta" for pid in lote),
         "totais": [str(cp["total_min"]), str(cp["total_max"]), str(cf["total_min"]), str(cf["total_max"])]}
    if not r["funcoes_iguais"]:
        r["so_na_previa"] = [x for x in mp["funcoes"] if x not in mf["funcoes"]]
        r["so_no_final"] = [x for x in mf["funcoes"] if x not in mp["funcoes"]]
    r["ok"] = all(r[k] for k in ("funcoes_iguais", "hipoteses_iguais", "totais_iguais", "cobertura_igual", "lote_sem_resposta"))
    return r


def relacao_segundo_lote(previa1: Dict[str, Any], previa2: Dict[str, Any]) -> Dict[str, Any]:
    """D2c, turno 2 (respostas parciais, sem "calcular"): a nova prévia registra as respostas, não repete pergunta
    do lote 1 e traz o lote 2 ou o pedido de confirmação. Sem lote 2, o percurso fica registrado como não exercitado."""
    lote1 = {p["id"] for p in previa1.get("pendencias", []) if p.get("situacao") == "perguntada"}
    p2 = {p["id"]: p for p in previa2.get("pendencias", [])}
    n, perguntas, _ = apf.lote_atual(previa2)
    repetidas = sorted(pid for pid in lote1 if p2.get(pid, {}).get("situacao") == "perguntada")
    r = {"lote1_fechado": all(p2.get(pid, {}).get("situacao") in ("resolvida", "sem-resposta") for pid in lote1 if pid in p2),
         "sem_repeticao": not repetidas, "repetidas": repetidas,
         "com_esclarecimentos": bool(previa2.get("esclarecimentos")),
         "com_sem_resposta": any(p.get("situacao") == "sem-resposta" for p in p2.values()),
         "segundo_lote": bool(perguntas) and n >= 2, "lote": n if perguntas else None}
    r["percurso"] = "segundo lote" if r["segundo_lote"] else "confirmação (segundo lote não exercitado)"
    r["ok"] = all(r[k] for k in ("lote1_fechado", "sem_repeticao", "com_esclarecimentos", "com_sem_resposta"))
    return r


def relacao_correcao(antes: Dict[str, Any], depois: Dict[str, Any]) -> Dict[str, Any]:
    """D2d: a correção "não haverá lista de mesários ausentes por local" retira exatamente uma CE e 4 PF nos dois
    extremos, sem mexer no resto do modelo."""
    ca, cd = apf.calcular(antes), apf.calcular(depois)
    fa, fd = _modelo(antes)["funcoes"], _modelo(depois)["funcoes"]
    restantes = list(fd)
    retiradas = []
    for x in fa:
        if x in restantes:
            restantes.remove(x)
        else:
            retiradas.append(x)
    r = {"menos_4_nos_dois_extremos": (ca["total_min"] - cd["total_min"], ca["total_max"] - cd["total_max"]) == (4, 4),
         "uma_ce_retirada": len(retiradas) == 1 and retiradas[0][0] == "CE",
         "retirada_e_a_lista_de_ausentes": len(retiradas) == 1 and "ausent" in retiradas[0][2],
         "nada_acrescentado": not restantes, "retiradas": retiradas, "acrescentadas": restantes,
         "totais": [str(ca["total_min"]), str(ca["total_max"]), str(cd["total_min"]), str(cd["total_max"])]}
    r["ok"] = all(r[k] for k in ("menos_4_nos_dois_extremos", "uma_ce_retirada", "retirada_e_a_lista_de_ausentes",
                                 "nada_acrescentado"))
    return r
