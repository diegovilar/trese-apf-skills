"""Testes do runner e do verificador dos evals do agente, sem chamar Claude nem Codex (traces simulados)."""
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "agente"))
sys.path.insert(0, str(AQUI))
import calibracao  # noqa: E402
import casos as C  # noqa: E402
import fixtures as fx  # noqa: E402
import runner as R  # noqa: E402
import verificador as V  # noqa: E402
import juiz as J  # noqa: E402

apf = V.apf


def evento_texto(texto):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": texto}]}}


class Base(unittest.TestCase):
    def setUp(self):
        self.desde = time.time() - 1
        self.ws = R.preparar_ws("teste", C.CURTO)
        self.hash = V.sha_arvore(self.ws / ".claude" / "skills" / "trese-apf-aproximacao")
        self.saida = Path(tempfile.mkdtemp(prefix="saida-teste-"))

    def tearDown(self):
        shutil.rmtree(self.ws, ignore_errors=True)
        shutil.rmtree(self.saida, ignore_errors=True)

    def rodar(self, caso, eventos, final, c=None):
        """Grava o trace simulado, congela e verifica como o runner faz."""
        linhas = [json.dumps({"type": "system", "subtype": "init", "model": "x"})]
        for i, (tipo, dado) in enumerate(eventos):
            if tipo == "tool":
                nome, entrada, saida = dado
                linhas.append(json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "id": f"t{i}", "name": nome, "input": entrada}]}}))
                linhas.append(json.dumps({"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": f"t{i}", "content": saida}]}}))
            else:
                linhas.append(json.dumps(evento_texto(dado)))
        linhas.append(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": final}))
        (self.saida / "trace.jsonl").write_text("\n".join(linhas), encoding="utf-8")
        V.congelar(self.ws, self.saida, self.desde, time.time() + 1, self.hash)
        return V.verificar_snapshot(c or C.resolver(caso), self.saida)


class TestInvocacao(unittest.TestCase):
    def test_todas_as_invocacoes(self):
        esperado = {
            "G01": ("/trese-apf-aproximacao tipo=desenvolvimento interativo=nao -- ./pedido.md", True),
            "A04": ("/trese-apf-aproximacao ./pedido.md", True),
            "A06": ("/trese-apf-aproximacao modo indicativa -- ./pedido.md", True),
            "A11": ("/trese-apf-aproximacao modo=indicativa ./pedido.md", True),
            "A12": ("/trese-apf-aproximacao -- ./nao-existe.pdf", False),
        }
        for cid, (prompt, arq) in esperado.items():
            self.assertEqual(R.montar_invocacao(C.resolver(cid)), (prompt, arq), cid)
        p, arq = R.montar_invocacao(C.resolver("A15"))
        self.assertTrue(p.startswith("/trese-apf-aproximacao interativo=nao -- tipo=SEI"))
        self.assertFalse(arq)
        p, _ = R.montar_invocacao(C.resolver("A14"))
        self.assertTrue(p.startswith("/trese-apf-aproximacao Sistema novo"))
        p, arq = R.montar_invocacao(C.resolver("L01"))
        self.assertFalse(p.startswith("/"))
        self.assertTrue(arq)
        for cid in C.CASOS:
            R.montar_invocacao(C.resolver(cid))


class TestAuditoria(Base):
    def test_dentro_e_fora(self):
        ws = str(self.ws)
        ok = [{"nome": "Read", "entrada": {"file_path": f"{ws}/pedido.md"}},
              {"nome": "Bash", "entrada": {"command": f"/usr/bin/python3 {ws}/.claude/skills/x/apf.py check \"$D/e.json\" 2>/dev/null"}},
              {"nome": "Bash", "entrada": {"command": "D=$(mktemp -d /tmp/apf-work.XXXXXX) && python3 --version"}},
              {"nome": "Bash", "entrada": {"command": "cat /tmp/apf-work.ab12/e.json"}},
              {"nome": "Read", "entrada": {"file_path": "pedido.md"}}]
        self.assertEqual(V.auditar(ok, self.ws, ["/tmp/apf-work.ab12"]), [])
        ruins = [{"nome": "Read", "entrada": {"file_path": "/Users/x/evals/gabaritos-iniciais.md"}},
                 {"nome": "Bash", "entrada": {"command": "cat /Users/x/evals/gabaritos-iniciais.md"}},
                 {"nome": "Bash", "entrada": {"command": "cat ../../evals/x"}},
                 {"nome": "Bash", "entrada": {"command": "curl https://exemplo.com"}},
                 {"nome": "Bash", "entrada": {"command": "ls ~/"}},
                 {"nome": "Bash", "entrada": {"command": "cat /tmp/apf-fontes/sisp-3.0.txt"}},
                 {"nome": "Read", "entrada": {"file_path": "../fora.md"}}]
        for r in ruins:
            self.assertTrue(V.auditar([r], self.ws, ["/tmp/apf-work.ab12"]), r)


class TestVerificacao(Base):
    def _g01(self):
        est = fx.g01()
        calc = apf.calcular(est)
        return est, calc, apf.render_md(est, calc, "chat")

    def _execucao_valida(self, est, md):
        (self.ws / "tmp" / "d").mkdir()
        (self.ws / "tmp" / "d" / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        return [("tool", ("Read", {"file_path": "pedido.md"}, "texto")),
                ("tool", ("Bash", {"command": "python3 s/apf.py check tmp/d/e.json"}, "OK")),
                ("tool", ("Bash", {"command": "python3 s/apf.py render tmp/d/e.json --format md"}, md))]

    def test_agente_perfeito_g01(self):
        est, calc, md = self._g01()
        v = self.rodar("G01", self._execucao_valida(est, md) + [("texto", md)], "Quer exportar? `.md`, `.txt`, `.xlsx` ou nenhum.")
        self.assertIsNone(v["invalido"])
        for k in ("K1", "K2", "S1_prefiltro", "S2"):
            self.assertTrue(v["criterios"][k]["ok"], (k, v["criterios"][k]))

    def test_tabela_reescrita_reprova_k2(self):
        est, calc, md = self._g01()
        v = self.rodar("G01", self._execucao_valida(est, md), md.replace("| F10 |", "| F10x |") + "\nQuer exportar?")
        self.assertFalse(v["criterios"]["K2"]["ok"])

    def test_json_escolhido_pelo_conteudo(self):
        est, calc, md = self._g01()
        outro = json.loads(json.dumps(est))
        outro["funcoes"].pop()
        (self.ws / "outro.json").write_text(json.dumps(outro, ensure_ascii=False), encoding="utf-8")
        v = self.rodar("G01", self._execucao_valida(est, md) + [("texto", md)], "Quer exportar?")
        self.assertTrue(v["tem_json"])
        self.assertTrue(v["json"].endswith("e.json"))
        self.assertTrue(v["criterios"]["S2"]["ok"])

    def test_sem_render_no_trace(self):
        est, calc, md = self._g01()
        (self.ws / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        v = self.rodar("G01", [("tool", ("Bash", {"command": "python3 s/apf.py check e.json"}, "OK"))], md)
        self.assertFalse(v["tem_json"])
        self.assertIn("render", v["criterios"]["K2"]["motivo"])

    def test_exportacao_xlsx_identica(self):
        est, calc, md = self._g01()
        (self.ws / "estimativa-apf-g01.xlsx").write_bytes(apf.gerar_xlsx(est, calc))
        eventos = self._execucao_valida(est, md) + [
            ("tool", ("Bash", {"command": "python3 s/apf.py render tmp/d/e.json --format xlsx --out estimativa-apf-g01.xlsx"}, "ok"))]
        v = self.rodar("G01", eventos + [("texto", md)], "Arquivo exportado", c=dict(C.resolver("G01"), exporta="xlsx"))
        self.assertTrue(v["criterios"]["K2"]["exportacao_identica"])
        self.assertTrue(v["criterios"]["K2"]["ok"])

    def test_alerta1_correto_e_violacoes(self):
        alerta = "ALERTA: argumentos inválidos. Nada foi executado.\n- valor desconhecido: modo=detalhada"
        self.assertTrue(self.rodar("A05", [], alerta)["criterios"]["K1"]["ok"])
        self.assertFalse(self.rodar("A05", [("tool", ("Read", {"file_path": "pedido.md"}, "x"))], alerta)["criterios"]["K1"]["ok"])
        self.assertFalse(self.rodar("A05", [], alerta + "\nMesmo assim, estimei 23 PF.")["criterios"]["K1"]["ok"])
        (self.ws / "tmp" / "x.json").write_text("{}")
        self.assertFalse(self.rodar("A05", [], alerta)["criterios"]["K1"]["ok"])

    def test_alerta_com_linha_de_chaves_nao_e_contagem(self):
        alerta = ("ALERTA: argumentos inválidos. Nada foi executado.\n- valor desconhecido: modo=detalhada\n"
                  "Formato: [chave=valor ...] -- <subsídio>\n"
                  "Chaves: modo=estimada|indicativa · tipo=desenvolvimento|melhoria · melhoria=sem-fatores|nesma · "
                  "saida=md|txt|xlsx · interativo=sim|nao\nExemplo: modo=estimada tipo=melhoria saida=xlsx -- ./pedido.pdf")
        self.assertTrue(self.rodar("A05", [], alerta)["criterios"]["K1"]["ok"])
        self.assertTrue(V.tem_contagem("| F01 | Curso | ALI |"))

    def test_alerta2_pode_ler(self):
        v = self.rodar("A13b", [("tool", ("Read", {"file_path": "pedido.md"}, "x"))], "ALERTA: argumentos inválidos. Nada foi executado.")
        self.assertTrue(v["criterios"]["K1"]["ok"])

    def test_skill_modificada_invalida(self):
        (self.ws / ".claude" / "skills" / "trese-apf-aproximacao" / "SKILL.md").write_text("adulterado")
        self.assertIn("modificada", self.rodar("A05", [], "ALERTA")["invalido"])

    def test_contaminada_invalida(self):
        v = self.rodar("A05", [("tool", ("Bash", {"command": "cat /Users/diegovilar/workspace/skill-apf/evals/gabaritos-iniciais.md"}, "x"))], "ALERTA")
        self.assertIn("contaminada", v["invalido"])

    def test_snapshot_adulterado_invalida(self):
        v = self.rodar("A05", [], "ALERTA")
        self.assertIsNone(v["invalido"])
        (self.saida / "snapshot" / "ws" / "pedido.md").write_text("mudou")
        self.assertIn("snapshot", V.verificar_snapshot(C.resolver("A05"), self.saida)["invalido"])

    def test_nl_confirma(self):
        v = self.rodar("L01", [("tool", ("Read", {"file_path": "pedido.md"}, "x"))], "Entendi `saida=xlsx -- ./pedido.md`. Confirma?")
        self.assertTrue(v["criterios"]["K1"]["ok"])


class TestVerificacaoPrevia(Base):
    """Casos que usam o padrão interativo=sim e devem terminar na prévia (D52)."""

    def _curto(self):
        est = fx.base(titulo="Portaria")
        est["funcoes"] = [
            {"id": "F01", "requisito": "registra a entrada do visitante", "nome": "Visita", "tipo": "ALI", "operacao": None,
             "hipotese": None, "justificativa": "mantida aqui"},
            {"id": "F02", "requisito": "registra a entrada", "nome": "Registrar entrada", "tipo": "EE", "operacao": None,
             "hipotese": None, "justificativa": "mantém Visita"},
        ]
        est["pendencias"] = [{"id": "P1", "descricao": "relatórios", "pergunta": "Há relatórios de visitas?",
                              "situacao": "perguntada", "lote": 1}]
        return est

    def _eventos(self, est, previa):
        (self.ws / "tmp" / "d").mkdir()
        (self.ws / "tmp" / "d" / "e.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
        return [("tool", ("Read", {"file_path": "pedido.md"}, "texto")),
                ("tool", ("Bash", {"command": "python3 s/apf.py check tmp/d/e.json"}, "OK")),
                ("tool", ("Bash", {"command": "python3 s/apf.py render tmp/d/e.json --format previa"}, previa))]

    def test_previa_correta(self):
        est = self._curto()
        previa = apf.render_previa(est)
        v = self.rodar("A04", self._eventos(est, previa), previa)
        self.assertIsNone(v["invalido"])
        for k in ("K1", "K2", "config"):
            self.assertTrue(v["criterios"][k]["ok"], (k, v["criterios"][k]))
        self.assertEqual(v["lote"], {"numero": 1, "perguntas": 1, "abertas_restantes": 0, "pendencias": 1})

    def test_previa_com_pf_ou_render_final_reprova(self):
        est = self._curto()
        previa = apf.render_previa(est)
        v = self.rodar("A04", self._eventos(est, previa), previa + "\nPor alto, dá uns 11 PF.")
        self.assertFalse(v["criterios"]["K1"]["sem_pf_na_resposta"])
        self.assertFalse(v["criterios"]["K1"]["ok"])

    def test_render_final_antes_da_confirmacao_reprova(self):
        est = self._curto()
        previa = apf.render_previa(est)
        eventos = self._eventos(est, previa) + [("tool", ("Bash", {"command": "python3 s/apf.py render tmp/d/e.json --format md"}, "x"))]
        v = self.rodar("L02", eventos, previa)
        self.assertFalse(v["criterios"]["K1"]["sem_render_final"])

    def test_previa_reescrita_reprova_k2(self):
        est = self._curto()
        previa = apf.render_previa(est)
        v = self.rodar("A14", self._eventos(est, previa), previa.replace("| F02 |", "| F2 |"))
        self.assertFalse(v["criterios"]["K2"]["ok"])

    def test_sem_previa_no_trace(self):
        est = self._curto()
        v = self.rodar("A04", self._eventos(est, "")[:2], apf.render_previa(est))
        self.assertFalse(v["criterios"]["K1"]["previa"])
        self.assertFalse(v["criterios"]["K2"]["ok"])


class TestBlocoPresente(unittest.TestCase):
    def setUp(self):
        est = fx.g01()
        self.md = apf.render_md(est, apf.calcular(est))

    def test_quebra_suave_aceita(self):
        linha = next(l for l in self.md.splitlines() if l.startswith("- **SE:**"))
        corte = linha.index(" ", 60)
        quebrada = self.md.replace(linha, linha[:corte] + "\n" + linha[corte + 1:])
        self.assertTrue(V.bloco_presente(self.md, "Intro\n\n" + quebrada + "\n\nQuer exportar?"))

    def test_numero_alterado_reprova(self):
        self.assertIn("**Total:** 45 PF", self.md)
        self.assertFalse(V.bloco_presente(self.md, self.md.replace("**Total:** 45 PF", "**Total:** 46 PF")))

    def test_linha_de_tabela_omitida_fundida_ou_reordenada_reprova(self):
        linhas = self.md.splitlines()
        i = next(k for k, l in enumerate(linhas) if l.startswith("| F03 |"))
        omitida = "\n".join(linhas[:i] + linhas[i + 1:])
        self.assertFalse(V.bloco_presente(self.md, omitida))
        fundida = "\n".join(linhas[:i] + [linhas[i] + " " + linhas[i + 1]] + linhas[i + 2:])
        self.assertFalse(V.bloco_presente(self.md, fundida))
        trocada = list(linhas)
        trocada[i], trocada[i + 1] = trocada[i + 1], trocada[i]
        self.assertFalse(V.bloco_presente(self.md, "\n".join(trocada)))


class TestJanelaDeTemporarios(unittest.TestCase):
    def test_limite_superior(self):
        antes = time.time() - 1
        d = tempfile.mkdtemp(prefix="apf-janela-", dir="/tmp")
        try:
            time.sleep(1.1)
            depois = time.time()
            self.assertIn(Path(d).name, [p.name for p in V.temporarios_novos(antes, depois)])
            self.assertNotIn(Path(d).name, [p.name for p in V.temporarios_novos(depois, None)])
            self.assertNotIn(Path(d).name, [p.name for p in V.temporarios_novos(antes - 100, antes)])
        finally:
            os.rmdir(d)


class TestJuizECalibracao(unittest.TestCase):
    def test_dossies_de_calibracao_validos(self):
        for did, caso, est, alvo in calibracao.dossies():
            self.assertEqual(apf.validar(est), [], did)

    def test_dossie_autocontido(self):
        for cid in ("G01", "G03a", "G03b", "G04", "G07", "G08", "M01"):
            d = R.montar_dossie(cid, "/trese-apf-aproximacao ...", C.CASOS[cid]["subsidio"], {"x": 1}, "resposta",
                                C.CASOS[cid].get("nota_juiz", ""))
            self.assertIn("## Gabarito do caso", d)
            self.assertIn("Total aceito" if cid not in ("G03b", "G04", "G07", "G08") else "rubrica", d)
            self.assertIn("C4. Transação alterada", d)
            self.assertIn(C.CASOS[cid]["subsidio"][:60], d)

    def test_interpretar_veredito(self):
        bom = {k: {"ok": True, "justificativa": "", "citacao": ""} for k in ("K3", "S1", "S3", "S4", "S5")}
        bom["observacoes"] = ""
        self.assertIsNotNone(R.interpretar_veredito(json.dumps(bom)))
        self.assertIsNone(R.interpretar_veredito("não sei"))
        del bom["S5"]
        self.assertIsNone(R.interpretar_veredito(json.dumps(bom)))

    def test_dossies_da_previa_validos_e_rastreaveis(self):
        for did, caso, est, alvo in calibracao.dossies():
            if did not in calibracao.CALIBRACAO_EXATA or caso in C.DIALOGOS:
                continue
            self.assertTrue(C.CASOS[caso].get("previa"), did)
            self.assertEqual(apf.validar_previa(est), [], did)
            sub = C.CASOS[caso]["subsidio"]
            for f in est["funcoes"]:
                for parte in f["requisito"].split("(...)"):
                    self.assertIn(parte.strip(), sub, (did, f["id"]))

    def test_dossie_da_previa_usa_instrucoes_proprias(self):
        for cid in ("H1", "H2c", "H3", "G04i", "G08i"):
            c = C.CASOS[cid]
            d = R.montar_dossie(cid, "/trese-apf-aproximacao ...", c["subsidio"], {"x": 1}, "prévia", c.get("nota_juiz", ""))
            self.assertIn("PRÉVIA", d)
            self.assertIn("- R (perguntas e pendências indevidas)", d)
            self.assertIn("## JSON da prévia produzido pelo agente", d)
            self.assertIn(c["subsidio"][:60], d)
            self.assertEqual(J.schema_de(cid).name, "veredito-previa.schema.json")
        g04i = R.montar_dossie("G04i", "x", C.G04, {}, "p", C.CASOS["G04i"]["nota_juiz"])
        self.assertIn("S4_antigo: avalie também", g04i)
        self.assertIn("## G04 ·", g04i)
        d = R.montar_dossie("G01", "x", C.G01, {}, "r")
        self.assertNotIn("PRÉVIA", d)
        self.assertEqual(J.schema_de("G01").name, "veredito.schema.json")

    def test_veredito_da_previa_exige_r_e_medidas(self):
        crit = {"ok": True, "justificativa": "", "citacao": ""}
        bom = {k: dict(crit) for k in ("K3", "S1", "S3", "S4", "S5", "R")}
        bom.update({"S4_antigo": None, "observacoes": "", "medidas": {"n_perguntas": 3, "genericas": [], "nao_mudam_contagem": [],
                                                                       "redundantes": [], "diagnostico_presentes": []}})
        self.assertIsNotNone(R.interpretar_veredito(json.dumps(bom), previa=True))
        sem_r = dict(bom)
        del sem_r["R"]
        self.assertIsNone(R.interpretar_veredito(json.dumps(sem_r), previa=True))
        self.assertIsNotNone(R.interpretar_veredito(json.dumps(sem_r)))  # fora da prévia, R não é exigido
        sem_medidas = dict(bom)
        del sem_medidas["medidas"]
        self.assertIsNone(R.interpretar_veredito(json.dumps(sem_medidas), previa=True))
        r_falso = json.loads(json.dumps(bom))
        r_falso["R"]["ok"] = False
        r_falso["S4_antigo"] = {"ok": False, "justificativa": "", "citacao": ""}
        self.assertEqual(R.reprovados_do_veredito(r_falso, True), ["R", "S4_antigo"])
        self.assertEqual(R.reprovados_do_veredito(r_falso, False), [])
        resumo = R.resumo_tarefa("juiz-H2-r1", {"fase": "julgado", "veredito": r_falso})
        self.assertFalse(resumo["juiz"]["R"])
        self.assertFalse(resumo["juiz"]["S4+R"])
        self.assertFalse(resumo["juiz"]["S4_antigo (fora da aprovação)"])

    def test_schema_da_previa(self):
        s = json.loads((AQUI.parent / "agente" / "veredito-previa.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(s["required"]), set(s["properties"]))
        self.assertIn("R", s["required"])

    def test_secoes_dos_gabaritos_existem(self):
        for cid, c in C.CASOS.items():
            if c["tipo"] == "contagem":
                self.assertTrue(R.secao_gabarito(c["secao"]), cid)


class TestPreparacaoEHashes(unittest.TestCase):
    def test_tarefas_e_dependencias(self):
        nome = "teste-unitario-preparacao"
        d = R.dir_rodada(nome)
        shutil.rmtree(d, ignore_errors=True)
        original = R.versoes
        try:
            R.versoes = lambda: {}
            R.preparar(nome, "curta", 1, None)
            est = R.carregar_estado(nome)
            self.assertIn("hash_execucao", est)
            self.assertIn("hash_verificador", est)
            execs = [t for t in est["tarefas"].values() if t["tipo"] == "exec"]
            juizes = [t for t in est["tarefas"].values() if t["tipo"] == "juiz"]
            self.assertEqual(len(execs), len(C.CASOS))
            self.assertEqual(len(juizes), sum(1 for c in C.CASOS.values() if c["tipo"] == "contagem" and not c.get("sem_juiz")))
            self.assertEqual(R.proxima(nome)["consome"], "claude")
        finally:
            R.versoes = original
            shutil.rmtree(d, ignore_errors=True)

    def test_repetir_execucao_invalida(self):
        nome = "teste-unitario-repetir"
        d = R.dir_rodada(nome)
        shutil.rmtree(d, ignore_errors=True)
        original = R.versoes
        try:
            R.versoes = lambda: {}
            R.preparar(nome, "completa", 5, ["G04"])
            with self.assertRaises(SystemExit):  # só inválida se repete
                R.repetir(nome, "exec-G04-r2")
            est = R.carregar_estado(nome)
            est["tarefas"]["exec-G04-r2"]["fase"] = "invalido"
            R.salvar_estado(nome, est)
            R.repetir(nome, "exec-G04-r2")
            est = R.carregar_estado(nome)
            self.assertEqual(est["tarefas"]["exec-G04-r2"]["repetida_por"], "exec-G04-r6")
            self.assertEqual(est["tarefas"]["exec-G04-r6"]["repete"], "exec-G04-r2")
            self.assertEqual(est["tarefas"]["juiz-G04-r6"]["depende"], "exec-G04-r6")
            self.assertEqual(est["tarefas"]["juiz-G04-r6"]["fase"], "pendente")
            with self.assertRaises(SystemExit):  # não repete duas vezes
                R.repetir(nome, "exec-G04-r2")
        finally:
            R.versoes = original
            shutil.rmtree(d, ignore_errors=True)

    def test_verificador_fora_do_hash_de_execucao(self):
        self.assertNotIn("verificador", Path(R.__file__).read_text().split("def hash_execucao")[1].split("def hash_juiz")[0])


if __name__ == "__main__":
    unittest.main()


class TestCaminhos(unittest.TestCase):
    """D73: a skill distribuída fica em trese-apf-skills/skills/<skill>; o desenvolvimento, em dev/<skill>."""

    def test_modulos_resolvem_dev_e_skill_independente_do_cwd(self):
        import execucao as E
        cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            for skill in (R.SKILL, E.SKILL, V.SKILL):
                self.assertTrue((skill / "SKILL.md").is_file(), skill)
                self.assertEqual(skill.parent.name, "skills")
                self.assertEqual(skill.name, R.RAIZ.name)
            self.assertTrue((R.RAIZ / "evals" / "agente" / "runner.py").is_file())
            self.assertEqual(R.RAIZ.parent.name, "dev")
            self.assertTrue(R.GABARITOS.is_file())
        finally:
            os.chdir(cwd)


class TestMigracao(unittest.TestCase):
    """O diff da migração cobre o repositório inteiro, inclusive a skill distribuída (D73)."""

    PREFIXO = "trese-apf-skills/dev/x"
    ARQUIVOS = ["trese-apf-skills/dev/x/evals/agente/verificador.py", "trese-apf-skills/dev/x/evals/agente/execucao.py",
                "trese-apf-skills/dev/x/evals/gabaritos-iniciais.md", "trese-apf-skills/dev/x/PLANO.md",
                "trese-apf-skills/skills/x/scripts/apf.py", "trese-apf-skills/skills/x/README.md", ".gitignore"]

    def setUp(self):
        import subprocess
        self.sp = subprocess
        self.topo = Path(tempfile.mkdtemp(prefix="git-migracao-")).resolve()
        for a in self.ARQUIVOS:
            (self.topo / a).parent.mkdir(parents=True, exist_ok=True)
            (self.topo / a).write_text("v1\n")
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        self.sp.run(["git", "init", "-q"], cwd=self.topo, check=True)
        self.sp.run(["git", "add", "-A"], cwd=self.topo, check=True)
        self.sp.run(g + ["commit", "-q", "-m", "base"], cwd=self.topo, check=True)
        self.base = self.sp.run(["git", "rev-parse", "HEAD"], cwd=self.topo, capture_output=True, text=True,
                                check=True).stdout.strip()

    def tearDown(self):
        shutil.rmtree(self.topo, ignore_errors=True)

    def proibidos(self, *mudar):
        for a in mudar:
            (self.topo / a).parent.mkdir(parents=True, exist_ok=True)
            (self.topo / a).write_text("v2\n")
        return R.proibidos_na_migracao(R.mudados_desde(self.base, self.topo), self.PREFIXO)

    def test_aceita_verificador_plano_e_gitignore(self):
        self.assertEqual(self.proibidos("trese-apf-skills/dev/x/evals/agente/verificador.py",
                                        "trese-apf-skills/dev/x/PLANO.md", ".gitignore",
                                        "trese-apf-skills/dev/x/evals/unit/test_novo.py"), [])

    def test_recusa_skill_distribuida_execucao_e_gabaritos(self):
        for a in ("trese-apf-skills/skills/x/scripts/apf.py", "trese-apf-skills/skills/x/README.md",
                  "trese-apf-skills/dev/x/evals/agente/execucao.py",
                  "trese-apf-skills/dev/x/evals/gabaritos-iniciais.md",
                  "trese-apf-skills/skills/x/references/novo.md"):
            with self.subTest(a=a):
                self.assertEqual(self.proibidos(a), [a])
                self.sp.run(["git", "checkout", "-q", "--", "."], cwd=self.topo, check=True)
                self.sp.run(["git", "clean", "-qfd"], cwd=self.topo, check=True)

    def test_recusa_mover_arquivo_protegido_para_caminho_permitido(self):
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        (self.topo / "trese-apf-skills/dev/x/evals/unit").mkdir(parents=True)
        self.sp.run(["git", "mv", "trese-apf-skills/skills/x/README.md", "trese-apf-skills/dev/x/evals/unit/README.md"],
                    cwd=self.topo, check=True)
        self.sp.run(g + ["commit", "-q", "-m", "mover"], cwd=self.topo, check=True)
        self.assertEqual(self.proibidos(), ["trese-apf-skills/skills/x/README.md"])

    def test_nome_com_espaco(self):
        self.assertEqual(self.proibidos("trese-apf-skills/skills/x/references/com espaço.md"),
                         ["trese-apf-skills/skills/x/references/com espaço.md"])

    def test_raiz_git_do_repositorio(self):
        self.assertEqual(R.RAIZ.relative_to(R.raiz_git()).as_posix(), "trese-apf-skills/dev/trese-apf-aproximacao")
