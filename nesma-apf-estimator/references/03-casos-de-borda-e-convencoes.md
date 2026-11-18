# 03 · Casos de borda e convenções

Regras práticas para situações que aparecem em quase todo pedido. O SISP 3.0 entra aqui como **referência técnica subsidiária**, sem as fórmulas contratuais dele (fator de impacto de 63/84%, manutenção cosmética de 0,39 PF, deflatores). O TRE/SE não é órgão do SISP e esta skill não serve para contratação.

## 1. Convenção de evidência (C1)

[convenção da skill]

- **Evidência:** a função é sustentada por um trecho do pedido (cite o trecho em `requisito`).
- **Hipótese:** a função é **implicada** por uma palavra ou frase do pedido, sem ser afirmada (ex.: "gerenciar" pode implicar incluir, alterar, cancelar e consultar). Conte-a ligada a uma hipótese (`hipotese: "H1"`), com o trecho que a implica. O script calcula o efeito no total e os cenários.
- **Pendência:** a função **não** é mencionada nem implicada, mas costuma existir em sistemas parecidos (ex.: lista de seleção, relatório de auditoria, notificação por e-mail). **Não conte** e não crie hipótese; se for relevante para a viabilidade, registre em `pendencias`.
- Não conte funções por analogia com "o que todo sistema tem". Estimativa conservadora **não** é subcontar: tudo o que o pedido implica entra como hipótese com efeito visível, e não é descartado.
- **Cada cenário precisa ser uma aplicação possível.** Um ALI exige algum processo que o mantenha e um AIE exige algum processo que o leia. Quando arquivo e transações dependem de hipóteses diferentes, ligue-as com `requer` (05 §1) ou ponha o arquivo e a transação mínima na mesma hipótese (exemplo 3 de 04). Quando duas interpretações se excluem ("mantido aqui" ou "lido de outro sistema"), use um grupo.
- **Origem não afirmada** (SKILL.md, etapa 2): se o pedido nomeia um grupo de dados sem dizer quem o mantém, as duas origens entram como alternativas do mesmo grupo, cada uma com a transação mínima compatível, e a origem vai também para as pendências. Não fixe uma delas como evidência nem deixe as duas só na pendência: a pendência de confirmação não tira a hipótese dos cenários.
- **Verbo amplo** ("gerenciar", "manter", "acompanhar", "controlar") sem as operações discriminadas: cada operação implicada é hipótese, e o alcance do verbo vai para as pendências ("quais operações '<verbo>' abrange"). Se o pedido lista as operações, elas são evidência e não há o que perguntar.
- **Registros submetidos a uma unidade** [convenção da skill]: quando o pedido trata de registros que alguém apresenta, solicita ou submete a uma unidade (solicitações, requerimentos, atestados, pedidos) e não diz se há análise ou decisão sobre eles (conferir, aprovar, deferir, homologar), registre a pendência "há análise ou decisão sobre <os registros>, e por quem?". Não presuma o fluxo e não conte PF por ele (C1). Se o pedido descreve o fluxo, não pergunte se ele existe; perguntas sobre detalhes dele (prazos, recurso, notificação) continuam possíveis.

## 2. Mesma consulta em várias mídias e formatos (C2)

[convenção adotada com apoio no SISP §8.1]

- A mesma consulta em tela e em PDF, DOC, XLS ou papel, com **os mesmos dados e a mesma lógica**, é **uma função** (*single instance*). "Exportar a lista em PDF/CSV" não cria função nova [SISP §8.1, cenários 1, 2 e 6].
- São funções distintas quando a lógica ou os dados diferem: relatório impresso com totais que a tela não tem; entrada em lote (arquivo) com validações próprias além da entrada on-line [SISP §8.1, cenário 4]; a mesma funcionalidade desenvolvida duas vezes para canais diferentes (web e app nativo, interface e web service) [SISP §8.1, cenários 5 e 7].
- Na dúvida, conte uma função e registre a alternativa como hipótese, se o pedido sugerir lógica diferente.

## 3. CRUD e cadastros

[convenção da skill, com base em 01 §3]

| Pedido diz | Conte |
|---|---|
| "cadastrar X" sem detalhar | EE de inclusão (evidência); alterar, excluir e consultar só como hipóteses, se o texto as implicar ("manter", "gerenciar", "atualizar") |
| "incluir, alterar e excluir X" | 3 EE |
| "consultar X" ou "visualizar X" | 1 CE (detalhe de um registro e lista com filtros só são duas funções se o pedido as distinguir e tiverem lógica diferente) |
| "listar X com totais" ou "com quantidade por…" | SE |
| "cancelar X" que grava a situação | EE (é exclusão lógica ou alteração; conte uma só) |
| cadastro mestre-detalhe numa única tela, gravado de uma vez | uma EE por operação sobre o conjunto (o detalhe não gera EE própria) |
| detalhe mantido separadamente ("incluir turma num curso existente") | EE próprias para o detalhe |

Nunca conte funções para manter dados de código (UF, status, tipos fixos) [normativa: SISP §8.4.1].

## 4. Autenticação, perfis e controle de acesso

Não há regra normativa nas fontes desta skill para login. As regras abaixo são convenções e devem aparecer como tal na justificativa ou nas premissas.

Separe a **infraestrutura externa** das **funcionalidades requisitadas na aplicação**:

- **Infraestrutura externa** [adaptação institucional: TRE/SE]: login, logout e recuperação de senha feitos inteiramente pela autenticação institucional existente (SSO ou AD), sem nenhum requisito do pedido sobre como a aplicação usa a identidade. Não conte; registre em `nao_contados` como `fora-do-escopo` ("autenticação pela infraestrutura institucional existente").
- **Funcionalidade requisitada na aplicação**: tudo o que o pedido pede que a aplicação **faça** com a identidade ou o acesso conta pelas regras normais de 01, mesmo que a autenticação em si seja externa. Exemplos: vincular a conta do AD a um cadastro da aplicação, escolher o perfil ativo, consultar os próprios acessos, carregar dados do usuário autenticado para preencher um registro (o grupo lido pode ser AIE).
- **Usuários e perfis mantidos pela própria aplicação** (cadastro de usuários, atribuição de perfis ou permissões, mantidos pelo gestor do sistema): são dados de negócio. Identifique os arquivos pelas regras de agrupamento de 01 §2 (não há número fixo de ALIs: usuário, perfil e permissão podem ser um ou mais arquivos, conforme o pedido) e conte as transações pedidas.
- **Controle de acesso** que só restringe o que cada perfil vê ou faz: é regra das funções existentes, não função nova [convenção da skill].
- Se o pedido não diz como será a autenticação, registre pendência; não crie hipótese com PF.
- **Registro vinculado a uma pessoa** [convenção da skill]: quando o pedido liga registros ou operações a uma pessoa ("minhas solicitações", "a própria reserva", documentos apresentados por alguém) e o subsídio não diz como essa pessoa é identificada nos dados de negócio nem de onde vêm os dados necessários a esse vínculo, registre a pendência explicitamente: "como <a pessoa> é identificada e de onde vêm os dados dela". Uma pendência genérica sobre integrações não basta. Não presuma cadastro, atributos nem integração, e não acrescente PF sem evidência ou hipótese sustentada pelo texto. Se o pedido já informa a origem (ex.: "os dados dos servidores vêm do RH"), não pergunte. Isso é identificação funcional, diferente da autenticação institucional.

## 5. Log, trilha de auditoria e histórico

[normativa: SISP §8.2]

- **Log técnico** (registro de ações da aplicação para diagnóstico de falhas e desempenho): não conta.
- **Trilha de auditoria** (quem fez o quê e quando, sobre dados de negócio): só conta se **solicitada pelo usuário** e se houver **funcionalidade específica de consulta** a esses dados (a consulta conta como CE ou SE). Se for política corporativa aplicada a todos os sistemas, é requisito não funcional e não conta.
- **Histórico** de estados de um registro: a consulta ao histórico, se pedida, conta como transação; não se contam EE separadas para gravar o histórico. O histórico é parte do ALI principal, salvo se mantido independentemente (ver 01 §2).

## 6. Integrações (APIs REST/SOAP, mensageria, arquivos, batch)

[convenção da skill, aplicando as definições de 01 §2 e §4]

Sempre pela ótica da fronteira da aplicação medida:

| Situação | Conte |
|---|---|
| A aplicação **lê** dados mantidos por outra (consulta a API, view, serviço) para usar num processo dela | AIE para o grupo lógico lido (uma vez por grupo, não por chamada), se for grupo reconhecido pelo usuário e ALI da outra aplicação |
| A aplicação **recebe** dados de outra e os **grava** num ALI próprio (importação, fila, arquivo, carga periódica) | EE de recebimento; o grupo gravado é ALI da medida; a origem não vira AIE |
| A aplicação **fornece** dados para outra (expõe API, gera arquivo, publica mensagem) | CE, ou SE se houver cálculo ou dado derivado, ou se a função também grava |
| A aplicação **envia** dados para outra gravar (chama serviço que inclui/atualiza no outro sistema) | SE ou CE pela saída de dados (a gravação acontece fora da fronteira) |
| A mesma funcionalidade oferecida pela interface **e** por API, desenvolvida duas vezes | duas funções (SISP §8.1, cenário 7); se a interface só consome a própria API, uma |
| Integração descrita só como "integrar com o sistema X", sem dizer o que entra ou sai | pendência; se o texto implicar uma direção, hipótese |

Middleware, filas e protocolos não são funções; o que conta é o dado que entra ou sai e o grupo lógico mantido ou lido.

## 7. Itens não contados

Use `nao_contados` com uma destas categorias:

| Categoria | Exemplos | Fonte |
|---|---|---|
| `absorvido` | mensagens de erro, confirmação e validação; validação de máscara e formato; abas e etapas de um mesmo processo; gravação de histórico | SISP §5.1, §8.2.3, §8.3 |
| `dado-de-codigo` | UF, status, tipos fixos, listas de valores válidos e suas telas de manutenção | SISP §8.4.1 |
| `fora-do-escopo` | menus e telas só de navegação; refatoração técnica sem mudança funcional; desempenho, segurança, usabilidade; log técnico; autenticação feita inteiramente pela infraestrutura institucional (§4) | SISP §5.1, §8.2.1; convenção para autenticação |
| `sem-evidencia` | funções esperadas mas não mencionadas nem implicadas (ver C1); cada item aponta as pendências que cobrem todos os assuntos dele (campo `pendencias`, 05 §1) | convenção C1 |

`sem-evidencia` é lacuna de requisito: o pedido não diz se a função existe. O que o pedido **exclui expressamente** (ex.: "as datas não são exibidas nem gravadas") não é lacuna e não gera pergunta: se o dado é usado dentro de outra função, é `absorvido`; senão, não registre.

Em projeto de **melhoria**, alteração só cosmética (rótulo, cor, layout, texto de mensagem, título de relatório):

- no regime `nesma`, **é** contada, com fator 0,25 [normativa: EFPA §3.5.1, exemplo 9];
- no regime `sem-fatores`, **não** é contada, porque não muda dados, arquivos nem lógica da transação (convenção C4, 02 §4.1). Registre em `nao_contados` como `fora-do-escopo`, com a justificativa "alteração cosmética; no regime nesma valeria 0,25 × peso".

Um pedido composto só de mudanças cosméticas dá, portanto, zero no `sem-fatores`. Inclua em `avisos` a frase "pedido só cosmético: no regime nesma valeria 0,25 × peso por transação alterada; considere `melhoria=nesma` se esse tamanho importar para a viabilidade". O script acrescenta sozinho o aviso de que zero PF não significa ausência de trabalho.

## 8. Requisitos não funcionais e o que fica fora da APF

[normativa: SISP §8.4.1, princípio geral do CPM]

Desempenho, disponibilidade, segurança, acessibilidade, responsividade, migração de tecnologia sem mudança funcional, atualização de versão de framework e refatoração não são tamanho funcional. Registre-os como `fora-do-escopo` quando o pedido os mencionar, porque pesam na análise de viabilidade mesmo sem PF.

## 9. Cobertura desta skill

Coberto: desenvolvimento e melhoria de sistemas transacionais administrativos e judiciais, com cadastros, consultas, relatórios, painéis simples, integrações e cargas.

Não coberto (registre a limitação nas premissas e não improvise regra): Data Warehouse e Data Lake (ETL, cubos), inteligência artificial e chatbots, geoprocessamento, aplicativos multiplataforma com contagem por plataforma, manutenção corretiva, apuração especial, páginas estáticas de portal. O SISP 3.0 tem capítulos próprios para alguns desses casos, mas esta skill não os incorporou. Quando o pedido cair nessas áreas, conte apenas a parte transacional que as regras de 01 cobrem e declare o restante como fora da cobertura.

## 10. Roteiro do ciclo do processo (lacunas e perguntas)

[convenção da skill]

Antes de fechar as pendências, nos dois modos, percorra as etapas do processo que o pedido descreve ou implica. Em cada etapa, pergunte-se: o pedido responde? Se sim, não há o que registrar. Se não, e a resposta pode mudar a contagem, registre uma pendência (sem PF, C1). No modo interativo, essa pendência ganha `pergunta` (SKILL.md, 2A).

| Etapa | O que verificar |
|---|---|
| a. Entrada | como o registro nasce e quem o apresenta; quem mantém os dados (§1, origem não afirmada; §4, registro vinculado a uma pessoa) |
| b. Dados de terceiros | pessoas, unidades e outros sistemas que o processo lê ou alimenta (§4, §6) |
| c. Análise ou decisão | se alguém confere, aprova, defere ou homologa o registro, e quem (§1, registros submetidos) |
| d. Depois da decisão ou da conclusão | o que acontece em seguida com o registro, quando houver: por exemplo, execução, efeitos financeiros, comprovação ou prestação de contas, arquivamento, recurso, cancelamento |
| e. Cálculos e valores | valores, prazos ou indicadores que o sistema calcula, e não só exibe |
| f. Consultas e relatórios | consultas, relatórios ou painéis além dos que o pedido cita |
| g. Avisos e prazos | avisos ou ações disparados por data ou prazo, sem comando do usuário (01 §4) |
| h. Dados existentes | carga inicial ou migração de dados de outro sistema ou planilha (01 §6) |

Regras:

- **Só as etapas ligadas ao processo descrito.** Uma etapa que não tem relação com o pedido é ignorada, sem pergunta. Os exemplos da etapa d são possibilidades a considerar, não uma lista a perguntar em todo pedido.
- **"Muda a contagem"** quer dizer: muda a identificação ou a classificação de uma função (inclusive CE × SE), a operação em melhoria, o fator EFPA, os cenários ou a cobertura. Não pergunte detalhe que a contagem estimada não usa (campos, telas, layout, regras de validação), salvo TDs e ARs quando o regime `nesma` precisar deles.
- **Pergunta aberta quando não há base para uma específica.** Se uma etapa relevante não tem nenhum indício no pedido, prefira uma pergunta aberta sobre ela ("o que acontece com a solicitação depois de aprovada?") a uma lista de possibilidades. Pergunte de forma específica quando o pedido sugerir a possibilidade.
- **Não pergunte o que o pedido responde.** Se o pedido descreve a etapa, não pergunte se ela existe; perguntas sobre um detalhe dela que mude a contagem continuam possíveis.
- **O roteiro não cria função nem hipótese.** Ele só gera pendências e perguntas. Hipótese continua exigindo um trecho do pedido que a implique (§1).
