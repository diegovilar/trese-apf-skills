"""Testes unitários de nesma-apf-estimator/scripts/apf.py (stdlib unittest).

Rodar a partir da raiz do repositório:
    python3 -m unittest discover -s evals/unit -v
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal

AQUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(AQUI, "..", "..", "nesma-apf-estimator", "scripts", "apf.py")
sys.path.insert(0, os.path.dirname(SCRIPT))
sys.path.insert(0, AQUI)

import apf  # noqa: E402
import fixtures as fx  # noqa: E402

D = Decimal


class TestGabaritos(unittest.TestCase):
    def total(self, est):
        self.assertEqual(apf.validar(est), [])
        return apf.calcular(est)

    def test_g01(self):
        c = self.total(fx.g01())
        self.assertEqual(c["total"], D(45))
        self.assertEqual(c["unidade"], "PF")

    def test_g02_sem_fatores(self):
        c = self.total(fx.g02())
        self.assertEqual(c["total"], D(20))
        self.assertEqual(c["unidade"], "PF de melhoria")
        self.assertIsNone(c["rotulo"])

    def test_g03a_efpa(self):
        c = self.total(fx.g03a())
        fatores = {ln["id"]: ln["fator_min"] for ln in c["linhas"]}
        self.assertEqual(fatores, {"F01": D("0.25"), "F02": D("1.00"), "F03": D("0.75"), "F04": D("0.50"), "F05": D("0.75")})
        self.assertEqual(c["total"], D("14.75"))
        self.assertEqual(c["unidade"], "PFM")
        self.assertEqual(c["rotulo"], apf.ROTULO_HIBRIDO)

    def test_g03b_faixa_parcial(self):
        c = self.total(fx.g03b())
        self.assertIsNone(c["total"])
        self.assertTrue(c["tem_faixa_de_fator"])
        self.assertEqual(c["total_min"], D("5") + D("1.75") + D("1") + D("1"))
        self.assertEqual(c["total_max"], D("5") + D("7") + D("6") + D("4"))
        self.assertIn("PARCIAL", apf.texto_total(c))

    def test_g04_cenarios(self):
        c = self.total(fx.g04())
        # mínimo coerente: AIE de outro sistema + a consulta que ele exige (5 + 4)
        self.assertEqual(c["total_min"], D(9))
        self.assertEqual(c["hipoteses_cenario_min"], ["H3", "H5"])
        # máximo: H2 exige H1, então o grupo fica em H1: 7 + 4 + 8 + 4 + 5
        self.assertEqual(c["total_max"], D(28))
        self.assertEqual(c["hipoteses_cenario_max"], ["H1", "H2", "H3", "H4"])
        self.assertEqual(c["efeito_hipoteses"]["H2"]["min"], D(8))

    def test_g05_indicativa(self):
        c = self.total(fx.g05())
        self.assertEqual(c["total"], D(100))
        self.assertTrue(all(ln["complexidade"] == "—" for ln in c["linhas"]))

    def test_g06(self):
        self.assertEqual(self.total(fx.g06())["total"], D(47))


class TestTabelasEFPA(unittest.TestCase):
    def test_tabela_dados_limites(self):
        self.assertEqual(apf.fator_dados((1, 3), False), D("0.25"))
        self.assertEqual(apf.fator_dados((2, 3), False), D("0.50"))
        self.assertEqual(apf.fator_dados((3, 3), False), D("0.75"))
        self.assertEqual(apf.fator_dados((4, 3), False), D("1.00"))
        self.assertEqual(apf.fator_dados(None, True), D("0.40"))
        self.assertEqual(apf.fator_dados((1, 12), True), D("0.40"))  # maior entre 0,25 e 0,40
        self.assertEqual(apf.fator_dados((5, 10), True), D("0.50"))  # exemplo 3 do guia

    def test_tabela_transacoes_matriz(self):
        esperado = [["0.25", "0.50", "0.75"], ["0.50", "0.75", "1.00"], ["0.75", "1.00", "1.25"], ["1.00", "1.25", "1.50"]]
        ars = [(1, 3), (2, 3), (3, 3), (4, 3)]
        tds = [(2, 3), (3, 3), (4, 3)]
        for i, ar in enumerate(ars):
            for j, td in enumerate(tds):
                self.assertEqual(apf.fator_transacao(td, ar), D(esperado[i][j]), (ar, td))

    def test_exemplo_11_do_guia(self):
        # 8 de 16 TDs afetados (50%), 2 de 2 ARs (100%) -> 0,75
        self.assertEqual(apf.fator_transacao((8, 16), (2, 2)), D("0.75"))


class TestValidacao(unittest.TestCase):
    def erros(self, est):
        return apf.validar(est)

    def test_indicativa_com_melhoria(self):
        e = fx.g05()
        e["tipo_projeto"] = "melhoria"
        e["regime_melhoria"] = "sem-fatores"
        self.assertTrue(any("indicativa" in x for x in self.erros(e)))

    def test_indicativa_sem_transacoes(self):
        e = fx.g05()
        e["funcoes"].append(fx._f("F09", "EE", "Incluir bem"))
        self.assertTrue(any("só tem funções de dados" in x for x in self.erros(e)))

    def test_operacao_obrigatoria_em_melhoria(self):
        e = fx.g02()
        e["funcoes"][0]["operacao"] = None
        self.assertTrue(any("operacao" in x for x in self.erros(e)))

    def test_regime_fora_de_melhoria(self):
        e = fx.g01()
        e["regime_melhoria"] = "nesma"
        self.assertTrue(self.erros(e))

    def test_hipotese_inexistente(self):
        e = fx.g01()
        e["funcoes"][1]["hipotese"] = "H9"
        self.assertTrue(any("H9" in x for x in self.erros(e)))

    def test_hipotese_solta(self):
        e = fx.g01()
        e["hipoteses"] = [{"id": "H1", "descricao": "x"}]
        self.assertTrue(any("não está ligada" in x for x in self.erros(e)))

    def test_efpa_faltando(self):
        e = fx.g03a()
        del e["funcoes"][0]["efpa"]
        self.assertTrue(self.erros(e))

    def test_efpa_em_sem_fatores(self):
        e = fx.g02()
        e["funcoes"][0]["efpa"] = {"td": {"afetados": 1, "originais": 12}}
        self.assertTrue(self.erros(e))

    def test_faixa_e_dados_juntos(self):
        e = fx.g03a()
        e["funcoes"][0]["efpa"]["faixa"] = {"min": "0.25", "max": "0.50", "justificativa": "x"}
        self.assertTrue(any("não informe 'faixa'" in x for x in self.erros(e)))

    def test_faixa_fora_das_tabelas(self):
        e = fx.g03b()
        e["funcoes"][0]["efpa"]["faixa"]["max"] = "0.60"
        self.assertTrue(any("fora dos valores" in x for x in self.erros(e)))

    def test_faixa_dados_nao_aceita_1_50(self):
        e = fx.g03b()
        e["funcoes"][0]["efpa"]["faixa"]["max"] = "1.50"
        self.assertTrue(self.erros(e))

    def test_td_sem_ar_em_transacao(self):
        e = fx.g03a()
        del e["funcoes"][2]["efpa"]["ar"]
        self.assertTrue(any("'td' e 'ar' juntos" in x for x in self.erros(e)))

    def test_dados_sem_td_afetado(self):
        e = fx.g03a()
        e["funcoes"][0]["efpa"] = {"td": {"afetados": 0, "originais": 12}}
        self.assertTrue(any("exemplo 8" in x for x in self.erros(e)))

    def test_ids_repetidos(self):
        e = fx.g01()
        e["funcoes"][1]["id"] = "F01"
        self.assertTrue(any("repetido" in x for x in self.erros(e)))

    def test_grupo_com_uma_hipotese(self):
        e = fx.g04()
        e["hipoteses"][3]["grupo"] = "origem do servidor"
        self.assertTrue(any("grupo" in x for x in self.erros(e)))


class TestGrupos(unittest.TestCase):
    def test_alternativa_exigida_por_hipotese_solta(self):
        e = fx.base()
        e["hipoteses"] = [{"id": "H1", "descricao": "a", "grupo": "g"}, {"id": "H2", "descricao": "b", "grupo": "g"},
                          {"id": "H3", "descricao": "c", "requer": ["H2"]}]
        e["funcoes"] = [fx._f("F01", "ALI", "x", hip="H1"), fx._f("F02", "AIE", "y", hip="H2"),
                        fx._f("F03", "CE", "z", hip="H3"), fx._f("F04", "EE", "w")]
        c = apf.calcular(e)
        self.assertEqual(c["hipoteses_cenario_min"], ["H2"])  # 5 < 7
        self.assertEqual(c["hipoteses_cenario_max"], ["H2", "H3"])  # H3 força H2
        self.assertEqual((c["total_min"], c["total_max"]), (D(4 + 5), D(4 + 5 + 4)))

    def test_exigencia_impossivel(self):
        e = fx.base()
        e["hipoteses"] = [{"id": "H1", "descricao": "a", "grupo": "g", "requer": ["H2"]},
                          {"id": "H2", "descricao": "b", "grupo": "g", "requer": ["H1"]}]
        e["funcoes"] = [fx._f("F01", "ALI", "x", hip="H1"), fx._f("F02", "AIE", "y", hip="H2"), fx._f("F03", "EE", "w")]
        self.assertTrue(any("nenhuma combinação" in x for x in apf.validar(e)))

    def test_cenario_sem_transacao_rejeitado(self):
        e = fx.base()
        e["hipoteses"] = [{"id": "H1", "descricao": "a", "grupo": "g"}, {"id": "H2", "descricao": "b", "grupo": "g"},
                          {"id": "H3", "descricao": "consultar"}]
        e["funcoes"] = [fx._f("F01", "ALI", "x", hip="H1"), fx._f("F02", "AIE", "y", hip="H2"), fx._f("F03", "CE", "z", hip="H3")]
        self.assertTrue(any("nenhuma transação" in x for x in apf.validar(e)))
        e["hipoteses"][0]["requer"] = ["H3"]
        e["hipoteses"][1]["requer"] = ["H3"]
        self.assertEqual(apf.validar(e), [])

    def test_requer_inexistente(self):
        e = fx.g04()
        e["hipoteses"][0]["requer"] = ["H9"]
        self.assertTrue(any("H9" in x for x in apf.validar(e)))


class TestRobustez(unittest.TestCase):
    """JSON malformado gera erros, nunca exceção; JSON aceito sempre calcula e renderiza (O2)."""

    VALORES_RUINS = [None, [], {}, "", "x", 0, -1, 1.5, True, "sNaN", "NaN", "Infinity", [1], {"a": 1}]

    def _caminhos(self, obj, prefixo=()):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield prefixo + (k,)
                yield from self._caminhos(v, prefixo + (k,))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield prefixo + (i,)
                yield from self._caminhos(v, prefixo + (i,))

    def _trocar(self, obj, caminho, valor):
        alvo = obj
        for k in caminho[:-1]:
            alvo = alvo[k]
        alvo[caminho[-1]] = valor

    def test_mutacoes(self):
        bases = [fx.g01(), fx.g02(), fx.g03a(), fx.g03b(), fx.g04(), fx.g05()]
        for b in bases:
            for caminho in list(self._caminhos(b)):
                for ruim in self.VALORES_RUINS:
                    e = fx.clone(b)
                    self._trocar(e, caminho, ruim)
                    try:
                        erros = apf.validar(e)
                        if not erros:
                            c = apf.calcular(e)
                            apf.render_md(e, c)
                            apf.render_txt(e, c)
                            apf.gerar_xlsx(e, c)
                    except Exception as exc:  # pragma: no cover
                        self.fail(f"{b['projeto']['titulo']} {caminho} = {ruim!r}: {type(exc).__name__}: {exc}")

    def test_remocoes(self):
        for b in [fx.g01(), fx.g03a(), fx.g04()]:
            for caminho in list(self._caminhos(b)):
                e = fx.clone(b)
                alvo = e
                for k in caminho[:-1]:
                    alvo = alvo[k]
                if isinstance(alvo, dict):
                    del alvo[caminho[-1]]
                else:
                    alvo.pop(caminho[-1])
                try:
                    if not apf.validar(e):
                        c = apf.calcular(e)
                        apf.render_md(e, c)
                        apf.gerar_xlsx(e, c)
                except Exception as exc:  # pragma: no cover
                    self.fail(f"remover {caminho}: {type(exc).__name__}: {exc}")

    def test_funcoes_ausente(self):
        e = fx.g01()
        del e["funcoes"]
        self.assertTrue(any("funcoes" in x for x in apf.validar(e)))

    def test_fator_snan(self):
        e = fx.g03b()
        e["funcoes"][0]["efpa"]["faixa"]["min"] = "sNaN"
        self.assertTrue(any("inválido" in x for x in apf.validar(e)))


class TestMudancaDeTipo(unittest.TestCase):
    def test_tipo_com_tds_desconhecidos_usa_faixa_a_partir_de_040(self):
        e = fx.base(tipo="melhoria", regime="nesma")
        e["funcoes"] = [fx._f("F01", "ALI", "x", "A", efpa={"mudanca_tipo": True, "faixa": {"min": "0.40", "max": "1.00", "justificativa": "TDs também mudam, proporção desconhecida"}})]
        c = apf.calcular(e)
        self.assertEqual((c["total_min"], c["total_max"]), (D("2.80"), D("7.00")))
        e["funcoes"][0]["efpa"]["faixa"]["min"] = "0.25"
        self.assertTrue(any("min >= 0.40" in x for x in apf.validar(e)))

    def test_so_tipo(self):
        e = fx.base(tipo="melhoria", regime="nesma")
        e["funcoes"] = [fx._f("F01", "AIE", "x", "A", efpa={"mudanca_tipo": True})]
        self.assertEqual(apf.calcular(e)["total"], D("2.00"))


class TestCoberturaEAvisos(unittest.TestCase):
    def test_parcial_aparece_mesmo_com_total_unico(self):
        e = fx.g03a()
        e["cobertura"] = {"status": "parcial", "motivo": "baseline incompleta"}
        c = apf.calcular(e)
        self.assertEqual(c["total"], D("14.75"))
        for saida in (apf.render_md(e, c), apf.render_txt(e, c)):
            self.assertIn("PARCIAL", saida)
            self.assertIn("baseline incompleta", saida)

    def test_parcial_exige_motivo(self):
        e = fx.g01()
        e["cobertura"] = {"status": "parcial"}
        self.assertTrue(any("motivo" in x for x in apf.validar(e)))

    def test_aviso_de_zero(self):
        e = fx.base(tipo="melhoria", regime="sem-fatores")
        e["nao_contados"] = [{"item": "título", "categoria": "fora-do-escopo", "justificativa": "cosmética"}]
        e["avisos"] = ["Pedido só cosmético: no regime nesma valeria 0,25 × peso por transação."]
        c = apf.calcular(e)
        md = apf.render_md(e, c)
        self.assertIn("não significa ausência de trabalho", md)
        self.assertIn("só cosmético", md)


class TestRender(unittest.TestCase):
    def test_md_contem_total_e_legenda(self):
        e = fx.g01()
        md = apf.render_md(e, apf.calcular(e))
        self.assertIn("**Total:** 45 PF", md)
        self.assertIn("## Legenda", md)
        self.assertIn("| F01 |", md)

    def test_md_escapa_barra_vertical(self):
        e = fx.g01()
        e["funcoes"][0]["nome"] = "Curso | Turma"
        md = apf.render_md(e, apf.calcular(e))
        self.assertIn("Curso \\| Turma", md)

    def test_formato_brasileiro(self):
        e = fx.g03a()
        md = apf.render_md(e, apf.calcular(e))
        self.assertIn("14,75 PFM", md)

    def test_md_txt_mesmos_valores(self):  # par metamórfico M03
        for est in (fx.g01(), fx.g03a(), fx.g04()):
            c = apf.calcular(est)
            md, txt = apf.render_md(est, c), apf.render_txt(est, c)
            alvo = apf.texto_total(c)
            self.assertIn(alvo, md)
            self.assertIn(alvo, txt)

    def test_indicativa_tem_aviso(self):
        e = fx.g05()
        self.assertIn("50%", apf.render_md(e, apf.calcular(e)))
        self.assertIn("50%", apf.render_txt(e, apf.calcular(e)))


class TestXlsx(unittest.TestCase):
    def abrir(self, est):
        dados = apf.gerar_xlsx(est, apf.calcular(est))
        return zipfile.ZipFile(io.BytesIO(dados))

    def test_estrutura_e_xml_bem_formado(self):
        import xml.dom.minidom
        for est in (fx.g01(), fx.g03b(), fx.g04(), fx.g05()):
            z = self.abrir(est)
            nomes = z.namelist()
            self.assertIn("xl/workbook.xml", nomes)
            for n in nomes:
                xml.dom.minidom.parseString(z.read(n))

    def test_total_e_formula_com_cache(self):
        z = self.abrir(fx.g01())
        mem = z.read("xl/worksheets/sheet2.xml").decode()
        self.assertIn("<f>SUMPRODUCT(J2:J11,M2:M11)</f><v>45.00</v>", mem)
        res = z.read("xl/worksheets/sheet1.xml").decode()
        self.assertIn("<f>'Memória de cálculo'!J13</f><v>45.00</v>", res)

    def test_legenda_presente(self):
        z = self.abrir(fx.g01())
        wb = z.read("xl/workbook.xml").decode()
        self.assertIn('name="Legenda"', wb)

    def test_caracteres_especiais(self):
        e = fx.g01()
        e["funcoes"][0]["nome"] = "A & B <x> \"y\" \x01"
        z = self.abrir(e)
        import xml.dom.minidom
        xml.dom.minidom.parseString(z.read("xl/worksheets/sheet2.xml"))


class TestCLI(unittest.TestCase):
    def rodar(self, *args):
        return subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True)

    def test_check_ok_e_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            ruim = os.path.join(d, "ruim.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh, ensure_ascii=False)
            e = fx.g01()
            e["metodo"] = "detalhada"
            with open(ruim, "w", encoding="utf-8") as fh:
                json.dump(e, fh)
            self.assertEqual(self.rodar("check", ok).returncode, 0)
            r = self.rodar("check", ruim)
            self.assertEqual(r.returncode, 1)
            self.assertIn("metodo", r.stderr)
            r = self.rodar("render", ruim, "--format", "md")
            self.assertEqual(r.returncode, 1)
            self.assertEqual(r.stdout, "")

    def test_render_xlsx_exige_out(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh)
            self.assertEqual(self.rodar("render", ok, "--format", "xlsx").returncode, 2)
            saida = os.path.join(d, "x.xlsx")
            self.assertEqual(self.rodar("render", ok, "--format", "xlsx", "--out", saida).returncode, 0)
            self.assertTrue(zipfile.is_zipfile(saida))

    def test_calc_json(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g03a(), fh)
            r = self.rodar("calc", ok)
            self.assertEqual(json.loads(r.stdout)["total"], "14.75")

    def test_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh)
            for fmt in ("md", "txt", "xlsx"):
                destino = os.path.join(d, "existente." + fmt)
                with open(destino, "w") as fh:
                    fh.write("conteúdo original")
                r = self.rodar("render", ok, "--format", fmt, "--out", destino)
                self.assertEqual(r.returncode, 3, r.stderr)
                with open(destino) as fh:
                    self.assertEqual(fh.read(), "conteúdo original")


if __name__ == "__main__":
    unittest.main()
