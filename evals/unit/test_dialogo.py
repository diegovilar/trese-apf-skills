"""Camada 2 mínima (consultas 40 e 41): diálogos roteirizados, retomada de sessão, continuidade dos snapshots,
relações entre turnos e juiz do diálogo. Sem chamar Claude nem Codex."""
import copy
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "agente"))
sys.path.insert(0, str(AQUI))
import calibracao  # noqa: E402
import casos as C  # noqa: E402
import execucao as E  # noqa: E402
import juiz as J  # noqa: E402
import runner as R  # noqa: E402
import verificador as V  # noqa: E402

apf = V.apf


class TestCasosDeDialogo(unittest.TestCase):
    def test_turnos(self):
        c1 = C.caso_do_turno("D2b", 1)
        self.assertTrue(c1["previa"])  # o turno 1 é o caso-base da camada 1
        c2 = C.caso_do_turno("D2b", 2)
        self.assertFalse(c2["previa"])
        self.assertIn((C.D(46), C.D(46)), c2["totais"])
        self.assertIn((C.D(41), C.D(46)), c2["totais"])
        self.assertFalse(C.caso_do_turno("D2b", 3).get("totais"))
        self.assertTrue(C.caso_do_turno("D2c", 2)["previa"])
        self.assertFalse(C.caso_do_turno("D2c", 3)["previa"])
        self.assertNotIn("nota_juiz", C.caso_do_turno("D2a", 2))
        # D2b acrescenta exatamente as duas frases que o H2c tem a mais
        for trecho in ("mantida no sistema de locais da Justiça Eleitoral",
                       C.D2B_FATOS.split(". ")[1].strip()):
            self.assertIn(trecho, C.H2C_TEXTO)
            self.assertNotIn(trecho, C.H2_TEXTO)
        self.assertNotIn("calcular", C.D2C_PARCIAL)
        self.assertIn("Não sei", C.D2C_PARCIAL)

    def test_preparar(self):
        nome = "teste-unitario-dialogo"
        d = R.dir_rodada(nome)
        shutil.rmtree(d, ignore_errors=True)
        original = R.versoes
        try:
            R.versoes = lambda: {}
            R.preparar(nome, "dialogo", 3, None)
            t = R.carregar_estado(nome)["tarefas"]
            execs = [x for x in t.values() if x["tipo"] == "exec"]
            self.assertEqual(len(execs), 3 * (2 + 3 + 3))  # D2a 2 turnos, D2b 3, D2c 3
            self.assertEqual([k for k in t if k.startswith("juiz-")], ["juiz-D2b-r1-t2", "juiz-D2b-r2-t2", "juiz-D2b-r3-t2"])
            self.assertEqual(t["exec-D2b-r1-t3"]["depende"], "exec-D2b-r1-t2")
            self.assertNotIn("depende", t["exec-D2b-r1-t1"])
            self.assertEqual(t["exec-D2b-r1-t1"]["sessao"], t["exec-D2b-r1-t3"]["sessao"])
            self.assertNotEqual(t["exec-D2b-r1-t1"]["sessao"], t["exec-D2b-r2-t1"]["sessao"])
            self.assertEqual(R.proxima(nome)["tarefa"], "exec-D2a-r1-t1")
            est = R.carregar_estado(nome)
            est["tarefas"]["exec-D2a-r1-t1"]["fase"] = "invalido"
            R.salvar_estado(nome, est)
            R.proxima(nome)
            self.assertEqual(R.carregar_estado(nome)["tarefas"]["exec-D2a-r1-t2"]["fase"], "pulado")
            est = R.carregar_estado(nome)
            est["tarefas"]["exec-D2a-r1-t1"]["fase"] = "invalido"
            R.salvar_estado(nome, est)
            with self.assertRaises(SystemExit):  # turno de diálogo não se repete
                R.repetir(nome, "exec-D2a-r1-t1")
        finally:
            R.versoes = original
            shutil.rmtree(d, ignore_errors=True)

    def test_comando_com_sessao(self):
        capturado = {}

        def falso(cmd, **kw):
            capturado["cmd"] = cmd
            return mock.Mock(returncode=0, stdout="", stderr="")
        with tempfile.TemporaryDirectory() as ws, tempfile.TemporaryDirectory() as saida, \
                mock.patch.object(E.subprocess, "run", side_effect=falso):
            E.rodar_claude(Path(ws), "p", Path(saida))
            self.assertIn("--no-session-persistence", capturado["cmd"])
            E.rodar_claude(Path(ws), "p", Path(saida), sessao="u-1")
            self.assertEqual(capturado["cmd"][capturado["cmd"].index("--session-id") + 1], "u-1")
            self.assertNotIn("--no-session-persistence", capturado["cmd"])
            E.rodar_claude(Path(ws), "msg", Path(saida), sessao="u-1", retomar=True)
            self.assertEqual(capturado["cmd"][capturado["cmd"].index("--resume") + 1], "u-1")
            self.assertNotIn("--session-id", capturado["cmd"])
            self.assertEqual(capturado["cmd"][capturado["cmd"].index("-p") + 1], "msg")


class TestContinuidade(unittest.TestCase):
    def test_temporario_herdado_e_recopiado_e_permitido(self):
        ws = R.preparar_ws("teste-dialogo", None)
        fora = Path(tempfile.mkdtemp(prefix="apf-herdado-", dir="/tmp")).resolve()
        saida1, saida2 = Path(tempfile.mkdtemp(prefix="saida-t1-")), Path(tempfile.mkdtemp(prefix="saida-t2-"))
        try:
            h = V.sha_arvore(ws / ".claude" / "skills" / "nesma-apf-estimator")
            (fora / "e.json").write_text("{\"v\": 1}", encoding="utf-8")
            m1 = V.congelar(ws, saida1, time.time() - 5, time.time() + 1, h)
            self.assertIn(str(fora), m1["temporarios"].values())
            (fora / "e.json").write_text("{\"v\": 2}", encoding="utf-8")
            m2 = V.congelar(ws, saida2, time.time() + 100, time.time() + 200, h, [str(fora)])  # janela não cobre
            self.assertIn(str(fora), m2["temporarios"].values())
            i = next(k for k, v in m2["temporarios"].items() if v == str(fora))
            self.assertEqual(json.loads((saida2 / "snapshot" / "tmp" / i / "e.json").read_text())["v"], 2)
            i1 = next(k for k, v in m1["temporarios"].items() if v == str(fora))
            self.assertEqual(json.loads((saida1 / "snapshot" / "tmp" / i1 / "e.json").read_text())["v"], 1)  # turno 1 intacto
            cmd = [{"nome": "Bash", "entrada": {"command": f"python3 x.py check {fora}/e.json"}}]
            self.assertEqual(V.auditar(cmd, ws, list(m2["temporarios"].values())), [])
            self.assertTrue(V.auditar(cmd, ws, []))
        finally:
            for p in (ws, fora, saida1, saida2):
                shutil.rmtree(p, ignore_errors=True)


def _previa_g04():
    e = copy.deepcopy(calibracao.g04i_correto_v2())
    return e


def _final_de(previa):
    e = copy.deepcopy(previa)
    for p in e["pendencias"]:
        if p.get("situacao") == "perguntada":
            p["situacao"] = "sem-resposta"
    return e


class TestRelacoes(unittest.TestCase):
    def test_preservacao(self):
        p = _previa_g04()
        self.assertEqual(apf.validar_previa(p), [])
        f = _final_de(p)
        self.assertEqual(apf.validar_final(f), [])
        self.assertTrue(V.relacao_preservacao(p, f)["ok"])
        # renumeração consistente de funções e hipóteses é tolerada
        g = copy.deepcopy(f)
        mapa = {h["id"]: "H" + str(10 + i) for i, h in enumerate(g["hipoteses"])}
        for h in g["hipoteses"]:
            h["id"] = mapa[h["id"]]
            h["requer"] = [mapa[r] for r in h.get("requer") or []]
        for i, x in enumerate(g["funcoes"]):
            x["id"] = f"F{20 + i}"
            if x.get("hipotese"):
                x["hipotese"] = mapa[x["hipotese"]]
        self.assertTrue(V.relacao_preservacao(p, g)["ok"])
        # troca de uma função por outra do mesmo tipo reprova
        h = copy.deepcopy(f)
        h["funcoes"][-1]["nome"] = "Consultar saldo de diárias"
        r = V.relacao_preservacao(p, h)
        self.assertFalse(r["ok"])
        self.assertTrue(r["so_na_previa"] and r["so_no_final"])
        # função nova reprova
        n = copy.deepcopy(f)
        n["funcoes"].append({"id": "F99", "requisito": "gerenciar", "nome": "Aprovar", "tipo": "EE", "operacao": None,
                             "hipotese": None, "justificativa": "x"})
        self.assertFalse(V.relacao_preservacao(p, n)["ok"])
        # pergunta do lote que não virou sem-resposta reprova
        s = copy.deepcopy(f)
        s["pendencias"][0]["situacao"] = "resolvida"
        s["esclarecimentos"] = [{"id": "E1", "pendencia": s["pendencias"][0]["id"], "resposta": "x", "lote": 1}]
        self.assertFalse(V.relacao_preservacao(p, s)["lote_sem_resposta"])

    def test_segundo_lote(self):
        p1 = _previa_g04()
        p2 = copy.deepcopy(p1)
        st = {"P1": "resolvida", "P2": "resolvida", "P3": "sem-resposta", "P4": "resolvida"}
        for p in p2["pendencias"]:
            p["situacao"] = st[p["id"]]
        p2["esclarecimentos"] = [{"id": f"E{i}", "pendencia": pid, "resposta": "x", "lote": 1}
                                 for i, pid in enumerate(("P1", "P2", "P3", "P4"), start=1)]
        p2["pendencias"].append({"id": "P9", "descricao": "carga", "pergunta": "Há carga?", "situacao": "perguntada", "lote": 2})
        self.assertEqual(apf.validar_previa(p2), [])
        r = V.relacao_segundo_lote(p1, p2)
        self.assertTrue(r["ok"])
        self.assertEqual(r["percurso"], "segundo lote")
        sem = copy.deepcopy(p2)
        sem["pendencias"] = sem["pendencias"][:-1]
        r = V.relacao_segundo_lote(p1, sem)
        self.assertTrue(r["ok"])
        self.assertEqual(r["percurso"], "confirmação (segundo lote não exercitado)")
        rep = copy.deepcopy(p2)
        rep["pendencias"][2].update({"situacao": "perguntada", "lote": 2})
        self.assertFalse(V.relacao_segundo_lote(p1, rep)["sem_repeticao"])

    def test_correcao(self):
        antes = calibracao.d2b_correto()
        depois = copy.deepcopy(antes)
        depois["funcoes"] = [f for f in depois["funcoes"] if f["id"] != "F10"]
        r = V.relacao_correcao(antes, depois)
        self.assertTrue(r["ok"], r)
        errado = copy.deepcopy(antes)
        errado["funcoes"] = [f for f in errado["funcoes"] if f["id"] != "F08"]  # retirou a CE errada
        self.assertFalse(V.relacao_correcao(antes, errado)["ok"])
        self.assertFalse(V.relacao_correcao(antes, antes)["ok"])


class TestJuizDoDialogo(unittest.TestCase):
    def test_calibracao_valida_e_rastreavel(self):
        ds = {d[0]: d for d in calibracao.dossies()}
        for did in ("P7", "E14"):
            _, caso, est, alvo = ds[did]
            self.assertEqual(caso, "D2b")
            self.assertEqual(apf.validar(est), [], did)
            self.assertEqual(apf.validar_final(est), [], did)
            fonte = C.H2_TEXTO + " " + C.D2B_FATOS
            for f in est["funcoes"]:
                trecho = f["requisito"].split(" (resposta do analista)")[0]
                self.assertIn(trecho, fonte, (did, f["id"]))
        c = apf.calcular(ds["P7"][2])
        self.assertIn((c["total_min"], c["total_max"]), C.caso_do_turno("D2b", 2)["totais"])
        self.assertEqual(ds["E14"][3], ["S4"])
        self.assertIn("E14", calibracao.CALIBRACAO_EXATA)

    def test_dossie(self):
        inv, msgs = R.mensagens_do_dialogo("D2b", 2)
        self.assertIn("/nesma-apf-estimator tipo=desenvolvimento -- ./pedido.md", inv)
        self.assertEqual(msgs, [C.D2B_FATOS])
        d = J.montar_dossie_dialogo(inv, C.H2_TEXTO, msgs, "H2c", {"x": 1}, "resp", C.NOTA_D2B)
        self.assertIn(J.INSTRUCOES_DIALOGO, d)
        self.assertIn("## H2c ·", d)
        self.assertIn(C.D2B_FATOS, d)
        self.assertIn(C.H2_TEXTO[:80], d)
        self.assertNotIn("PRÉVIA", d)
        self.assertIn("resolvida", J.INSTRUCOES_DIALOGO)
        _, msgs3 = R.mensagens_do_dialogo("D2b", 3)
        self.assertEqual(msgs3, [C.D2B_FATOS, C.D2D_CORRECAO])


if __name__ == "__main__":
    unittest.main()


class TestK2PorCategorias(unittest.TestCase):
    """D67: conteúdo literal; orientação de uso com o sentido correto; sem introdução redundante."""

    def setUp(self):
        e = calibracao.g01_correto()
        self.md = apf.render_md(e, apf.calcular(e), "chat")
        self.previa = apf.render_previa(calibracao.g04i_correto_v2())

    def test_final_literal(self):
        r = V.k2_por_categorias(self.md, "Segue.\n\n" + self.md + "\nQuer exportar?")
        self.assertTrue(r["conteudo_literal"] and r["orientacao"])

    def test_final_orientacao_reescrita_com_sentido(self):
        resp = self.md.replace(apf.FECHO_CORRECAO, "Se algo estiver errado, diga o item e a correção: recalculo e você pode exportar de novo.")
        r = V.k2_por_categorias(self.md, resp)
        self.assertTrue(r["conteudo_literal"] and r["orientacao"], r)

    def test_final_orientacao_omitida_reprova(self):
        r = V.k2_por_categorias(self.md, self.md.replace(apf.FECHO_CORRECAO, ""))
        self.assertTrue(r["conteudo_literal"])
        self.assertFalse(r["orientacao"])

    def test_final_conteudo_alterado_reprova(self):
        r = V.k2_por_categorias(self.md, self.md.replace("**Total:** 45 PF", "**Total:** 46 PF"))
        self.assertFalse(r["conteudo_literal"])

    def test_previa(self):
        self.assertIn(apf.PREVIA_FECHO_PERGUNTAS, self.previa)
        ok = V.k2_por_categorias(self.previa, "Esta é a prévia.\n\n" + self.previa)
        self.assertTrue(ok["conteudo_literal"] and ok["orientacao"])
        reescrita = self.previa.replace(apf.PREVIA_FECHO_PERGUNTAS,
                                        "Responda pelo número; pode dizer \"não sei\" ou pedir para calcular com o que já sabe.")
        r = V.k2_por_categorias(self.previa, reescrita)
        self.assertTrue(r["conteudo_literal"] and r["orientacao"], r)
        sem = V.k2_por_categorias(self.previa, self.previa.replace(apf.PREVIA_FECHO_PERGUNTAS, "Responda."))
        self.assertFalse(sem["orientacao"])
        tirou_pergunta = V.k2_por_categorias(self.previa, self.previa.replace("**(P3)**", "**(P9)**"))
        self.assertFalse(tirou_pergunta["conteudo_literal"])
