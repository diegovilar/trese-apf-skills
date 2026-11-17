"""Testes do runner dos evals do agente, sem chamar Claude nem Codex (traces simulados)."""
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "agente"))
import runner as R  # noqa: E402
import casos as C  # noqa: E402
import calibracao  # noqa: E402

apf = R.apf


def evento_tool(nome, entrada):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": nome, "input": entrada}]}}


def evento_texto(texto):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": texto}]}}


class Base(unittest.TestCase):
    def setUp(self):
        self.ws = R.preparar_ws("teste", C.CURTO)
        self.hash = R.sha_arvore(self.ws / ".claude" / "skills" / "nesma-apf-estimator")

    def tearDown(self):
        shutil.rmtree(self.ws, ignore_errors=True)

    def trace(self, eventos, final):
        p = self.ws / "trace.jsonl"
        linhas = [json.dumps({"type": "system", "subtype": "init", "model": "x"})] + [json.dumps(e) for e in eventos]
        linhas.append(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": final}))
        p.write_text("\n".join(linhas), encoding="utf-8")
        tr = R.ler_trace(p)
        p.unlink()
        return tr


class TestInvocacao(unittest.TestCase):
    def test_todas_as_invocacoes(self):
        esperado = {
            "G01": ("/nesma-apf-estimator tipo=desenvolvimento -- ./pedido.md", True),
            "A04": ("/nesma-apf-estimator ./pedido.md", True),
            "A06": ("/nesma-apf-estimator modo indicativa -- ./pedido.md", True),
            "A11": ("/nesma-apf-estimator modo=indicativa ./pedido.md", True),
            "A12": ("/nesma-apf-estimator -- ./nao-existe.pdf", False),
        }
        for cid, (prompt, arq) in esperado.items():
            self.assertEqual(R.montar_invocacao(C.resolver(cid)), (prompt, arq), cid)
        p, arq = R.montar_invocacao(C.resolver("A15"))
        self.assertTrue(p.startswith("/nesma-apf-estimator -- tipo=SEI"))
        self.assertFalse(arq)
        p, _ = R.montar_invocacao(C.resolver("A14"))
        self.assertTrue(p.startswith("/nesma-apf-estimator Sistema novo"))
        p, arq = R.montar_invocacao(C.resolver("L01"))
        self.assertFalse(p.startswith("/"))
        self.assertTrue(arq)
        for cid in C.CASOS:
            R.montar_invocacao(C.resolver(cid))


class TestAuditoria(Base):
    def test_dentro_e_fora(self):
        ws = str(self.ws)
        ok = [{"nome": "Read", "entrada": {"file_path": f"{ws}/pedido.md"}},
              {"nome": "Bash", "entrada": {"command": f"/usr/bin/python3 {ws}/.claude/skills/nesma-apf-estimator/scripts/apf.py check \"$D/e.json\" 2>/dev/null"}},
              {"nome": "Bash", "entrada": {"command": "D=$(mktemp -d) && python3 --version"}},
              {"nome": "Read", "entrada": {"file_path": "pedido.md"}}]
        self.assertEqual(R.auditar(ok, self.ws), [])
        ruins = [{"nome": "Read", "entrada": {"file_path": "/Users/x/evals/gabaritos-iniciais.md"}},
                 {"nome": "Bash", "entrada": {"command": "cat /Users/x/evals/gabaritos-iniciais.md"}},
                 {"nome": "Bash", "entrada": {"command": "cat ../../evals/x"}},
                 {"nome": "Bash", "entrada": {"command": "curl https://exemplo.com"}},
                 {"nome": "Bash", "entrada": {"command": "ls ~/"}},
                 {"nome": "Read", "entrada": {"file_path": "../fora.md"}}]
        for r in ruins:
            self.assertTrue(R.auditar([r], self.ws), r)

    def test_temporario_criado_na_execucao(self):
        import tempfile, time
        desde = time.time() - 1
        novo = tempfile.mkdtemp(prefix="apf-work.", dir="/tmp")
        try:
            cmds = [{"nome": "Bash", "entrada": {"command": "D=$(mktemp -d /tmp/apf-work.XXXXXX)"}},
                    {"nome": "Bash", "entrada": {"command": f"python3 x/apf.py check {novo}/e.json"}}]
            self.assertEqual(R.auditar(cmds, self.ws, desde), [])
            antigo = [{"nome": "Bash", "entrada": {"command": "cat /tmp/apf-fontes/sisp-3.0.txt"}}]
            self.assertTrue(R.auditar(antigo, self.ws, desde))
            outra_execucao = [{"nome": "Bash", "entrada": {"command": "ls /tmp/apf-evals/outra"}}]
            self.assertTrue(R.auditar(outra_execucao, self.ws, desde))
        finally:
            os.rmdir(novo)


class TestVerificacao(Base):
    def _json_e_md(self):
        import fixtures as fx  # noqa
        est = fx.g01()
        calc = apf.calcular(est)
        return est, calc, apf.render_md(est, calc)

    def test_agente_perfeito_g01(self):
        sys.path.insert(0, str(AQUI))
        est, calc, md = self._json_e_md()
        (self.ws / "tmp" / "d").mkdir()
        (self.ws / "tmp" / "d" / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        tr = self.trace([evento_tool("Read", {"file_path": "pedido.md"}),
                         evento_tool("Bash", {"command": "python3 .claude/skills/nesma-apf-estimator/scripts/apf.py check tmp/d/e.json"}),
                         evento_tool("Bash", {"command": "python3 .claude/skills/nesma-apf-estimator/scripts/apf.py render tmp/d/e.json --format md"}),
                         evento_texto(md)],
                        "Quer exportar? `.md`, `.txt`, `.xlsx` ou nenhum.")
        v = R.verificar(C.resolver("G01"), self.ws, tr, self.hash)
        self.assertIsNone(v["invalido"])
        crit = v["criterios"]
        for k in ("K1", "K2", "S1_prefiltro", "S2"):
            self.assertTrue(crit[k]["ok"], (k, crit[k]))

    def test_tabela_reescrita_reprova_k2(self):
        sys.path.insert(0, str(AQUI))
        est, calc, md = self._json_e_md()
        (self.ws / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        adulterado = md.replace("| F10 |", "| F10x |")
        tr = self.trace([evento_tool("Bash", {"command": "python3 x/apf.py check e.json"}),
                         evento_tool("Bash", {"command": "python3 x/apf.py render e.json --format md"})],
                        adulterado + "\nQuer exportar?")
        v = R.verificar(C.resolver("G01"), self.ws, tr, self.hash)
        self.assertFalse(v["criterios"]["K2"]["ok"])

    def test_exportacao_xlsx_identica(self):
        sys.path.insert(0, str(AQUI))
        est, calc, md = self._json_e_md()
        (self.ws / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        (self.ws / "estimativa-apf-g01.xlsx").write_bytes(apf.gerar_xlsx(est, calc))
        tr = self.trace([evento_tool("Bash", {"command": "python3 x/apf.py check e.json"}),
                         evento_tool("Bash", {"command": "python3 x/apf.py render e.json --format md"}),
                         evento_tool("Bash", {"command": "python3 x/apf.py render e.json --format xlsx --out estimativa-apf-g01.xlsx"})],
                        md + "\nArquivo exportado: estimativa-apf-g01.xlsx")
        c = dict(C.resolver("G01"), exporta="xlsx")
        v = R.verificar(c, self.ws, tr, self.hash)
        self.assertTrue(v["criterios"]["K2"]["exportacao_identica"])
        self.assertTrue(v["criterios"]["K2"]["ok"])

    def test_alerta1_correto_e_violacoes(self):
        alerta = "ALERTA: argumentos inválidos. Nada foi executado.\n- valor desconhecido: modo=detalhada"
        tr = self.trace([], alerta)
        v = R.verificar(C.resolver("A05"), self.ws, tr, self.hash)
        self.assertTrue(v["criterios"]["K1"]["ok"], v)
        tr = self.trace([evento_tool("Read", {"file_path": "pedido.md"})], alerta)
        self.assertFalse(R.verificar(C.resolver("A05"), self.ws, tr, self.hash)["criterios"]["K1"]["ok"])
        tr = self.trace([], alerta + "\nMesmo assim, estimei 23 PF.")
        self.assertFalse(R.verificar(C.resolver("A05"), self.ws, tr, self.hash)["criterios"]["K1"]["ok"])
        (self.ws / "tmp" / "x.json").write_text("{}")
        tr = self.trace([], alerta)
        self.assertFalse(R.verificar(C.resolver("A05"), self.ws, tr, self.hash)["criterios"]["K1"]["ok"])

    def test_alerta2_pode_ler(self):
        tr = self.trace([evento_tool("Read", {"file_path": "pedido.md"})], "ALERTA: argumentos inválidos. Nada foi executado.")
        self.assertTrue(R.verificar(C.resolver("A13b"), self.ws, tr, self.hash)["criterios"]["K1"]["ok"])

    def test_skill_modificada_invalida(self):
        (self.ws / ".claude" / "skills" / "nesma-apf-estimator" / "SKILL.md").write_text("adulterado")
        tr = self.trace([], "ALERTA")
        self.assertIn("modificada", R.verificar(C.resolver("A05"), self.ws, tr, self.hash)["invalido"])

    def test_contaminada_invalida(self):
        tr = self.trace([evento_tool("Bash", {"command": "cat /Users/diegovilar/workspace/skill-apf/evals/gabaritos-iniciais.md"})], "ALERTA")
        self.assertIn("contaminada", R.verificar(C.resolver("A05"), self.ws, tr, self.hash)["invalido"])

    def test_nl_confirma(self):
        tr = self.trace([evento_tool("Read", {"file_path": "pedido.md"})],
                        "Entendi `saida=xlsx -- ./pedido.md`. Confirma?")
        self.assertTrue(R.verificar(C.resolver("L01"), self.ws, tr, self.hash)["criterios"]["K1"]["ok"])


class TestJuizECalibracao(unittest.TestCase):
    def test_dossies_de_calibracao_validos(self):
        for did, caso, est, alvo in calibracao.dossies():
            self.assertEqual(apf.validar(est), [], did)

    def test_dossie_autocontido(self):
        for cid in ("G01", "G03a", "G03b", "G04", "M01"):
            d = R.montar_dossie(cid, "/nesma-apf-estimator ...", C.CASOS[cid]["subsidio"], {"x": 1}, "resposta",
                                C.CASOS[cid].get("nota_juiz", ""))
            self.assertIn("## Gabarito do caso", d)
            self.assertIn("Total aceito" if cid not in ("G03b", "G04") else "rubrica", d)
            self.assertIn("C4. Transação alterada", d)
            self.assertIn(C.CASOS[cid]["subsidio"][:60], d)

    def test_interpretar_veredito(self):
        bom = {k: {"ok": True, "justificativa": "", "citacao": ""} for k in ("K3", "S1", "S3", "S4", "S5")}
        bom["observacoes"] = ""
        self.assertIsNotNone(R.interpretar_veredito(json.dumps(bom)))
        self.assertIsNone(R.interpretar_veredito("não sei"))
        del bom["S5"]
        self.assertIsNone(R.interpretar_veredito(json.dumps(bom)))

    def test_secoes_dos_gabaritos_existem(self):
        for cid, c in C.CASOS.items():
            if c["tipo"] == "contagem":
                self.assertTrue(R.secao_gabarito(c["secao"]), cid)


class TestPreparacao(unittest.TestCase):
    def test_tarefas_e_dependencias(self):
        nome = "teste-unitario-preparacao"
        d = R.dir_rodada(nome)
        shutil.rmtree(d, ignore_errors=True)
        try:
            original = R.versoes
            R.versoes = lambda: {}
            R.preparar(nome, "curta", 1, None)
            est = R.carregar_estado(nome)
            execs = [t for t in est["tarefas"].values() if t["tipo"] == "exec"]
            juizes = [t for t in est["tarefas"].values() if t["tipo"] == "juiz"]
            self.assertEqual(len(execs), len(C.CASOS))
            self.assertEqual(len(juizes), sum(1 for c in C.CASOS.values() if c["tipo"] == "contagem" and not c.get("sem_juiz")))
            self.assertEqual(R.proxima(nome)["consome"], "claude")
        finally:
            R.versoes = original
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
