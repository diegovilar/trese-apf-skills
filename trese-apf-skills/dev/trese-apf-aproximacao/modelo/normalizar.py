"""Normaliza o modelo .docx editado pelo usuário e o grava como assets/modelo.docx da skill (D74).

    python3 modelo/normalizar.py EDITADO.docx DESTINO.docx

O que faz, sem reserializar o XML (só trocas textuais pontuais):
- fixa os IDs dos estilos "APF ..." pelo nome (o editor pode ter gerado outros IDs) e atualiza as referências
  (basedOn, next, link, pStyle, rStyle) em estilos, documento, cabeçalhos e rodapés;
- esvazia o corpo do documento, mantendo só o w:sectPr final (página, margens, cabeçalho e rodapé);
- remove atributos w:rsid*;
- confere que cabeçalhos e rodapés não têm revisões nem comentários e que toda imagem referenciada existe;
- valida o resultado com o mesmo leitor que o apf.py usa em produção.
Nunca sobrescreve o destino.
"""
from __future__ import annotations

import os
import posixpath
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(AQUI))), "skills",
                     os.path.basename(os.path.dirname(AQUI)))
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import apf  # noqa: E402

# nome do estilo (como aparece no editor) -> ID fixo que o apf.py referencia
ESTILOS = {
    "APF Titulo": "APFTitulo", "APF Secao": "APFSecao", "APF Texto": "APFTexto", "APF Item": "APFItem",
    "APF Aviso": "APFAviso", "APF Legenda": "APFLegenda", "APF Rotulo": "APFRotulo", "APF Celula": "APFCelula",
    "APF Celula Numero": "APFCelulaNumero", "APF Cabecalho Tabela": "APFCabecalhoTabela", "APF Termo": "APFTermo",
    "APF Campo a preencher": "APFCampo",
}
OPCIONAIS = {"APF Cabecalho": "APFCabecalho", "APF Rodape": "APFRodape"}


class Erro(Exception):
    pass


def mapa_de_ids(estilos: str) -> dict:
    mapa, usados = {}, {}
    for bloco in re.findall(r"<w:style\b.*?</w:style>", estilos, re.S):
        nome = re.search(r'<w:name w:val="([^"]*)"', bloco)
        sid = re.search(r'w:styleId="([^"]*)"', bloco)
        if nome and sid:
            usados[sid.group(1)] = nome.group(1)
            alvo = ESTILOS.get(nome.group(1)) or OPCIONAIS.get(nome.group(1))
            if alvo:
                mapa[sid.group(1)] = alvo
    faltando = [n for n in ESTILOS if n not in usados.values()]
    if faltando:
        raise Erro("estilos ausentes (foram renomeados ou apagados?): " + ", ".join(faltando))
    for antigo, novo in mapa.items():
        if novo in usados and usados[novo] != usados[antigo] and novo not in mapa:
            raise Erro(f"o ID {novo} já pertence a outro estilo ({usados[novo]})")
    return {a: n for a, n in mapa.items() if a != n}


def trocar_ids(xml: str, mapa: dict) -> str:
    for antigo, novo in mapa.items():
        xml = xml.replace(f'w:styleId="{antigo}"', f'w:styleId="{novo}"')
        xml = re.sub(r'(<w:(?:basedOn|next|link|pStyle|rStyle)\b[^>]*\bw:val=")' + re.escape(antigo) + '"',
                     lambda m: m.group(1) + novo + '"', xml)
    return xml


def normalizar(origem: str, destino: str) -> None:
    with zipfile.ZipFile(origem) as z:
        partes = [(i, z.read(i.filename)) for i in z.infolist()]
    nomes = {i.filename: d for i, d in partes}
    estilos = nomes["word/styles.xml"].decode("utf-8")
    mapa = mapa_de_ids(estilos)
    novas = {}
    for nome, dados in nomes.items():
        if not (nome.startswith("word/") and nome.endswith(".xml")):
            continue
        xml = dados.decode("utf-8")
        xml = re.sub(r'\s+w:rsid\w*="[0-9A-Fa-f]+"', "", xml)
        xml = trocar_ids(xml, mapa)
        base = posixpath.basename(nome)
        if re.match(r"(header|footer)\d*\.xml$", base):
            if re.search(r"<w:(ins|del|commentRangeStart|commentReference)\b", xml):
                raise Erro(f"{nome} tem revisões ou comentários; aceite/remova e salve de novo")
        if nome == "word/document.xml":
            m = re.search(r"<w:body>(.*)</w:body>", xml, re.S)
            if not m or m.group(1).count("<w:sectPr") != 1:
                raise Erro("o documento precisa ter exatamente uma seção (sem quebras de seção)")
            sect = re.search(r"<w:sectPr\b.*</w:sectPr>", m.group(1), re.S).group(0)
            xml = xml[:m.start(1)] + sect + xml[m.end(1):]
        novas[nome] = xml.encode("utf-8")
    # imagens e outras relações de cabeçalhos e rodapés precisam existir no pacote
    for nome, dados in nomes.items():
        if re.match(r"word/_rels/(header|footer)\d*\.xml\.rels$", nome):
            relacoes = ET.fromstring(dados).iter("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
            for alvo, modo in ((r.get("Target", ""), r.get("TargetMode")) for r in relacoes):
                if modo == "External":
                    raise Erro(f"{nome}: relação externa ({alvo}); incorpore a imagem em vez de vinculá-la")
                caminho = posixpath.normpath(posixpath.join("word", alvo))
                if caminho not in nomes:
                    raise Erro(f"{nome}: {alvo} não está no pacote")
    with zipfile.ZipFile(destino, "x", zipfile.ZIP_DEFLATED) as z:
        for info, dados in partes:
            z.writestr(info, novas.get(info.filename, dados))
    try:
        apf._ler_modelo(destino)
    except apf.ErroModelo as e:
        os.remove(destino)
        raise Erro(str(e))
    print(destino)
    if mapa:
        print("IDs de estilo fixados: " + ", ".join(f"{a} -> {n}" for a, n in sorted(mapa.items())))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        normalizar(sys.argv[1], sys.argv[2])
    except (Erro, FileExistsError) as e:
        sys.exit(f"ERRO: {e}")
