"""Testes da exportação .docx (D74): modelo, corpo gerado, CLI e normalização do modelo.

Rodar a partir de trese-apf-skills/dev/trese-apf-aproximacao/:
    python3 -m unittest discover -s evals/unit -v
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr
from xml.etree import ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.dirname(os.path.dirname(AQUI))
SCRIPT = os.path.join(os.path.dirname(os.path.dirname(DEV)), "skills", os.path.basename(DEV), "scripts", "apf.py")
sys.path.insert(0, os.path.dirname(SCRIPT))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(DEV, "modelo"))

import apf  # noqa: E402
import fixtures as fx  # noqa: E402
import normalizar  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FIXTURES = (fx.g01, fx.g02, fx.g03a, fx.g03b, fx.g04, fx.g05, fx.g06)


def partes(dados):
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        return {n: z.read(n) for n in z.namelist()}


def texto_do_corpo(dados):
    raiz = ET.fromstring(partes(dados)["word/document.xml"])
    return " ".join("".join(t.text or "" for t in p.iter(W + "t")) for p in raiz.iter(W + "p"))


def reescrever(origem, destino, trocas):
    """Copia um .docx trocando partes: {nome: bytes ou None para remover}."""
    with zipfile.ZipFile(origem) as zi, zipfile.ZipFile(destino, "w") as zo:
        for info in zi.infolist():
            if info.filename in trocas:
                if trocas[info.filename] is not None:
                    zo.writestr(info, trocas[info.filename])
            else:
                zo.writestr(info, zi.read(info.filename))


class TestModelo(unittest.TestCase):
    def test_modelo_da_skill_e_valido(self):
        _, _, sect, _, util = apf._ler_modelo(apf.MODELO_DOCX)
        self.assertIn("w:headerReference", sect)
        self.assertIn("w:footerReference", sect)
        self.assertGreater(util, 5000)

    def test_modelo_da_skill_tem_corpo_vazio(self):
        doc = partes(open(apf.MODELO_DOCX, "rb").read())["word/document.xml"].decode("utf-8")
        corpo = re.search(r"<w:body>(.*)</w:body>", doc, re.S).group(1)
        self.assertTrue(corpo.strip().startswith("<w:sectPr"))

    def test_cabecalho_e_rodape_referenciados_existem(self):
        p = partes(open(apf.MODELO_DOCX, "rb").read())
        rels = p["word/_rels/document.xml.rels"].decode("utf-8")
        _, _, sect, _, _ = apf._ler_modelo(apf.MODELO_DOCX)
        for rid in re.findall(r'r:id="([^"]+)"', sect):
            alvo = re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, rels)
            self.assertIsNotNone(alvo, rid)
            self.assertIn("word/" + alvo.group(1), p)

    def test_modelos_invalidos(self):
        with tempfile.TemporaryDirectory() as d:
            casos = {}
            casos["ausente"] = os.path.join(d, "nao-existe.docx")
            corrompido = os.path.join(d, "corrompido.docx")
            with open(corrompido, "wb") as fh:
                fh.write(b"isto nao e zip")
            casos["corrompido"] = corrompido
            estilos = partes(open(apf.MODELO_DOCX, "rb").read())["word/styles.xml"]
            sem_estilo = os.path.join(d, "sem-estilo.docx")
            reescrever(apf.MODELO_DOCX, sem_estilo, {"word/styles.xml": estilos.replace(b'w:styleId="APFCelula"', b'w:styleId="Outro"')})
            casos["sem estilo"] = sem_estilo
            doc = partes(open(apf.MODELO_DOCX, "rb").read())["word/document.xml"]
            duas = os.path.join(d, "duas-secoes.docx")
            reescrever(apf.MODELO_DOCX, duas, {"word/document.xml": doc.replace(
                b"<w:body>", b"<w:body><w:p><w:pPr><w:sectPr/></w:pPr></w:p>")})
            casos["duas seções"] = duas
            sem_parte = os.path.join(d, "sem-estilos.docx")
            reescrever(apf.MODELO_DOCX, sem_parte, {"word/styles.xml": None})
            casos["sem styles.xml"] = sem_parte
            sem_cabecalho = os.path.join(d, "sem-cabecalho.docx")
            reescrever(apf.MODELO_DOCX, sem_cabecalho, {"word/header1.xml": None})
            casos["cabeçalho referenciado ausente"] = sem_cabecalho
            xml_quebrado = os.path.join(d, "xml-quebrado.docx")
            reescrever(apf.MODELO_DOCX, xml_quebrado, {"word/styles.xml": estilos + b"<lixo"})
            casos["XML inválido"] = xml_quebrado
            rels_texto = os.path.join(d, "rels-texto.docx")
            reescrever(apf.MODELO_DOCX, rels_texto, {"_rels/.rels": b"isto nao e xml"})
            casos["_rels/.rels inválido"] = rels_texto
            rels = partes(open(apf.MODELO_DOCX, "rb").read())["word/_rels/document.xml.rels"]
            sem_rel = os.path.join(d, "sem-rel.docx")
            reescrever(apf.MODELO_DOCX, sem_rel, {"word/_rels/document.xml.rels": rels.replace(b'Id="rId2"', b'Id="rId99"')})
            casos["seção referencia rId ausente"] = sem_rel
            e = fx.g01()
            c = apf.calcular(e)
            for nome, caminho in casos.items():
                with self.subTest(nome):
                    with self.assertRaises(apf.ErroModelo):
                        apf.gerar_docx(e, c, caminho)


class TestCorpo(unittest.TestCase):
    def test_xml_bem_formado_e_estilos_existentes(self):
        estilos_modelo = set(re.findall(r'w:styleId="([^"]+)"', partes(open(apf.MODELO_DOCX, "rb").read())["word/styles.xml"].decode()))
        for f in FIXTURES:
            e = f()
            dados = apf.gerar_docx(e, apf.calcular(e))
            with self.subTest(f.__name__):
                p = partes(dados)
                for nome, conteudo in p.items():
                    if nome.endswith(".xml") or nome.endswith(".rels"):
                        ET.fromstring(conteudo)
                doc = p["word/document.xml"].decode("utf-8")
                self.assertEqual(doc.count("<w:sectPr"), 1)
                self.assertTrue(re.search(r"</w:sectPr>\s*</w:body>", doc))
                usados = set(re.findall(r'<w:(?:pStyle|rStyle) w:val="([^"]+)"', doc))
                self.assertLessEqual(usados, estilos_modelo)
                # tudo do modelo, menos o corpo, fica igual
                modelo = partes(open(apf.MODELO_DOCX, "rb").read())
                self.assertEqual({n: v for n, v in p.items() if n != "word/document.xml"},
                                 {n: v for n, v in modelo.items() if n != "word/document.xml"})

    def test_conteudo_igual_ao_do_md(self):
        for f in FIXTURES:
            e = f()
            c = apf.calcular(e)
            texto = texto_do_corpo(apf.gerar_docx(e, c))
            with self.subTest(f.__name__):
                self.assertTrue(texto.startswith(apf.TITULO_DOCUMENTO))
                for _, valor, _ in apf.identificacao(e, "arquivo"):
                    self.assertIn(apf._md(valor), texto)
                self.assertIn(apf.texto_total(c), texto)
                for ln in c["linhas"]:
                    self.assertIn(ln["id"], texto)
                for fn in e["funcoes"]:
                    self.assertIn(apf._md(fn["nome"]), texto)
                self.assertIn(apf.AVISO_PENDENCIAS, texto)
                for termo, desc in apf.legenda(e, c, "arquivo"):
                    self.assertIn(f"{termo}: {desc}", texto)
                self.assertNotIn(apf.FECHO_CORRECAO, texto)
                for h in e.get("hipoteses", []):
                    self.assertIn(h["id"], texto)

    def test_campos_a_preencher_com_estilo_proprio(self):
        e = fx.g01()
        doc = partes(apf.gerar_docx(e, apf.calcular(e)))["word/document.xml"].decode("utf-8")
        for _, v in apf.CAMPOS_A_PREENCHER:
            self.assertIn(f'<w:rStyle w:val="APFCampo"/></w:rPr><w:t xml:space="preserve">{v}</w:t>', doc)

    def test_caracteres_especiais_e_texto_longo(self):
        e = fx.g01()
        longo = "x" * 40000
        e["projeto"]["titulo"] = "A & B <c> \"d\" 😀 \x07fim"
        e["funcoes"][0]["justificativa"] = longo
        dados = apf.gerar_docx(e, apf.calcular(e))
        ET.fromstring(partes(dados)["word/document.xml"])
        texto = texto_do_corpo(dados)
        self.assertIn("A & B <c> \"d\" 😀 fim", texto)
        self.assertIn(longo, texto)  # sem truncamento (o xlsx trunca em 32.767; o docx não)

    def test_largura_das_tabelas_igual_a_area_util(self):
        _, _, _, _, util = apf._ler_modelo(apf.MODELO_DOCX)
        for f in (fx.g01, fx.g03b, fx.g04):
            e = f()
            doc = partes(apf.gerar_docx(e, apf.calcular(e)))["word/document.xml"].decode("utf-8")
            for grade in re.findall(r"<w:tblGrid>(.*?)</w:tblGrid>", doc):
                self.assertEqual(sum(int(x) for x in re.findall(r'w:w="(\d+)"', grade)), util)


class TestCLIDocx(unittest.TestCase):
    def rodar(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)

    def test_exige_out_grava_e_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh, ensure_ascii=False)
            self.assertEqual(self.rodar("render", ok, "--format", "docx").returncode, 2)
            saida = os.path.join(d, "x.docx")
            r = self.rodar("render", ok, "--format", "docx", "--out", saida)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(zipfile.is_zipfile(saida))
            antes = open(saida, "rb").read()
            self.assertEqual(self.rodar("render", ok, "--format", "docx", "--out", saida).returncode, 3)
            self.assertEqual(open(saida, "rb").read(), antes)

    def test_modelo_ausente_nao_grava_nada(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh, ensure_ascii=False)
            saida = os.path.join(d, "x.docx")
            original = apf.MODELO_DOCX
            apf.MODELO_DOCX = os.path.join(d, "sumiu.docx")
            try:
                with redirect_stderr(io.StringIO()) as err:
                    codigo = apf.main(["render", ok, "--format", "docx", "--out", saida])
            finally:
                apf.MODELO_DOCX = original
            self.assertEqual(codigo, 2)
            self.assertIn("Nada foi gravado", err.getvalue())
            self.assertFalse(os.path.exists(saida))


class TestNormalizar(unittest.TestCase):
    ESQUELETO = os.path.join(DEV, "modelo", "esqueleto.docx")

    def test_esqueleto_normalizado_e_valido_e_ids_fixados(self):
        with tempfile.TemporaryDirectory() as d:
            p = partes(open(self.ESQUELETO, "rb").read())
            # simula o LibreOffice: ID derivado do nome, com referência em outro estilo
            estilos = p["word/styles.xml"].replace(b'w:styleId="APFCampo"', b'w:styleId="APFCampoapreencher"')
            estilos = estilos.replace(b'w:styleId="APFCelulaNumero"', b'w:styleId="APFCelulaNumero1"')
            doc = p["word/document.xml"].replace(b'w:val="APFCampo"', b'w:val="APFCampoapreencher"')
            editado = os.path.join(d, "editado.docx")
            reescrever(self.ESQUELETO, editado, {"word/styles.xml": estilos, "word/document.xml": doc})
            destino = os.path.join(d, "modelo.docx")
            with redirect_stdout_silencioso():
                normalizar.normalizar(editado, destino)
            apf._ler_modelo(destino)
            st = partes(open(destino, "rb").read())["word/styles.xml"].decode()
            self.assertIn('w:styleId="APFCampo"', st)
            self.assertIn('w:styleId="APFCelulaNumero"', st)
            self.assertNotIn("APFCampoapreencher", st)
            e = fx.g03b()
            apf.gerar_docx(e, apf.calcular(e), destino)

    def test_relacao_externa_recusada_em_qualquer_ordem(self):
        with tempfile.TemporaryDirectory() as d:
            for ordem in ('Target="media/x.png" TargetMode="External"', 'TargetMode="External" Target="media/x.png"'):
                with self.subTest(ordem):
                    rel = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/'
                           'package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
                           f'officeDocument/2006/relationships/image" {ordem}/></Relationships>').encode()
                    editado = os.path.join(d, "editado.docx")
                    with zipfile.ZipFile(self.ESQUELETO) as zi, zipfile.ZipFile(editado, "w") as zo:
                        for info in zi.infolist():
                            zo.writestr(info, zi.read(info.filename))
                        zo.writestr("word/_rels/header1.xml.rels", rel)
                        zo.writestr("word/media/x.png", b"png")  # o caminho existe no pacote: só o modo deve recusar
                    with self.assertRaises(normalizar.Erro):
                        normalizar.normalizar(editado, os.path.join(d, "modelo.docx"))
                    os.remove(editado)

    def test_estilo_apagado_e_recusado(self):
        with tempfile.TemporaryDirectory() as d:
            p = partes(open(self.ESQUELETO, "rb").read())
            estilos = p["word/styles.xml"].replace(b'<w:name w:val="APF Aviso"/>', b'<w:name w:val="Outro"/>')
            editado = os.path.join(d, "editado.docx")
            reescrever(self.ESQUELETO, editado, {"word/styles.xml": estilos})
            with self.assertRaises(normalizar.Erro):
                normalizar.normalizar(editado, os.path.join(d, "modelo.docx"))
            self.assertFalse(os.path.exists(os.path.join(d, "modelo.docx")))


class redirect_stdout_silencioso:
    def __enter__(self):
        self._antigo = sys.stdout
        sys.stdout = io.StringIO()

    def __exit__(self, *a):
        sys.stdout = self._antigo


if __name__ == "__main__":
    unittest.main()
