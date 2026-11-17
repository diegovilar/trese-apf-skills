"""Dossiês de calibração do juiz: resultados com veredito conhecido.

Positivos (tudo deve passar) e erros plantados (o critério-alvo deve reprovar).
As respostas finais são o render confiável do JSON, como o executor deveria mostrar.
"""
import copy

import casos as C


def _f(fid, tipo, nome, requisito, justificativa, op=None, hip=None):
    return {"id": fid, "requisito": requisito, "nome": nome, "tipo": tipo, "operacao": op, "hipotese": hip,
            "justificativa": justificativa}


def _base(titulo, fronteira, tipo="desenvolvimento"):
    return {"versao_esquema": 1, "metodo": "estimada", "tipo_projeto": tipo, "regime_melhoria": None,
            "projeto": {"titulo": titulo, "fronteira": fronteira, "origem_subsidio": "arquivo ./pedido.md", "data": "2026-11-17"},
            "cobertura": {"status": "completa", "motivo": None}, "avisos": [],
            "funcoes": [], "hipoteses": [], "premissas": [], "pendencias": [], "nao_contados": []}


def g01_correto():
    e = _base("Cursos de capacitação da EJE", "novo sistema da EJE; RH é externo")
    e["funcoes"] = [
        _f("F01", "ALI", "Curso (Turma como RET)", "O servidor da EJE cadastra cursos (...) e, para cada curso, as turmas", "turma só existe dentro de um curso"),
        _f("F02", "AIE", "Servidor (RH)", "os dados dos servidores vêm do sistema de RH (apenas leitura)", "mantido pelo RH, lido para o instrutor"),
        _f("F03", "EE", "Incluir curso", "Deve ser possível incluir, alterar e excluir cursos", "mantém Curso"),
        _f("F04", "EE", "Alterar curso", "Deve ser possível incluir, alterar e excluir cursos", "mantém Curso"),
        _f("F05", "EE", "Excluir curso", "Deve ser possível incluir, alterar e excluir cursos", "mantém Curso e exclui as turmas"),
        _f("F06", "EE", "Incluir turma", "as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma separadamente", "operação independente"),
        _f("F07", "EE", "Alterar turma", "as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma separadamente", "operação independente"),
        _f("F08", "EE", "Excluir turma", "as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma separadamente", "operação independente"),
        _f("F09", "CE", "Consultar cursos com filtros", "consultar cursos com filtros por período e modalidade", "só recuperação"),
        _f("F10", "SE", "Relatório de vagas por modalidade no semestre", "relatório gerencial com o total de vagas ofertadas por modalidade no semestre", "totalização"),
    ]
    e["nao_contados"] = [{"item": "Modalidade", "categoria": "dado-de-codigo", "justificativa": "lista fixa: presencial, EaD ou híbrida"}]
    return e


def g04_correto():
    e = _base("Gerenciar diárias", "não determinada pelo pedido; origem das solicitações em aberto")
    e["cobertura"] = {"status": "parcial", "motivo": "pedido de uma linha; o que 'gerenciar' abrange é desconhecido"}
    e["hipoteses"] = [
        {"id": "H1", "descricao": "Solicitações mantidas por este sistema, com registro", "trecho": "minhas solicitações", "grupo": "origem"},
        {"id": "H5", "descricao": "Solicitações nascem em outro sistema e são lidas", "trecho": "minhas solicitações", "grupo": "origem", "requer": ["H3"]},
        {"id": "H2", "descricao": "Gerenciar inclui alterar e cancelar", "trecho": "gerenciar", "requer": ["H1"]},
        {"id": "H3", "descricao": "Gerenciar inclui consultar", "trecho": "gerenciar"},
        {"id": "H4", "descricao": "O registro lê os dados do servidor no RH", "trecho": None, "requer": ["H1"]},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Solicitação de diária", "minhas solicitações de diárias", "mantida aqui sob H1", hip="H1"),
        _f("F02", "EE", "Registrar solicitação", "gerenciar minhas solicitações", "manutenção mínima sob H1", hip="H1"),
        _f("F03", "AIE", "Solicitação de diária (outro sistema)", "minhas solicitações de diárias", "lida sob H5", hip="H5"),
        _f("F04", "EE", "Alterar solicitação", "gerenciar", "H2", hip="H2"),
        _f("F05", "EE", "Cancelar solicitação", "gerenciar", "H2", hip="H2"),
        _f("F06", "CE", "Consultar minhas solicitações", "gerenciar", "H3", hip="H3"),
        _f("F07", "AIE", "Servidor (RH)", "servidor", "H4", hip="H4"),
    ]
    e["pendencias"] = [
        {"id": "P1", "descricao": "O que 'gerenciar' abrange."},
        {"id": "P2", "descricao": "Fluxo de aprovação da solicitação."},
        {"id": "P3", "descricao": "Cálculo do valor da diária."},
        {"id": "P4", "descricao": "Prestação de contas."},
        {"id": "P5", "descricao": "Origem dos dados do servidor."},
    ]
    return e


def g07_correto():
    e = _base("Atestados médicos", "sistema da Seção de Assistência à Saúde; origem dos atestados em aberto")
    e["cobertura"] = {"status": "parcial", "motivo": "pedido de uma linha; o que 'controlar' abrange é desconhecido"}
    e["hipoteses"] = [
        {"id": "H1", "descricao": "Atestados mantidos por este sistema, com registro", "trecho": "controlar os atestados médicos", "grupo": "origem dos atestados"},
        {"id": "H2", "descricao": "Atestados mantidos por outro sistema e lidos aqui", "trecho": "controlar os atestados médicos", "grupo": "origem dos atestados", "requer": ["H3"]},
        {"id": "H3", "descricao": "Controlar inclui consultar os atestados", "trecho": "controlar"},
        {"id": "H4", "descricao": "Controlar inclui alterar o atestado", "trecho": "controlar", "requer": ["H1"]},
        {"id": "H5", "descricao": "Controlar inclui excluir o atestado", "trecho": "controlar", "requer": ["H1"]},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Atestado médico", "controlar os atestados médicos", "mantido aqui sob H1", hip="H1"),
        _f("F02", "EE", "Registrar atestado", "atestados médicos apresentados pelos servidores", "manutenção mínima sob H1", hip="H1"),
        _f("F03", "AIE", "Atestado médico (outro sistema)", "controlar os atestados médicos", "lido sob H2", hip="H2"),
        _f("F04", "CE", "Consultar atestados", "controlar", "H3", hip="H3"),
        _f("F05", "EE", "Alterar atestado", "controlar", "H4", hip="H4"),
        _f("F06", "EE", "Excluir atestado", "controlar", "H5", hip="H5"),
    ]
    e["pendencias"] = [
        {"id": "P1", "descricao": "Quais operações 'controlar' abrange."},
        {"id": "P2", "descricao": "Onde os atestados são registrados: neste sistema ou em outro, do qual seriam lidos."},
        {"id": "P3", "descricao": "Se a Seção confere e aceita formalmente cada atestado, ou se ele passa por junta médica, e quem faz isso."},
        {"id": "P4", "descricao": "Como o servidor é identificado e de onde vêm os dados dele."},
    ]
    return e


def g08_correto():
    e = _base("Requerimentos do Protocolo", "sistema da Seção de Protocolo; dados dos servidores em aberto")
    e["hipoteses"] = [
        {"id": "H1", "descricao": "A análise inclui consultar os requerimentos registrados", "trecho": "Cada requerimento é analisado pela chefia da seção"},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Requerimento", "registrar os requerimentos que os servidores entregam no balcão", "mantido pela aplicação"),
        _f("F02", "EE", "Registrar requerimento", "registrar os requerimentos que os servidores entregam no balcão", "inclui o requerimento"),
        _f("F03", "EE", "Registrar decisão do requerimento", "registra no sistema a decisão: deferido ou indeferido", "grava a decisão; deferido e indeferido são valores do mesmo processo"),
        _f("F04", "CE", "Consultar requerimentos", "Cada requerimento é analisado pela chefia da seção", "H1", hip="H1"),
    ]
    e["pendencias"] = [
        {"id": "P1", "descricao": "Como o servidor é identificado no requerimento e de onde vêm os dados dele."},
        {"id": "P2", "descricao": "Há prazos ou critérios para a análise, ou recurso contra o indeferimento?"},
    ]
    return e


def dossies():
    """(id, caso, json, critérios que devem reprovar; vazio = positivo)."""
    out = [("P1", "G01", g01_correto(), []), ("P2", "G04", g04_correto(), [])]

    e = g01_correto()  # E1: função trocada, mesmos tipos e total
    e["funcoes"][7] = _f("F08", "EE", "Emitir certificado de conclusão", "as turmas podem ser incluídas, alteradas e excluídas", "registra a conclusão do curso")
    out.append(("E1", "G01", e, ["S1"]))

    e = g01_correto()  # E2: citação inventada
    e["funcoes"][8]["requisito"] = "a EJE precisa consultar os cursos por instrutor, com histórico de avaliações"
    out.append(("E2", "G01", e, ["S5"]))

    e = g01_correto()  # E3: função proibida (dado de código como ALI)
    e["funcoes"].append(_f("F11", "ALI", "Modalidade", "Modalidade é uma de: presencial, EaD ou híbrida", "tabela de modalidades"))
    e["nao_contados"] = []
    out.append(("E3", "G01", e, ["K3"]))

    e = g04_correto()  # E4: pendências obrigatórias omitidas
    e["pendencias"] = [{"id": "P1", "descricao": "O que 'gerenciar' abrange."}]
    out.append(("E4", "G04", e, ["S4"]))

    e = g04_correto()  # E5: alternativas excludentes sem grupo: máximo conta ALI e AIE da mesma entidade
    for h in e["hipoteses"]:
        h.pop("grupo", None)
    out.append(("E5", "G04", e, ["S3"]))

    # Calibração delta (consulta 13): S4 pelo significado e pendências proibidas (contraste).
    out.append(("P3", "G07", g07_correto(), []))  # homologação por paráfrase inequívoca

    e = g07_correto()  # E6: homologação só como verbo ambíguo numa lista de operações
    e["pendencias"] = [
        {"id": "P1", "descricao": "Quais operações 'controlar' abrange (registrar, alterar, excluir, consultar, validar)."},
        {"id": "P2", "descricao": "Onde os atestados são registrados: neste sistema ou em outro, do qual seriam lidos."},
        {"id": "P4", "descricao": "Como o servidor é identificado e de onde vêm os dados dele."},
    ]
    out.append(("E6", "G07", e, ["S4"]))

    out.append(("P4", "G08", g08_correto(), []))

    e = g08_correto()  # E7: pergunta indevida (o pedido descreve o fluxo)
    e["pendencias"].append({"id": "P3", "descricao": "Há análise ou decisão sobre os requerimentos? Por quem?"})
    out.append(("E7", "G08", e, ["S4"]))
    return [(i, c, copy.deepcopy(j), alvo) for i, c, j, alvo in out]
