---
name: nesma-apf-estimator
description: Estima o tamanho funcional (Análise de Pontos de Função, contagem estimada ou indicativa da NESMA) de um pedido de desenvolvimento ou melhoria de sistema, para a análise de viabilidade de projetos de TI da equipe interna do TRE/SE. Use quando o usuário pedir estimativa de pontos de função, APF, PF, contagem NESMA ou tamanho funcional de um pedido, história de usuário ou documento de requisitos, anexado ou no prompt. Funciona offline e gera a saída em .md, .txt ou .xlsx.
---

# nesma-apf-estimator

Estimativa **preliminar** de tamanho funcional para análise de viabilidade. Não é medição nem contagem detalhada e não serve para contratação. Os subsídios são incompletos por natureza: a skill estima com o que há, deixa explícito o que assumiu e lista o que falta.

Funciona **offline**: todo o conhecimento necessário está em `references/`. Não pesquise na web nem use regra de contagem que não esteja nesses arquivos. Se o caso não estiver coberto, declare a limitação (03 §9) em vez de improvisar.

## 0. Antes de qualquer coisa

1. **Valide os argumentos** (seção 1). Se houver erro de estágio 1, emita o alerta e **pare**, sem ler o subsídio.
2. **Verifique o Python:** rode `python3 --version`; se falhar, `python --version`; no Windows, `py -3 --version`. É preciso Python 3.8 ou superior. Use nas etapas seguintes o primeiro comando que funcionar. Sem Python, emita o alerta abaixo e **pare**: não estime, não some, não exporte.
   > ALERTA: esta skill precisa de Python 3.8 ou superior para calcular a estimativa, e ele não foi encontrado nesta máquina. Nada foi calculado.
3. **Leia, nesta ordem e por inteiro,** `references/01-fundamentos-e-identificacao.md`, `02-regras-nesma.md`, `03-casos-de-borda-e-convencoes.md`, `04-exemplos-praticos.md` e `05-saida-e-legenda.md`. Não comece a contar antes.

## 1. Argumentos

A invocação é o texto que acompanha o acionamento da skill (por exemplo, depois de `/nesma-apf-estimator`).

**Gramática**

```
[chave=valor ...] -- <subsídio>
<subsídio>
```

- Argumentos vêm **no início**, no formato `chave=valor`, e terminam em `--`. Tudo depois de `--` é subsídio (texto do pedido ou caminho de arquivo) e **nunca** é lido como argumento, mesmo que contenha `chave=valor`.
- Sem argumentos, a invocação inteira é subsídio, desde que o primeiro token **não** tenha a forma `chave=valor`.
- Valores com espaço vão entre aspas: `saida="xlsx"` (os valores válidos não têm espaço; aspas só são removidas).
- Chaves e valores não diferenciam maiúsculas de minúsculas nem acentos.

| Chave | Valores | Padrão |
|---|---|---|
| `modo` | `estimada` \| `indicativa` | `estimada` |
| `tipo` | `desenvolvimento` \| `melhoria` | inferido do subsídio (seção 2, etapa 1) |
| `melhoria` | `sem-fatores` \| `nesma` (só em projeto de melhoria) | `sem-fatores` |
| `saida` | `md` \| `txt` \| `xlsx` | perguntar depois de imprimir o resultado |
| `interativo` | `sim` \| `nao` | `sim` (prévia e perguntas antes do cálculo, seção 2A) |

**Sinônimos** (lista fechada; nada fora dela é aceito):

| Valor canônico | Aceita também |
|---|---|
| `estimada` | `estimativa`, `estimated`, `high-level` |
| `indicativa` | `indicative`, `macro` |
| `desenvolvimento` | `dev`, `novo` |
| `melhoria` (valor de `tipo`) | `evolutiva`, `manutencao-evolutiva`, `enhancement` |
| `sem-fatores` | `sem-fator`, `soma-simples` |
| `nesma` (valor de `melhoria`) | `efpa` |
| `md` | `markdown` |
| `txt` | `texto`, `text` |
| `xlsx` | `excel`, `planilha` |
| `sim` (valor de `interativo`) | `s`, `true`, `1`, `on`, `yes`, `verdadeiro` |
| `nao` (valor de `interativo`) | `n`, `false`, `0`, `off`, `no`, `falso` |

**Validação em dois estágios**

*Estágio 1, sintático: antes de abrir o subsídio.* É erro:

- chave desconhecida (`formato=md`);
- valor fora da tabela e dos sinônimos (`modo=detalhada`, `saida=pdf`);
- token com cara de argumento sem `=` antes do `--` (`modo indicativa -- ...`);
- a mesma chave com valores diferentes (`modo=estimada modo=indicativa`);
- argumentos sem `--` antes do subsídio (`modo=indicativa Sistema para...`);
- combinação inválida explícita: `modo=indicativa` com `tipo=melhoria`; `melhoria=...` com `tipo=desenvolvimento`.

*Estágio 2, contextual: o subsídio pode ser lido, mas nada é contado nem exportado.* É erro:

- caminho de arquivo inexistente ou ilegível;
- `melhoria=...` informado, `tipo` não informado e o subsídio indica sistema novo (desenvolvimento);
- `modo=indicativa` informado, `tipo` não informado e o subsídio indica melhoria.

Em qualquer erro, responda **só** com o alerta e pare. Não execute a parte válida, não proponha contagem parcial e não corrija o argumento por conta própria:

```
ALERTA: argumentos inválidos. Nada foi executado.
- <problema 1>: <token ou trecho>
- <problema 2>: ...
Formato: [chave=valor ...] -- <subsídio>
Chaves: modo=estimada|indicativa · tipo=desenvolvimento|melhoria · melhoria=sem-fatores|nesma · saida=md|txt|xlsx · interativo=sim|nao
Exemplo: modo=estimada tipo=melhoria saida=xlsx -- ./pedido.pdf
```

**Pedidos em linguagem natural.** Se a skill foi acionada por uma mensagem em prosa, separe duas coisas:

- **Descrição do sistema** ("quero um novo sistema…", "no sistema X, já em produção…"): é subsídio. Serve para inferir o tipo e a fronteira (seção 2). Nunca gera confirmação.
- **Pedido explícito de configuração da estimativa**, dirigido a você e não ao sistema: formato de saída ("gere em planilha", "exporte em txt"), método ("faça a contagem indicativa"), regime de melhoria ("use os fatores da NESMA", "sem fatores") ou interação ("calcule direto, sem perguntas" = `interativo=nao`). Não aplique a configuração por conta própria: responda com a invocação equivalente na gramática e peça confirmação antes de executar. Exemplo: "Entendi `modo=indicativa saida=xlsx -- <pedido>`. Confirma?" Se a configuração pedida não existir na gramática (ex.: "em PDF", "contagem detalhada"), emita o alerta de argumentos inválidos.

Sem pedido explícito de configuração, trate a mensagem inteira como subsídio, com os padrões.

## 2. Fluxo de contagem

**Etapa 1: escopo, tipo e fronteira.** Leia o subsídio inteiro (arquivo ou texto). Determine:

- *tipo de projeto:* se `tipo` foi informado, use-o. Senão, é melhoria quando o subsídio diz que o sistema já existe ("já em produção", "no sistema X, incluir…", "alterar a funcionalidade…"), e desenvolvimento quando descreve um sistema ou módulo novo. Se não der para decidir, **pergunte** e pare até a resposta;
- *fronteira:* o que é a aplicação medida e quais sistemas são externos (01 §1). Se a fronteira não puder ser definida, **pergunte** e pare até a resposta.

**Etapa 2: funções de dados.** Identifique ALI e AIE (01 §2), descartando dados de código (01 §5) e registrando-os em `nao_contados`. Depois de decidir o agrupamento, verifique **quem mantém** cada grupo de dados de negócio, sem desfazer o que o pedido já afirma (01 §2, teste 3). O pedido afirma a manutenção local quando diz que a aplicação medida inclui, altera ou registra os dados, ou quando separa o que vem de outros sistemas do resto; afirma a leitura externa quando diz que outra aplicação mantém o grupo e a medida só o usa (receber e gravar num arquivo próprio é ALI com EE, não AIE: 03 §6). Se as duas leituras continuarem plausíveis (ex.: "minhas solicitações", "acompanhar os contratos"), não escolha uma e não deixe a questão só como pendência: ponha as duas como alternativas de um grupo de origem, cada uma com a transação mínima compatível (03 §1; exemplo 3 de 04), e registre também a pendência. Se o pedido liga os registros a uma pessoa sem dizer como ela é identificada nem de onde vêm os dados dela, registre essa pendência explicitamente (03 §4). No modo indicativo, esta é a última etapa de identificação, e as alternativas ficam só entre ALI e AIE.

**Etapa 3: funções transacionais.** Quebre o pedido em processos elementares únicos (01 §3) e classifique cada um em EE, SE ou CE pela intenção primária (01 §4). Aplique os casos de borda de 03 (CRUD, múltiplas mídias, autenticação, auditoria, integrações, itens não contados). Em melhoria, marque a operação (I/A/E). No regime `nesma`, determine o `efpa` de cada alterada (02 §4.2; faixa quando faltarem números). No `sem-fatores`, aplique a convenção C4 (02 §4.1).

**Etapa 3A: lacunas do ciclo do processo** (nos dois modos). Percorra o roteiro de 03 §10 e registre como pendência cada etapa ligada ao processo do pedido que ele não responde e cuja resposta pode mudar a contagem. O roteiro não cria função nem hipótese. Com `interativo=sim`, siga para a seção 2A antes da etapa 4; com `interativo=nao`, siga direto para a etapa 4.

**Etapa 4: cálculo.** Monte o JSON canônico (05 §1) num diretório temporário e rode `apf.py check`. Corrija até passar. Com `interativo=sim`, o JSON já foi montado na seção 2A, e esta etapa só acontece depois que o analista confirmar a prévia ou pedir para calcular. Os pesos, fatores, cenários e totais vêm **só** do script. Declare `cobertura: parcial` sempre que o subsídio não permitir identificar todas as funções afetadas (ex.: melhoria sem baseline, pedido vago), e ponha em `avisos` o que o resumo precisa dizer (ex.: pedido só cosmético no `sem-fatores`).

**Etapa 5: memória de cálculo e premissas.** Rode `apf.py render --format md`, sem `--out` (o script usa o perfil de chat, com a legenda só dos termos que aparecem no resultado), e **copie a saída inteira para a sua resposta**, exatamente como o script a imprimiu: resumo executivo, memória de cálculo, hipóteses e cenários, premissas, itens não contados, pendências e legenda. A saída de um comando não chega ao usuário por si só (fica recolhida no resultado da ferramenta); só o que está na sua mensagem é lido. Não resuma, não reescreva números nem palavras (nem para "corrigir" a concordância) e não diga "veja acima". Depois:

- se `saida` foi informado, exporte nesse formato (antes ou depois de mostrar a tabela; o que não pode faltar é a tabela na sua mensagem);
- senão, pergunte pelo canal (2B), com seleção múltipla: "Quer exportar? `.md`, `.txt`, `.xlsx` ou nenhum." As opções são `.md`, `.txt`, `.xlsx` e "Nenhum", que não se combina com as outras. Exporte cada formato escolhido, todos do mesmo JSON; com "Nenhum", não exporte;
- exporte com `apf.py render --format <fmt> --out <arquivo>` (nome e local: 05 §4) e informe o caminho. O script nunca sobrescreve: se sair com código 3, use o próximo sufixo `-2`, `-3`….

## 2A. Modo interativo (`interativo=sim`, padrão)

Quem responde é o analista de TI que faz a análise de viabilidade. Ele não precisa saber APF: escreva as perguntas em termos do negócio e, quando citar um tipo de função, ponha o termo APF entre parênteses ("os atestados ficam guardados neste sistema (ALI) ou são lidos de outro (AIE)?").

1. **Monte o JSON** das etapas 1 a 3A e dê `pergunta` (e, se ajudar, `opcoes`) só às pendências cuja resposta pode mudar a contagem (03 §10). Todas começam com `situacao: "aberta"`. Pendência sem efeito na contagem fica sem pergunta.
2. **Escolha o lote:** as próximas perguntas abertas, até 7, cada uma sobre um único assunto, na ordem do roteiro (fronteira e origem dos dados primeiro). Marque-as `perguntada` com o número do lote. Não invente perguntas para preencher o lote.
3. **Mostre a prévia e pergunte:** rode `apf.py check` e depois `apf.py render --format previa`, e copie a saída inteira para a sua resposta, sem reescrever (como na etapa 5). A prévia não tem PF: **não mostre números de pontos de função, totais nem cenários, e não exporte nada** antes de o analista confirmar ou pedir para calcular. Depois da prévia, faça as perguntas do lote pelo canal da seção 2B e só então espere a resposta.
4. **Registre as respostas:** para cada pergunta do lote, crie um esclarecimento (`E1`…) com a resposta e marque a pendência `resolvida`, ou `sem-resposta` se ele disse "não sei" ou não respondeu. Incorpore **só o que foi respondido**: "sim, há pagamento" sem dizer se este sistema o executa não cria função; gera uma pendência mais estreita. Uma resposta pode confirmar ou retirar hipóteses, criar funções (com `esclarecimentos: ["E1"]`) ou abrir perguntas novas. Correções do analista à lista também viram esclarecimentos. Rode `check` de novo: ele revalida grupos e `requer`.
5. **Próximo lote:** se ainda houver perguntas abertas e o analista não pediu para calcular, volte ao passo 2. Pergunta `sem-resposta` não é repetida, a menos que uma resposta nova a torne respondível (então crie outra pendência). Sem perguntas restantes, a prévia fecha pedindo confirmação da lista.
6. **Calcular:** quando o analista confirmar ou disser "calcular", marque as perguntas ainda `perguntada` como `sem-resposta` e siga as etapas 4 e 5. As abertas que nunca foram apresentadas continuam como pendências.

## 2B. Canal das perguntas

Vale para toda pergunta ao analista: tipo e fronteira (etapa 1), lotes da prévia (2A), exportação (etapa 5) e correção ambígua (2C). A mensagem segue sempre esta ordem:

1. **Texto primeiro:** o que o analista precisa ler para responder (a prévia ou o resultado, copiados), quando houver. Perguntas de tipo e fronteira vêm antes de qualquer prévia.
2. **Pergunta pelo canal:** se esta execução tiver uma ferramenta própria para perguntar ao usuário, use-a; se ela tiver limite de perguntas por chamada, divida o mesmo conjunto em chamadas seguidas, sem criar, juntar nem cortar perguntas. Use seleção múltipla quando mais de uma opção puder valer. Sem essa ferramenta, pergunte em texto, numerado (no lote, as perguntas numeradas da prévia já bastam).
3. **Espere a resposta.** Resposta livre, "não sei" e "calcular" valem nos dois canais.

## 2C. Correções depois do resultado

Depois do resultado, o analista pode corrigir ou completar qualquer item (função, hipótese, pendência, resposta dada antes).

1. **Registre a correção** como esclarecimento. Se ela responde ou muda a resposta de uma pendência (inclusive uma que ficou sem resposta), atualize o esclarecimento dessa pendência com a resposta nova, sem guardar a anterior (vale a última; o histórico de versões fica fora da skill), e marque a pendência `resolvida`. Se não corresponde a nenhuma pendência, crie um esclarecimento novo com `pendencia: null`.
2. **Refaça a identificação** dos itens afetados pelas etapas 1 a 3A, como numa resposta da prévia (2A, passo 4): funções, hipóteses, grupos, `requer`, itens não contados, pendências, fronteira e cobertura. Retire o que a correção desfaz. Se ela for ambígua a ponto de mudar a contagem de formas diferentes, pergunte (2B) antes de recalcular.
3. **Recalcule e mostre** pelas etapas 4 e 5: resultado inteiro de novo e exportação como na etapa 5 (com `saida` informado, exporte direto nesse formato; senão, pergunte de novo). Os arquivos anteriores não são sobrescritos.

## 3. Política de incerteza

- **Pergunte apenas** quando a lacuna impede definir o tipo de projeto ou a fronteira, e, com `interativo=sim`, nas perguntas da prévia (2A), limitadas ao que muda a contagem; depois do resultado, só diante de correção ambígua (2C). Para o resto, não pergunte: estime. O canal de toda pergunta está na seção 2B.
- Classifique cada função como **evidência** (afirmada no pedido), **hipótese** (implicada por uma palavra ou frase, com o trecho) ou **pendência** (nem afirmada nem implicada: não conta). Veja a convenção C1 em 03 §1.
- Uma hipótese com efeito em PF entra nos cenários mesmo quando também gera pendência de confirmação: a pendência não substitui a hipótese.
- Verbo amplo ("gerenciar", "manter", "acompanhar", "controlar") sem as operações discriminadas: além das hipóteses que ele implica, registre a pendência "quais operações '<verbo>' abrange". Se o pedido lista as operações, não pergunte.
- Registros que alguém apresenta ou solicita a uma unidade, sem dizer se há análise ou decisão sobre eles: registre essa pendência, sem presumir o fluxo e sem PF (03 §1). Se o pedido descreve o fluxo, não pergunte se ele existe.
- As demais etapas do processo que o pedido não cobre vêm do roteiro de 03 §10 (etapa 3A), só quando ligadas ao processo descrito e quando a resposta muda a contagem.
- Toda hipótese que muda o total entra ligada às funções correspondentes. O script calcula o cenário mínimo e o máximo. Alternativas excludentes ("ALI **ou** AIE") vão num grupo, e hipóteses que só fazem sentido juntas são ligadas com `requer`, para que cada cenário seja uma aplicação possível (03 §1). Não apresente valor central nem "total provável".
- Cobertura parcial (funções que o subsídio não permite identificar) é diferente de faixa de fator (fatores EFPA desconhecidos). Declare as duas quando houver.
- "Conservador" não significa subcontar: nada implicado pelo pedido é descartado em silêncio.
- Não invente percentuais de confiança. A única medida de incerteza é a diferença entre os cenários e a lista de pendências.
- Premissas que não mudam o total (ex.: autenticação institucional) vão em `premissas`.

## 4. Proibições

- Calcular PF, fatores ou totais fora do script, ou alterar os números que ele imprime.
- Com `interativo=sim`, mostrar PF, totais ou cenários, ou exportar, antes de o analista confirmar a prévia ou pedir para calcular.
- Contar funções sem evidência ou hipótese ligada ao texto do pedido.
- Chamar PFM de PF, ou omitir o rótulo de estimativa híbrida e o aviso da indicativa (o script os inclui; não os remova).
- Aplicar fórmulas contratuais do SISP (fator de impacto de 63/84%, 0,39 PF de manutenção cosmética, deflatores).
- Pesquisar na web ou usar regra que não esteja em `references/`.
