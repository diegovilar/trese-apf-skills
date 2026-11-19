"""Testes do modo interativo do apf.py: esquema v3, estado das perguntas, prévia e resultado final (D47–D51)."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.dirname(os.path.dirname(AQUI))  # trese-apf-skills/dev/<skill>
SCRIPT = os.path.join(os.path.dirname(os.path.dirname(DEV)), "skills", os.path.basename(DEV), "scripts", "apf.py")
sys.path.insert(0, os.path.dirname(SCRIPT))
sys.path.insert(0, AQUI)

import apf  # noqa: E402
import fixtures as fx  # noqa: E402


def g04_lote1():
    """G04 com três perguntas no lote 1, uma ainda aberta e uma pendência sem pergunta."""
    e = fx.g04()
    e["cobertura"] = {"status": "parcial", "motivo": "pedido vago"}
    e["pendencias"] = [
        {"id": "P1", "descricao": "origem das solicitações", "pergunta": "As solicitações são registradas neste sistema (ALI) ou vêm de outro (AIE)?",
         "opcoes": ["registradas aqui", "vêm de outro sistema"], "situacao": "perguntada", "lote": 1},
        {"id": "P2", "descricao": "alcance de 'gerenciar'", "pergunta": "Gerenciar inclui alterar e cancelar?", "situacao": "perguntada", "lote": 1},
        {"id": "P3", "descricao": "o que acontece depois da aprovação", "pergunta": "O que acontece com a solicitação depois de aprovada?",
         "situacao": "perguntada", "lote": 1},
        {"id": "P4", "descricao": "relatórios gerenciais", "pergunta": "Há relatórios além da consulta das próprias solicitações?", "situacao": "aberta"},
        {"id": "P5", "descricao": "forma de autenticação"},
    ]
    e["nao_contados"] = [{"item": "Prestação de contas", "categoria": "sem-evidencia", "justificativa": "não mencionada", "pendencias": ["P3"]}]
    return e


def g04_respondido():
    """Lote 1 respondido: P1 resolvida, P2 sem resposta, P3 resolvida (abre função nova); P4 vai para o lote 2."""
    e = g04_lote1()
    p = {x["id"]: x for x in e["pendencias"]}
    p["P1"]["situacao"] = "resolvida"
    p["P2"]["situacao"] = "sem-resposta"
    p["P3"]["situacao"] = "resolvida"
    p["P4"].update({"situacao": "perguntada", "lote": 2})
    e["esclarecimentos"] = [
        {"id": "E1", "pendencia": "P1", "pergunta": "Registradas aqui ou vêm de outro sistema?", "resposta": "registradas aqui", "lote": 1},
        {"id": "E2", "pendencia": "P2", "pergunta": "Gerenciar inclui alterar e cancelar?", "resposta": "não sei", "lote": 1},
        {"id": "E3", "pendencia": "P3", "pergunta": "O que acontece depois?", "resposta": "o servidor registra a prestação de contas", "lote": 1},
    ]
    e["hipoteses"] = [h for h in e["hipoteses"] if h["id"] != "H5"]
    e["hipoteses"][0]["grupo"] = None
    e["hipoteses"][0]["esclarecimentos"] = ["E1"]
    e["funcoes"] = [f for f in e["funcoes"] if f["id"] != "F07"]
    for f in e["funcoes"]:
        if f["hipotese"] == "H1":
            f["hipotese"] = None
            f["esclarecimentos"] = ["E1"]
    e["hipoteses"] = [h for h in e["hipoteses"] if h["id"] != "H1"]
    for h in e["hipoteses"]:
        h["requer"] = [r for r in (h.get("requer") or []) if r != "H1"]
    e["funcoes"].append({"id": "F08", "requisito": "resposta E3", "nome": "Registrar prestação de contas", "tipo": "EE",
                         "operacao": None, "hipotese": None, "justificativa": "informada pelo analista", "esclarecimentos": ["E3"]})
    e["nao_contados"] = []
    return e


def calcular_final(e):
    e = json.loads(json.dumps(e))
    for p in e["pendencias"]:
        if p.get("situacao") == "perguntada":
            p["situacao"] = "sem-resposta"
    return e


class TestEsquemaV3(unittest.TestCase):
    def erros(self, e):
        return apf.validar(e)

    def test_fluxo_valido(self):
        self.assertEqual(self.erros(g04_lote1()), [])
        self.assertEqual(self.erros(g04_respondido()), [])

    def test_pergunta_exige_situacao(self):
        e = g04_lote1()
        del e["pendencias"][3]["situacao"]
        self.assertTrue(any("situacao" in x for x in self.erros(e)))

    def test_situacao_invalida(self):
        e = g04_lote1()
        e["pendencias"][0]["situacao"] = "respondida"
        self.assertTrue(any("situacao" in x for x in self.erros(e)))

    def test_opcoes_sem_pergunta_ou_mal_formadas(self):
        e = g04_lote1()
        e["pendencias"][4]["opcoes"] = ["a", "b"]
        self.assertTrue(any("opcoes" in x for x in self.erros(e)))
        e = g04_lote1()
        e["pendencias"][0]["opcoes"] = ["só uma"]
        self.assertTrue(any("opcoes" in x for x in self.erros(e)))

    def test_perguntada_exige_lote_e_aberta_nao_tem(self):
        e = g04_lote1()
        del e["pendencias"][0]["lote"]
        self.assertTrue(any("lote" in x for x in self.erros(e)))
        e = g04_lote1()
        e["pendencias"][3]["lote"] = 1
        self.assertTrue(any("lote" in x for x in self.erros(e)))

    def test_teto_do_lote(self):
        e = g04_lote1()
        for i in range(6, 11):
            e["pendencias"].append({"id": f"P{i}", "descricao": "x", "pergunta": "x?", "situacao": "perguntada", "lote": 1})
        self.assertTrue(any("máximo é 7" in x for x in self.erros(e)))

    def test_perguntada_em_lote_antigo(self):
        e = g04_respondido()
        e["pendencias"][1]["situacao"] = "perguntada"  # P2 no lote 1, mas o lote 2 existe
        self.assertTrue(any("ainda 'perguntada' no lote 1" in x for x in self.erros(e)))

    def test_resolvida_exige_esclarecimento(self):
        e = g04_respondido()
        e["esclarecimentos"] = [x for x in e["esclarecimentos"] if x["pendencia"] != "P1"]
        for o in e["hipoteses"] + e["funcoes"]:
            if "E1" in (o.get("esclarecimentos") or []):
                del o["esclarecimentos"]
        self.assertTrue(any("exige um esclarecimento" in x for x in self.erros(e)))

    def test_esclarecimento_de_pendencia_aberta(self):
        e = g04_respondido()
        e["esclarecimentos"].append({"id": "E4", "pendencia": "P4", "pergunta": None, "resposta": "sim", "lote": 2})
        self.assertTrue(any("'P4' tem resposta registrada" in x for x in self.erros(e)))

    def test_esclarecimento_sem_pendencia_e_aceito(self):
        e = g04_respondido()
        e["esclarecimentos"].append({"id": "E4", "pendencia": None, "pergunta": None, "resposta": "também há um relatório mensal", "lote": None})
        self.assertEqual(self.erros(e), [])

    def test_referencias_de_esclarecimento(self):
        e = g04_respondido()
        e["funcoes"][0]["esclarecimentos"] = ["E9"]
        self.assertTrue(any("'E9' não existe" in x for x in self.erros(e)))
        e = g04_respondido()
        e["funcoes"][0]["esclarecimentos"] = []
        self.assertTrue(any("lista não vazia" in x for x in self.erros(e)))
        e = g04_respondido()
        e["esclarecimentos"][0]["id"] = "X1"
        self.assertTrue(any("formato E1" in x for x in self.erros(e)))

    def test_sem_evidencia_so_com_pendencias_resolvidas(self):
        e = g04_respondido()
        e["nao_contados"] = [{"item": "Prestação de contas", "categoria": "sem-evidencia", "justificativa": "x", "pendencias": ["P3"]}]
        self.assertTrue(any("todas as pendências apontadas foram resolvidas" in x for x in self.erros(e)))
        e["nao_contados"][0]["pendencias"] = ["P3", "P5"]
        self.assertEqual(self.erros(e), [])

    def test_esquema_v2_recusado(self):
        e = g04_lote1()
        e["versao_esquema"] = 2
        self.assertTrue(any("versao_esquema" in x for x in self.erros(e)))

    def test_mutacoes_nao_geram_excecao(self):
        valores = [None, 0, -1, 1.5, "", "x", [], {}, ["x"], [1], True]
        base = g04_respondido()
        for alvo in ("pendencias", "esclarecimentos"):
            for i in range(len(base[alvo])):
                for chave in list(base[alvo][i].keys()) + ["lote", "situacao", "opcoes", "pergunta"]:
                    for v in valores:
                        e = json.loads(json.dumps(base))
                        e[alvo][i][chave] = v
                        try:
                            apf.validar(e)
                        except Exception as exc:  # pragma: no cover
                            self.fail(f"{alvo}[{i}].{chave}={v!r}: {exc!r}")
        for v in valores:
            e = json.loads(json.dumps(base))
            e["esclarecimentos"] = v
            apf.validar(e)
            e = json.loads(json.dumps(base))
            e["funcoes"][0]["esclarecimentos"] = v
            apf.validar(e)


class TestPrevia(unittest.TestCase):
    def test_sem_numeros_de_pf(self):
        texto = apf.render_previa(g04_lote1())
        self.assertNotRegex(texto, r"\bPF\b|PFM|Total|Cenário|Complexidade")
        self.assertNotRegex(texto, r"\|\s*\d+\s*\|")  # nenhuma célula só com número
        self.assertTrue(texto.startswith("# Prévia da estimativa: "))
        self.assertNotIn("confira a lista", texto)  # D67: sem introdução redundante

    def test_tipos_em_termos_de_negocio(self):
        texto = apf.render_previa(g04_lote1())
        self.assertIn("dados mantidos pelo sistema (ALI)", texto)
        self.assertIn("dados lidos de outro sistema (AIE)", texto)
        self.assertIn("consulta sem cálculo (CE)", texto)
        self.assertIn("suposta (H1)", texto)

    def test_lote_atual_e_restantes(self):
        texto = apf.render_previa(g04_lote1())
        self.assertIn("## Perguntas (lote 1)", texto)
        perguntas = re.findall(r"^\d+\. \*\*\((P\d+)\)\*\*", texto, re.M)
        self.assertEqual(perguntas, ["P1", "P2", "P3"])
        self.assertIn("Opções: registradas aqui; vêm de outro sistema.", texto)
        self.assertIn("Ainda falta 1 pergunta, que vem no próximo lote.", texto)
        self.assertIn(apf.PREVIA_FECHO_PERGUNTAS, texto)
        self.assertIn("por texto, use o número", apf.PREVIA_FECHO_PERGUNTAS)  # fecho válido nos dois canais (2B)
        self.assertNotIn(apf.FECHO_CORRECAO, texto)
        self.assertIn(apf.AVISO_PENDENCIAS, texto)
        outras = texto.split("## Outras pendências registradas")[1]
        self.assertIn("**P4.**", outras)
        self.assertIn("**P5.**", outras)
        self.assertNotIn("**P1.**", outras)

    def test_canal_ferramenta_so_anuncia_o_lote(self):
        """D62: com ferramenta, a prévia não traz as perguntas nem o convite a responder por texto; o resto é igual."""
        e = g04_lote1()
        texto, ferr = apf.render_previa(e), apf.render_previa(e, "ferramenta")
        self.assertEqual(texto, apf.render_previa(e, "texto"))
        self.assertIn("## Perguntas (lote 1)", ferr)
        self.assertIn("As 3 perguntas deste lote vêm a seguir, na ferramenta de perguntas.", ferr)
        for q in e["pendencias"][:3]:
            self.assertNotIn(q["pergunta"], ferr)
        self.assertNotIn("Opções:", ferr)
        self.assertNotIn(apf.PREVIA_FECHO_PERGUNTAS, ferr)
        self.assertIn(apf.PREVIA_FECHO_FERRAMENTA, ferr)
        self.assertIn("Ainda falta 1 pergunta, que vem no próximo lote.", ferr)
        self.assertIn(apf.AVISO_PENDENCIAS, ferr)
        antes = lambda t: t.split("## Perguntas")[0]
        depois = lambda t: t.split("## Outras pendências registradas")[1].split("**Aviso:**")[0]
        self.assertEqual(antes(texto), antes(ferr))
        self.assertEqual(depois(texto), depois(ferr))
        self.assertIn("A pergunta deste lote vem a seguir", apf._anuncio_ferramenta(1))
        # sem perguntas, os dois canais são iguais
        self.assertEqual(apf.render_previa(fx.g01(), "ferramenta"), apf.render_previa(fx.g01()))
        with self.assertRaises(ValueError):
            apf.render_previa(e, "chat")

    def test_cli_canal(self):
        with tempfile.TemporaryDirectory() as d:
            j = os.path.join(d, "e.json")
            with open(j, "w", encoding="utf-8") as fh:
                json.dump(g04_lote1(), fh, ensure_ascii=False)
            r = subprocess.run([sys.executable, SCRIPT, "render", j, "--format", "previa", "--canal", "ferramenta"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("vêm a seguir, na ferramenta de perguntas", r.stdout)
            r = subprocess.run([sys.executable, SCRIPT, "render", j, "--format", "previa"], capture_output=True, text=True)
            self.assertIn(apf.PREVIA_FECHO_PERGUNTAS, r.stdout)
            ok = os.path.join(d, "ok.json")
            with open(ok, "w", encoding="utf-8") as fh:
                json.dump(fx.g01(), fh, ensure_ascii=False)
            r = subprocess.run([sys.executable, SCRIPT, "render", ok, "--format", "md", "--canal", "texto"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)

    def test_segundo_lote_mostra_esclarecimentos(self):
        texto = apf.render_previa(g04_respondido())
        self.assertIn("## Perguntas (lote 2)", texto)
        self.assertIn("## Esclarecimentos já recebidos", texto)
        self.assertIn("afirmada (ver E1)", texto)
        self.assertIn("(perguntada no lote 1, sem resposta)", texto)
        self.assertNotIn("Ainda falta", texto)

    def test_sem_perguntas(self):
        e = fx.g01()
        texto = apf.render_previa(e)
        self.assertNotIn("## Perguntas", texto)
        self.assertIn(apf.PREVIA_FECHO_SEM_PERGUNTAS, texto)

    def test_abertas_sem_lote_recusadas(self):
        e = g04_lote1()
        for p in e["pendencias"]:
            if p.get("situacao") == "perguntada":
                p["situacao"] = "aberta"
                del p["lote"]
        self.assertEqual(apf.validar(e), [])
        self.assertTrue(apf.validar_previa(e))
        self.assertEqual(apf.validar_previa(g04_lote1()), [])

    def test_melhoria_mostra_situacao(self):
        texto = apf.render_previa(fx.g02())
        self.assertIn("| Situação |", texto)
        self.assertIn("alterada", texto)


class TestFinal(unittest.TestCase):
    def test_final_recusa_perguntada(self):
        self.assertTrue(apf.validar_final(g04_lote1()))
        self.assertEqual(apf.validar_final(calcular_final(g04_lote1())), [])

    def test_resolvidas_saem_das_pendencias_e_vao_para_esclarecimentos(self):
        e = calcular_final(g04_respondido())
        calc = apf.calcular(e)
        for texto in (apf.render_md(e, calc, "chat"), apf.render_txt(e, calc)):
            pend = re.split(r"DÚVIDAS DE REQUISITO E PENDÊNCIAS|Dúvidas de requisito e pendências", texto)[1]
            self.assertNotIn("P1.", pend)
            self.assertNotIn("P3.", pend)
            self.assertIn("perguntada no lote 1, sem resposta", pend)
            self.assertIn("perguntada no lote 2, sem resposta", pend)
            self.assertIn("o servidor registra a prestação de contas", " ".join(texto.split()))
        md = apf.render_md(e, calc, "chat")
        self.assertIn("## Esclarecimentos do analista", md)
        self.assertIn("| evidência (ver E3) |", md)
        self.assertIn("Esclarecimento (E1, E2…)", md)

    def test_legenda_chat_sem_esclarecimentos(self):
        e = fx.g01()
        md = apf.render_md(e, apf.calcular(e), "chat")
        self.assertNotIn("Esclarecimento", md)
        self.assertNotIn("Esclarecimento", apf.render_md(e, apf.calcular(e), "arquivo"))  # D64

    def test_xlsx_tem_esclarecimentos(self):
        import io
        import zipfile
        e = calcular_final(g04_respondido())
        dados = apf.gerar_xlsx(e, apf.calcular(e))
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            xml = "".join(z.read(n).decode("utf-8") for n in z.namelist() if n.startswith("xl/worksheets/"))
        self.assertIn("Esclarecimento do analista", xml)
        self.assertIn("evidência (ver E3)", xml)

    def test_nao_sei_em_tudo_equivale_ao_modo_nao_interativo(self):
        """Relação metamórfica D44 no nível do script: perguntas sem resposta não mudam funções, cenários nem totais."""
        sem_perguntas = fx.g04()
        sem_perguntas["pendencias"] = [{"id": f"P{i}", "descricao": d} for i, d in
                                       enumerate(["origem", "gerenciar", "depois da aprovação", "relatórios", "autenticação"], 1)]
        com_nao_sei = calcular_final(g04_lote1())
        for p in com_nao_sei["pendencias"]:
            if p.get("situacao") == "aberta":
                p.update({"situacao": "sem-resposta", "lote": 2})
        com_nao_sei["nao_contados"] = []
        com_nao_sei["cobertura"] = sem_perguntas["cobertura"]
        a, b = apf.calcular(sem_perguntas), apf.calcular(com_nao_sei)
        for chave in ("total_min", "total_max", "hipoteses_cenario_min", "hipoteses_cenario_max", "unidade"):
            self.assertEqual(a[chave], b[chave], chave)
        self.assertEqual([(ln["id"], ln["tipo"]) for ln in a["linhas"]], [(ln["id"], ln["tipo"]) for ln in b["linhas"]])


class TestEquivalenciaDeRepresentacao(unittest.TestCase):
    """Consulta 24: grupo com uma alternativa vazia × hipótese opcional sem grupo (base da regra do juiz no S3)."""

    def _base(self):
        e = fx.base(titulo="conferência")
        e["funcoes"] = [
            {"id": "F01", "requisito": "x", "nome": "Remessa", "tipo": "ALI", "operacao": None, "hipotese": None, "justificativa": "x"},
            {"id": "F02", "requisito": "x", "nome": "Registrar retorno", "tipo": "EE", "operacao": None, "hipotese": None, "justificativa": "x"},
            {"id": "F03", "requisito": "x", "nome": "Registrar conferência", "tipo": "EE", "operacao": None, "hipotese": "H2", "justificativa": "x"},
        ]
        return e

    def _grupo(self):
        e = self._base()
        e["hipoteses"] = [
            {"id": "H1", "descricao": "conferência no registro do retorno", "trecho": "x", "grupo": "conferência"},
            {"id": "H2", "descricao": "conferência registrada depois", "trecho": "x", "grupo": "conferência"},
        ]
        return e

    def _opcional(self):
        e = self._base()
        e["hipoteses"] = [{"id": "H2", "descricao": "conferência registrada depois", "trecho": "x"}]
        return e

    def test_mesmos_cenarios(self):
        a, b = apf.calcular(self._grupo()), apf.calcular(self._opcional())
        self.assertEqual((a["total_min"], a["total_max"]), (b["total_min"], b["total_max"]))
        self.assertEqual((a["total_min"], a["total_max"]), (11, 15))

    def test_alternativa_vazia_com_restricao_nao_equivale(self):
        """Se a alternativa vazia exige outra hipótese, a forma opcional perderia essa restrição."""
        g = self._grupo()
        g["funcoes"].append({"id": "F04", "requisito": "x", "nome": "Consultar pendentes de conferência", "tipo": "CE",
                             "operacao": None, "hipotese": "H3", "justificativa": "x"})
        g["hipoteses"][0]["requer"] = ["H3"]
        g["hipoteses"].append({"id": "H3", "descricao": "consulta exigida pela conferência no retorno", "trecho": "x"})
        o = self._opcional()
        o["funcoes"].append(g["funcoes"][-1])
        o["hipoteses"].append({"id": "H3", "descricao": "consulta exigida pela conferência no retorno", "trecho": "x"})
        a, b = apf.calcular(g), apf.calcular(o)
        self.assertNotEqual((a["total_min"], a["total_max"]), (b["total_min"], b["total_max"]))


class TestCLIInterativo(unittest.TestCase):
    def rodar(self, *args):
        return subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True)

    def gravar(self, d, nome, e):
        caminho = os.path.join(d, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(e, fh, ensure_ascii=False)
        return caminho

    def test_previa_imprime_e_nao_grava(self):
        with tempfile.TemporaryDirectory() as d:
            j = self.gravar(d, "e.json", g04_lote1())
            r = self.rodar("render", j, "--format", "previa")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("# Prévia da estimativa", r.stdout)
            r = self.rodar("render", j, "--format", "previa", "--out", os.path.join(d, "p.md"))
            self.assertEqual(r.returncode, 2)
            self.assertFalse(os.path.exists(os.path.join(d, "p.md")))

    def test_final_recusado_com_pergunta_pendente(self):
        with tempfile.TemporaryDirectory() as d:
            j = self.gravar(d, "e.json", g04_lote1())
            for fmt in ("md", "txt"):
                r = self.rodar("render", j, "--format", fmt)
                self.assertEqual(r.returncode, 1)
                self.assertEqual(r.stdout, "")
                self.assertIn("ainda 'perguntada'", r.stderr)
            r = self.rodar("render", j, "--format", "xlsx", "--out", os.path.join(d, "x.xlsx"))
            self.assertEqual(r.returncode, 1)
            self.assertFalse(os.path.exists(os.path.join(d, "x.xlsx")))
            self.assertEqual(self.rodar("check", j).returncode, 0)

    def test_previa_recusada_sem_lote(self):
        e = g04_lote1()
        for p in e["pendencias"]:
            if p.get("situacao") == "perguntada":
                p["situacao"] = "aberta"
                del p["lote"]
        with tempfile.TemporaryDirectory() as d:
            j = self.gravar(d, "e.json", e)
            r = self.rodar("render", j, "--format", "previa")
            self.assertEqual(r.returncode, 1)
            self.assertIn("nenhuma no lote atual", r.stderr)


if __name__ == "__main__":
    unittest.main()
