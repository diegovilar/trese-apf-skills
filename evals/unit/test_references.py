"""Consistência entre references/ e o script: os números publicados nos exemplos batem com apf.py."""
import json
import os
import re
import sys
import unittest
from decimal import Decimal

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(AQUI, "..", "..", "nesma-apf-estimator")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
sys.path.insert(0, AQUI)

import apf  # noqa: E402
import fixtures as fx  # noqa: E402

D = Decimal


def ler(nome):
    with open(os.path.join(SKILL, "references", nome), encoding="utf-8") as fh:
        return fh.read()


class TestExemplosDe04(unittest.TestCase):
    def test_exemplo1_json_de_05(self):
        texto = ler("05-saida-e-legenda.md")
        bloco = texto.split("## 5. Exemplo completo")[1].split("```json")[1].split("```")[0]
        est = json.loads(bloco)
        self.assertEqual(apf.validar(est), [])
        self.assertEqual(apf.calcular(est)["total"], D(41))
        self.assertIn("**41 PF**", ler("04-exemplos-praticos.md"))

    def test_exemplo2_sem_fatores(self):
        e = fx.base(tipo="melhoria", regime="sem-fatores")
        e["funcoes"] = [fx._f("F01", "ALI", "Requisição", "A"), fx._f("F02", "AIE", "Saldo", "I"),
                        fx._f("F03", "EE", "Registrar", "A"), fx._f("F04", "CE", "Consultar", "A")]
        self.assertEqual(apf.calcular(e)["total"], D(20))

    def test_exemplo2_nesma_faixas(self):
        e = fx.base(tipo="melhoria", regime="nesma")
        fa = lambda a, b: {"faixa": {"min": a, "max": b, "justificativa": "x"}}
        e["funcoes"] = [fx._f("F01", "ALI", "Requisição", "A", efpa=fa("0.25", "0.75")),
                        fx._f("F02", "AIE", "Saldo", "I"),
                        fx._f("F03", "EE", "Registrar", "A", efpa=fa("0.25", "1.25")),
                        fx._f("F04", "CE", "Consultar", "A", efpa=fa("0.25", "1.00"))]
        c = apf.calcular(e)
        self.assertEqual((c["total_min"], c["total_max"]), (D("8.75"), D("19.25")))
        self.assertIn("8,75–19,25 PFM", ler("04-exemplos-praticos.md"))

    def test_exemplo2_faixas_sao_os_extremos_das_tabelas(self):
        # ALI: 1 TD novo sobre N originais (N >= 1)
        fat = {apf.fator_dados((1, n), False) for n in range(1, 40)}
        self.assertEqual((min(fat), max(fat)), (D("0.25"), D("0.75")))
        # EE: 2 ARs afetados sobre n >= 1 originais; 1 TD novo sobre m >= 1 originais
        fat = {apf.fator_transacao((1, m), (2, n)) for n in range(1, 40) for m in range(1, 40)}
        self.assertEqual((min(fat), max(fat)), (D("0.25"), D("1.25")))
        # CE: 1 AR afetado sobre n >= 1; 1 TD novo sobre m >= 1
        fat = {apf.fator_transacao((1, m), (1, n)) for n in range(1, 40) for m in range(1, 40)}
        self.assertEqual((min(fat), max(fat)), (D("0.25"), D("1.00")))

    def test_exemplo3_grupo(self):
        e = fx.base()
        e["hipoteses"] = [{"id": "H1", "descricao": "mantidos aqui", "grupo": "origem", "requer": ["H3"]},
                          {"id": "H2", "descricao": "lidos de outro", "grupo": "origem", "requer": ["H3"]},
                          {"id": "H3", "descricao": "consultar", "trecho": "acompanhar"}]
        e["funcoes"] = [fx._f("F01", "ALI", "Contrato", hip="H1"), fx._f("F02", "EE", "Registrar contrato", hip="H1"),
                        fx._f("F03", "AIE", "Contrato", hip="H2"), fx._f("F04", "CE", "Consultar", hip="H3")]
        c = apf.calcular(e)
        self.assertEqual((c["total_min"], c["total_max"]), (D(9), D(15)))
        texto = ler("04-exemplos-praticos.md")
        self.assertIn("**Cenário mínimo:** 9 PF", texto)
        self.assertIn("**Cenário máximo:** 15 PF", texto)

    def test_exemplo4_indicativa(self):
        e = fx.base(metodo="indicativa")
        e["funcoes"] = [fx._f("F01", "ALI", "a"), fx._f("F02", "ALI", "b"), fx._f("F03", "ALI", "c"),
                        fx._f("F04", "AIE", "d"), fx._f("F05", "AIE", "e")]
        self.assertEqual(apf.calcular(e)["total"], D(135))
        self.assertIn("**135 PF**", ler("04-exemplos-praticos.md"))


class TestPesosPublicados(unittest.TestCase):
    def test_tabela_estimada_em_02_bate_com_script(self):
        texto = ler("02-regras-nesma.md")
        for tipo, peso in apf.PESOS_ESTIMADA.items():
            self.assertRegex(texto, rf"\| {tipo} \| (Baixa|Média) \| {peso} \|")

    def test_tabela2_em_02_bate_com_script(self):
        texto = ler("02-regras-nesma.md")
        rotulos = ["≤ 1/3", "≤ 2/3", "≤ 100%", "> 100%"]
        for rot, linha in zip(rotulos, apf.TABELA_TRANSACOES):
            valores = " | ".join(apf.num(v, 2) for v in linha)
            self.assertIn(f"| {rot} | {valores} |", texto)


class TestVazio(unittest.TestCase):
    def test_pedido_so_cosmetico_sem_fatores(self):
        e = fx.base(tipo="melhoria", regime="sem-fatores")
        e["nao_contados"] = [{"item": "Trocar título do relatório", "categoria": "fora-do-escopo",
                              "justificativa": "alteração cosmética; no regime nesma valeria 0,25 × peso"}]
        c = apf.calcular(e)
        self.assertEqual(c["total"], D(0))
        apf.render_md(e, c)
        apf.render_txt(e, c)
        self.assertTrue(apf.gerar_xlsx(e, c))

    def test_vazio_sem_justificativa_rejeitado(self):
        e = fx.base()
        self.assertTrue(apf.validar(e))


if __name__ == "__main__":
    unittest.main()
