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

"previa": True  o caso usa o padrão interativo=sim e deve terminar na prévia (D52): check, render --format
                previa copiado, nenhum PF na resposta, nada exportado. Os demais casos fixam interativo=nao.
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
G08 = ("A Seção de Protocolo precisa registrar os requerimentos que os servidores entregam no balcão. "
       "Cada requerimento é analisado pela chefia da seção, que registra no sistema a decisão: deferido ou indeferido.")
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

# Holdouts da iteração 2 (camada 1), transcritos de evals/gabaritos-iniciais.md (seções H1 a H3c).
H1_TEXTO = 'Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria. A equipe quer gerenciar esses registros, e o cidadão precisa consultar as suas manifestações.'
H1C_TEXTO = 'Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria, com nome e CPF informados pelo próprio cidadão para identificar quais manifestações são dele na consulta. A equipe da Ouvidoria poderá corrigir o texto e cancelar registros feitos por engano, além de analisar o conteúdo e registrar a resposta final ao cidadão.'
H2_TEXTO = 'Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.'
H2C_TEXTO = 'Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço, mantida no sistema de locais da Justiça Eleitoral. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega, e essas respostas devem atualizar a situação da convocação na nomeação. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.'
H3_TEXTO = 'Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.\n\nAntes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber.\n\nTambém queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas.\n\nA consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.\n\nO acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.'
H3C_TEXTO = 'Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.\n\nAntes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. A chegada é anotada assim que as urnas entram no depósito; outro servidor confere o material mais tarde e registra que aquele retorno foi conferido. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber. Esses responsáveis são servidores do Tribunal: usaremos a matrícula e o nome que vêm do cadastro de servidores do sistema de pessoal.\n\nTambém queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas. A equipe da seção analisa cada ocorrência e registra sua conclusão para dar o caso por encerrado.\n\nA consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.\n\nO acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.'

# Contrato de cada caso da camada 1 fixado aqui, e não no gabarito compartilhado, para não alterar
# o julgamento histórico de G04, G07 e G08 (consulta 23, O-G04).
NOTA_CAMADA1 = ("Variante da camada 1 (modo interativo; a execução termina na prévia). O gabarito vale integralmente: "
                "as pendências obrigatórias dele são as do S4 (contrato v2), exigidas com `pergunta`; as pendências "
                "proibidas valem para o R. S4_antigo: responda null.")
NOTA_G04I = ("Variante da camada 1 (modo interativo; a execução termina na prévia). Funções, proibidas e cenários: o "
             "gabarito do G04 vale integralmente. Contrato do S4 v2 (D43; pedido de pouco subsídio): são obrigatórias, "
             "com `pergunta`, só as pendências das regras gerais: (1) a origem das solicitações (mantidas por este "
             "sistema ou lidas de outro); (2) o que \"gerenciar\" abrange; (3) como o servidor é identificado e de onde "
             "vêm os dados dele; (4) se há análise, aprovação ou decisão sobre as solicitações, e por quem. Cálculo do "
             "valor e prestação de contas são pendências de diagnóstico (relatadas em medidas.diagnostico_presentes, não "
             "reprovam). S3: exigir a consulta também na alternativa \"mantidas por este sistema\" segue o exemplo 3 "
             "das referências da skill e não reprova; premissa que fixa algo que uma pendência declara desconhecido "
             "continua sendo incoerência (decisão do usuário após a `curta-4`). S4_antigo: avalie também a lista de pendências obrigatórias do gabarito do G04 (o que "
             "\"gerenciar\" abrange; fluxo de aprovação; cálculo do valor; prestação de contas; origem dos dados do "
             "servidor), pela regra da iteração 1.")

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
    "G01": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G01,
            "tipos": _ms(("ALI", None, 1), ("AIE", None, 1), ("EE", None, 6), ("CE", None, 1), ("SE", None, 1)),
            "totais": [(D(45), D(45))]},
    "G02": {"tipo": "contagem", "secao": "G02", "args": "tipo=melhoria interativo=nao", "subsidio": G02,
            "tipos": _ms(("ALI", "A", 1), ("AIE", "I", 1), ("EE", "A", 1), ("CE", "A", 1)),
            "totais": [(D(20), D(20))], "unidade": "PF de melhoria"},
    "G03a": {"tipo": "contagem", "secao": "G03a", "args": "tipo=melhoria melhoria=nesma interativo=nao", "subsidio": G02,
             "tipos": _ms(("ALI", "A", 1), ("AIE", "I", 1), ("EE", "A", 2), ("CE", "A", 1)),
             "totais": [(D("14.75"), D("14.75"))], "unidade": "PFM"},
    "G03b": {"tipo": "contagem", "secao": "G03b", "args": "tipo=melhoria melhoria=nesma interativo=nao", "subsidio": G03B,
             "tipos": None, "totais": None, "unidade": "PFM", "cobertura": "parcial"},
    "G04": {"tipo": "contagem", "secao": "G04", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G04,
            "tipos": None, "totais": None, "cobertura": "parcial"},
    "G05": {"tipo": "contagem", "secao": "G05", "args": "modo=indicativa interativo=nao", "subsidio": G05,
            "tipos": _ms(("ALI", None, 2), ("AIE", None, 2)), "totais": [(D(100), D(100))]},
    "G06": {"tipo": "contagem", "secao": "G06", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G06,
            "tipos": _ms(("ALI", None, 2), ("EE", None, 5), ("CE", None, 2), ("SE", None, 1)),
            "totais": [(D(47), D(47))]},
    "G07": {"tipo": "contagem", "secao": "G07", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G07,
            "tipos": None, "totais": None, "cobertura": "parcial"},
    "G08": {"tipo": "contagem", "secao": "G08", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G08,
            "tipos": None, "totais": None},
    # ---------------------------------------------------------------- holdouts da iteração 2 (camada 1: terminam na prévia, com juiz)
    "H1": {"tipo": "contagem", "secao": "H1", "args": "tipo=desenvolvimento", "subsidio": H1_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    "H1c": {"tipo": "contagem", "secao": "H1c", "args": "tipo=desenvolvimento", "subsidio": H1C_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    "H2": {"tipo": "contagem", "secao": "H2", "args": "tipo=desenvolvimento", "subsidio": H2_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    "H2c": {"tipo": "contagem", "secao": "H2c", "args": "tipo=desenvolvimento", "subsidio": H2C_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    "H3": {"tipo": "contagem", "secao": "H3", "args": "tipo=desenvolvimento", "subsidio": H3_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    "H3c": {"tipo": "contagem", "secao": "H3c", "args": "tipo=desenvolvimento", "subsidio": H3C_TEXTO,
            "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}},
    # ---------------------------------------------------------------- G04, G07 e G08 na camada 1 (D44, consulta 23)
    "G04i": {"tipo": "contagem", "secao": "G04", "args": "tipo=desenvolvimento", "subsidio": G04,
             "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"},
             "nota_juiz": NOTA_G04I},
    "G07i": {"tipo": "contagem", "secao": "G07", "args": "tipo=desenvolvimento", "subsidio": G07,
             "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"},
             "nota_juiz": NOTA_CAMADA1},
    "G08i": {"tipo": "contagem", "secao": "G08", "args": "tipo=desenvolvimento", "subsidio": G08,
             "tipos": None, "totais": None, "previa": True, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"},
             "nota_juiz": NOTA_CAMADA1},
    # ---------------------------------------------------------------- metamórficos (variantes)
    "M01": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G01_PARAFRASE,
            "tipos": "G01", "totais": "G01", "nota_juiz": "Subsídio parafraseado do G01: o gabarito do G01 vale integralmente."},
    "M02": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G01_REPETIDO,
            "tipos": "G01", "totais": "G01", "nota_juiz": "G01 com uma frase repetida: nenhuma função pode ser duplicada."},
    "M03a": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento saida=md interativo=nao", "subsidio": G01,
             "tipos": "G01", "totais": "G01", "exporta": "md", "sem_juiz": True},
    "M03b": {"tipo": "contagem", "secao": "G01", "args": "tipo=desenvolvimento saida=txt interativo=nao", "subsidio": G01,
             "tipos": "G01", "totais": "G01", "exporta": "txt", "sem_juiz": True},
    "M04": {"tipo": "contagem", "secao": "G06", "args": "tipo=desenvolvimento interativo=nao", "subsidio": G06_SEM_MENU,
            "tipos": "G06", "totais": "G06", "nota_juiz": "G06 sem as frases do menu e da mensagem de confirmação: o gabarito do G06 vale integralmente."},
    # ---------------------------------------------------------------- argumentos
    "A01": {"tipo": "valido", "args": "modo=estimada saida=md interativo=nao", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "exporta": "md"},
    "A02": {"tipo": "valido", "args": "modo=estimativa interativo=nao", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "pergunta_formato": True},
    "A03": {"tipo": "valido", "args": "saida=excel interativo=nao", "subsidio": CURTO, "espera": {"metodo": "estimada"}, "exporta": "xlsx"},
    "A04": {"tipo": "valido", "args": None, "subsidio": CURTO, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}, "previa": True},
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
    "A14": {"tipo": "valido", "args": None, "subsidio": CURTO_COM_TEXTO_DE_ARGUMENTO, "inline": True, "espera": {"metodo": "estimada"}, "previa": True},
    "A15": {"tipo": "valido", "args": "interativo=nao", "subsidio": CURTO_TOKEN_INICIAL, "inline": True, "espera": {"metodo": "estimada"}, "pergunta_formato": True},
    # ---------------------------------------------------------------- linguagem natural
    "L01": {"tipo": "nl_confirma", "prosa": "Estime os pontos de função do pedido que está em ./pedido.md e gere o resultado em planilha.",
            "subsidio": CURTO, "espera_invocacao": "saida=xlsx"},
    "L02": {"tipo": "nl_executa", "prosa": "Preciso estimar o tamanho funcional, em pontos de função, deste pedido de sistema: " + CURTO,
            "subsidio": None, "espera": {"metodo": "estimada", "tipo_projeto": "desenvolvimento"}, "previa": True},
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


# ---------------------------------------------------------------- camada 2 mínima (D60 item 3; consultas 40 e 41)
# Diálogos roteirizados, sem simulador: cada turno depois do primeiro é uma mensagem fixa do analista.
# O primeiro turno é a invocação do caso-base (camada 1, termina na prévia). "espera" diz o que o turno deve
# produzir: "previa" (nova prévia, sem PF) ou "final" (resultado calculado). Testes parciais: não substituem o
# diálogo da D44 nem a equivalência entre modos, que continua pendente.

D2B_FATOS = ("A relação de locais de votação é mantida no sistema de locais da Justiça Eleitoral. O serviço de comunicação "
             "avisará o sistema quando houver devolução do e-mail ou confirmação de entrega, e essas respostas devem "
             "atualizar a situação da convocação na nomeação. Não sei o resto. calcular")
D2D_CORRECAO = "Correção: não haverá lista de mesários ausentes por local."
D2C_PARCIAL = ("As solicitações são registradas e guardadas neste sistema. O servidor pode registrar, alterar, cancelar e "
               "consultar as próprias solicitações. A chefia imediata aprova ou devolve a solicitação, e o sistema registra "
               "a decisão. Não sei como o servidor é identificado nem de onde vêm os dados dele.")

NOTA_D2B = ("Diálogo D2b: o pedido original é o do H2; a mensagem do analista acrescenta exatamente as duas frases que o H2c "
            "tem a mais (origem dos locais e retorno da entrega). Avalie o resultado final pelo gabarito do H2c, inclusive as "
            "decomposições alternativas que ele aceita (envio autônomo ou absorvido; consulta dos locais própria ou absorvida). "
            "A autonomia do envio não foi respondida e pode continuar como hipótese.")

DIALOGOS = {
    "D2a": {"base": "G04i", "relacao": "preservacao",
            "turnos": [{"msg": "Não sei para todas. calcular", "espera": "final"}]},
    "D2b": {"base": "H2", "relacao": "correcao",
            "turnos": [{"msg": D2B_FATOS, "espera": "final", "juiz": {"secao": "H2c", "nota": NOTA_D2B},
                        # Totais aceitos pelo gabarito do H2c: decomposições (a)/(b) e consulta dos locais própria ou
                        # absorvida; com a autonomia do envio como hipótese, o máximo fica 5 PF acima do mínimo.
                        "totais": [(37, 37), (41, 41), (42, 42), (46, 46), (37, 42), (41, 46)]},
                       {"msg": D2D_CORRECAO, "espera": "final"}]},  # D2d: correção depois do resultado
    "D2c": {"base": "G04i", "relacao": "segundo_lote",
            "turnos": [{"msg": D2C_PARCIAL, "espera": "previa"}, {"msg": "calcular", "espera": "final"}]},
}


def caso_do_turno(did, k):
    """Caso efetivo para verificar o turno k (1 = invocação do caso-base) de um diálogo."""
    d = DIALOGOS[did]
    c = resolver(d["base"])
    if k == 1:
        return c
    turno = d["turnos"][k - 2]
    c["previa"] = turno["espera"] == "previa"
    c.pop("nota_juiz", None)
    if turno.get("totais"):
        c["totais"] = [(D(a), D(b)) for a, b in turno["totais"]]
    return c
