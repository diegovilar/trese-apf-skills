"""Gera o esqueleto do modelo .docx da exportação (D74), para edição no LibreOffice.

O esqueleto traz uma amostra de cada elemento que a exportação produz, com estilos nomeados
("APF Titulo", "APF Secao"...), um cabeçalho e um rodapé provisórios. Depois de editado e devolvido,
é normalizado e vira assets/modelo.docx da skill. Só biblioteca padrão.

    python3 modelo/gerar_esqueleto.py modelo/esqueleto.docx
"""
from __future__ import annotations

import sys
import zipfile
from typing import List, Optional, Sequence, Tuple, Union

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'

# A4 paisagem, em twips (1 cm = 567)
PAGINA_L, PAGINA_A = 16838, 11906
MARGEM = 1134
UTIL = PAGINA_L - 2 * MARGEM

COR_BORDA = "A6A6A6"
COR_ROTULO = "F2F2F2"
COR_CABECALHO = "D9E1F2"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ----------------------------------------------------------------- parágrafos e trechos

Trecho = Union[str, Tuple[str, str]]  # texto, ou (texto, estilo de caractere | "b")


def run(t: Trecho) -> str:
    if isinstance(t, str):
        texto, rpr = t, ""
    else:
        texto, est = t
        rpr = "<w:rPr><w:b/></w:rPr>" if est == "b" else f'<w:rPr><w:rStyle w:val="{est}"/></w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(texto)}</w:t></w:r>'


def campo(instr: str, amostra: str) -> str:
    return f'<w:fldSimple w:instr=" {instr} "><w:r><w:t>{amostra}</w:t></w:r></w:fldSimple>'


def par(trechos: Union[Trecho, Sequence[Trecho]], estilo: str, extra: str = "") -> str:
    if isinstance(trechos, (str, tuple)):
        trechos = [trechos]
    corpo = "".join(t if isinstance(t, str) and t.startswith("<w:") else run(t) for t in trechos)
    return f'<w:p><w:pPr><w:pStyle w:val="{estilo}"/>{extra}</w:pPr>{corpo}</w:p>'


# ----------------------------------------------------------------- tabelas

def celula(conteudo: Union[Trecho, Sequence[Trecho]], largura: int, estilo: str, fundo: Optional[str] = None) -> str:
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fundo}"/>' if fundo else ""
    return f'<w:tc><w:tcPr><w:tcW w:w="{largura}" w:type="dxa"/>{shd}</w:tcPr>{par(conteudo, estilo)}</w:tc>'


def tabela(linhas: List[str], larguras: Sequence[int]) -> str:
    bordas = "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="{COR_BORDA}"/>'
                     for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grade = "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(larguras)}" w:type="dxa"/><w:tblBorders>{bordas}</w:tblBorders>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>'
            '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="0000"/></w:tblPr>'
            f'<w:tblGrid>{grade}</w:tblGrid>{"".join(linhas)}</w:tbl>')


def linha(celulas: List[str], cabecalho: bool = False) -> str:
    trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if cabecalho else "<w:trPr><w:cantSplit/></w:trPr>"
    return f"<w:tr>{trpr}{''.join(celulas)}</w:tr>"


def tabela_rotulada(pares: List[Tuple[str, Union[Trecho, Sequence[Trecho]]]]) -> str:
    """Tabela de duas colunas sem cabeçalho: rótulo sombreado à esquerda, valor à direita."""
    larg = [3000, UTIL - 3000]
    return tabela([linha([celula(r, larg[0], "APFRotulo", COR_ROTULO), celula(v, larg[1], "APFCelula")])
                   for r, v in pares], larg)


def tabela_dados(cab: List[str], linhas_: List[List[Union[Trecho, Sequence[Trecho]]]], larg: List[int],
                 numericas: Sequence[int] = ()) -> str:
    """Tabela com linha de cabeçalho repetida a cada página."""
    ls = [linha([celula(c, larg[i], "APFCabecalhoTabela", COR_CABECALHO) for i, c in enumerate(cab)], cabecalho=True)]
    for ln in linhas_:
        ls.append(linha([celula(c, larg[i], "APFCelulaNumero" if i in numericas else "APFCelula")
                         for i, c in enumerate(ln)]))
    return tabela(ls, larg)


# ----------------------------------------------------------------- estilos

def estilo_par(id_: str, nome: str, ppr: str = "", rpr: str = "", base: str = "Normal", prox: Optional[str] = None) -> str:
    prox_xml = f'<w:next w:val="{prox}"/>' if prox else ""
    return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{id_}"><w:name w:val="{nome}"/>'
            f'<w:basedOn w:val="{base}"/>{prox_xml}<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def estilo_car(id_: str, nome: str, rpr: str) -> str:
    return (f'<w:style w:type="character" w:customStyle="1" w:styleId="{id_}"><w:name w:val="{nome}"/>'
            f'<w:qFormat/><w:rPr>{rpr}</w:rPr></w:style>')


def tam(pt: float) -> str:
    v = int(pt * 2)
    return f'<w:sz w:val="{v}"/><w:szCs w:val="{v}"/>'


ESTILOS = (
    XML + f'<w:styles xmlns:w="{W}">'
    '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
    f'{tam(10)}<w:lang w:val="pt-BR" w:eastAsia="pt-BR" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
    '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
    '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/>'
    '<w:uiPriority w:val="1"/><w:semiHidden/></w:style>'
    '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:semiHidden/>'
    '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
    '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>'
    + estilo_par("APFTitulo", "APF Titulo", '<w:jc w:val="center"/><w:spacing w:before="120" w:after="240"/>',
                 "<w:b/><w:bCs/>" + tam(16), prox="APFTexto")
    + estilo_par("APFSecao", "APF Secao", '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="0"/>',
                 "<w:b/><w:bCs/>" + tam(12), prox="APFTexto")
    + estilo_par("APFTexto", "APF Texto", '<w:spacing w:after="80"/>')
    + estilo_par("APFItem", "APF Item", '<w:spacing w:after="60"/><w:ind w:left="567" w:hanging="567"/>')
    + estilo_par("APFAviso", "APF Aviso", '<w:spacing w:before="120" w:after="80"/>', "<w:i/><w:iCs/>")
    + estilo_par("APFLegenda", "APF Legenda", '<w:spacing w:after="60"/>', tam(9))
    + estilo_par("APFRotulo", "APF Rotulo", "", "<w:b/><w:bCs/>" + tam(9))
    + estilo_par("APFCelula", "APF Celula", "", tam(9))
    + estilo_par("APFCelulaNumero", "APF Celula Numero", '<w:jc w:val="right"/>', tam(9), base="APFCelula")
    + estilo_par("APFCabecalhoTabela", "APF Cabecalho Tabela", "", "<w:b/><w:bCs/>" + tam(9))
    + estilo_par("APFCabecalho", "APF Cabecalho", "", tam(9))
    + estilo_par("APFRodape", "APF Rodape", "", tam(8))
    + estilo_car("APFTermo", "APF Termo", "<w:b/><w:bCs/>")
    + estilo_car("APFCampo", "APF Campo a preencher", '<w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/>')
    + "</w:styles>"
)


# ----------------------------------------------------------------- conteúdo de amostra

def corpo() -> str:
    b: List[str] = []
    b.append(par("CÁLCULO DE TAMANHO FUNCIONAL APROXIMADO", "APFTitulo"))
    b.append(tabela_rotulada([
        ("Objeto", "Sistema de Agendamento de Atendimento ao Eleitor: lembrete de agendamento por e-mail"),
        ("Responsável", ("[NOME DA UNIDADE]", "APFCampo")),
        ("Participantes", ("[LISTA DE UNIDADES OU SERVIDORES PARTICIPANTES]", "APFCampo")),
    ]))

    b.append(par("Resumo executivo", "APFSecao"))
    b.append(tabela_rotulada([
        ("Tipo de projeto", "melhoria"),
        ("Regime de melhoria", "nesma"),
        ("Método", "NESMA estimada"),
        ("Fronteira da aplicação", "Sistema de Agendamento de Atendimento ao Eleitor"),
        ("Origem do subsídio", "Documento de requisitos enviado pela unidade demandante"),
        ("Data", "19/11/2026"),
        ("Total", ("de 9,60 a 14,00 PFM (cenários mínimo e máximo; sem valor central)", "b")),
        ("Cobertura", "completa em relação ao pedido analisado"),
    ]))

    b.append(par("Memória de cálculo", "APFSecao"))
    cab = ["ID", "Requisito / História", "Função identificada", "Tipo", "Operação (I/A/E)", "Complexidade",
           "PF base", "Fator", "PFM", "Base", "Justificativa técnica"]
    larg = [600, 1700, 1750, 600, 1150, 1500, 700, 1100, 1100, 1000]
    larg.append(UTIL - sum(larg))
    linhas_ = [
        ["F01", "RF01: o eleitor recebe lembrete do agendamento", "Enviar lembrete de agendamento", "SE", "I", "Média",
         "5", "1,00", "5,00", "evidência", "Processo novo que envia dados para fora com dado derivado (prazo restante)."],
        ["F02", "RF02: o atendente configura a antecedência do lembrete", "Manter configuração de lembrete", "EE", "I",
         "Média", "4", "1,00", "4,00", "H1 (ver E1)", "Altera o comportamento do sistema; depende de a configuração ser por unidade."],
        ["F03", "RF01", "Agendamento", "ALI", "A", "Baixa", "7", "0,40–0,65", "2,80–4,55", "evidência",
         "Ganha o campo de e-mail do eleitor. Faixa de fator: TDs atuais não informados no pedido."],
        ["", ("Total", "b"), "", "", "", "", "", "", ("9,60–14,00", "b"), "", ""],
    ]
    b.append(tabela_dados(cab, linhas_, larg, numericas=(6, 7, 8)))

    b.append(par("Hipóteses e cenários", "APFSecao"))
    cab = ["ID", "Hipótese", "Trecho do pedido", "Alternativas (grupo)", "Exige", "Efeito"]
    larg = [600, 4500, 4500, 1800, 900]
    larg.append(UTIL - sum(larg))
    b.append(tabela_dados(cab, [["H1", "A antecedência do lembrete é configurável por unidade (ver E1).",
                                 "\"cada cartório define com quantos dias de antecedência\"", "—", "—", "+4 PFM"]],
                          larg, numericas=(5,)))
    b.append(par([("Cenário mínimo: ", "APFTermo"), "9,60 PFM (hipóteses: nenhuma)"], "APFTexto",
                 '<w:spacing w:before="120"/>'))
    b.append(par([("Cenário máximo: ", "APFTermo"), "14,00 PFM (hipóteses: H1)"], "APFTexto"))

    b.append(par("Premissas assumidas", "APFSecao"))
    b.append(par([("P1.", "APFTermo"), "\tO envio de e-mail usa o serviço corporativo já existente, fora da fronteira."], "APFItem"))
    b.append(par([("P2.", "APFTermo"), "\tO e-mail do eleitor é informado no próprio agendamento."], "APFItem"))

    b.append(par("Itens não contados", "APFSecao"))
    larg = [4000, 3000]
    larg.append(UTIL - sum(larg))
    b.append(tabela_dados(["Item", "Categoria", "Justificativa"],
                          [["Tela de confirmação do envio", "absorvido no processo elementar",
                            "Faz parte do processo de envio do lembrete (F01)."]], larg))

    b.append(par("Esclarecimentos do analista", "APFSecao"))
    b.append(par([("E1.", "APFTermo"), "\t(Q1, lote 1) Pergunta: a antecedência é única ou por unidade? Resposta: não sei."],
                 "APFItem"))

    b.append(par("Dúvidas de requisito e pendências", "APFSecao"))
    b.append(par([("Q1.", "APFTermo"), "\tA antecedência do lembrete é única para o tribunal ou definida por unidade?"],
                 "APFItem"))
    b.append(par([("Aviso: ", "APFTermo"), "A lista de pendências não é exaustiva. Revise os requisitos e fluxos específicos "
                  "do domínio antes de usar a estimativa na análise de viabilidade."], "APFAviso"))

    b.append(par("Legenda", "APFSecao"))
    for termo, desc in [
        ("SE", "Saída Externa: processo que envia dados para fora com cálculo, dado derivado, atualização de ALI ou mudança de comportamento."),
        ("EE", "Entrada Externa: processo que recebe dados de fora e mantém ALI ou altera o comportamento do sistema."),
        ("PFM", "Regime 'nesma': pontos de função de melhoria (EFPA 2.2.1), unidade distinta de PF."),
    ]:
        b.append(par([(termo + ": ", "APFTermo"), desc], "APFLegenda"))

    sect = (f'<w:sectPr><w:headerReference w:type="default" r:id="rId2"/><w:footerReference w:type="default" r:id="rId3"/>'
            f'<w:pgSz w:w="{PAGINA_L}" w:h="{PAGINA_A}" w:orient="landscape"/>'
            f'<w:pgMar w:top="{MARGEM}" w:right="{MARGEM}" w:bottom="{MARGEM}" w:left="{MARGEM}" w:header="567" w:footer="567" w:gutter="0"/>'
            "</w:sectPr>")
    return (XML + f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>' + "".join(b) + sect + "</w:body></w:document>")


CABECALHO = (XML + f'<w:hdr xmlns:w="{W}" xmlns:r="{R}">'
             + par("[Insira aqui o logotipo]", "APFCabecalho")
             + par("[Texto fixo do cabeçalho, ex.: Tribunal Regional Eleitoral de Sergipe / Secretaria de Tecnologia da Informação]",
                   "APFCabecalho")
             + "</w:hdr>")

RODAPE = (XML + f'<w:ftr xmlns:w="{W}" xmlns:r="{R}">'
          + par("[Texto fixo do rodapé, ex.: unidade e contato]", "APFRodape")
          + par(["Página ", campo("PAGE", "1"), " de ", campo("NUMPAGES", "1")], "APFRodape", '<w:jc w:val="right"/>')
          + "</w:ftr>")

CT = "application/vnd.openxmlformats-officedocument.wordprocessingml"
TIPOS = (XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/>'
         f'<Override PartName="/word/document.xml" ContentType="{CT}.document.main+xml"/>'
         f'<Override PartName="/word/styles.xml" ContentType="{CT}.styles+xml"/>'
         f'<Override PartName="/word/header1.xml" ContentType="{CT}.header+xml"/>'
         f'<Override PartName="/word/footer1.xml" ContentType="{CT}.footer+xml"/>'
         "</Types>")
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RELS = (XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="word/document.xml"/></Relationships>')
DOC_RELS = (XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{REL}/styles" Target="styles.xml"/>'
            f'<Relationship Id="rId2" Type="{REL}/header" Target="header1.xml"/>'
            f'<Relationship Id="rId3" Type="{REL}/footer" Target="footer1.xml"/>'
            "</Relationships>")


def main(destino: str) -> None:
    with zipfile.ZipFile(destino, "x", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", TIPOS)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", corpo())
        z.writestr("word/styles.xml", ESTILOS)
        z.writestr("word/header1.xml", CABECALHO)
        z.writestr("word/footer1.xml", RODAPE)
    print(destino)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "esqueleto.docx")
