"""Casos dos evals do agente, derivados de evals/gabaritos-iniciais.md (revisão 3) e evals/README.md.

Cada caso define a invocação, o subsídio e o que as verificações automáticas esperam.
O gabarito completo (para o juiz) é extraído do Markdown pelo título da seção (`secao`).

tipos de caso:
  contagem     executa e é comparado com o gabarito
  valido       caso de argumento que deve executar; confere a configuração aplicada
  alerta1      erro de estágio 1: só ALERTA, sem acessar o subsídio, sem script, sem arquivos
  alerta2      erro de estágio 2: só ALERTA, leitura permitida, sem script, sem arquivos
  nl_confirma  prosa com pedido de configuração: só pede confirmação, sem script, sem arquivos
  nl_executa   prosa só com descrição: executa com os padrões, sem pedir confirmação
"""
from decimal import Decimal as D

G01 = (
    "Novo sistema para a Escola Judiciária Eleitoral gerenciar cursos de capacitação. O servidor da EJE cadastra "
    "cursos (título, carga horária, modalidade, período de inscrição) e, para cada curso, as turmas (data de início, "
    "data de fim, vagas, instrutor). Uma turma só existe dentro de um curso: ao excluir um curso, as turmas dele são "
    "excluídas. Depois de criado o curso, as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada "
    "uma separadamente. Modalidade é uma de: presencial, EaD ou híbrida. O instrutor é um servidor do tribunal, "
    "informado pela matrícula; os dados dos servidores vêm do sistema de RH (apenas leitura). Deve ser possível incluir, "
    "alterar e excluir cursos, consultar cursos com filtros por período e modalidade e emitir um relatório gerencial com "
    "o total de vagas ofertadas por modalidade no semestre."
)

G01_PARAFRASE = (
    "A Escola Judiciária Eleitoral precisa de um sistema novo para as capacitações. Os cursos poderão ser incluídos, "
    "alterados e excluídos pelo servidor da EJE; cada curso tem título, carga horária, modalidade (que só pode ser "
    "presencial, EaD ou híbrida) e período de inscrição. Dentro de cada curso ficam as turmas, com data de início, data "
    "de fim, número de vagas e instrutor; uma turma não existe fora do seu curso e, se o curso for excluído, as turmas "
    "também são. Com o curso já criado, cada turma pode ser incluída, alterada ou excluída separadamente, quando for "
    "preciso. O instrutor é sempre um servidor do tribunal, identificado pela matrícula, e os dados de servidores são só "
    "lidos do sistema de RH. A EJE também quer consultar os cursos filtrando por período e por modalidade, e tirar um "
    "relatório gerencial que totalize, por modalidade, as vagas oferecidas no semestre."
)

G01_REPETIDO = G01.replace(
    "Depois de criado o curso, as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma separadamente.",
    "Depois de criado o curso, as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma "
    "separadamente. Repetindo: depois de criado o curso, as turmas podem ser incluídas, alteradas e excluídas a qualquer "
    "momento, cada uma separadamente.",
)

G02_BASELINE = (
    "O sistema de Diárias, já em produção, tem hoje: o cadastro de solicitações (12 tipos de dado); a função Registrar "
    "solicitação, com 10 tipos de dado, que lê a solicitação e os dados do servidor vindos do RH; a função Cancelar "
    "solicitação, com 3 tipos de dado, que lê apenas a solicitação; e a função Consultar solicitação, que exibe os 12 "
    "tipos de dado e lê a solicitação e os dados do servidor. Uma solicitação não pode ser alterada depois de "
    "registrada, só cancelada. O sistema de Diárias ainda não lê nenhum dado do sistema de Frequência."
)
G02_PEDIDO = (
    "Pedido: ao registrar uma solicitação, verificar se o servidor tem afastamento registrado no sistema de Frequência "
    "no período da viagem e, se tiver, impedir o registro. O sistema de Frequência é mantido por outra unidade; o de "
    "Diárias só lê os afastamentos. As datas do afastamento são usadas só na verificação e não são exibidas nem "
    "gravadas; o impedimento usa a área de mensagens que a função já tem. Incluir na solicitação o campo "
    "\"justificativa de urgência\", obrigatório quando a viagem começar em menos de 10 dias; é o único tipo de dado "
    "novo. O novo campo deve aparecer também na consulta da solicitação. A função Cancelar solicitação não muda: mesmos "
    "dados, mesmos arquivos e mesma lógica."
)
G02 = G02_BASELINE + "\n\n" + G02_PEDIDO
G03B = G02_PEDIDO.replace("Pedido: ", "No sistema de Diárias, já em produção: ") + \
    " O sistema de Diárias ainda não lê nenhum dado do sistema de Frequência."

G04 = "Como servidor, quero gerenciar minhas solicitações de diárias."

G07 = "A Seção de Assistência à Saúde precisa controlar os atestados médicos apresentados pelos servidores."
G05 = (
    "Sistema para o setor de patrimônio controlar os bens móveis do tribunal. O setor cadastra os bens (número de "
    "tombamento, descrição, valor, data de aquisição, estado de conservação, fornecedor, servidor responsável, unidade "
    "onde está) e os fornecedores (CNPJ, razão social, contato). O estado de conservação é um de: novo, bom, regular, "
    "inservível. Os servidores vêm do sistema de RH e as unidades vêm do sistema de estrutura organizacional; nenhum dos "
    "dois é mantido pelo patrimônio."
)

G06 = (
    "Sistema de reserva de salas de reunião. A administração cadastra as salas (nome, prédio, capacidade, recursos "
    "disponíveis), podendo incluir, alterar e excluir. O usuário consulta as salas livres informando data e horário e "
    "reserva uma delas, informando a finalidade; depois, pode cancelar a própria reserva. As reservas ficam guardadas "
    "como histórico mesmo depois que a sala é excluída. Qualquer usuário visualiza a agenda de uma sala num dia, "
    "informando a sala e o dia, e pode exportar essa mesma agenda em PDF. Ao reservar, o sistema exibe uma mensagem de "
    "confirmação. A tela inicial tem um menu com atalhos para as funcionalidades. A administração tem um painel com a "
    "taxa de ocupação de cada sala no mês."
)
G06_SEM_MENU = G06.replace(" Ao reservar, o sistema exibe uma mensagem de confirmação.", "").replace(
    " A tela inicial tem um menu com atalhos para as funcionalidades.", "")

# Pedido curto para os casos de argumentos que executam (custo baixo).
CURTO = (
    "Sistema novo para a portaria registrar visitantes. O vigilante registra a entrada do visitante (nome, documento, "
    "unidade de destino) e, depois, a saída. O vigilante consulta os visitantes que estão no prédio. As unidades vêm do "
    "sistema de estrutura organizacional."
)
CURTO_COM_TEXTO_DE_ARGUMENTO = CURTO + " Observação do solicitante: no formulário antigo havia um campo chamado modo=indicativa, que não deve ser migrado."
CURTO_TOKEN_INICIAL = "tipo=SEI é o nome do campo que guarda o número do processo no SEI. " + CURTO


def _ms(*pares):
    """Multiconjunto esperado de (tipo, operação)."""
    out = []
    for tipo, op, n in pares:
        out += [(tipo, op)] * n
    return sorted(out, key=lambda x: (x[0], x[1] or ""))


CASOS = {
    # ---------------------------------------------------------------- contagem
    "G01": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento", "subsidio": G01,
            "tipos": _ms(("ALI", None, 1), ("AIE", None, 1), ("EE", None, 6), ("CE", None, 1), ("SE", None, 1)),
            "totais": [(D(45), D(45))]},
    "G02": {"tipo": "contagem", "secao": "G02", "args": "tipo=melhoria", "subsidio": G02,
            "tipos": _ms(("ALI", "A", 1), ("AIE", "I", 1), ("EE", "A", 1), ("CE", "A", 1)),
            "totais": [(D(20), D(20))], "unidade": "PF de melhoria"},
    "G03a": {"tipo": "contagem", "secao": "G03a", "args": "tipo=melhoria melhoria=nesma", "subsidio": G02,
             "tipos": _ms(("ALI", "A", 1), ("AIE", "I", 1), ("EE", "A", 2), ("CE", "A", 1)),
             "totais": [(D("14.75"), D("14.75"))], "unidade": "PFM"},
    "G03b": {"tipo": "contagem", "secao": "G03b", "args": "tipo=melhoria melhoria=nesma", "subsidio": G03B,
             "tipos": None, "totais": None, "unidade": "PFM", "cobertura": "parcial"},
    "G04": {"tipo": "contagem", "secao": "G04", "args": "tipo=desenvolvimento", "subsidio": G04,
            "tipos": None, "totais": None, "cobertura": "parcial"},
    "G05": {"tipo": "contagem", "secao": "G05", "args": "modo=indicativa", "subsidio": G05,
            "tipos": _ms(("ALI", None, 2), ("AIE", None, 2)), "totais": [(D(100), D(100))]},
    "G06": {"tipo": "contagem", "secao": "G06", "args": "tipo=desenvolvimento", "subsidio": G06,
            "tipos": _ms(("ALI", None, 2), ("EE", None, 5), ("CE", None, 2), ("SE", None, 1)),
            "totais": [(D(47), D(47))]},
    "G07": {"tipo": "contagem", "secao": "G07", "args": "tipo=desenvolvimento", "subsidio": G07,
            "tipos": None, "totais": None, "cobertura": "parcial"},
    # ---------------------------------------------------------------- metamórficos (variantes)
    "M01": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento", "subsidio": G01_PARAFRASE,
            "tipos": "G01", "totais": "G01", "nota_juiz": "Subsídio parafraseado do G01: o gabarito do G01 vale integralmente."},
    "M02": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento", "subsidio": G01_REPETIDO,
            "tipos": "G01", "totais": "G01", "nota_juiz": "G01 com uma frase repetida: nenhuma função pode ser duplicada."},
    "M03a": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento saida=md", "subsidio": G01,
             "tipos": "G01", "totais": "G01", "exporta": "md", "sem_juiz": True},
    "M03b": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento saida=txt", "subsidio": G01,
             "tipos": "G01", "totais": "G01", "exporta": "txt", "sem_juiz": True},
    "M04": {"tipo": "contagem", "secao": "G06", "args": "tipo=desenvolvimento", "subsidio": G06_SEM_MENU,
            "tipos": "G06", "totais": "G06", "nota_juiz": "G06 sem as frases do menu e da mensagem de confirmação: o gabarito do G06 vale integralmente."},
    # ---------------------------------------------------------------- argumentos
    "A01": {"tipo": "valido", "args": "modo=estimada saida=md", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "exporta": "md"},
    "A02": {"tipo": "valido", "args": "modo=estimativa", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "pergunta_formato": True},
    "A03": {"tipo": "valido", "args": "saida=excel", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "exporta": "xlsx"},
    "A04": {"tipo": "valido", "args": None, "subsidio": CURTO, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}, "pergunta_formato": True},
    "A05": {"tipo": "alerta1", "args": "modo=detalhada", "subsidio": CURTO},
    "A06": {"tipo": "alerta1", "args": "modo indicativa", "subsidio": CURTO},
    "A07": {"tipo": "alerta1", "args": "modo=estimada modo=indicativa", "subsidio": CURTO},
    "A08": {"tipo": "alerta1", "args": "modo=indicativa tipo=melhoria", "subsidio": CURTO},
    "A09": {"tipo": "alerta1", "args": "saida=pdf", "subsidio": CURTO},
    "A10": {"tipo": "alerta1", "args": "formato=md", "subsidio": CURTO},
    "A11": {"tipo": "alerta1", "args": "modo=indicativa", "subsidio": CURTO, "sem_delimitador": True},
    "A12": {"tipo": "alerta2", "args": None, "subsidio": None, "arquivo_inexistente": "./nao-existe.pdf"},
    "A13a": {"tipo": "alerta1", "args": "melhoria=nesma tipo=desenvolvimento", "subsidio": CURTO},
    "A13b": {"tipo": "alerta2", "args": "melhoria=nesma", "subsidio": CURTO},
    "A14": {"tipo": "valido", "args": None, "subsidio": CURTO_COM_TEXTO_DE_ARGUMENTO, "inline": True, "espera": {"metodo": "estimada"}, "pergunta_formato": True},
    "A15": {"tipo": "valido", "args": "", "subsidio": CURTO_TOKEN_INICIAL, "inline": True, "espera": {"metodo": "estimada"}, "pergunta_formato": True},
    # ---------------------------------------------------------------- linguagem natural
    "L01": {"tipo": "nl_confirma", "prosa": "Estime os pontos de função do pedido que está em ./pedido.md e gere o resultado em planilha.",
            "subsidio": CURTO, "espera_invocacao": "saida=xlsx"},
    "L02": {"tipo": "nl_executa", "prosa": "Preciso estimar o tamanho funcional, em pontos de função, deste pedido de sistema: " + CURTO,
            "subsidio": None, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}, "pergunta_formato": True},
}

# Relações metamórficas entre casos (verificadas sobre os JSONs, sem juiz).
PARES = {
    "M01": ("G01", "M01", "mesmo multiconjunto (tipo, operação) e mesmo total"),
    "M02": ("G01", "M02", "mesmo multiconjunto (tipo, operação) e mesmo total"),
    "M03": ("M03a", "M03b", "mesmo multiconjunto, mesmos totais e mesmas funções (nomes podem variar)"),
    "M04": ("G06", "M04", "mesmo multiconjunto (tipo, operação) e mesmo total"),
    "M05": ("G02", "G03a", "G03a = G02 + Cancelar (EE, A); G02 = 20 PF de melhoria; G03a = 14,75 PFM"),
}


def resolver(caso_id):
    """Resolve referências ("tipos": "G01") para os valores do caso base."""
    c = dict(CASOS[caso_id])
    for chave in ("tipos", "totais"):
        if isinstance(c.get(chave), str):
            c[chave] = CASOS[c[chave]][chave]
    return c
