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
- Cenário mínimo e máximo **coerentes**: nenhum cenário pode ter arquivo sem transação que o mantenha ou leia (o script rejeita). Referência de cálculo: com origem em grupo, registro dentro da alternativa "mantidas aqui", consulta exigida pela alternativa "lidas de outro sistema", alterar/cancelar exigindo "mantidas aqui" e o AIE de servidor ligado à função que o lê (o registro, que exige "mantidas aqui"), o mínimo é 9 e o máximo é 28. Todo AIE precisa estar ligado a uma transação que o lê (revisão 4, após a calibração do juiz).
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

## G07 · Origem não afirmada, fora dos exemplos (holdout, rubrica)

Argumentos: `tipo=desenvolvimento`

> A Seção de Assistência à Saúde precisa controlar os atestados médicos apresentados pelos servidores.

Caso de transferência do G04 (consulta 10 ao popper), aprovado pelo usuário em 17/11/2026. Não tem exemplo correspondente em `references/`. Avaliado por rubrica, sem total fixo:

- **Origem dos atestados** como alternativas excludentes: mantidos por este sistema (ALI, com ao menos a transação que os registra) ou lidos de outro sistema (AIE, com ao menos uma transação que os lê). Nenhuma das duas como evidência isolada, e nenhuma só como pendência.
- Registrar, alterar, excluir e consultar só são aceitos como hipótese explícita, ligada a "controlar" ou a outra parte do texto (C1), com o efeito em PF. O AIE de servidor é opcional; se entrar, é hipótese ligada a uma transação que o lê.
- Cenário mínimo e máximo **coerentes**, com mínimo acima de zero. Referência de cálculo (não é exigência numérica): 9 a 23 PF, ou 28 com o AIE de servidor.
- Cobertura parcial.
- **Proibidas** (como funções ou como hipóteses com PF): homologação ou perícia; lançamento do afastamento na frequência ou na folha; cálculo de dias de afastamento; notificações.
- **Pendências obrigatórias:** quais operações "controlar" abrange; onde os atestados são registrados (origem); homologação ou perícia; origem dos dados do servidor.

## G08 · Origem e fluxo afirmados (holdout com contrastes, rubrica)

Argumentos: `tipo=desenvolvimento`

> A Seção de Protocolo precisa registrar os requerimentos que os servidores entregam no balcão. Cada requerimento é analisado pela chefia da seção, que registra no sistema a decisão: deferido ou indeferido.

Caso de transferência das D33, D36 e D37 (consulta 12 ao popper), escrito antes de qualquer execução. Não tem exemplo correspondente em `references/`. Testa também quando a skill **não** deve perguntar. Avaliado por rubrica, sem total fixo:

- **Requerimento** é ALI por evidência: "registrar" afirma que a aplicação o mantém. Grupo de alternativas de origem (ALI × AIE) para o requerimento reprova S1.
- **Registrar requerimento** é EE por evidência. **Registrar a decisão** é uma EE por evidência: deferido e indeferido são valores do mesmo processo (mesma lógica, mesmos dados), não duas funções.
- Consultar requerimentos é aceito como hipótese ligada a "analisado", e a ausência também é aceita. O AIE de servidor é opcional; se entrar, é hipótese ligada a uma transação que o lê.
- Cenário mínimo e máximo coerentes. Cobertura completa ou parcial.
- **Proibidas** (como funções ou como hipóteses com PF): edição genérica dos dados do requerimento ou exclusão dele, como funções adicionais (03 §3: "registrar" não as implica; o registro da decisão, que muda a situação do requerimento, **não** é essa edição); notificação ao servidor; recurso; consulta do servidor à situação do próprio requerimento.
- **Pendências obrigatórias:** como o servidor é identificado e de onde vêm os dados dele.
- **Pendências proibidas (contraste):** perguntar **se existe** análise ou decisão (o pedido a descreve); perguntar quem mantém os requerimentos ou de onde vêm (a origem está afirmada). Perguntas sobre detalhes do fluxo (prazos, recurso, notificação, critérios) são aceitas.

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

---

## Holdouts da iteração 2 (camada 1)

Redigidos por um agente `general-intern` com contexto limpo, depois do congelamento da variante (D46, commit `451690d`): ele leu só 01, 02 e 03 §1–§9 das referências. Segunda versão revisada (consultas 21 e 22 ao popper) e aprovada pelo usuário em 17/11/2026, com três ajustes: duas decomposições aceitas para o envio da convocação (H2, H2c); separações de arquivos e máximos de H3/H3c não obrigatórios; E2 e E3 exigidas como pendência com pergunta na camada 1. Contrato do S4 versão 2 (D43): as pendências obrigatórias valem sobre **todas** as pendências do JSON da prévia, não só as do primeiro lote; as de diagnóstico são relatadas e não reprovam; as proibidas (contrastes) reprovam. Os cenários são referências de cálculo, não exigência numérica. Invocação: `tipo=desenvolvimento`, com o padrão `interativo=sim`; a execução termina na prévia.

**H4** (D70): redigido em 18/11/2026 por um `general-intern` de contexto limpo, com só o pacote da D46/D70 (01, 02, 03 §1–§9, convenções C1–C4, critérios do juiz da prévia, contrato do S4 v2, teste de admissibilidade, modelo vazio); duas devoluções (consultas 49 e 50) e aprovado pelo usuário sem ajustes (consulta 51). Mede transferência de um padrão de lacuna próximo ao E3 do H3 (registro intermediário de resultados parciais), não descoberta de etapas em geral; a obrigatória é a pergunta, não a função.

## H1 · Manifestações à Ouvidoria (holdout, pouco subsídio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria. A equipe quer gerenciar esses registros, e o cidadão precisa consultar as suas manifestações.

**Informação ausente:** quais operações a equipe espera de “gerenciar”; como identificar o cidadão e obter os dados necessários para vincular suas manifestações; se há análise ou decisão sobre o que foi encaminhado e quem a realiza.

**Regras gerais acionadas:**
- Verbo amplo: “A equipe quer gerenciar esses registros”, sem operações discriminadas.
- Vínculo com pessoa: “o cidadão precisa consultar as suas manifestações”, sem identificador ou origem dos dados.
- Submissão a uma unidade: “manifestações enviadas pelos cidadãos à Ouvidoria”, sem tratamento descrito.
- Origem não afirmada: não se aplica às manifestações, cujo registro na aplicação é solicitado. “Cidadãos” não autoriza inventar um cadastro de pessoas para então oferecer ALI × AIE.

**O que o texto já responde:** há registro das manifestações na aplicação, seu destino é a Ouvidoria e o cidadão consultará as suas. Não há justificativa para perguntar se essas três coisas existem.

**Funções:**
- Obrigatórias (evidência):
  - Manifestações — **ALI**; “registrar no sistema as manifestações”.
  - Registrar manifestação — **EE**; “registrar no sistema”.
  - Consultar as próprias manifestações — **CE**; “o cidadão precisa consultar as suas manifestações”, sem processamento além da recuperação indicado.
- Aceitas como hipótese:
  - Corrigir manifestação — **EE**; “gerenciar”.
  - Cancelar manifestação — **EE**; “gerenciar”; não somar cancelamento e exclusão lógica da mesma operação.
  - Consultar manifestações pela equipe — **CE**; “A equipe quer gerenciar”. Só é adicional se houver uma distinção funcional fundamentada em relação à consulta individual, não apenas outro perfil de acesso.
  - São hipóteses opcionais de operações sobre o ALI obrigatório. Não há grupo de alternativas de origem. Interpretações que apenas renomeiem a mesma operação não são somáveis.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - Analisar, distribuir, deferir, responder ou encerrar atendimento — o verbo genérico não basta para presumir esse fluxo específico; sua existência fica como pendência.
  - ALI de cidadãos ou AIE de cadastro eleitoral, de pessoas ou de identidade — solução para o vínculo ainda não descrita.
  - Avisos, anexos, painel estatístico e migração — não mencionados nem implicados.
  - Arquivo próprio de status fixos, confirmação do registro e navegação — dados de código ou partes de funções, não funções adicionais.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo: registro e consulta individual — **1 ALI × 7 + 1 EE × 4 + 1 CE × 4 = 15 PF**.
- Máximo sem consulta adicional da equipe: incluir correção e cancelamento — **1 ALI × 7 + 3 EE × 4 + 1 CE × 4 = 23 PF**.
- Máximo com consulta funcionalmente distinta da equipe: **1 ALI × 7 + 3 EE × 4 + 2 CE × 4 = 27 PF**.
- Em todos, a EE de registro mantém Manifestações e as consultas leem esse ALI. Não acrescentar cadastro pessoal ou fluxo de resposta para completar o cenário.

**Cobertura:** **parcial**. A faixa cobre operações implicadas por “gerenciar”, não um tratamento ou uma identificação funcional que ainda não foram especificados.

**Pendências obrigatórias (reprovam se ausentes):**
- Quais operações “gerenciar” abrange para a equipe?
- Como o cidadão é identificado e de onde vêm os dados usados para vinculá-lo às suas manifestações?
- Há análise ou decisão sobre as manifestações encaminhadas à Ouvidoria? Por quem?
- **Descoberta de etapas além das quatro regras: nenhuma passou no teste.** A recepção não permite exigir, sem ampliar o pedido, distribuição, resposta, recursos ou prazos. As três perguntas acima decorrem das regras gerais, não demonstram por si só descoberta de etapas do domínio.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Se haverá distribuição, resposta, prazos, anexos ou avisos.
- Como será a autenticação, sem substituir a pergunta sobre identificação funcional.
- Por ser pouco subsidiado, as possibilidades de ciclo ficam aqui e não geram PF.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: se haverá registro no sistema, se o destino é a Ouvidoria ou se o cidadão consultará suas manifestações.
- Não reabrir a origem das manifestações como ALI × AIE.
- Identificação, alcance de “gerenciar” e existência de análise são obrigatórios aqui, mas estarão respondidos em H1c.

**Notas para o juiz:** aceitar máximos de 23 ou 27 PF conforme a fundamentação da consulta pela equipe. Exigir hipóteses com efeito visível nos cenários, não CRUD tratado como evidência. “Quais integrações?” ou “Terá usuários?” não substituem a pergunta explícita sobre identificação do cidadão. Não reprovar por ausência de perguntas sobre etapas sem âncora textual. Este par mede as regras gerais, não o objetivo adicional de descoberta de etapas.

## H1c · Identificação e resposta definidas (contraste de H1, pouco subsídio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria, com nome e CPF informados pelo próprio cidadão para identificar quais manifestações são dele na consulta. A equipe da Ouvidoria poderá corrigir o texto e cancelar registros feitos por engano, além de analisar o conteúdo e registrar a resposta final ao cidadão.

**Informação ausente:** nenhuma das três lacunas obrigatórias de H1 permanece. Avisos, anexos e requisitos de autenticação continuam não descritos, mas não são funcionalidades presumidas.

**Regras gerais acionadas:**
- Identificação respondida por nome e CPF informados pelo próprio cidadão.
- Tratamento respondido pela análise da equipe da Ouvidoria e registro da resposta final.
- O verbo amplo foi substituído por operações concretas.
- A origem das manifestações continua local; os dados pessoais são informados no registro, sem requisito de um grupo independente de pessoas.

**O que o texto já responde:** fonte dos dados de identificação, vínculo das manifestações ao cidadão, correção, cancelamento e análise com resposta pela equipe da Ouvidoria.

**Funções:**
- Obrigatórias (evidência):
  - Manifestações — **ALI**; “registrar no sistema as manifestações”, incluindo identificação e resposta.
  - Registrar manifestação — **EE**; “registrar no sistema”.
  - Consultar as próprias manifestações — **CE**; “identificar quais manifestações são dele na consulta”.
  - Corrigir texto — **EE**; “poderá corrigir o texto”.
  - Cancelar manifestação — **EE**; “cancelar registros feitos por engano”.
  - Registrar resposta final — **EE**; “registrar a resposta final ao cidadão”. A análise humana não é outra transação.
- Aceitas como hipótese:
  - Nenhuma adicional necessária. O texto não pede consulta autônoma da equipe com lógica diferente.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - Cadastro de cidadãos ou leitura de cadastro externo — não decorrem de nome e CPF informados na própria manifestação.
  - EE separada de análise, aprovação ou encerramento — não foram pedidas operações autônomas para isso.
  - SE de envio de resposta por e-mail — registrar uma resposta não pede uma notificação independente.
  - Consulta adicional apenas por haver outro perfil; avisos, anexos, painéis e migração — sem suporte.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo = máximo de referência: **1 ALI × 7 + 4 EE × 4 + 1 CE × 4 = 27 PF**.
- Registro, correção, cancelamento e resposta mantêm Manifestações; a CE lê esse ALI. Não há arquivo de pessoas a alimentar.

**Cobertura:** **completa para o escopo expresso**, não para todos os serviços possíveis de uma Ouvidoria.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das lacunas obrigatórias de H1 permanece. Nenhuma lacuna adicional de etapa foi identificada com âncora suficiente.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Segurança e autenticação da consulta; possíveis avisos ou anexos.
- Eventual consulta autônoma da equipe, sem PF enquanto não sustentada.
- Não confundir identificação funcional respondida com suficiência dos mecanismos de segurança.

**Pendências ou perguntas proibidas (contrastes):**
- Como identificar o cidadão ou de onde vêm nome e CPF.
- Quais operações “gerenciar” abrange.
- Se há análise, quem a faz ou se a equipe registra resposta.
- Se as manifestações serão registradas no sistema ou consultadas pelo cidadão.

**Notas para o juiz:** o contraste é mais informativo, embora mantenha “pouco subsídio” como rótulo do par. Não é necessário que ele preserve o total máximo do holdout: a resposta passa de possibilidade não contável a função expressa. Aqui o resultado também é 27 PF, por composição diferente do máximo de H1 com consulta da equipe. Perguntas proibidas reprovam mesmo se registradas fora do primeiro lote.

## H2 · Nomeações e entrega das convocações (holdout, médio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.

**Informação ausente:** quem mantém os locais de votação; o que a área chama de problema de entrega e como essa informação chega ao sistema após o envio. Não há pedido de dispensa, aprovação de nomeação ou tratamento disciplinar de faltas.

**Regras gerais acionadas:**
- Origem não afirmada: “relação de locais de votação, com nome e endereço” não informa o mantenedor.
- Identificação pessoal: respondida por inscrição e nome consultados no cadastro eleitoral.
- Verbo amplo: as operações de preparar nomeações e enviar convocações são detalhadas; não é necessário perguntar genericamente o significado de “preparar”.
- Submissão a uma unidade: não se aplica. O cartório cria nomeações; não há pedido apresentado por mesário.
- A entrada do resultado da entrega é uma lacuna de etapa adicional, não mera repetição da regra sobre origem de um grupo de dados.

**O que o texto já responde:** registro das nomeações, origem da identificação dos mesários, consulta dos locais, envio por e-mail, data de envio na nomeação, relação de problemas de entrega, registro de presença/ausência e lista de ausentes. “Providenciar outro contato” não exige, por si só, um módulo de telefonia ou outro canal de envio.

**Funções:**
- Obrigatórias (evidência):
  - Nomeações — **ALI**; “registrar cada nomeação”, com data de envio e situação de presença.
  - Eleitores — **AIE**; “inscrição e o nome [...] consultados no cadastro eleitoral, que é mantido no sistema eleitoral”. Lido ao registrar a nomeação.
  - Registrar nomeação — **EE**; “O cartório vai registrar cada nomeação”.
  - Consultar locais — **CE**; “consultar a relação de locais de votação, com nome e endereço”. **Decomposição alternativa aceita** (decisão do usuário após a `curta-4`, só para rodadas futuras): a consulta tratada como parte do registro da nomeação, porque serve à escolha do local nesse registro (01 §3), com fundamentação. Nesse caso não há a CE (−4 PF em todas as referências de cálculo), e o arquivo de locais (AIE ou ALI) é lido pelo registro da nomeação.
  - Enviar convocação — o envio é **evidência** (“enviar as convocações por e-mail”; “a data de envio [...] fique na nomeação”); a **autonomia** dele não está decidida pelo texto. Aceitar, com fundamentação, uma de duas decomposições coerentes, sem contar o envio duas vezes: **(a)** **SE** autônoma (por evidência ou hipótese), que envia e grava a data na nomeação; **(b)** envio absorvido na EE Registrar nomeação, como consequência dela (01 §4). Se a autonomia ficar como hipótese, os efeitos dela precisam aparecer coerentemente nos cenários.
  - Consultar convocações com problema de entrega — **CE**; “uma relação das convocações com problema de entrega”, sem indicadores pedidos.
  - Registrar comparecimento ou ausência — **EE**; “registrará o comparecimento ou a ausência na nomeação”. É uma operação com resultados alternativos.
  - Listar ausentes por local — **CE**; “lista dos mesários marcados como ausentes, por local”. Recupera a ausência registrada, sem inferi-la.
- Aceitas como hipótese:
  - Grupo **L — origem dos locais**, exatamente uma alternativa:
    - **L-externa:** Locais — **AIE**, lido pela CE de consulta dos locais.
    - **L-local:** Locais — **ALI** e uma **EE** mínima para alimentá-lo. Arquivo e mantenedora integram a mesma alternativa.
    - Âncora de ambas: “relação de locais de votação”, sem origem. Não presumir simultaneamente cadastro manual e importação.
  - Grupo **R — resultado da entrega**, alternativas excludentes quanto ao retorno posterior:
    - **R-no-envio:** os problemas são erros conhecidos e guardados durante o envio; sem transação adicional. A função que envia (a SE autônoma, na decomposição a, ou a EE de registro, na b) mantém esse resultado.
    - **R-posterior:** receber e registrar resultados posteriores do serviço de comunicação — uma **EE**, mantendo a situação na nomeação.
    - Âncora: “convocações com problema de entrega”. Não é evidência de integração de retorno, mas sustenta a hipótese com efeito em PF.
  - Se a interpretação fundamentada for registro manual de retorno posterior, aceitar **EE** em lugar da EE de recebimento automático. Não contar ambas sem requisito.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI e AIE de locais simultâneos — origens alternativas.
  - ALI de eleitores ou EE de importação — o pedido descreve consulta externa.
  - AIE do serviço de comunicação só por receber avisos — receber dados e gravá-los em Nomeações não caracteriza leitura de arquivo externo.
  - CE de eleitor apenas para preencher nomeação, EE separada de data de envio ou de erro imediato — leituras e gravações absorvidas pelas funções existentes.
  - Uma EE para presença e outra para ausência; SE de estatísticas só por agrupar por local — não decorrem do texto.
  - Sistema de telefonia, envio por outro canal, dispensa, treinamento, aprovação ou punição por falta — não pedidos.
  - CRUD completo de nomeações ou locais — sem verbo amplo ou enumeração que o sustente.

**Cenários (referência de cálculo, não exigência numérica):**
- Base comum: **1 ALI × 7 + 1 AIE × 5 + 2 EE × 4 + 3 CE × 4 + 1 SE × 5 = 37 PF**.
- Mínimo, L-externa + R-no-envio: base + **1 AIE × 5 = 42 PF**.
- Intermediário, L-externa + R-posterior: base + **1 AIE × 5 + 1 EE × 4 = 46 PF**.
- Máximo, L-local + R-posterior: base + **1 ALI × 7 + 2 EE × 4 = 52 PF**. As duas EE adicionais são alimentação dos locais e retorno da entrega.
- Nomeações é mantido por registro, envio, presença e, quando aplicável, retorno. A situação de falha é gravada na função que envia ou na EE posterior; a CE de problemas não lê um dado sem origem. Eleitores é lido no registro, e Locais é lido pela consulta, com mantenedora no cenário local.
- **Consulta dos locais absorvida no registro** (decomposição alternativa da CE): subtrair 4 PF de qualquer referência acima; combina com (a) ou (b).
- **Decomposição (b), envio absorvido no registro:** base **1 ALI × 7 + 1 AIE × 5 + 2 EE × 4 + 3 CE × 4 = 32 PF**; mínimo **37 PF**, intermediário **41 PF**, máximo **47 PF**. As duas faixas (42–52 e 37–47) são aceitas conforme a decomposição fundamentada.

**Cobertura:** **completa para as interpretações delimitadas nos cenários**, com origem e alcance do retorno ainda abertos. Também aceitar cobertura parcial se a skill explicar que ainda não consegue delimitar os resultados de entrega envolvidos; não aceitar “parcial” como desculpa para omitir funções já expressas ou as alternativas.

**Pendências obrigatórias (reprovam se ausentes):**
- **Regra geral:** quem mantém os locais de votação: a nova aplicação ou outra fonte consultada?
- **Etapa E2 — resultado da entrega:** o que entra na relação de problemas e como o sistema fica sabendo desses problemas? São apenas erros identificados no envio ou também resultados posteriores que precisam ser registrados?
  - **Âncora textual:** “uma relação das convocações com problema de entrega”. Para produzir essa relação, o resultado precisa chegar a Nomeações por algum processo.
  - **Duas respostas plausíveis e consequências:**
    - “Queremos só os e-mails rejeitados na hora do envio; os demais casos continuam fora desse controle.” O resultado é parte da SE de envio já contada; **nenhuma função adicional**.
    - “O serviço de comunicação mandará depois as devoluções e confirmações, e queremos atualizar a situação na nomeação.” Acrescenta **uma EE de recebimento/registro de resultado, 4 PF**; não cria AIE automaticamente.
  - **Por que é necessário delimitar este pedido:** a relação de problemas foi solicitada, mas sua informação de entrada não foi explicada. A pergunta define como uma saída já pedida pode funcionar e se existe processamento posterior ao envio; não oferece um serviço alheio ao escopo.
  - A pergunta só sobre “integrações” não basta. É necessário identificar o retorno da entrega e seu registro; não é obrigatório mencionar tecnologia de callback, API ou protocolo.
  - **Na camada 1 (prévia):** E2 precisa estar em `pendencias` **com `pergunta`**, em qualquer situação e mesmo fora do primeiro lote. Mencioná-la só numa justificativa ou em `nao_contados` não basta. Avaliar pelo significado: uma pergunta aberta que identifique a lacuna basta, sem reproduzir as duas respostas do teste.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autenticação, correção ou cancelamento de nomeações e eventual substituição de mesários.
- Como o cartório executa o outro contato fora do que foi solicitado; não presumir nova função de comunicação.
- Dispensa, treinamento e consequências das ausências pertencem ao domínio, mas não ao escopo apresentado.
- O detalhamento dos resultados do envio pode ser solicitado sem exigir todos os estados possíveis para a estimativa.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: como identificar o mesário ou de onde vêm inscrição e nome.
- Se há envio por e-mail, registro da data, relação de problemas ou registro de presença.
- Se a ausência é calculada a partir de presença não registrada: o texto manda marcar ausências.
- Se há pedidos de dispensa a decidir, como se estivessem mencionados.
- Origem dos locais e mecanismo do resultado da entrega são perguntas necessárias aqui, mas respondidas em H2c.

**Notas para o juiz:** E2 é o objetivo adicional de descoberta de etapa. A primeira resposta do teste restringe “problema de entrega” aos erros observáveis no envio; a segunda inclui um evento posterior. Não transformar essa distinção em dois canais de saída: a função adicional é de entrada. A consulta dos problemas é obrigatória em ambos os cenários. Uma resposta com EE posterior só como pendência, sem hipótese de efeito em PF, perde a distinção implicada pelo texto. Não exigir fases do ciclo eleitoral que o pedido não abrange.

## H2c · Resultado da entrega recebido do serviço (contraste de H2, médio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço, mantida no sistema de locais da Justiça Eleitoral. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega, e essas respostas devem atualizar a situação da convocação na nomeação. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.

**Informação ausente:** nenhuma das duas lacunas obrigatórias de H2 permanece. Tecnologias e detalhes operacionais das fontes não são necessários para reabrir a classificação funcional já respondida.

**Regras gerais acionadas:**
- Origem dos locais: respondida por mantenedor externo.
- Identificação do mesário: continua respondida por inscrição e cadastro eleitoral.
- Verbo amplo e submissão a uma unidade: continuam não exigindo perguntas genéricas.
- A etapa E2 foi explicada por retorno posterior do serviço de comunicação, com atualização da nomeação.

**O que o texto já responde:** tudo o que H2 respondia, mais origem dos locais e entrada das devoluções/confirmações após o envio.

**Funções:**
- Obrigatórias (evidência):
  - Nomeações — **ALI**; “registrar cada nomeação”, com situação da convocação e presença.
  - Eleitores — **AIE**; “consultados no cadastro eleitoral, que é mantido no sistema eleitoral”.
  - Locais — **AIE**; “relação de locais [...] mantida no sistema de locais da Justiça Eleitoral”.
  - Registrar nomeação — **EE**; “O cartório vai registrar cada nomeação”.
  - Consultar locais — **CE**; “o servidor precisa consultar a relação de locais”. Mesma decomposição alternativa aceita em H2: consulta como parte do registro da nomeação, com fundamentação (−4 PF; o AIE de locais é lido pelo registro).
  - Enviar convocação — mesmas duas decomposições aceitas em H2: **(a)** **SE** autônoma ou **(b)** envio absorvido na EE Registrar nomeação, sem contar duas vezes.
  - Receber e registrar resultado da entrega — **EE**; “O serviço de comunicação avisará o sistema [...] e essas respostas devem atualizar a situação”.
  - Consultar convocações com problema — **CE**; “uma relação das convocações com problema de entrega”.
  - Registrar comparecimento ou ausência — **EE**; “registrará o comparecimento ou a ausência na nomeação”.
  - Listar ausentes por local — **CE**; “lista dos mesários marcados como ausentes, por local”.
- Aceitas como hipótese:
  - Nenhuma necessária para os cenários de referência. Os grupos L e R foram resolvidos.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI local de locais e sua alimentação — o pedido esclareceu a consulta à relação mantida externamente.
  - AIE de serviço de comunicação ou ALI separado de comprovantes de entrega apenas porque existem mensagens — o requisito é receber informação e atualizar Nomeações.
  - Duas EE só por haver confirmação e devolução — são resultados alternativos do mesmo processo de recebimento, salvo lógica adicional não descrita.
  - Importação de eleitores, CE autônoma de eleitor para preencher nomeação, gravação de data contada outra vez, presença/ausência duplicadas — mesmos motivos de H2.
  - Funções de outro contato, dispensa, treinamento, substituição e punição — sem requisito.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo = máximo: **1 ALI × 7 + 2 AIE × 5 + 3 EE × 4 + 3 CE × 4 + 1 SE × 5 = 46 PF** na decomposição (a); **41 PF** na (b), com o envio absorvido no registro. Com a consulta dos locais absorvida no registro, 4 PF a menos (42 ou 37).
- Registro, presença e resultado da entrega mantêm Nomeações; o envio também grava nesse ALI. Eleitores é lido no registro e Locais na consulta. O recebimento de mensagens não deixa um AIE fictício sem leitura.

**Cobertura:** **completa para o escopo expresso**. As duas alternativas do holdout agora têm respostas funcionais.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das lacunas obrigatórias de H2 permanece; não pedir de novo o mecanismo de entrada dos resultados.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autenticação e eventual tratamento operacional de mensagens inválidas ou repetidas.
- O outro contato providenciado pelo cartório, sem transformar isso em módulo adicional.
- Outros processos eleitorais continuam fora do pedido apresentado.

**Pendências ou perguntas proibidas (contrastes):**
- Quem mantém os locais ou se é preciso cadastrar a relação na nova aplicação.
- Como o mesário é identificado ou de onde vêm seus dados.
- Se haverá resultados posteriores ao envio, quem os fornece ou se eles atualizam a nomeação.
- Se a relação trata somente de erros imediatos: o retorno posterior está expresso.
- Se há registro da data de envio, de comparecimento/ausência ou lista de problemas.
- Pode haver pergunta técnica sobre o serviço, mas não usá-la para reabrir a existência ou a direção do fluxo já descrito.

**Notas para o juiz:** contraste mais informativo, com o nível “médio” mantido pelo par. Ele responde à origem e à etapa E2 sem acrescentar substituição, dispensa ou outros canais. Locais passa a AIE de evidência e a EE de retorno também passa a evidência; alternativas e perguntas correspondentes devem desaparecer. Não contar uma função para cada valor de resultado.

## H3 · Remessas, retorno e conferência de urnas (holdout, rico, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.
>
> Antes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber.
>
> Também queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas.
>
> A consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.
>
> O acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.

**Informação ausente:** identificação e fonte dos dados dos responsáveis; existência e autoria de análise/decisão sobre ocorrências; como a conferência é registrada em relação à chegada do material. O texto também não resolve totalmente a autonomia lógica dos registros de movimentação e ocorrência, de modo que não se deve impor um único agrupamento de arquivos.

**Regras gerais acionadas:**
- Vínculo pessoal: “identificar os responsáveis por entregar e receber”, sem identificador ou fonte.
- Submissão a uma unidade: ocorrência registrada e aviso à Seção de Logística, sem dizer se a seção analisa ou decide algo.
- Origem: remessas e registros operacionais são registrados na aplicação; urnas continuam no cadastro do sistema nacional. Não há origem em aberto para as urnas.
- Verbo amplo: “organizar” é desenvolvido nas operações seguintes. Não perguntar genericamente o que organizar remessas significa.
- A articulação entre chegada e conferência é uma lacuna de etapa adicional, não a pergunta geral sobre análise das ocorrências.

**O que o texto já responde:** criação, correção e cancelamento de remessas; registro de saída, entrega e retorno; possibilidade de retornos parciais; existência da conferência; ocorrências de transporte e aviso à seção ao registrá-las; consultas, ficha em PDF e quadro quantitativo. A fonte das urnas, a autenticação externa e as exclusões técnicas estão expressas.

**Funções:**
- Obrigatórias (evidência):
  - Remessas — **ALI**; “vai registrar cada remessa com a data prevista, a zona de destino e as urnas”.
  - Urnas — **AIE**; “números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro”. É lido, pelo menos, no registro das urnas da remessa.
  - Registrar remessa — **EE**; “vai registrar cada remessa”.
  - Corrigir remessa — **EE**; “pode corrigir a data ou a relação de urnas”. São atributos da mesma operação, não duas funções.
  - Cancelar remessa — **EE**; “cancelar uma remessa que não será mais realizada”.
  - Registrar saída — **EE**; “registrar a saída efetiva, com a data e as urnas que saíram”.
  - Registrar entrega — **EE**; “depois a entrega à zona, com a data e as urnas recebidas”.
  - Registrar retorno — **EE**; “No retorno ao depósito, serão registradas a data e as urnas que chegaram”.
  - Registrar ocorrência — **EE**; “Também queremos registrar ocorrências de transporte”, inclusive fatos no trajeto, não apenas na conferência.
  - Consultar ocorrências — **CE**; “consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas”.
  - Consultar ficha da remessa — **CE**; “A consulta da remessa deve reunir seus dados e os registros [...] imprimir essa ficha em PDF”.
  - Quadro por zona — **SE**; “quantidades [...] além do saldo que ainda está fora do depósito”. Exige agregação e cálculo.
- Aceitas como hipótese:
  - Grupo **C — registro da conferência**, exatamente uma alternativa:
    - **C-na-chegada:** conferência concluída ao registrar o retorno; não há transação adicional.
    - **C-posterior:** confirmar e registrar a conferência após a chegada — **EE** adicional, mantendo o retorno/remessa.
    - Âncora: “A devolução só deve ser considerada concluída depois da conferência do material”, sem dizer se chegada e conferência geram registros em momentos diferentes.
  - **Agrupamento dos dados internos:** o modelo de referência mais agregado tem um ALI Remessas com itens, movimentações e ocorrências. A consulta reunida não prova, porém, que todos tenham o mesmo ciclo de vida.
    - **G-movimentações:** um ALI Movimentações separado, **+7 PF**, se saída, entrega e retorno forem interpretados como registros de negócio mantidos e conservados com autonomia, não simples histórico da remessa. Âncora: os registros próprios de saída, entrega e devolução.
    - **G-ocorrências:** um ALI Ocorrências separado, **+7 PF**, se a ocorrência for interpretada como objeto acompanhado pela seção com autonomia em relação à remessa. Âncora: registro de ocorrências de transporte e consulta própria pela seção.
    - Cada dimensão é uma escolha excludente entre subgrupo e arquivo separado; as duas separações podem coexistir. São hipóteses de agrupamento, não evidência de três arquivos. Se a leitura for de simples histórico, ele fica no ALI principal.
    - As EE já obrigatórias mantêm os arquivos correspondentes quando separados; não surgem novas EE só por mudar o agrupamento.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI local de urnas e manutenção do cadastro nacional — o mantenedor externo está indicado.
  - Cadastro de responsáveis ou AIE de pessoal — solução da identificação ainda não descrita.
  - Analisar, aprovar ou concluir ocorrência — o aviso à seção não especifica tratamento.
  - Função autônoma de aviso só porque há comunicação à seção — “Ao registrar” descreve consequência do registro.
  - CE adicional de PDF — “imprimir essa ficha” é outra mídia da consulta, sem outro conteúdo ou lógica implicados.
  - Uma EE por retorno parcial ou por urna; arquivos por tabela física ou por status — repetição, detalhe ou implementação não criam funções.
  - Somar simultaneamente o arquivo e um segundo arquivo que apenas duplica o mesmo grupo lógico.
  - (Decisão do usuário após a `curta-4`, só para rodadas futuras: separar ALI **como certeza**, sem hipótese de autonomia, não é função proibida e não reprova o K3; reprova o **S3**, por omitir a incerteza de agrupamento.)
  - Gestão local de usuários, software de urna, carga de software, votação e apuração — exclusões expressas.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo, agrupamento agregado + C-na-chegada: **1 ALI × 7 + 1 AIE × 5 + 7 EE × 4 + 2 CE × 4 + 1 SE × 5 = 53 PF**.
- Conferência posterior, sem separar arquivos: **1 ALI × 7 + 1 AIE × 5 + 8 EE × 4 + 2 CE × 4 + 1 SE × 5 = 57 PF**.
- Uma separação de arquivo acrescenta **7 PF**; duas acrescentam **14 PF**. Máximo de referência, dois arquivos separados + C-posterior: **3 ALI × 7 + 1 AIE × 5 + 8 EE × 4 + 2 CE × 4 + 1 SE × 5 = 71 PF**.
- No modelo agregado, as sete ou oito EE mantêm Remessas. No separado, registrar/corrigir/cancelar mantém Remessas; saída/entrega/retorno e eventual conferência mantêm Movimentações; registro de ocorrência mantém Ocorrências. AIE Urnas é lido na validação. As consultas e o quadro leem os grupos necessários.
- Esses extremos não incluem identificação ou tratamento de ocorrências ainda não descritos. Não são limite superior de uma solução futura.
- **As separações G-movimentações e G-ocorrências e o máximo de 71 PF não são obrigatórios.** Um agrupamento agregado coerente aprova; cobra-se só o efeito das hipóteses que o executor de fato adotar.

**Cobertura:** **parcial**. A conferência e os agrupamentos têm alternativas contabilizadas, mas a fonte da identificação pessoal e o possível tratamento das ocorrências ainda podem introduzir funções sem base suficiente para contá-las.

**Pendências obrigatórias (reprovam se ausentes):**
- **Regra geral:** como são identificados os responsáveis por entregar e receber e de onde vêm os dados deles? Não basta perguntar pelo login do operador.
- **Regra geral:** há análise ou decisão sobre as ocorrências comunicadas à Seção de Logística e quem a realiza?
- **Etapa E3 — conferência do retorno:** o registro de chegada já inclui a conferência ou o material é recebido primeiro e a conferência precisa ser registrada depois? O que marca a devolução como conferida?
  - **Âncora textual:** “No retorno [...] serão registradas a data e as urnas que chegaram” e “A devolução só deve ser considerada concluída depois da conferência do material”.
  - **Duas respostas plausíveis e consequências:**
    - “Quem recebe confere na hora e só registra o retorno depois de conferir.” A EE de retorno já cobre o resultado da conferência; **nenhuma função adicional**.
    - “Anotamos a chegada assim que o material entra, mas outra pessoa confere mais tarde e registra que terminou.” Acrescenta **uma EE de confirmação/registro da conferência, 4 PF**. O número de ALI não muda apenas por isso.
  - **Por que é necessário delimitar este pedido:** a conclusão da devolução foi condicionada à conferência, enquanto o registro de chegada também foi solicitado. É preciso saber se são uma ou duas atividades completas da aplicação para atender ao controle pedido, especialmente com retornos parciais; não se está propondo uma nova fase do transporte.
  - Não perguntar apenas “há conferência?”: sua existência já está afirmada. É necessário distinguir o registro da chegada do registro do resultado da conferência.
  - **Na camada 1 (prévia):** E3 precisa estar em `pendencias` **com `pergunta`**, em qualquer situação e mesmo fora do primeiro lote. Mencioná-la só numa justificativa ou em `nao_contados` não basta. Avaliar pelo significado: uma pergunta aberta que identifique a lacuna basta.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autonomia de movimentações e ocorrências: são partes da ficha da remessa ou registros com acompanhamento e conservação próprios? A incerteza deve aparecer nas hipóteses se alterar o agrupamento, mas esta pergunta não é usada como pendência reprovadora de etapa.
- Eventuais anexos, cobrança de atrasos e correção de movimentações já registradas.
- Preparação física anterior e planejamento detalhado de rotas pertencem ao domínio, mas não são etapas exigidas deste pedido.
- Não inventar dúvidas sobre votação ou software de urna para avaliar a parte administrativa.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: quem mantém o cadastro de urnas; se haverá devolução parcial, conferência, ocorrências, consulta pela seção, PDF ou quadro quantitativo.
- Perguntar se existe conferência não substitui E3 e reabre informação respondida.
- Quais operações “organizar” abrange, de forma genérica, ignorando as operações descritas.
- Se haverá gestão local de usuários ou se o pedido inclui software de urna, votação ou apuração.
- A fonte dos responsáveis, a existência de análise e a forma de registrar a conferência ficam respondidas em H3c; a autonomia dos arquivos não.

**Notas para o juiz:** E3 mede descoberta da relação entre duas etapas, além das regras gerais. A conferência física existe, mas isso não prova uma EE autônoma; a hipótese deve depender de quando e como seu resultado é registrado. Aceitar agrupamentos fundamentados, sem impor um “dossiê” único nem premiar ALI por tabela. Os modelos de um a três ALI são referências de interpretações, não licença para qualquer separação: exigir explicação de autonomia, ligação ao texto e mantenedora. Se a leitura for de histórico de estados, aplicar sua inclusão no arquivo principal. Total menor com agrupamento coerente não é subcontagem automática.

## H3c · Conferência posterior e tratamento definidos (contraste de H3, rico, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.
>
> Antes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. A chegada é anotada assim que as urnas entram no depósito; outro servidor confere o material mais tarde e registra que aquele retorno foi conferido. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber. Esses responsáveis são servidores do Tribunal: usaremos a matrícula e o nome que vêm do cadastro de servidores do sistema de pessoal.
>
> Também queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas. A equipe da seção analisa cada ocorrência e registra sua conclusão para dar o caso por encerrado.
>
> A consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.
>
> O acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.

**Informação ausente:** nenhuma das três lacunas obrigatórias de H3 permanece. A autonomia lógica de movimentações e ocorrências continua não totalmente explicitada; o contraste não a resolveu por precisão artificial.

**Regras gerais acionadas:**
- Identificação respondida por matrícula/nome do cadastro de servidores do sistema de pessoal.
- Análise e responsável respondidos pela equipe da seção, que registra a conclusão.
- Origem das urnas continua respondida; as operações continuam detalhando “organizar”.
- E3 é respondida pela anotação da chegada seguida de conferência posterior por outro servidor, com resultado registrado.

**O que o texto já responde:** tudo o que H3 respondia, mais identificação funcional dos responsáveis, fonte de pessoal, tratamento das ocorrências e autonomia temporal e funcional do registro da conferência.

**Funções:**
- Obrigatórias (evidência):
  - Remessas — **ALI**; “vai registrar cada remessa com a data prevista, a zona de destino e as urnas”.
  - Urnas — **AIE**; “relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro”.
  - Servidores — **AIE**; “matrícula e o nome que vêm do cadastro de servidores do sistema de pessoal”. Leitura para identificar responsáveis nas movimentações.
  - Registrar remessa — **EE**; “vai registrar cada remessa”.
  - Corrigir remessa — **EE**; “pode corrigir a data ou a relação de urnas”.
  - Cancelar remessa — **EE**; “cancelar uma remessa que não será mais realizada”.
  - Registrar saída — **EE**; “registrar a saída efetiva”.
  - Registrar entrega — **EE**; “depois a entrega à zona”.
  - Registrar retorno — **EE**; “No retorno [...] serão registradas a data e as urnas que chegaram” e “A chegada é anotada assim que as urnas entram”.
  - Registrar conferência do retorno — **EE**; “outro servidor confere o material mais tarde e registra que aquele retorno foi conferido”. É atividade completa posterior, não outra tela suposta.
  - Registrar ocorrência — **EE**; “Também queremos registrar ocorrências de transporte”.
  - Registrar conclusão da ocorrência — **EE**; “A equipe da seção analisa cada ocorrência e registra sua conclusão para dar o caso por encerrado”.
  - Consultar ocorrências — **CE**; “consultar uma lista das ocorrências recebidas”.
  - Consultar ficha da remessa — **CE**; “A consulta da remessa deve reunir seus dados e os registros [...] imprimir essa ficha em PDF”.
  - Quadro por zona — **SE**; “quantidades [...] além do saldo que ainda está fora do depósito”.
- Aceitas como hipótese:
  - Permanecem as escolhas **G-movimentações** e **G-ocorrências** de H3: subgrupos de Remessas ou arquivos separados, **+7 PF** por separação fundamentada em autonomia lógica.
  - Conferência mantém o grupo onde estiver o retorno; conclusão mantém o grupo onde estiver a ocorrência. Não acrescentar EE apenas por separar esses grupos.
  - A hipótese C-posterior deixa de ser hipótese: o registro posterior da conferência agora é evidência. Não conservar C-na-chegada nos cenários.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI de servidores ou cadastro local para resolver a identificação — a fonte informada é o cadastro do sistema de pessoal; nenhuma manutenção local foi pedida.
  - CE autônoma de servidores apenas por preencher responsáveis — leitura absorvida pelas EE que usam a identidade.
  - EE extra de análise humana ou outra de encerramento além da conclusão — “registra sua conclusão para dar o caso por encerrado” descreve uma atividade de negócio, não três transações.
  - SE autônoma de aviso à seção, CE extra de PDF, EE por retorno parcial, arquivo por status — mesmos motivos de H3.
  - ALI de urnas, gestão local de usuários e funções de votação/apuração — fonte externa ou exclusão expressa.
  - (Decisão do usuário após a `curta-4`, só para rodadas futuras: arquivos adicionais apresentados como certeza só porque foram citados registros diferentes não reprovam o K3; reprovam o **S3**, porque o agrupamento ainda exige hipótese fundamentada.)

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo, modelo agregado: **1 ALI × 7 + 2 AIE × 5 + 9 EE × 4 + 2 CE × 4 + 1 SE × 5 = 66 PF**.
- Uma separação de arquivo: **73 PF**; duas separações: **3 ALI × 7 + 2 AIE × 5 + 9 EE × 4 + 2 CE × 4 + 1 SE × 5 = 80 PF**.
- As nove EE são remessa, correção, cancelamento, saída, entrega, retorno, conferência, ocorrência e conclusão. Em relação ao mínimo identificável de H3, há **+5 PF** de Servidores, **+4 PF** de conferência posterior e **+4 PF** de conclusão.
- No modelo separado, Remessas é mantido por registro/correção/cancelamento; Movimentações por saída/entrega/retorno/conferência; Ocorrências por registro/conclusão. Nos modelos agregados, as mesmas EE mantêm os respectivos subgrupos. Urnas e Servidores são lidos nas validações e identificações solicitadas.
- Trata-se de desenvolvimento: não contar novamente saída, entrega e retorno só porque agora a fonte de identificação foi esclarecida.
- **As separações de arquivos e o máximo de 80 PF não são obrigatórios.** Um agrupamento agregado coerente (66 PF) aprova; cobra-se só o efeito das hipóteses que o executor de fato adotar.

**Cobertura:** **completa para o escopo administrativo expresso, com incerteza de agrupamento contabilizada**. Aceitar cobertura parcial se acompanhada de justificativa específica sobre autonomia dos registros ainda não resolvida; não alegar ausência de identificação, conferência ou tratamento.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das três de H3 permanece. As respostas sobre fonte dos responsáveis, tratamento e registro posterior da conferência estão no pedido.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autonomia e conservação de movimentações e ocorrências, para confirmar as alternativas de agrupamento ainda abertas.
- Anexos, cobrança de atraso e correção posterior de movimentações, sem PF por mera plausibilidade.
- Detalhes técnicos das consultas externas não reabrem origem ou existência das fontes.

**Pendências ou perguntas proibidas (contrastes):**
- Como identificar os responsáveis ou de onde vêm matrícula e nome.
- Se há análise das ocorrências, quem a faz ou se a conclusão é registrada.
- Se chegada e conferência são anotadas juntas ou se há registro posterior da conferência: o texto responde que são etapas registradas em momentos distintos.
- Se haverá conferência, devolução parcial, PDF, quadro quantitativo ou gestão local de usuários.
- Quem mantém o cadastro de urnas; se o pedido abrange votação, apuração ou software da urna.
- A pergunta sobre autonomia dos arquivos continua permitida, pois não foi respondida no contraste.

**Notas para o juiz:** contraste mais informativo, com o nível “rico” do par. As inserções respondem somente às lacunas obrigatórias de H3; não fixam o agrupamento dos arquivos. A conferência passa a EE de evidência pela separação entre chegada registrada e resultado posterior registrado, não por ser feita por outro perfil. A conclusão é EE, não SE só por conter um resultado. A origem pessoal é funcional e não deve ser confundida com autenticação. Perguntas proibidas reprovam mesmo em listas secundárias; dúvidas residuais de agrupamento não reprovam.

## H4 · Eliminação de documentos em papel (holdout, médio, rubrica)

Argumentos: `tipo=desenvolvimento`

> A Seção de Arquivo precisa de um sistema para registrar os lotes de documentos administrativos em papel do TRE que vão passar por avaliação, com o número do lote, os anos dos documentos e a quantidade de caixas. A Comissão de Avaliação examina os lotes e registra no sistema sua decisão para cada um, indicando se está liberado para eliminação ou retido. Só os lotes liberados seguem para fragmentação, que é feita fora do sistema e pode ocorrer em remessas em dias diferentes. A cada remessa, a equipe de fragmentação entrega ao Arquivo um comprovante em papel com o número do lote, a data e a quantidade de caixas fragmentadas, para a conferência daquele lote. Os servidores do Arquivo conferem os comprovantes à medida que chegam, e a chefia registra no sistema a data de conclusão quando a conferência comprova que todas as caixas do lote foram eliminadas. Enquanto o lote ainda está aberto, o Arquivo usa a quantidade de caixas fragmentadas na última remessa conferida para ajustar quantas caixas separa para a próxima retirada. A Seção consulta no sistema uma lista que mostra apenas o número de cada lote, a decisão da Comissão e, quando já registrada, a data de conclusão. O pessoal do Arquivo e da Comissão usa o login institucional do TRE, sem cadastro de usuários nesse sistema.

**Informação ausente:** o Arquivo usa resultados parciais para preparar novas retiradas enquanto o lote está aberto. O pedido não diz se algum desses resultados é registrado no novo sistema antes da baixa ou se esse acompanhamento fica fora dele e o único lançamento da execução ocorre na baixa. A resposta determina se o sistema precisa de uma operação para registrar resultados parciais, além da baixa.

**Regras gerais acionadas:**
- Origem e manutenção dos dados (03 §1 e §6): “um sistema para registrar os lotes” fixa onde os lotes são mantidos; “entrega ao Arquivo um comprovante em papel” fixa a origem das informações da fragmentação. Não há origem de grupo de dados a esclarecer. O ponto em aberto é se resultados parciais são registrados no sistema durante a execução, antes da baixa (E1).
- Registro submetido a uma unidade, com análise ou decisão (03 §1): “A Comissão de Avaliação examina os lotes e registra no sistema sua decisão para cada um”. O pedido já informa que há avaliação, quem decide, onde e quais são os resultados possíveis. Não há pendência pela regra geral.
- Verbo amplo (03 §1): não se aplica; o pedido discrimina o registro do lote, da decisão e da conclusão, além do conteúdo da consulta. “Examinar” e “conferir” descrevem ações do processo de trabalho, não pedidos genéricos de manutenção de dados.
- Registro vinculado a uma pessoa e autenticação (03 §4): Arquivo, Comissão e chefia identificam papéis no processo, não titulares dos lotes nem pessoas cujos dados precisam ser vinculados a eles. O pedido também já define o uso do login institucional, sem cadastro de usuários no sistema.

**O que o texto já responde:** o novo sistema registra os lotes, a decisão da Comissão e a data de conclusão lançada pela chefia. Só os liberados vão para fragmentação, que ocorre fora do sistema e pode ser fracionada em remessas. O Arquivo recebe e confere um comprovante em papel por remessa e, enquanto o lote está aberto, usa a quantidade comprovada na última remessa para ajustar quantas caixas separa para a próxima retirada. A conclusão pressupõe a eliminação comprovada de todas as caixas. A listagem só recupera os três dados especificados; o acesso usa o login institucional, sem cadastro local de usuários. Esses fatos podem ser contexto de uma pergunta, não aquilo que se pede confirmar. O local da fragmentação física e a origem em papel não resolvem se o acompanhamento dos resultados parciais inclui registros no sistema antes da baixa.

**Lacunas de etapa (teste de admissibilidade):**
- E1 (etapa-alvo) — Registro de resultados parciais enquanto o lote está aberto. Âncora: “Enquanto o lote ainda está aberto, o Arquivo usa a quantidade de caixas fragmentadas na última remessa conferida para ajustar quantas caixas separa para a próxima retirada.” A baixa não atende a esse uso: a informação já precisa estar disponível ao Arquivo para preparar a próxima retirada. É necessário esclarecer se o sistema participa desse acompanhamento ou se o trabalho é todo feito com os comprovantes até a baixa. Resposta A: o Arquivo usa os comprovantes em papel para ajustar a próxima retirada; nenhum resultado parcial é lançado no sistema e o único lançamento da execução ocorre na baixa, quando a chefia registra a conclusão → nenhuma EE adicional. Resposta B: o Arquivo registra no lote ainda aberto o resultado de pelo menos uma remessa conferida (data e quantidade de caixas), como parte do acompanhamento que orienta a próxima retirada; a chefia registra a conclusão depois → uma EE adicional, que mantém o mesmo ALI de lotes. Delimita: a pergunta esclarece onde se registra a informação já usada para preparar a próxima retirada; não propõe que o sistema dimensione, agende ou execute as retiradas. A pergunta conta como descoberta se esclarecer se há algum resultado parcial registrado no sistema enquanto o lote está aberto ou se o acompanhamento fica fora dele e o lançamento só ocorre na baixa. Não basta perguntar se a baixa é uma operação separada ou como se trata o último comprovante.

**Funções:**
- Obrigatórias (evidência):
  - Lotes de documentos para eliminação — **ALI**; “um sistema para registrar os lotes de documentos administrativos em papel do TRE”.
  - Registrar lote para avaliação — **EE**; “registrar os lotes de documentos administrativos em papel do TRE que vão passar por avaliação, com o número do lote, os anos dos documentos e a quantidade de caixas”.
  - Registrar decisão da Comissão sobre o lote — **EE**; “registra no sistema sua decisão para cada um, indicando se está liberado para eliminação ou retido”.
  - Registrar a conclusão da eliminação do lote (dar baixa) — **EE**; “a chefia registra no sistema a data de conclusão quando a conferência comprova que todas as caixas do lote foram eliminadas”.
  - Consultar a lista de lotes com decisão e data de conclusão — **CE**; “uma lista que mostra apenas o número de cada lote, a decisão da Comissão e, quando já registrada, a data de conclusão”.
- Aceitas como hipótese:
  - Registrar o resultado parcial da fragmentação do lote — **EE**; “usa a quantidade de caixas fragmentadas na última remessa conferida para ajustar quantas caixas separa para a próxima retirada”. Só na resposta B de E1, quando se lança ao menos um resultado de remessa conferida enquanto o lote está aberto. Mantém o ALI obrigatório e não substitui a baixa dada pela chefia. As respostas A e B são excludentes; A não acrescenta função.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI independente de remessas, comprovantes, decisões ou baixas — os comprovantes são para a conferência do lote identificado; não há ciclo de vida próprio descrito. Decisão, conclusão e eventual registro por remessa são dados do lote.
  - AIE ou integração com a equipe de fragmentação — os comprovantes são entregues em papel. Lançar seus dados, se for o caso, não é consultar nem importar de outra aplicação.
  - Fragmentar documentos, dimensionar ou agendar retiradas no sistema, ou gerir transporte — a execução física está fora do sistema; o uso do resultado pelo Arquivo não é um pedido para automatizar a preparação da próxima retirada.
  - EE distintas para liberar e para reter, ou para examinar e para decidir — os dois resultados pertencem ao mesmo registro da decisão por lote; o exame não tem outro registro solicitado.
  - Validar comprovantes como operação autônoma além do eventual lançamento, digitalizá-los, calcular e exibir saldo de caixas, emitir certificados ou avisos, ou consultar remessas em separado — não há pedido desses resultados no sistema. A conferência dos papéis é conhecida, mas não implica essas funções.
  - Alterar, excluir ou reabrir lotes, manter a lista de situações, cadastrar usuários ou implementar login local — não decorrem das operações descritas; as situações são valores da decisão e o acesso é institucional.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo (E1-A): 1 ALI (lotes) + 3 EE (registrar lote, decisão e conclusão) + 1 CE (lista) = 7 + 3 × 4 + 4 = **23 PF**.
- Máximo (E1-B): mesmas funções, mais 1 EE (registrar resultado parcial no lote aberto) = 23 + 4 = **27 PF**.
- Em ambos, o registro cria o lote, a decisão e a baixa o atualizam, e a lista o lê sem cálculo. Em B, o lançamento do resultado parcial também atualiza o lote: a mesma operação pode ser usada uma ou mais vezes, sem multiplicar a quantidade de funções. Não há AIE.

**Cobertura:** completa para o processo transacional descrito, com a incerteza de E1 representada nos cenários. A fragmentação física não é parte da aplicação.

**Pendências obrigatórias (reprovam se ausentes):**
- E1 — Perguntar se o Arquivo registra no novo sistema algum resultado parcial enquanto o lote está aberto ou se acompanha as remessas fora dele e só faz o lançamento da execução na baixa. Uma pergunta aberta sobre como ficam registrados, antes da baixa, os resultados parciais usados para preparar a próxima retirada também serve. Não é preciso perguntar por todas as remessas nem pelo último comprovante.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Nenhuma adicional. O pedido não dá âncora para investigar recurso contra retenção, reabertura de lote ou comunicação à equipe de fragmentação.

**Pendências ou perguntas proibidas (contrastes):**
- Perguntar se a Comissão avalia ou decide, quem decide, se a decisão é registrada no sistema ou quais dos dois resultados são possíveis.
- Perguntar se só lotes liberados seguem, se a fragmentação é feita pelo sistema, se pode haver mais de uma remessa, se o Arquivo recebe e confere os comprovantes ou se usa o resultado da última remessa antes da baixa para ajustar a próxima retirada. Perguntar se algum dos resultados parciais fica registrado no sistema enquanto o lote está aberto é E1, não uma repetição desses fatos.
- Perguntar de onde vêm os comprovantes ou se são recebidos por integração; perguntar se há registro da data de conclusão, por quem, ou em que ponto o lote é dado por concluído.
- Perguntar o que a lista exibe, se há totais nela, onde os lotes são mantidos ou se haverá login ou cadastro local de usuários.

**Notas para o juiz:** avalie por significado: “baixa”, por exemplo, só equivale a registrar a conclusão se se referir à eliminação de todas as caixas, não à retenção do lote nem a excluir o registro. Aceite E1-B como hipótese opcional sem grupo ou A/B como grupo excludente; em ambos, a baixa continua obrigatória. A distinção relevante é se existe ao menos um registro de resultado parcial anterior à baixa. Em B, o tratamento do último comprovante não altera S4 nem a contagem: ele pode ficar em papel, ser lançado pela mesma operação já usada para resultados parciais ou ser tratado na baixa. Não exija PF na prévia. Para S4, E1 precisa aparecer em `pendencias` com `pergunta`: mencionar a hipótese na lista de funções não basta. Este caso mede a descoberta do registro intermediário, não detalhes de comprovantes, telas ou autenticação.
