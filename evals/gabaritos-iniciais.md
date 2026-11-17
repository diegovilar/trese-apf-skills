# Gabaritos iniciais (rascunho para validação, revisão 2)

Casos sintéticos e critérios de aceitação, escritos **antes** de references/ e do código (etapa 2 do `PLANO.md`). Depois de validados pelo usuário, viram arquivos legíveis por máquina em `evals/casos/`.

Pesos (NESMA estimada): ALI 7, AIE 5, EE 4, SE 5, CE 4. Indicativa: 35×ALI + 15×AIE.

## Critérios de aceitação

**Críticos** (precisam passar em **todas** as execuções):

- K1. Validação de argumentos conforme os casos A (alerta e parada no estágio certo, sem contagem nem exportação).
- K2. O JSON canônico passa em `apf.py check`, e os totais impressos e exportados são os calculados pelo script.
- K3. Nenhuma função proibida é contada.
- K4. Nos regimes de melhoria, unidade e rótulo corretos: PFM no `nesma`, sem valor central quando houver cenário.

**Semânticos** (taxa provisória, exploratória: N = 5 execuções, passa com 4):

- S1. Funções obrigatórias presentes, com o tipo correto e, em melhoria, com a operação correta (I/A/E). Nomes podem variar.
- S2. Total igual a um dos aceitos ou, nos casos avaliados por rubrica, coerente com as hipóteses declaradas.
- S3. Toda hipótese que muda o total aparece com seu efeito em PF. Os cenários mínimo e máximo são conjuntos coerentes de hipóteses.
- S4. Pendências obrigatórias presentes.
- S5. Rastreabilidade: cada função aponta para o trecho do pedido ou para a hipótese que a sustenta.

## Convenções usadas nos gabaritos

- **C1. Convenção de evidência** [convenção da skill]: função que o pedido não menciona nem implica não é contada nem vira hipótese; se for relevante, entra como pendência. Função implicada por uma palavra do pedido (ex.: "gerenciar") pode virar hipótese.
- **C2. Mesma consulta em outro formato** [convenção adotada com apoio no SISP 3.0 §8.1]: consulta em tela e a mesma consulta em PDF, DOC, XLS ou papel, com os mesmos dados e a mesma lógica, é uma única função (*single instance*). Se a lógica ou os dados diferirem, são funções distintas.
- **C3 (removida).** Mestre-detalhe e autonomia das entidades ficam declarados no próprio enunciado de cada caso, em vez de uma regra universal.
- **C4. Transação alterada no regime `sem-fatores`** [convenção da skill com apoio no SISP 3.0 §7.3, a aprovar pelo usuário]: a transação conta como alterada quando mudam os seus dados, os arquivos que ela referencia (inclusão ou retirada de arquivo) ou a sua lógica. A simples alteração de um arquivo que ela já usa, sem efeito nos dados ou na lógica dela, não a torna alterada. No regime `nesma`, vale o EFPA: um arquivo referenciado alterado conta como AR afetado (exemplo 7 do guia). Consequência: os dois regimes diferem não só nos fatores, mas também em **quais funções entram** na contagem.

## Validação de argumentos em dois estágios (interpretação de D5, a confirmar com o usuário)

- **Estágio 1, sintático:** chave ou valor desconhecido, `=` ausente, valores conflitantes, combinação explícita inválida, argumentos sem `--`. Alerta sem ler o subsídio.
- **Estágio 2, contextual:** problemas que só aparecem ao abrir o subsídio (arquivo inexistente, `tipo` inferido incompatível com `melhoria=`). O subsídio pode ser lido; alerta sem contagem nem exportação.

---

## G01 · Desenvolvimento: mestre-detalhe, consulta filtrada e relatório gerencial

Argumentos: `tipo=desenvolvimento`

> Novo sistema para a Escola Judiciária Eleitoral gerenciar cursos de capacitação. O servidor da EJE cadastra cursos (título, carga horária, modalidade, período de inscrição) e, para cada curso, as turmas (data de início, data de fim, vagas, instrutor). Uma turma só existe dentro de um curso: ao excluir um curso, as turmas dele são excluídas. Depois de criado o curso, as turmas podem ser incluídas, alteradas e excluídas a qualquer momento, cada uma separadamente. Modalidade é uma de: presencial, EaD ou híbrida. O instrutor é um servidor do tribunal, informado pela matrícula; os dados dos servidores vêm do sistema de RH (apenas leitura). Deve ser possível incluir, alterar e excluir cursos, consultar cursos com filtros por período e modalidade e emitir um relatório gerencial com o total de vagas ofertadas por modalidade no semestre.

| Função | Tipo | PF | Fundamento |
|---|---|---|---|
| Curso (Turma como RET) | ALI | 7 | turma sem significado fora do curso (declarado) |
| Servidor (RH) | AIE | 5 | grupo lógico mantido pelo RH, só lido |
| Incluir / Alterar / Excluir curso | EE ×3 | 12 | |
| Incluir / Alterar / Excluir turma | EE ×3 | 12 | operações independentes (declarado) |
| Consultar cursos com filtros | CE | 4 | sem cálculo |
| Relatório de vagas por modalidade no semestre | SE | 5 | totalização |

- **Total aceito:** 45.
- **Proibidas:** Modalidade como ALI (dado de código); Turma como ALI separado; lista de servidores (o instrutor é informado pela matrícula).

## G02 · Melhoria, regime `sem-fatores` (padrão), com baseline explícita

Argumentos: `tipo=melhoria`

> O sistema de Diárias, já em produção, tem hoje: o cadastro de solicitações (12 tipos de dado); a função Registrar solicitação, com 10 tipos de dado, que lê a solicitação e os dados do servidor vindos do RH; a função Cancelar solicitação, com 3 tipos de dado, que lê apenas a solicitação; e a função Consultar solicitação, que exibe os 12 tipos de dado e lê a solicitação e os dados do servidor. Uma solicitação não pode ser alterada depois de registrada, só cancelada. O sistema de Diárias ainda não lê nenhum dado do sistema de Frequência.
>
> Pedido: ao registrar uma solicitação, verificar se o servidor tem afastamento registrado no sistema de Frequência no período da viagem e, se tiver, impedir o registro. O sistema de Frequência é mantido por outra unidade; o de Diárias só lê os afastamentos. As datas do afastamento são usadas só na verificação e não são exibidas nem gravadas; o impedimento usa a área de mensagens que a função já tem. Incluir na solicitação o campo "justificativa de urgência", obrigatório quando a viagem começar em menos de 10 dias; é o único tipo de dado novo. O novo campo deve aparecer também na consulta da solicitação. A função Cancelar solicitação não muda: mesmos dados, mesmos arquivos e mesma lógica.

| Função | Tipo | Op. | PF | Fundamento |
|---|---|---|---|---|
| Solicitação de diária | ALI | A | 7 | novo atributo persistido |
| Afastamento (Frequência) | AIE | I | 5 | novo grupo lógico lido, mantido por outra aplicação; ainda não referenciado (declarado) |
| Registrar solicitação | EE | A | 4 | nova regra, novo campo, novo arquivo referenciado |
| Consultar solicitação | CE | A | 4 | novo campo exibido |

- **Total aceito:** 20 PF de melhoria, soma simples.
- **Proibidas:** Cancelar solicitação como alterada (C4); mensagem de impedimento como função própria; qualquer fator ≠ 1.

## G03a · Mesmo pedido de G02, regime `nesma` (EFPA), com baseline explícita

Argumentos: `tipo=melhoria melhoria=nesma`

| Função | Tipo | Op. | PF base | %TD | %AR | Fator | PFM |
|---|---|---|---|---|---|---|---|
| Afastamento (Frequência) | AIE | I | 5 | — | — | 1,00 | 5,00 |
| Solicitação de diária | ALI | A | 7 | 1/12 ≤ 1/3 | — | 0,25 | 1,75 |
| Registrar solicitação | EE | A | 4 | 1/10 ≤ 2/3 | 2/2 (Solicitação alterada + Afastamento novo) ≤ 100% | 0,75 | 3,00 |
| Cancelar solicitação | EE | A | 4 | 0/3 ≤ 2/3 | 1/1 (Solicitação alterada) ≤ 100% | 0,75 | 3,00 |
| Consultar solicitação | CE | A | 4 | 1/12 ≤ 2/3 | 1/2 (Solicitação alterada) ≤ 2/3 | 0,50 | 2,00 |

- **Total aceito:** 14,75 PFM. Cancelar entra pelo exemplo 7 do guia (arquivo referenciado alterado).
- Os numeradores e denominadores de TD e AR vêm todos do subsídio (tipos de dado declarados, único tipo de dado novo, datas de afastamento não exibidas nem gravadas, mensagem existente reaproveitada).
- **Proibidas:** chamar o resultado de PF; omitir Cancelar solicitação.

## G03b · Pedido de G02 sem a baseline, regime `nesma` (cenários)

Argumentos: `tipo=melhoria melhoria=nesma`. Subsídio: só o parágrafo "Pedido" de G02, com a frase "O sistema de Diárias ainda não lê nenhum dado do sistema de Frequência".

Avaliado por rubrica, sem total fixo:

- AIE Afastamento com fator firme 1,00 (5,00 PFM).
- ALI Solicitação, Registrar e Consultar alteradas, cada uma com faixa de fatores justificada pelo que se sabe e pelo que falta (TDs e ARs originais).
- Total apresentado como faixa, sem valor central, com o rótulo "estimativa híbrida: pesos NESMA estimada + fatores EFPA", e com **cobertura parcial** (o total vale só para as funções identificadas, porque o número de outras transações impactadas é desconhecido).
- **Pendências obrigatórias:** baseline da aplicação (campos do cadastro, campos e arquivos de cada transação) e outras transações que usam o cadastro de solicitações e, pelo EFPA, também seriam impactadas.

## G04 · Requisito ambíguo de backlog (rubrica)

Argumentos: `tipo=desenvolvimento`

> Como servidor, quero gerenciar minhas solicitações de diárias.

Avaliado por rubrica, sem total fixo:

- **Nenhuma função é evidência isolada** (revisão 3, após a consulta 5 ao popper): "minhas solicitações" não diz se elas são mantidas por este sistema (ALI, com ao menos uma função que as mantém) ou nascem em outro fluxo e são lidas (AIE, com ao menos uma função que as lê). As duas origens devem aparecer como alternativas excludentes.
- Toda função transacional (registrar, alterar, cancelar, consultar) e o AIE de servidor só são aceitos como hipótese explícita, ligada à palavra "gerenciar" ou a outra parte do texto (C1), com o efeito em PF. "Gerenciar" não comprova nem o registro.
- Cenário mínimo e máximo **coerentes**: nenhum cenário pode ter arquivo sem transação que o mantenha ou leia (o script rejeita). Referência de cálculo: com origem em grupo, registro dentro da alternativa "mantidas aqui", consulta exigida pela alternativa "lidas de outro sistema" e alterar/cancelar exigindo "mantidas aqui", o mínimo é 9 e o máximo é 28.
- Cobertura parcial.
- **Proibidas:** aprovação pela chefia, cálculo de valor, pagamento ou prestação de contas contados como funções ou como hipóteses com PF.
- **Pendências obrigatórias:** o que "gerenciar" abrange; fluxo de aprovação; cálculo do valor; prestação de contas; origem dos dados do servidor.

## G05 · Indicativa

Argumentos: `modo=indicativa`

> Sistema para o setor de patrimônio controlar os bens móveis do tribunal. O setor cadastra os bens (número de tombamento, descrição, valor, data de aquisição, estado de conservação, fornecedor, servidor responsável, unidade onde está) e os fornecedores (CNPJ, razão social, contato). O estado de conservação é um de: novo, bom, regular, inservível. Os servidores vêm do sistema de RH e as unidades vêm do sistema de estrutura organizacional; nenhum dos dois é mantido pelo patrimônio.

| Função | Tipo | PF |
|---|---|---|
| Bem | ALI | 35 |
| Fornecedor | ALI | 35 |
| Servidor (RH) | AIE | 15 |
| Unidade (estrutura organizacional) | AIE | 15 |

- **Total aceito:** 100.
- **Proibidas:** Estado de conservação como ALI (dado de código); funções transacionais na tabela.
- **Obrigatório:** registrar que, na pesquisa da NESMA, a indicativa desviou até cerca de 50% da detalhada em alguns casos. É uma observação, não um limite garantido de erro.

## G06 · Casos de borda em desenvolvimento

Argumentos: `tipo=desenvolvimento`

> Sistema de reserva de salas de reunião. A administração cadastra as salas (nome, prédio, capacidade, recursos disponíveis), podendo incluir, alterar e excluir. O usuário consulta as salas livres informando data e horário e reserva uma delas, informando a finalidade; depois, pode cancelar a própria reserva. As reservas ficam guardadas como histórico mesmo depois que a sala é excluída. Qualquer usuário visualiza a agenda de uma sala num dia, informando a sala e o dia, e pode exportar essa mesma agenda em PDF. Ao reservar, o sistema exibe uma mensagem de confirmação. A tela inicial tem um menu com atalhos para as funcionalidades. A administração tem um painel com a taxa de ocupação de cada sala no mês.

| Função | Tipo | PF | Fundamento |
|---|---|---|---|
| Sala | ALI | 7 | |
| Reserva | ALI | 7 | sobrevive à exclusão da sala (declarado) |
| Incluir / Alterar / Excluir sala | EE ×3 | 12 | |
| Reservar sala | EE | 4 | |
| Cancelar reserva | EE | 4 | |
| Consultar salas livres | CE | 4 | |
| Agenda da sala no dia | CE | 4 | exportação PDF é a mesma função (C2) |
| Painel de taxa de ocupação | SE | 5 | cálculo |

- **Total aceito:** 47.
- **Proibidas:** exportação PDF como função separada; menu; mensagem de confirmação como função; "recursos disponíveis" como ALI.

---

## Casos de argumentos

| # | Invocação | Esperado |
|---|---|---|
| A01 | `modo=estimada saida=md -- <pedido>` | executa |
| A02 | `modo=estimativa -- <pedido>` | executa como `estimada` (sinônimo) |
| A03 | `saida=excel -- <pedido>` | executa como `xlsx` (sinônimo) |
| A04 | `<pedido>` sem argumentos | executa com os padrões e pergunta o formato depois de imprimir |
| A05 | `modo=detalhada -- <pedido>` | estágio 1: valor desconhecido |
| A06 | `modo indicativa -- <pedido>` | estágio 1: chave sem `=` |
| A07 | `modo=estimada modo=indicativa -- <pedido>` | estágio 1: valores conflitantes |
| A08 | `modo=indicativa tipo=melhoria -- <pedido>` | estágio 1: combinação não suportada |
| A09 | `saida=pdf -- <pedido>` | estágio 1: valor desconhecido |
| A10 | `formato=md -- <pedido>` | estágio 1: chave desconhecida |
| A11 | `modo=indicativa <pedido>` (sem `--`) | estágio 1: argumentos sem delimitador |
| A12 | `-- ./nao-existe.pdf` | estágio 2: arquivo não encontrado |
| A13a | `melhoria=nesma tipo=desenvolvimento -- <pedido>` | estágio 1: regime de melhoria em desenvolvimento |
| A13b | `melhoria=nesma -- <pedido de sistema novo>` | estágio 2: `tipo` inferido como desenvolvimento, incompatível com `melhoria=` |
| A14 | `<pedido contendo "modo=indicativa" no meio>` | executa; o texto não é argumento |
| A15 | `-- tipo=SEI é o nome do campo que ...` | executa; `--` faz o primeiro token ser lido como texto |

## Pares metamórficos

| # | Transformação | Esperado |
|---|---|---|
| M01 | G01 parafraseado (mesmo conteúdo, outras palavras e outra ordem) | mesmas funções, tipos e total |
| M02 | G01 com a frase sobre turmas repetida | nenhuma função duplicada |
| M03 | G01 com `saida=md` e com `saida=txt` | valores idênticos |
| M04 | G06 sem as frases sobre o menu e a mensagem de confirmação | mesmo total |
| M05 | G02 e G03a (mesmo pedido, regimes diferentes) | mesmo inventário de funções existentes; os conjuntos contabilizados diferem só pela inclusão de Cancelar no EFPA; mudam fator e unidade |
