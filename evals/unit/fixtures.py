"""JSONs canônicos dos gabaritos aprovados (evals/gabaritos-iniciais.md, revisão 2)."""
import copy


def _proj(titulo):
    return {"titulo": titulo, "fronteira": "aplicação descrita no pedido", "origem_subsidio": "gabarito sintético", "data": "2026-11-17"}


def _f(fid, tipo, nome, op=None, hip=None, efpa=None):
    d = {"id": fid, "requisito": "trecho do pedido", "nome": nome, "tipo": tipo, "operacao": op,
         "hipotese": hip, "justificativa": "conforme gabarito"}
    if efpa is not None:
        d["efpa"] = efpa
    return d


def base(metodo="estimada", tipo="desenvolvimento", regime=None, titulo="caso"):
    return {"versao_esquema": 1, "metodo": metodo, "tipo_projeto": tipo, "regime_melhoria": regime,
            "projeto": _proj(titulo), "cobertura": {"status": "completa", "motivo": None},
            "funcoes": [], "hipoteses": [], "premissas": [], "pendencias": [], "nao_contados": []}


def g01():
    e = base(titulo="G01 Cursos EJE")
    e["funcoes"] = [
        _f("F01", "ALI", "Curso (Turma como RET)"),
        _f("F02", "AIE", "Servidor (RH)"),
        _f("F03", "EE", "Incluir curso"), _f("F04", "EE", "Alterar curso"), _f("F05", "EE", "Excluir curso"),
        _f("F06", "EE", "Incluir turma"), _f("F07", "EE", "Alterar turma"), _f("F08", "EE", "Excluir turma"),
        _f("F09", "CE", "Consultar cursos com filtros"),
        _f("F10", "SE", "Relatório de vagas por modalidade"),
    ]
    e["nao_contados"] = [{"item": "Modalidade", "categoria": "dado-de-codigo", "justificativa": "lista fixa de valores"}]
    return e


def _g02_funcoes(nesma):
    fs = [
        _f("F01", "ALI", "Solicitação de diária", "A",
           efpa={"td": {"afetados": 1, "originais": 12}} if nesma else None),
        _f("F02", "AIE", "Afastamento (Frequência)", "I"),
        _f("F03", "EE", "Registrar solicitação", "A",
           efpa={"td": {"afetados": 1, "originais": 10}, "ar": {"afetados": 2, "originais": 2}} if nesma else None),
        _f("F04", "CE", "Consultar solicitação", "A",
           efpa={"td": {"afetados": 1, "originais": 12}, "ar": {"afetados": 1, "originais": 2}} if nesma else None),
    ]
    if nesma:
        fs.append(_f("F05", "EE", "Cancelar solicitação", "A",
                     efpa={"td": {"afetados": 0, "originais": 3}, "ar": {"afetados": 1, "originais": 1}}))
    return fs


def g02():
    e = base(tipo="melhoria", regime="sem-fatores", titulo="G02 Diárias")
    e["funcoes"] = _g02_funcoes(False)
    return e


def g03a():
    e = base(tipo="melhoria", regime="nesma", titulo="G03a Diárias EFPA")
    e["funcoes"] = _g02_funcoes(True)
    return e


def g03b():
    e = base(tipo="melhoria", regime="nesma", titulo="G03b Diárias EFPA sem baseline")
    faixa = lambda a, b: {"faixa": {"min": a, "max": b, "justificativa": "TDs e ARs originais desconhecidos"}}
    e["funcoes"] = [
        _f("F01", "ALI", "Solicitação de diária", "A", efpa=faixa("0.25", "1.00")),
        _f("F02", "AIE", "Afastamento (Frequência)", "I"),
        _f("F03", "EE", "Registrar solicitação", "A", efpa=faixa("0.25", "1.50")),
        _f("F04", "CE", "Consultar solicitação", "A", efpa=faixa("0.25", "1.00")),
    ]
    e["pendencias"] = [{"id": "P1", "descricao": "baseline da aplicação"}]
    e["cobertura"] = {"status": "parcial", "motivo": "outras transações que usam o cadastro alterado são desconhecidas"}
    return e


def g04():
    e = base(titulo="G04 Gerenciar diárias")
    e["hipoteses"] = [
        {"id": "H1", "descricao": "solicitações mantidas por este sistema (com registro)", "trecho": "minhas solicitações", "grupo": "origem"},
        {"id": "H5", "descricao": "solicitações nascem em outro sistema e são lidas", "trecho": "minhas solicitações", "grupo": "origem", "requer": ["H3"]},
        {"id": "H2", "descricao": "gerenciar inclui alterar e cancelar", "trecho": "gerenciar", "requer": ["H1"]},
        {"id": "H3", "descricao": "gerenciar inclui consultar", "trecho": "gerenciar"},
        {"id": "H4", "descricao": "o registro lê os dados do servidor no RH", "requer": ["H1"]},
    ]
    e["funcoes"] = [
        _f("F01", "ALI", "Solicitação de diária", hip="H1"),
        _f("F02", "EE", "Registrar solicitação", hip="H1"),
        _f("F07", "AIE", "Solicitação de diária (outro sistema)", hip="H5"),
        _f("F03", "EE", "Alterar solicitação", hip="H2"),
        _f("F04", "EE", "Cancelar solicitação", hip="H2"),
        _f("F05", "CE", "Consultar minhas solicitações", hip="H3"),
        _f("F06", "AIE", "Servidor (RH)", hip="H4"),
    ]
    return e


def g05():
    e = base(metodo="indicativa", titulo="G05 Patrimônio")
    e["funcoes"] = [_f("F01", "ALI", "Bem"), _f("F02", "ALI", "Fornecedor"),
                    _f("F03", "AIE", "Servidor (RH)"), _f("F04", "AIE", "Unidade")]
    return e


def g06():
    e = base(titulo="G06 Salas")
    e["funcoes"] = [
        _f("F01", "ALI", "Sala"), _f("F02", "ALI", "Reserva"),
        _f("F03", "EE", "Incluir sala"), _f("F04", "EE", "Alterar sala"), _f("F05", "EE", "Excluir sala"),
        _f("F06", "EE", "Reservar sala"), _f("F07", "EE", "Cancelar reserva"),
        _f("F08", "CE", "Consultar salas livres"), _f("F09", "CE", "Agenda da sala no dia"),
        _f("F10", "SE", "Painel de taxa de ocupação"),
    ]
    return e


def clone(e):
    return copy.deepcopy(e)
