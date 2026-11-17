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
Chaves: modo=estimada|indicativa · tipo=desenvolvimento|melhoria · melhoria=sem-fatores|nesma · saida=md|txt|xlsx
Exemplo: modo=estimada tipo=melhoria saida=xlsx -- ./pedido.pdf
```

**Pedidos em linguagem natural.** Se a skill foi acionada por uma mensagem em prosa, separe duas coisas:

- **Descrição do sistema** ("quero um novo sistema…", "no sistema X, já em produção…"): é subsídio. Serve para inferir o tipo e a fronteira (seção 2). Nunca gera confirmação.
- **Pedido explícito de configuração da estimativa**, dirigido a você e não ao sistema: formato de saída ("gere em planilha", "exporte em txt"), método ("faça a contagem indicativa") ou regime de melhoria ("use os fatores da NESMA", "sem fatores"). Não aplique a configuração por conta própria: responda com a invocação equivalente na gramática e peça confirmação antes de executar. Exemplo: "Entendi `modo=indicativa saida=xlsx -- <pedido>`. Confirma?" Se a configuração pedida não existir na gramática (ex.: "em PDF", "contagem detalhada"), emita o alerta de argumentos inválidos.

Sem pedido explícito de configuração, trate a mensagem inteira como subsídio, com os padrões.

## 2. Fluxo de contagem

**Etapa 1: escopo, tipo e fronteira.** Leia o subsídio inteiro (arquivo ou texto). Determine:

- *tipo de projeto:* se `tipo` foi informado, use-o. Senão, é melhoria quando o subsídio diz que o sistema já existe ("já em produção", "no sistema X, incluir…", "alterar a funcionalidade…"), e desenvolvimento quando descreve um sistema ou módulo novo. Se não der para decidir, **pergunte** e pare até a resposta;
- *fronteira:* o que é a aplicação medida e quais sistemas são externos (01 §1). Se a fronteira não puder ser definida, **pergunte** e pare até a resposta.

**Etapa 2: funções de dados.** Identifique ALI e AIE (01 §2), descartando dados de código (01 §5) e registrando-os em `nao_contados`. No modo indicativo, esta é a última etapa de identificação.

**Etapa 3: funções transacionais.** Quebre o pedido em processos elementares únicos (01 §3) e classifique cada um em EE, SE ou CE pela intenção primária (01 §4). Aplique os casos de borda de 03 (CRUD, múltiplas mídias, autenticação, auditoria, integrações, itens não contados). Em melhoria, marque a operação (I/A/E). No regime `nesma`, determine o `efpa` de cada alterada (02 §4.2; faixa quando faltarem números). No `sem-fatores`, aplique a convenção C4 (02 §4.1).

**Etapa 4: cálculo.** Monte o JSON canônico (05 §1) num diretório temporário e rode `apf.py check`. Corrija até passar. Os pesos, fatores, cenários e totais vêm **só** do script. Declare `cobertura: parcial` sempre que o subsídio não permitir identificar todas as funções afetadas (ex.: melhoria sem baseline, pedido vago), e ponha em `avisos` o que o resumo precisa dizer (ex.: pedido só cosmético no `sem-fatores`).

**Etapa 5: memória de cálculo e premissas.** Rode `apf.py render --format md` e **copie a saída inteira para a sua resposta**, exatamente como o script a imprimiu: resumo executivo, memória de cálculo, hipóteses e cenários, premissas, itens não contados, pendências e legenda. A saída de um comando não chega ao usuário por si só (fica recolhida no resultado da ferramenta); só o que está na sua mensagem é lido. Não resuma, não reescreva números e não diga "veja acima". Depois:

- se `saida` foi informado, exporte nesse formato;
- senão, pergunte: "Quer exportar? `.md`, `.txt`, `.xlsx` ou nenhum." e exporte o que for escolhido;
- exporte com `apf.py render --format <fmt> --out <arquivo>` (nome e local: 05 §4) e informe o caminho. O script nunca sobrescreve: se sair com código 3, use o próximo sufixo `-2`, `-3`….

## 3. Política de incerteza

- **Pergunte apenas** quando a lacuna impede definir o tipo de projeto ou a fronteira. Para o resto, não pergunte: estime.
- Classifique cada função como **evidência** (afirmada no pedido), **hipótese** (implicada por uma palavra ou frase, com o trecho) ou **pendência** (nem afirmada nem implicada: não conta). Veja a convenção C1 em 03 §1.
- Toda hipótese que muda o total entra ligada às funções correspondentes. O script calcula o cenário mínimo e o máximo. Alternativas excludentes ("ALI **ou** AIE") vão num grupo, e hipóteses que só fazem sentido juntas são ligadas com `requer`, para que cada cenário seja uma aplicação possível (03 §1). Não apresente valor central nem "total provável".
- Cobertura parcial (funções que o subsídio não permite identificar) é diferente de faixa de fator (fatores EFPA desconhecidos). Declare as duas quando houver.
- "Conservador" não significa subcontar: nada implicado pelo pedido é descartado em silêncio.
- Não invente percentuais de confiança. A única medida de incerteza é a diferença entre os cenários e a lista de pendências.
- Premissas que não mudam o total (ex.: autenticação institucional) vão em `premissas`.

## 4. Proibições

- Calcular PF, fatores ou totais fora do script, ou alterar os números que ele imprime.
- Contar funções sem evidência ou hipótese ligada ao texto do pedido.
- Chamar PFM de PF, ou omitir o rótulo de estimativa híbrida e o aviso da indicativa (o script os inclui; não os remova).
- Aplicar fórmulas contratuais do SISP (fator de impacto de 63/84%, 0,39 PF de manutenção cosmética, deflatores).
- Pesquisar na web ou usar regra que não esteja em `references/`.
