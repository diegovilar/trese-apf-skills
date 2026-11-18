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
    return {"versao_esquema": 3, "metodo": "estimada", "tipo_projeto": tipo, "regime_melhoria": None,
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


# --------------------------------------------------------------------------- camada 1 (prévia), consulta 23

def _p(pid, descricao, pergunta=None, situacao=None, lote=None, opcoes=None):
    d = {"id": pid, "descricao": descricao}
    if pergunta:
        d.update({"pergunta": pergunta, "situacao": situacao or "aberta"})
        if lote:
            d["lote"] = lote
        if opcoes:
            d["opcoes"] = opcoes
    return d


def h2_correto():
    """H2 correto na decomposição (a), com perguntas complementares legítimas sobre E2 e contexto citado."""
    e = _base("Nomeações e convocações de mesários", "novo sistema do cartório; cadastro eleitoral é externo; origem dos locais em aberto")
    e["hipoteses"] = [
        {"id": "H1", "descricao": "A relação de locais de votação é mantida neste sistema, com cadastro", "trecho": "consultar a relação de locais de votação, com nome e endereço", "grupo": "origem dos locais"},
        {"id": "H2", "descricao": "A relação de locais de votação é lida de outro sistema", "trecho": "consultar a relação de locais de votação, com nome e endereço", "grupo": "origem dos locais"},
        {"id": "H3", "descricao": "Problemas de entrega informados depois do envio são recebidos e gravados na nomeação", "trecho": "uma relação das convocações com problema de entrega"},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Nomeação", "O cartório vai registrar cada nomeação, com o mesário e o local de votação", "mantida aqui; guarda data de envio e comparecimento"),
        _f("F02", "AIE", "Eleitor (cadastro eleitoral)", "a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral", "mantido por outro sistema, lido no registro"),
        _f("F03", "EE", "Registrar nomeação", "O cartório vai registrar cada nomeação", "mantém Nomeação; lê inscrição e nome no cadastro eleitoral"),
        _f("F04", "CE", "Consultar locais de votação", "o servidor precisa consultar a relação de locais de votação, com nome e endereço", "só recuperação; lê a relação de locais (F09 ou F11, conforme a origem)"),
        _f("F05", "SE", "Enviar convocação por e-mail", "enviar as convocações por e-mail", "saída autônoma que grava na nomeação a data de envio e os erros detectados no envio"),
        _f("F06", "CE", "Consultar convocações com problema de entrega", "uma relação das convocações com problema de entrega", "só recuperação"),
        _f("F07", "EE", "Registrar comparecimento ou ausência", "o cartório registrará o comparecimento ou a ausência na nomeação", "um processo com dois valores"),
        _f("F08", "CE", "Listar ausentes por local", "tirará a lista dos mesários marcados como ausentes, por local", "recupera a ausência registrada"),
        _f("F09", "ALI", "Local de votação (mantido aqui)", "relação de locais de votação, com nome e endereço", "alternativa H1", hip="H1"),
        _f("F10", "EE", "Cadastrar local de votação", "relação de locais de votação", "mantém o ALI na alternativa H1", hip="H1"),
        _f("F11", "AIE", "Local de votação (outro sistema)", "relação de locais de votação", "alternativa H2, lida pela consulta", hip="H2"),
        _f("F12", "EE", "Registrar resultado posterior da entrega", "convocações com problema de entrega", "hipótese H3", hip="H3"),
    ]
    e["pendencias"] = [
        _p("P1", "Quem mantém a relação de locais de votação.",
           "O pedido diz que o servidor consulta a relação de locais de votação. Essa relação é mantida neste novo sistema ou em outro sistema, do qual seria só lida?",
           "perguntada", 1, ["mantida neste sistema", "lida de outro sistema"]),
        _p("P2", "O que conta como problema de entrega.",
           "O que o cartório considera \"problema de entrega\": só o e-mail recusado no momento do envio, ou também devoluções e falta de confirmação depois?",
           "perguntada", 1),
        _p("P3", "Como o resultado da entrega chega ao sistema.",
           "Como o sistema fica sabendo desses problemas: ele mesmo detecta no envio, o serviço de e-mail avisa depois, ou alguém do cartório registra?",
           "perguntada", 1),
        _p("P5", "Correção, cancelamento ou substituição de nomeações não foram mencionados."),
    ]
    e["nao_contados"] = [{"item": "Situação de comparecimento", "categoria": "dado-de-codigo", "justificativa": "valores fixos: compareceu, ausente"}]
    return e


def h3_correto():
    """H3 correto (agrupamento agregado), com pergunta mista que só usa contexto (E3)."""
    e = _base("Remessas de urnas", "novo sistema da Seção de Logística; cadastro de urnas é do sistema nacional; software da urna fora")
    e["cobertura"] = {"status": "parcial", "motivo": "identificação dos responsáveis e tratamento das ocorrências não descritos"}
    e["hipoteses"] = [
        {"id": "H1", "descricao": "A conferência do retorno é registrada depois da chegada, numa operação própria", "trecho": "A devolução só deve ser considerada concluída depois da conferência do material"},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Remessa (com urnas, movimentações e ocorrências)", "A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela", "dados mantidos aqui; registros ligados à remessa"),
        _f("F02", "AIE", "Urna (sistema nacional de logística)", "Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro", "mantido por outro sistema"),
        _f("F03", "EE", "Registrar remessa", "A Seção de Logística vai registrar cada remessa", "mantém Remessa; lê Urna para conferir os números de série"),
        _f("F04", "EE", "Corrigir remessa", "a equipe pode corrigir a data ou a relação de urnas", "mantém Remessa"),
        _f("F05", "EE", "Cancelar remessa", "cancelar uma remessa que não será mais realizada", "mantém Remessa"),
        _f("F06", "EE", "Registrar saída", "registrar a saída efetiva, com a data e as urnas que saíram", "mantém Remessa"),
        _f("F07", "EE", "Registrar entrega à zona", "depois a entrega à zona, com a data e as urnas recebidas", "mantém Remessa"),
        _f("F08", "EE", "Registrar retorno", "No retorno ao depósito, serão registradas a data e as urnas que chegaram", "mantém Remessa; retornos parciais repetem a operação"),
        _f("F09", "EE", "Registrar ocorrência", "registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução", "mantém Remessa; o aviso à seção é consequência"),
        _f("F10", "CE", "Consultar ocorrências recebidas", "A seção precisa consultar uma lista das ocorrências recebidas", "só recuperação"),
        _f("F11", "CE", "Consultar ficha da remessa", "A consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência", "o PDF é a mesma consulta"),
        _f("F12", "SE", "Quadro por zona", "um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo", "cálculo de quantidades e saldo"),
        _f("F13", "EE", "Registrar conferência do retorno", "A devolução só deve ser considerada concluída depois da conferência do material", "hipótese H1", hip="H1"),
    ]
    e["pendencias"] = [
        _p("P1", "Como os responsáveis por entregar e receber são identificados e de onde vêm os dados deles.",
           "Os responsáveis por entregar e receber as urnas são servidores, terceirizados ou outras pessoas? Como são identificados (matrícula, CPF, nome digitado) e de onde vêm os dados deles?",
           "perguntada", 1),
        _p("P2", "Se há análise ou decisão sobre as ocorrências, e por quem.",
           "Depois de avisada, a Seção de Logística analisa ou decide algo sobre cada ocorrência e registra isso no sistema? Quem faz?",
           "perguntada", 1),
        _p("P3", "Se a conferência é registrada junto com a chegada ou depois.",
           "O pedido diz que a devolução só se conclui depois da conferência e que a chegada é registrada com a data e as urnas. A conferência é registrada no mesmo momento da chegada ou depois, numa anotação própria?",
           "perguntada", 1, ["no mesmo registro da chegada", "depois, em registro próprio"]),
        _p("P4", "Anexos, cobrança de atraso e correção de movimentações não foram mencionados."),
    ]
    return e


def h2c_correto():
    e = _base("Nomeações e convocações de mesários", "novo sistema do cartório; cadastro eleitoral e locais são externos")
    e["funcoes"] = [
        _f("F01", "ALI", "Nomeação", "O cartório vai registrar cada nomeação, com o mesário e o local de votação", "mantida aqui"),
        _f("F02", "AIE", "Eleitor (cadastro eleitoral)", "a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral", "lido no registro"),
        _f("F03", "AIE", "Local de votação (sistema de locais)", "relação de locais de votação, com nome e endereço, mantida no sistema de locais da Justiça Eleitoral", "lido pela consulta"),
        _f("F04", "EE", "Registrar nomeação", "O cartório vai registrar cada nomeação", "mantém Nomeação; lê inscrição e nome no cadastro eleitoral"),
        _f("F05", "CE", "Consultar locais de votação", "o servidor precisa consultar a relação de locais de votação", "só recuperação; lê Local de votação"),
        _f("F06", "SE", "Enviar convocação por e-mail", "enviar as convocações por e-mail", "saída autônoma que grava na nomeação a data de envio e os erros detectados no envio"),
        _f("F07", "EE", "Receber resultado da entrega", "O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega", "atualiza a situação na nomeação"),
        _f("F08", "CE", "Consultar convocações com problema de entrega", "uma relação das convocações com problema de entrega", "só recuperação"),
        _f("F09", "EE", "Registrar comparecimento ou ausência", "o cartório registrará o comparecimento ou a ausência na nomeação", "um processo"),
        _f("F10", "CE", "Listar ausentes por local", "tirará a lista dos mesários marcados como ausentes, por local", "recupera a ausência registrada"),
    ]
    e["pendencias"] = [_p("P1", "Autenticação de quem opera o sistema não foi descrita.")]
    return e


def d2b_correto():
    """Diálogo D2b (camada 2): prévia do H2 respondida com as duas frases do H2c e calculada. Pendências do lote 1
    resolvidas ficam como histórico (proibidas como pergunta no H2c, mas resolvidas aqui); envio autônomo (a)."""
    e = h2c_correto()
    e["projeto"]["fronteira"] = "novo sistema do cartório; cadastro eleitoral e sistema de locais são externos"
    msg_locais = "A relação de locais de votação é mantida no sistema de locais da Justiça Eleitoral."
    msg_retorno = ("O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega, "
                   "e essas respostas devem atualizar a situação da convocação na nomeação.")
    for f in e["funcoes"]:
        if f["id"] == "F03":
            f["requisito"] = "mantida no sistema de locais da Justiça Eleitoral (resposta do analista)"
            f["esclarecimentos"] = ["E1"]
        if f["id"] == "F07":
            f["requisito"] = "O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega"
            f["esclarecimentos"] = ["E2"]
    e["pendencias"] = [
        _p("P1", "Quem mantém a relação de locais de votação.",
           "Essa relação é mantida neste novo sistema ou em outro sistema, do qual seria só lida?", "resolvida", 1,
           ["mantida neste sistema", "lida de outro sistema"]),
        _p("P2", "Como o resultado da entrega chega ao sistema.",
           "Como o sistema fica sabendo dos problemas de entrega: ele mesmo detecta no envio, o serviço de e-mail avisa depois, ou alguém do cartório registra?",
           "resolvida", 1),
        _p("P5", "Correção, cancelamento ou substituição de nomeações não foram mencionados."),
        _p("P6", "Autenticação de quem opera o sistema não foi descrita."),
    ]
    e["esclarecimentos"] = [
        {"id": "E1", "pendencia": "P1", "pergunta": e["pendencias"][0]["pergunta"], "resposta": msg_locais, "lote": 1},
        {"id": "E2", "pendencia": "P2", "pergunta": e["pendencias"][1]["pergunta"], "resposta": msg_retorno, "lote": 1},
    ]
    return e


def g04i_correto_v2():
    """G04 na camada 1, correto no contrato v2 e sem cálculo nem prestação de contas (reprova só no S4 antigo)."""
    e = g04_correto()
    e["pendencias"] = [
        _p("P1", "O que 'gerenciar' abrange.", "Gerenciar as solicitações inclui o quê: registrar, alterar, cancelar, consultar?", "perguntada", 1),
        _p("P2", "Origem das solicitações.", "As solicitações de diárias são registradas neste sistema (ALI) ou já existem em outro sistema, do qual seriam só lidas (AIE)?", "perguntada", 1),
        _p("P3", "Identificação do servidor e origem dos dados dele.", "Como o servidor é identificado na solicitação e de onde vêm os dados dele (por exemplo, do sistema de pessoal)?", "perguntada", 1),
        _p("P4", "Análise ou decisão sobre as solicitações.", "Alguém analisa ou aprova as solicitações no sistema? Quem?", "perguntada", 1),
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

    # Calibração delta da camada 1 (consulta 23): prévia, S4 só de ausências com pergunta, R, S4 antigo.
    # Nestes, o acerto exige reprovar EXATAMENTE os critérios-alvo.
    out.append(("P5", "H2", h2_correto(), []))
    out.append(("P6", "H3", h3_correto(), []))

    e = h2_correto()  # E8: E2 ausente
    e["pendencias"] = [p for p in e["pendencias"] if p["id"] not in ("P2", "P3")]
    out.append(("E8", "H2", e, ["S4"]))

    e = h3_correto()  # E10: E3 só em nao_contados
    e["pendencias"] = [p for p in e["pendencias"] if p["id"] != "P3"]
    e["nao_contados"] = [{"item": "Registro da conferência do retorno", "categoria": "absorvido",
                          "justificativa": "tratado como parte do registro do retorno; não está claro se a conferência é registrada depois"}]
    out.append(("E10", "H3", e, ["S4"]))

    e = h2_correto()  # E12: E2 presente, mas sem pergunta
    e["pendencias"] = [p for p in e["pendencias"] if p["id"] != "P2"]
    e["pendencias"][1] = _p("P3", "Como o sistema fica sabendo dos problemas de entrega: só erros no envio ou também retornos posteriores.")
    out.append(("E12", "H2", e, ["S4"]))

    e = h2_correto()  # E9: repetição efetiva do que o pedido afirma
    e["pendencias"].append(_p("P6", "Identificação do mesário.",
                              "Os mesários são identificados pela inscrição eleitoral, com o nome vindo do cadastro eleitoral?", "aberta"))
    out.append(("E9", "H2", e, ["R"]))

    e = h2c_correto()  # E11: pergunta a origem dos locais, que o texto responde
    e["pendencias"].append(_p("P2", "Origem dos locais de votação.",
                              "A relação de locais de votação é mantida neste novo sistema ou lida de outro?", "perguntada", 1))
    out.append(("E11", "H2c", e, ["R"]))

    out.append(("E13", "G04i", g04i_correto_v2(), ["S4_antigo"]))

    # Calibração do juiz final em diálogo (camada 2, consulta 40): histórico resolvido × pendência reaberta.
    out.append(("P7", "D2b", d2b_correto(), []))
    e = d2b_correto()  # E14: pergunta de novo a origem dos locais, que o analista respondeu
    e["pendencias"].append(_p("P7", "Origem dos locais de votação.",
                              "A relação de locais é mantida neste sistema ou lida de outro?", "aberta"))
    out.append(("E14", "D2b", e, ["S4"]))
    return [(i, c, copy.deepcopy(j), alvo) for i, c, j, alvo in out]


CALIBRACAO_EXATA = ("P5", "P6", "E8", "E9", "E10", "E11", "E12", "E13", "P7", "E14")
