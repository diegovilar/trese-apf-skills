# Plano — skill `nesma-apf-estimator`

Estado: **iteração 2, desenho** (decisões D40–D45; ver "Iteração 2: decisões de desenho"). A iteração 1 foi encerrada como versão inicial (ver "Encerramento da iteração 1"). Etapas 1 a 5 concluídas: fontes, gabaritos, esquema e cálculo, references/ e SKILL.md, renderizadores e exportador (61 testes unitários; xlsx validado com openpyxl, LibreOffice e Excel).
Especificação original do usuário: instruções coladas na sessão de 17/11/2026 (Fases 1–3 e critérios de finalização).

## Contexto de uso

A skill serve para a **estimativa preliminar** de tamanho funcional em pedidos de desenvolvimento de solução tecnológica dirigidos à **equipe interna do TRE/SE**, como insumo da análise de viabilidade do projeto de TI. Não serve para contratação nem para medição. Nessa fase não há levantamento exaustivo de requisitos, e o pedido pode ser negado já com base na análise preliminar, que considera outros fatores além da APF. O método adotado pelo TRE/SE é a **NESMA estimativa**, independentemente do que recomenda o SISP 3.0.

## Decisões fechadas

| # | Decisão | Origem |
|---|---------|--------|
| D1 | Uso para estimativa preliminar em análise de viabilidade; subsídios incompletos, vindos de arquivo anexo ou do prompt. | Usuário |
| D2 | Saída final em `.xlsx`, `.md` ou `.txt`, à escolha do usuário. | Usuário |
| D3 | O resultado é sempre impresso em tabela formatada antes de perguntar o formato de exportação (se ainda não decidido). | Usuário |
| D4 | Dependência ou instalação para `.xlsx` só depois de conversar com o usuário. | Usuário |
| D5 | Argumentos interpretados pela LLM (não por script), com gramática fechada e tabela de sinônimos. Argumento inválido ou ambíguo gera um alerta e **nada** é executado, nem a parte válida. | Usuário |
| D6 | Regras do Judiciário entram só se houver fonte pública encontrada, com fonte e versão citadas. Nenhuma "prática do Judiciário" é inventada. | Sessão + popper |
| D7 | Cada regra em `references/` recebe uma marcação: `[normativa]`, `[adaptação institucional]` ou `[convenção da skill]`, com fonte e versão. | Sessão + popper |
| D8 | Este plano fica versionado em `PLANO.md` e é atualizado a cada decisão. | Sessão + popper |
| D9 | Método: **NESMA estimativa** (prática do TRE/SE). SFP não é implementado. | Usuário |
| D10 | Sem contratação: fator de impacto contratual (FI 63/84%), perfis de regime e glosas de fiscalização saem do escopo. | Usuário |
| D11 | Uso interno, sem distribuição. A instalação em qualquer harness fica a cargo do usuário. A licença do SISP (CC BY-NC-SA) deixa de ser bloqueio para uso interno não comercial. | Usuário |
| D12 | O plano inclui **evals** da skill, durante o desenvolvimento e no futuro. | Usuário |
| D13 | Melhoria com dois regimes, escolhidos por argumento: **fatores NESMA de melhoria (EFPA)**, que é o padrão, e **sem fatores**. | Usuário |
| D14 | Contagem **indicativa** como modo opcional, escolhido por argumento. O padrão é a estimada. | Usuário |
| D15 | Incerteza: perguntar só quando a lacuna impede definir fronteira ou tipo de projeto. No resto, premissa rastreada (evidência × hipótese × pendência), com cenário mínimo/máximo só para as hipóteses que mudam o total. | Usuário (proposta revisada pelo popper) |
| D16 | Não há material interno do TRE/SE: o modelo de planilha é criado na skill e **precisa ter legenda**. Sem busca por guias do Judiciário. | Usuário |
| D17 | Evals com casos sintéticos, escritos na sessão e validados pelo usuário. | Usuário |
| D18 | Python é requisito aceitável nas máquinas-alvo. Não dá para garantir a presença de `uv` nem de `pip`. | Usuário |
| D19 | **Padrão de melhoria passa a ser `sem-fatores`** (altera D13). O regime `nesma` (EFPA) continua disponível por argumento. | Usuário |
| D20 | No regime `nesma`, alteradas sem percentuais de TD/AR no subsídio entram como **cenários condicionais**, com os fatores compatíveis com o que se sabe, sem valor central e com o rótulo "estimativa híbrida: pesos NESMA estimada + fatores EFPA". Fatores firmes: incluída 1,00; excluída 0,40; só mudança de tipo AIE↔ALI 0,40; só cosmética 0,25. | Usuário (proposta revisada pelo popper) |
| D21 | Exportador `.xlsx` único, só com stdlib. Valores individuais gravados; **totais como fórmulas** (com valor em cache, para leitores que não recalculam). | Usuário; o valor em cache é decisão da sessão |
| D22 | Plano de engenharia e ordem de construção aprovados. | Usuário |
| D23 | Validação de argumentos em **dois estágios** (interpretação de D5). Estágio 1, sintático: alerta sem ler o subsídio. Estágio 2, contextual (arquivo inexistente, `tipo` inferido incompatível com `melhoria=`): o subsídio pode ser lido; alerta sem contagem nem exportação. | Usuário (proposta revisada pelo popper) |
| D24 | Convenção **C4**: no `sem-fatores`, a transação só conta como alterada se mudam os dados, os arquivos referenciados (inclusão ou retirada) ou a lógica dela. No `nesma`, vale o exemplo 7 do EFPA: transação que usa arquivo alterado entra. Os regimes diferem também em quais funções entram. | Usuário, condicionado ao acordo sessão + popper (houve acordo) |
| D25 | Gabaritos iniciais aprovados: `evals/gabaritos-iniciais.md`, revisão 2. O G04 foi ajustado depois (revisão 3) para ter cenários coerentes, e o usuário foi informado. | Usuário |
| D26 | Linguagem natural: descrição do sistema é subsídio, sem confirmação; pedido explícito de configuração (formato, método, regime) gera a invocação equivalente e pedido de confirmação; configuração inexistente gera alerta. | Usuário (proposta revisada pelo popper) |
| D27 | Autenticação feita inteiramente pela infraestrutura institucional (**SSO ou AD**; gov.br não é usado no TRE/SE) fica fora da contagem; o que o pedido pede que a aplicação faça com a identidade conta normalmente. | Usuário |
| D28 | Planilha gerada pelo exportador stdlib abriu no Excel sem reparo, com abas e totais corretos. | Usuário |

## Fatos verificados

- O link do SISP na especificação dá 404. A versão vigente é o **Roteiro de Métricas do SISP 3.0** (Portaria SGD/MGI nº 3.656, jun/2026), e o SISP não vincula o TRE/SE. O site da NESMA (nesma.org) também está fora do ar (404).
- Pesos NESMA estimada da especificação conferem: ALI 7, AIE 5, EE 4, SE 5, CE 4. Indicativa: 35×ALI + 15×AIE.
- **Guia NESMA "APF para Melhoria de Software" 2.2.1** (tradução PT, hospedada pela FATTO: `fattocs.com/wp-content/uploads/2020/04/APF-Melhoria-NESMA.pdf`):
  - incluída: I = 1,00; excluída: I = 0,40;
  - dados alterados: fator pelo % de TDs alterados (≤1/3 → 0,25; ≤2/3 → 0,50; ≤100% → 0,75; >100% → 1,00); mudança de tipo AIE↔ALI → 0,40, ou o maior entre esse e o fator por TDs;
  - transação alterada: matriz %AR × %TD, com fatores de 0,25 a 1,50; alteração só cosmética → 0,25;
  - resultado em **PFM** (pontos de função de melhoria), unidade distinta de PF; o PF base da alterada é o tamanho depois da alteração;
  - **não há procedimento para contagem estimada.** Sem TDs/ARs, o fator de alteradas não é determinável pelo guia.
- Ambiente de desenvolvimento: python3 3.9.6, **sem openpyxl**, com `uv` e LibreOffice (`soffice`).

## Ajustes à especificação (aceitos na revisão)

1. Substituir atalhos absolutos por critérios condicionais com exemplos contrastantes: "listar com filtros = CE" pode ser SE; CRUD não gera quatro funções automaticamente; exportar PDF/CSV não cria função por si; integração de leitura só é AIE se houver grupo lógico mantido como ALI de outra aplicação; dado de código ≠ dado de negócio.
2. "Itens não mensuráveis descartados" vira: absorvido no processo elementar; fora do escopo da APF. Em melhoria, a alteração só cosmética entra com fator 0,25 (EFPA).
3. Incluir funções de conversão de dados (cargas/migração) quando o pedido as exigir.
4. Incerteza: evidência × hipótese × pendência. "Conservadora" não significa subcontar. Sem percentuais estatísticos inventados. Cenários para **toda** hipótese que muda o total, sem filtro de relevância.
5. Matriz de cobertura: a skill declara o que cobre e, fora disso, pergunta ou registra a limitação, sem improvisar regra normativa.
6. Login/auditoria: sem regra categórica até haver fonte.
7. SISP 3.0 só como referência técnica subsidiária (identificação e casos de borda), sem fórmulas contratuais.

## Plano de engenharia (revisado com o popper; aguarda aprovação do usuário)

**Estrutura**

```text
nesma-apf-estimator/
├── SKILL.md                      gatilho, leitura obrigatória, argumentos, fluxo, incerteza, saída
├── references/
│   ├── 01-fundamentos-e-identificacao.md
│   ├── 02-regras-nesma.md        estimada, indicativa, melhoria (EFPA e sem fatores)
│   ├── 03-casos-de-borda-e-convencoes.md
│   ├── 04-exemplos-praticos.md   3 da especificação + 1 de indicativa
│   └── 05-saida-e-legenda.md     layouts md/txt/xlsx e texto da legenda
└── scripts/apf.py                stdlib, Python ≥ 3.8
evals/                            fora da skill, para o agente executor não carregar
```

**JSON canônico + script.** O agente monta um JSON (versão do esquema, modo, regime, funções com tipo/operação/evidência/hipótese, premissas, cenários e pendências). O `apf.py` valida o esquema, calcula pesos, fatores e totais com `Decimal` (a LLM não faz aritmética) e renderiza md (impresso no chat), txt e xlsx a partir do mesmo JSON. Cenários são conjuntos coerentes de hipóteses, não somas de extremos independentes. Isso não conflita com D5: interpretar a invocação continua com a LLM.

**Sem Python:** alerta de pré-requisito ausente, sem total nem exportação.

**.xlsx:** exportador único, só com stdlib, com valores materializados (sem depender de fórmula `SUM`) e abas de memória de cálculo, premissas e legenda. Sem cadeia uv → pip → stdlib. Validado no desenvolvimento lendo os valores (openpyxl via `uv`, só na máquina de dev, e LibreOffice headless) e abrindo uma vez no Excel.

**Gramática de argumentos**

- Tokens `chave=valor` no início, encerrados por `--`. Tudo depois de `--` é subsídio (texto ou caminho de arquivo) e nunca é interpretado como opção. Valores com espaço vão entre aspas.
- `modo` = `estimada` (padrão) | `indicativa`
- `melhoria` = `sem-fatores` (padrão, D19) | `nesma` (só vale em projeto de melhoria)
- `tipo` = `desenvolvimento` | `melhoria` (opcional; senão é inferido, e pergunta se não der)
- `saida` = `md` | `txt` | `xlsx` (opcional; senão pergunta depois de imprimir)
- Sinônimos fechados (ex.: estimativa → estimada; macro → indicativa; efpa → nesma; excel/planilha → xlsx; markdown → md; texto → txt). Sem `ifpug`/`puro`.
- Alerta e nada executado: chave ou valor desconhecido; chave repetida com valores conflitantes; token com cara de chave sem `=`; `modo=indicativa` com `tipo=melhoria`.

**Ordem de construção**

1. Coleta de fontes (SISP 3.0, EFPA PT 2.2.1, documento NESMA de early FPA a localizar). O IFPUG CPM não é livre: as regras dele entram via descrição do SISP 3.0, com a seção citada, ou como `[convenção da skill]`.
2. Gabaritos iniciais e critérios de aceitação (validados pelo usuário).
3. Esquema canônico e regras matemáticas.
4. references/ e SKILL.md (teto provisório de ~25k tokens, a testar no ambiente-alvo).
5. Renderizadores e exportador.
6. Evals completos e ajustes.
7. Remoção dos PDFs temporários e relatório final (arquivos, tamanhos, fontes).

## Evals

- **Testes unitários do script**: esquema, aritmética, fatores e renderização.
- **Interoperabilidade**: o xlsx abre e os valores lidos batem (openpyxl, LibreOffice, Excel).
- **Evals do agente**: casos sintéticos com rubrica além do total (identificação, deduplicação, fronteira, classificação, omissões, rastreabilidade, adequação das hipóteses). Nas entradas ambíguas, aceitar um conjunto de interpretações fundamentadas.
- **Pares metamórficos**: parafrasear o pedido não muda a estimativa; duplicar uma história não duplica funções; mudar só o formato de saída não muda nenhum valor.
- **Argumentos**: válidos, sinônimos, inválidos e ambíguos. Nos inválidos, os traces precisam mostrar que não houve leitura do subsídio nem chamada ao script.
- Execução headless (`claude -p` / `opencode run`, a confirmar) com N repetições por caso, para medir estabilidade. Versões de skill, modelo e harness registradas em cada resultado. Reexecutar a cada mudança da skill ou troca de modelo.

## Fontes coletadas (etapa 1)

Cópias de trabalho em `/tmp/apf-fontes/`, fora do repositório e removidas ao final:

| Fonte | Versão | Obtida em |
|---|---|---|
| Roteiro de Métricas de Software do SISP | 3.0 (Portaria SGD/MGI nº 3.656/2026) | gov.br (PDF, 283 p.) |
| NESMA, *Early Function Point Analysis* | 2015-07-15 (EN, 6 p.) | assets.zyrosite.com (site atual da NESMA) |
| NESMA, *Contagem Antecipada de Pontos de Função* | tradução autorizada da anterior | fattocs.com (página) |
| NESMA, *APF para Melhoria de Software* | 2.2.1 (PT, 2010, 28 p.) | fattocs.com (PDF) |

Fato adicional da NESMA: a indicativa supõe, em média, 3 EE + 2 SE + 1 CE por ALI e 1 SE + 1 CE por AIE. A pesquisa NESMA (~100 aplicações) mostrou que a estimada não difere significativamente da detalhada, enquanto a indicativa teve desvios de até ~50% em alguns casos.

## Decisões em aberto

- Ok para cada fase que consome cota: sondagens → calibração → rodada curta → rodada completa.
- Ok do usuário para a rodada completa (N = 5), depois da análise da curta.

## Consulta 7 ao popper: verificador separado e `reverificar` (17/11/2026)

- D31: três identificadores. **Execução** = skill + `casos.py` + `execucao.py` (perfil e invocação). **Juiz** = `juiz.py` + `calibracao.py` + schema + gabaritos, e o hash do dossiê em cada julgamento. **Verificador** = `verificador.py`, fora dos dois primeiros; mudá-lo exige só `reverificar`.
- Cada execução é congelada em snapshot com manifesto de hashes; a verificação lê só snapshot e trace.
- O JSON canônico é identificado pelo conteúdo (o render dele está contido na saída do `render --format md` no trace), não pela data; ambiguidade reprova.
- Bloco Markdown: prosa comparada com espaços normalizados; linhas de tabela idênticas e na mesma ordem. Exportações `.md`/`.txt` continuam com comparação estrita.
- Temporário de outro processo, sem citação no trace e sem `mktemp`, não conta como arquivo criado pelo agente.
- Veredito do juiz é mantido só com dossiê idêntico; senão volta a pendente, com histórico.
- Migração da `curta-3` (de `63389ce`): mudaram só `runner.py`, `verificador.py`, `execucao.py`, `juiz.py`, testes e `PLANO.md` (este, documentação). `execucao.py` e `juiz.py` são extração idêntica do runner de `63389ce` (comparação de AST: funções e `CONFIG` idênticos, salvo o acesso `CONFIG["executor"]`/`CONFIG["juiz"]` → `CONFIG`); foram aceitos uma única vez e saíram da lista de migração permitida.
- Resultado da reverificação da `curta-3`: as 7 execuções de contagem passam em todos os critérios automáticos (incluindo G04 e G06, antes falsos negativos do verificador); os vereditos de G01 a G05 foram mantidos (dossiês idênticos); `juiz-G06-r1` ficou pendente.

## Rodada curta: andamento

- `curta-1`: 1 execução (G01). Revelou que a skill não mandava copiar a saída do script para a resposta (corrigido no SKILL.md e em 05) e que o `mktemp` do executor ignora o `TMPDIR` (runner corrigido).
- `curta-2`: 1 execução (G01), invalidada por falso positivo da auditoria (temporário legítimo em `/tmp`); regra corrigida.
- `curta-3` (em andamento, parada por cota em 17/11/2026, janela de 5 horas do Claude em 22%):

| Caso | Automáticos | Juiz | Observação |
|---|---|---|---|
| G01 | todos ok (45 PF) | todos ok | |
| G02 | todos ok (20 PF de melhoria) | todos ok | |
| G03a | todos ok (14,75 PFM, com Cancelar) | todos ok | |
| G03b | todos ok (faixa, cobertura parcial) | todos ok | |
| G04 | todos ok (após reverificação) | todos ok | antes, falso negativo: quebra suave dentro de um item da legenda |
| G05 | todos ok (100 PF) | todos ok | |
| G06 | todos ok (47 PF, após reverificação) | pendente | antes, o runner não achava o JSON (caminho guardado num arquivo) |

**`curta-3` concluída (17/11/2026):** 30 execuções do executor (nenhuma inválida) e 10 do juiz.

| Grupo | Resultado automático | Juiz |
|---|---|---|
| Contagem G01–G06 (7) | todos os critérios ok | 7/7 aprovados em todos os critérios |
| Metamórficos M01, M02, M03a, M03b, M04 | M01, M03a, M04 ok; **M02 e M03b reprovaram no K2** | M01, M02, M04 aprovados |
| Relações metamórficas M01–M05 | 5/5 ok (45=45, 45=45, md=txt, 47=47, 20 PF × 14,75 PFM com Cancelar) | — |
| Argumentos válidos A01–A04, A14, A15 | todos ok (configuração, exportação idêntica, pergunta de formato) | — |
| Alertas A05–A13b | todos ok (estágio 1 sem acesso ao subsídio; estágio 2 sem contagem) | — |
| Linguagem natural L01, L02 | ok (L01 só pediu confirmação com `saida=xlsx`; L02 executou com os padrões) | — |

**Falha encontrada:** em M02 e M03b, a contagem estava certa (45 PF, tipos idênticos), mas o executor errou ao **redigitar a legenda** na resposta ("(dados)" → "(dado)"; "alteradas" → "alterada"). Em 2 de 19 execuções que mostram a tabela (~10%). As exportações, escritas pelo script, saíram idênticas. Com N = 5 e K2 crítico em todas as execuções, essa taxa reprovaria a rodada completa.

**Consulta 8 ao popper (mitigação, não correção comprovada):**
- D32: o script passa a ter dois perfis de renderização. `chat` (padrão sem `--out`) traz a legenda só com os termos que aparecem no resultado. `arquivo` (padrão com `--out`, e sempre na planilha) traz a legenda completa. Números, seções, hipóteses, premissas e avisos são idênticos nos dois perfis (testado). O verificador compara a resposta com o perfil `chat` e as exportações com o perfil `arquivo`.
- SKILL.md: copiar sem reescrever palavras; com `saida=` informado, exportar antes ou depois de mostrar a tabela é indiferente (o M03b exportou antes, e o SKILL.md não deixava isso claro; o runner não verifica a ordem).
- Próximo passo, se o usuário autorizar: rodada de **fumaça** com M02, M03b, G03a, G03b, G04, G05 e G06 (7 execuções e 5 juízes), sem conclusão estatística (zero erros em 19 ainda seria compatível com taxa de até cerca de 15%). Se passar, pedir ok para a rodada completa com esta versão congelada, sem misturar resultados antigos.
- 87 testes unitários passando.

## Fumaça `fumaca-1` (17/11/2026)

Versão congelada da skill com D32 (`config_hash` `a84c3792ac7d6311`). 13 tarefas (7 execuções e 6 juízes; o handoff contava 5 juízes), nenhuma inválida. Consumo: cerca de 3 pontos da janela de 5 h no Claude (81% → 78%) e no Codex (72% → 69%).

| Caso | Automáticos | Juiz |
|---|---|---|
| M02 | todos ok (K2 ok) | todos ok |
| M03b | todos ok (K2 ok) | — |
| G03a | todos ok | todos ok |
| G03b | todos ok | todos ok |
| G04 | todos ok | **S1, S3 e S4 reprovados** (K3, S5 ok) |
| G05 | todos ok | todos ok |
| G06 | todos ok | todos ok |

- **K2 (objetivo da fumaça):** 7/7, inclusive M02 e M03b. Sem conclusão estatística (consulta 8).
- **G04, falha semântica nova:** o executor não pôs a origem das solicitações em grupo excludente (ALI mantido aqui × AIE lido de outro sistema). A origem externa ficou só como pendência, todas as hipóteses ficaram independentes, e o cenário mínimo saiu 0 PF (obtido 0–23; na `curta-3`, 9–23, aprovado). Faltou também a pendência sobre o que "gerenciar" abrange. O juiz está certo nos três critérios. A skill já instrui o grupo (SKILL.md, 03 §1, exemplo 3 de 04), e a D32 só mexe na renderização: é variância do executor.
- **A fumaça não passou integralmente:** passou no K2 e revelou uma reprovação semântica.

**Consulta 9 ao popper:**
- Sem mudança na skill nem no script agora. O script calcula certo o JSON recebido (hipótese sem grupo é opcional) e não tem como saber que falta uma alternativa de origem; bloquear ou avisar o mínimo zero produziria falsos positivos (O4).
- Proposta ao usuário: rodada completa com a versão congelada, **começando pelas 5 repetições do G04** (exec e juiz de cada uma). Regra de parada definida antes: a rodada para quando a reprovação fica inevitável (qualquer K reprovado numa execução válida, ou o mesmo S reprovado 2 vezes no mesmo caso). Nenhum resultado desfavorável é descartado ou substituído (O2).
- O "9 a 28" do G04 é referência de cálculo, não exigência numérica; a falha é omitir a alternativa de origem e admitir cenário vazio (O3).

## Rodada completa `completa-1` (17/11/2026): parada no G04

Autorizada pelo usuário com o plano da consulta 9, começando pelo G04. Parou depois de 3 repetições, quando a reprovação ficou inevitável: S1, S3 e S4 do G04 somaram 2 reprovações cada (o máximo tolerado em 5 é 1). Consumo: Claude 5 h 76% → 75%; Codex 5 h 100% → 99%. As outras 194 tarefas ficaram pendentes e não serão executadas com esta versão.

| Execução | Mínimo–máximo | Grupo de origem | Pendência "gerenciar" | Juiz (S1, S3, S4) |
|---|---|---|---|---|
| `curta-3` r1 | 9–23 | sim | sim | ok, ok, ok |
| `fumaca-1` r1 | 0–23 | não (só pendência) | não | ✗, ✗, ✗ |
| `completa-1` r1 | 0–23 | não | sim | ✗, ✗, ok |
| `completa-1` r2 | 9–23 | sim | não | ok, ok, ✗ |
| `completa-1` r3 | 11–23 | não (ALI e registro como evidência) | não | ✗, ✗, ✗ |

- Em G04, a versão atual acerta tudo em 1 de 5 execuções: o grupo de origem saiu em 2 de 5 e a pendência sobre "gerenciar" em 2 de 5. Todas as execuções leram SKILL.md e as cinco referências: o problema não é leitura, é aplicação da regra.
- Na r3, o juiz citou também a falta do AIE de servidor no S3. A rubrica aceita sem ele (a `curta-3` foi aprovada com 9–23): é variação do juiz, não pesa na decisão.

**Consulta 10 ao popper e decisão do usuário (17/11/2026):**
- Diagnóstico: o gatilho da regra era implícito e ficava fora da etapa em que o agente decide os arquivos. Além disso, 01 §1 ("se não dá para decidir dentro/fora, pergunte") competia com o exemplo 3.
- D33: reforço textual, sem mudança no script. SKILL.md, etapa 2: decidir quem mantém cada grupo pelo que o pedido afirma, não por palavra-chave (O1); origem não afirmada vira grupo de alternativas e também pendência; receber e gravar continua sendo ALI com EE. Política de incerteza e 03 §1: a pendência não substitui a hipótese; verbo amplo sem as operações listadas gera a pendência sobre o alcance dele. 01 §1: dúvida de fronteira ≠ dúvida de origem de um grupo (O2). 04: exemplo 4 diz por que a origem local está afirmada (O5); exemplo 3 formula a pendência sobre o verbo. Aprovado pelo usuário.
- D34: caso holdout **G07** (atestados médicos, "controlar", fora de qualquer exemplo, um só grupo de dados; O3), aprovado pelo usuário sem ajustes. G01, G05 e G06 servem de contraste (origem afirmada, sem alternativas artificiais).
- D35: sem fumaça separada (O4). Nova rodada `completa-2` com a versão congelada (210 tarefas, com G07). Autorizado só o primeiro bloco: G04 e G07, 5 repetições cada (10 execuções e 10 juízes), com todos os K e S avaliados e a mesma regra de parada. As outras 190 tarefas precisam de novo ok.

## Rodada `completa-2` (17/11/2026): primeiro bloco, parado no S4 do G04

Versão com D33 e G07 (`config_hash` `5d2dfa2487945c76`). Executado o primeiro bloco autorizado, alternando G04 e G07, até a reprovação ficar inevitável. A G07 r5 e a G04 r6 não foram executadas. Consumo: Claude 5 h 72% → 66%; Codex 5 h 97% → 92%.

| Execução | Mínimo–máximo | Juiz | Observação |
|---|---|---|---|
| G04 r1 | 9–23 | S4 ✗ | origem dos dados do servidor só indireta (P3 identidade, P5 integrações) |
| G04 r2 | 9–23 | — | **inválida**: `echo $D > /tmp/apf_dir_path` (arquivo de nome fixo no `/tmp` compartilhado); repetida como r6 (comando novo `repetir`), não executada |
| G04 r3 | 9–23 | todos ok | |
| G04 r4 | 9–23 | todos ok | |
| G04 r5 | 9–23 | S4 ✗ | só "Integrações necessárias (RH, …)" |
| G07 r1–r4 | 9–28 (r3: 9–19) | todos ok | |

- A correção D33 funcionou no que mirava: grupo de origem em todas as execuções de G04 (inclusive a inválida) e de G07; pendência sobre o alcance do verbo em todas.
- Falha restante (S4 do G04, 2 de 4 válidas): pendência explícita sobre a origem dos dados do servidor, omitida de forma intermitente (genérica ou indireta nas reprovadas). Não há relação causal estabelecida com a hipótese do AIE de servidor: a G07 r3 não a criou (9–19) e registrou a pendência (O2 da consulta 11). O juiz foi coerente nas quatro.

**Consulta 11 ao popper:**
- D36: convenção nova em 03 §4, citada na etapa 2 do SKILL.md: registro ligado a uma pessoa ("minhas", "a própria", "apresentados por") sem dizer como ela é identificada nem de onde vêm os dados dela gera pendência explícita. Pendência genérica de integrações não basta. Sem presumir cadastro nem integração e sem PF. Não pergunta quando o pedido informa a origem. O gatilho é o vínculo funcional com a pessoa, não a simples menção de um papel (O1). Aprovado pelo usuário, com o primeiro bloco da `completa-3` (G04 e G07 5×; as demais tarefas exigem novo ok).
- Rubrica mantida; a reprovação da r1 é de fronteira, mas defensável, e a parada fica valendo.
- G04 e G07 orientaram a correção; repeti-los mede regressão e estabilidade, não generalização (O3). O G06 ("a própria reserva") não orientou esta correção e serve de verificação parcial fora deles, quando a rodada completa chegar a ele.
- Resultados da `completa-2` ficam como diagnóstico e não entram no denominador da próxima rodada. As ~190 tarefas restantes não serão executadas.
- Auditoria: a execução inválida é um caso legítimo do auditor (um arquivo de nome fixo no `/tmp` pode levar uma execução a ler o diretório de outra). O runner ganhou `repetir <rodada> <tarefa>`, que cria a repetição seguinte do mesmo caso e marca a inválida (fora dos hashes; 88 testes).

## Rodada `completa-3` (17/11/2026): primeiro bloco

Versão com D36 (`config_hash` `e9ae2ea398eb14c2`). Bloco completo: G04 e G07, 5 repetições cada, nenhuma inválida. Consumo: Claude 5 h 65% → 61%; Codex 5 h 91% → 84%.

- **G04: 5/5 em todos os critérios** (9–23 PF em todas; grupo de origem, alcance de "gerenciar" e dados do servidor presentes).
- **G07: S4 reprovado em 2 de 5** (r2 e r5); K3, S1, S3 e S5 ok em todas (9–23 PF). Nas duas faltou a pendência obrigatória sobre homologação ou perícia; na r5 havia só "validar" na lista de operações de "controlar", e o juiz não aceitou. A pendência D36 (identificação e dados do servidor) saiu em todas.
- Pela regra (S em ≥ 4 de 5), o bloco **reprova** no G07.
- Padrão das três rodadas: cada correção resolve o que mira, e aparece outra pendência obrigatória omitida de forma intermitente (origem → alcance do verbo → dados do servidor → homologação).

**Consultas 12 e 13 ao popper; decisões do usuário:**
- Auditoria do contrato do S4 (sem cota): das pendências obrigatórias de G03b, G04 e G07, as sem regra na skill são aprovação, cálculo e prestação de contas (G04, 9/9) e homologação (G07, 7/9). A conta de recall composto é hipótese, não diagnóstico (O1, consulta 12). **O usuário manteve todas como obrigatórias.**
- D37: convenção em 03 §1 e na política de incerteza: registros que alguém apresenta ou solicita a uma unidade, sem dizer se há análise ou decisão sobre eles, geram essa pendência; sem presumir o fluxo, sem PF; não pergunta se o fluxo existe quando o pedido o descreve. Cobre análise, aprovação e homologação; não garante cálculo nem prestação de contas.
- S4 do juiz: avaliado pelo significado no contexto; menção genérica ou ambígua não basta; pendência proibida pelo gabarito (contraste) reprova; sem obrigatórias nem proibidas, aprova (O1, consulta 13).
- G08 (holdout com contrastes): Protocolo registra requerimentos entregues por servidores; a chefia registra no sistema a decisão (deferido ou indeferido). Origem e fluxo afirmados: grupo de origem e pergunta "há análise?" reprovam; uma EE de decisão; proibida a edição genérica ou exclusão do requerimento, sem confundir com o registro da decisão (O2, O4).
- Calibração delta do juiz (O3): dossiês P3 (G07 correto, homologação por paráfrase), E6 (G07 só com "validar" na lista de operações → S4), P4 (G08 correto) e E7 (G08 com pergunta indevida → S4). Quatro chamadas do Codex; as demais da calibração antiga não são repetidas.
- **Aprovado pelo usuário (17/11/2026):** D37, G08, S4 e calibração delta (rodada `calib-3`, só P3, E6, P4 e E7). Se o juiz acertar os 4, está autorizado o primeiro bloco da `completa-4` (G04, G07 e G08, 5× cada, mesma regra de parada); se errar algum, parar e levar ao usuário. O resto da `completa-4` pede novo ok.

## Calibração delta `calib-3` e rodada `completa-4` (17/11/2026)

- `calib-3`: o juiz acertou os 4 dossiês (P3 e P4 aprovados; E6 e E7 reprovados só no S4).
- `completa-4` (`config_hash` `7565bc28c0507676`, 220 tarefas): primeiro bloco parado depois de 8 execuções. G04 r1 ok, **r2 e r3 S4 ✗**; G07 r1 e r2 ok; G08 r1 e r2 ok (15 e 15–19 PF; sem grupo de origem e sem perguntar se existe análise, como pedem os contrastes). Consumo: Claude 5 h 58% → 55%; Codex 5 h 79% → 75%.
- Falha do G04: cálculo do valor (r3) e prestação de contas (r2, r3) aparecem em `nao_contados` como `sem-evidencia`, com "(ver pendências)" na justificativa, mas sem pendência correspondente. Antes da D37 saíam 9/9, provavelmente numa pendência ampla ("há aprovação, cálculo, prestação de contas?") que a pendência específica da D37 passou a substituir. É uma regressão causada pela D37.
- A regra já existia: 03 §7 manda registrar a pendência de todo item `sem-evidencia`. O executor a lê e não a aplica, e o próprio JSON mostra a inconsistência.

**Consulta 14 ao popper:**
- Alcance: das 6 reprovações do S4 desde a `completa-2`, só as 2 da `completa-4` tinham o item faltante em `nao_contados`. Dados do servidor (`completa-2`) e homologação (`completa-3`) não estavam lá. A mudança previne essa classe de inconsistência; não garante completude (O2).
- Auditoria retrospectiva, sem cota (`completa-4` e controles da `curta-3`, 14 execuções, cerca de 40 itens `sem-evidencia`): quase todos tinham pendência correspondente, só sem vínculo formal (escrito à mão, "ver P3"); 3 itens sem pendência equivalente, todos nas duas execuções reprovadas; 1 uso indevido da categoria (G03b, `curta-3`: algo que o pedido exclui expressamente).
- D38 (proposta): esquema versão 2. Item `sem-evidencia` exige `pendencias`, lista não vazia de IDs existentes, sem repetição; uma pendência pode cobrir vários itens (O4). O `check` recusa sem isso. O script confere só os IDs; 05 §1 diz que as pendências apontadas precisam cobrir todos os assuntos do item, e o significado continua com o juiz (O1). O render acrescenta "(ver P1, P2)" em md, txt e xlsx. 03 §7: o que o pedido exclui expressamente não é `sem-evidencia` (O3). Verificador lê a versão do script. 94 testes (6 novos). Snapshots antigos não mudam. **Aprovado pelo usuário (17/11/2026), com o primeiro bloco da `completa-5` (G04, G07 e G08, 5× cada, mesma regra de parada); o resto pede novo ok.**

## Rodada `completa-5` (17/11/2026): primeiro bloco, parado no S4 do G04

Versão com D38 (`config_hash` `d26d7d0995350665`). 12 execuções e 12 juízes, nenhuma inválida; G07 r5 e G08 r5 não executadas. Consumo: Claude 5 h 53% → 45%; Codex 5 h 73% → 66%.

- G04: r1–r3 ok em tudo; **r4 e r5 S4 ✗** (r4: cálculo e prestação de contas ausentes até de `nao_contados`; r5: só prestação de contas ausente; o cálculo veio numa pendência explícita). Pela regra, o bloco reprova.
- G07: r1–r4 ok em tudo. G08: r1–r4 ok em tudo (15 ou 15–19 PF; os contrastes valeram).
- K2 ok em todas: o sufixo "(ver P…)" foi copiado sem erro.
- A D38 funcionou como vínculo (todos os itens `sem-evidencia` com pendência), mas a r4 mostra a rota de fuga prevista: o item simplesmente sai de `nao_contados`.
- Tendência desde a D37: prestação de contas no G04 faltou em 4 de 9 execuções (antes, 9/9). Homologação no G07: 8/8 desde a D37 (antes, 7/9). As pendências com regra na skill (origem, alcance do verbo, pessoa, análise) saíram em todas as execuções das `completa-4` e `-5`.

**Consulta 15 ao popper:**
- Não fazer a D39 (ampliar a pendência da D37 para o ciclo do registro) agora. Ela acrescentaria exatamente os assuntos omitidos no G04: é ajuste legítimo, mas não demonstra correção geral, e a relação causal com a D37 é hipótese (O2).
- O limite a declarar é de evidência e orçamento: esta versão não atende ao contrato atual do S4 no G04. Não está demonstrado que a skill seja incapaz de tratar pendências de domínio; os dados vêm de poucos pedidos, usados repetidamente no ajuste (O3).
- Se o trabalho continuar, primeiro um diagnóstico de regressão reduzido nos outros casos, com a versão atual congelada (1 repetição; contagens, metamórficos e ao menos um caminho xlsx, porque a D38 mexeu no esquema e na renderização), antes de outro bloco no G04 (O4).
- **Decisão do usuário (17/11/2026):** diagnóstico de regressão primeiro: rodada `diag-1` (curta, 1 repetição) com G01, G02, G03a, G03b, G05, G06, M01, M02, M03a, M03b, M04 e A03; 12 execuções e 9 juízes, mais `comparar`. Depois, ele decide entre encerrar com a limitação, desenho novo (checklist do ciclo) ou redefinir o escopo do S4.

## Diagnóstico de regressão `diag-1` (17/11/2026)

Versão da `completa-5` (`config_hash` `d26d7d0995350665`), 1 repetição. Consumo: Claude 5 h 45% → 38%; Codex 5 h 64% → 60%.

- 12 execuções (G01, G02, G03a, G03b, G05, G06, M01, M02, M03a, M03b, M04, A03), nenhuma inválida: **todas ok nos automáticos** (K1, K2, K4, S1 pré-filtro, S2, cobertura, configuração; exportações md, txt e xlsx).
- 9 juízes: **todos ok em todos os critérios**.
- Relações metamórficas M01–M05: **5/5 ok** (45 = 45; 45 = 45; md = txt; 47 = 47; 20 PF × 14,75 PFM).
- Conclusão limitada: D33–D38 não quebraram nada detectável fora de G04/G07/G08, com uma execução por caso. Não é declaração de estabilidade.

**Consulta 16 ao popper:** recomendar o encerramento do desenvolvimento **com requisito não atendido** (S4 do G04), condicionado ao aceite explícito do usuário de que a revisão humana das lacunas é obrigatória antes do uso. Isso não aprova a etapa 6. Aviso fixo no renderizador, que garante a presença em toda saída: "A lista de pendências não é exaustiva. Revise os requisitos e fluxos específicos do domínio antes de usar a estimativa na análise de viabilidade." (O3). Se o usuário não aceitar a condição, o caminho coerente é o desenho novo (checklist do ciclo). No relatório, não afirmar: "skill aprovada nos evals", "contagem estável", "pendências completas", "faixa cobre todo o projeto", "a D37 comprovadamente causou a regressão", "limite inevitável do modelo" (O1, O2).

## Encerramento da iteração 1 (17/11/2026)

- **Decisão do usuário:** encerrar o desenvolvimento desta versão como **versão inicial**, com o requisito S4 do G04 **não atendido**, aceitando a revisão humana obrigatória das lacunas antes do uso na análise de viabilidade. Não é aprovação da etapa 6. Outras soluções (desenho novo) ficam para uma iteração futura, com handoff próprio (`HANDOFF-iteracao-2.md`).
- D39: aviso fixo no renderizador (md nos dois perfis, txt e xlsx), ao fim das pendências: "A lista de pendências não é exaustiva. Revise os requisitos e fluxos específicos do domínio antes de usar a estimativa na análise de viabilidade." 05 §3 diz que ele faz parte da saída. 95 testes.
- Checagem do K2 com o aviso (rodada `k2-aviso`, G01 e G04, 1 execução cada, sem juiz), autorizada pelo usuário.
- Consulta 17 (pergunta do usuário sobre o G04): o pedido vago é a origem da incerteza; uma entrevista guiada pelo ciclo do processo pode ajudar (perguntas abertas, respostas do demandante), mas não foi testada e mudaria a D15. Vai para o handoff da iteração 2 como variante, junto com o roteiro do ciclo nas pendências.
- K2 com o aviso (`k2-aviso`): G01 e G04 ok; o aviso foi copiado sem alteração. xlsx da versão final relido com LibreOffice e openpyxl (Excel não reaberto). `/tmp/apf-fontes` removido (etapa 7); `/private/tmp/apf-evals` mantido para o usuário decidir.
- Consulta 18 (revisão do relatório e dos handoffs): resultado do S4 atribuído à versão com D38, não à final; `HANDOFF.md` atualizado (nenhuma fase autorizada; popper a partir da consulta 19); URLs das fontes descritas como estão; critério do S4 para entrevista (aspecto resolvido e refletido, ou pendente); base técnica `38f562b`.
- Entregues: `RELATORIO-iteracao-1.md` e `HANDOFF-iteracao-2.md`.

## Iteração 2: decisões de desenho (consulta 19, 17/11/2026)

Brainstorm com o usuário e consulta 19 ao popper (sessão `ses_e141aaae0ffeuGbrEAhpELk1I3`). Nada implementado; nenhuma fase que consome cota autorizada.

| # | Decisão | Origem |
|---|---------|--------|
| D40 | **Modo interativo** (altera a D15). Parâmetro `interativo` = `sim` (padrão) \| `nao`, com sinônimos fechados `s`/`n`, `true`/`false`, `1`/`0`, `on`/`off`, `yes`/`no`, `verdadeiro`/`falso`; demais regras de argumento da D5/D23. Com `sim`, antes do cálculo a skill mostra as funcionalidades detectadas (sem PF) e as lacunas que mudam a contagem, com perguntas objetivas (com espaço para nota) ou abertas, **em lotes**; a cada lote, mostra o que ainda falta e oferece calcular com o que já se sabe. Com `nao`, vale o comportamento atual da D15. Quem responde é o analista de TI: termos de negócio sempre, com o termo APF entre parênteses, sem presumir que ele lembra o significado. A lista preliminar não conflita com a D3 (que trata do resultado final). | Usuário (proposta revisada pelo popper) |
| D41 | **Roteiro do ciclo do processo** (variante 1 do handoff) como gerador das lacunas e perguntas, nos dois modos, inclusive perguntas abertas por etapa ("o que acontece depois da aprovação?"), quando o caso tiver a etapa. Perguntas limitadas às lacunas que mudam a contagem. "Não sei": função só sugerida pelo roteiro continua pendência sem PF; cenário só para o que o subsídio implica (03, C1). As hipóteses admissíveis são as mesmas nos dois modos. | Usuário; C1 lembrada pelo popper (O5) |
| D42 | **Ferramenta × texto**: instrução fechada, não escolha livre. Se houver ferramenta de perguntas na execução, a skill a usa; senão, perguntas numeradas no chat. A lista de funcionalidades detectadas vai sempre em texto. O lote é definido pelo conteúdo: se não couber numa chamada da ferramenta, é dividido sem criar nem cortar perguntas. | Usuário (proposta revisada pelo popper, O4) |
| D43 | **Contrato do S4, versão 2.** A rubrica de cada caso explicita a informação ausente, as regras gerais acionadas (origem e alcance do verbo, D33; pessoa, D36; análise ou decisão, D37) e o que o texto já responde (contrastes). Nos casos com pouco subsídio, classificados assim no gabarito, são obrigatórias só as lacunas das regras gerais aplicáveis; as do ciclo do processo (cálculo, prestação de contas etc.) viram medida de diagnóstico, relatada sem reprovar, e ficam para a confirmação do analista. A pergunta aberta sobre o que vem depois da decisão é contextual, sem obrigação de aparecer no primeiro lote. A avaliação pelo contrato antigo é mantida à parte: aprovar a versão 2 **não** demonstra que o requisito da iteração 1 foi atendido. Exige calibração delta do juiz. | Usuário (proposta revisada pelo popper, O1, O2) |
| D44 | **Evals.** Casos existentes fixam `interativo=nao` (muda `casos.py` e o hash). Camada 1: um turno com `interativo=sim`, perfil sem ferramenta de perguntas; o turno termina na lista e nas perguntas; o juiz avalia lacunas obrigatórias, contrastes e tamanho do lote. Camada 2 (diálogo com `claude -p --resume` e simulador que responde só a partir de um documento oculto, "não definido" ao resto, respostas registradas) só se a camada 1 passar; a estimativa final é comparada com o que foi revelado, não com o documento inteiro (O6). Relação metamórfica: não interativo ≡ interativo com "não sei" em tudo, por significado (funções, hipóteses, cenários, totais e cobertura iguais; pendências a mais aceitas) (O7). O caminho com ferramenta é checado com o usuário num harness interativo (perguntas preservadas, resposta livre, calcular sem responder tudo). Utilidade real só com teste com o usuário. | Usuário (proposta revisada pelo popper) |
| D45 | **Holdouts novos**: três domínios, um com pouco subsídio, um médio e um rico; cada um com um contraste (o mesmo pedido com a lacuna respondida): 6 casos. Resultados caso a caso, sem média compensatória. Variante e rubricas congeladas e aprovadas pelo usuário antes da primeira execução; caso que orientar ajuste deixa de ser holdout. Domínios corrigidos na consulta 20: **Ouvidoria** (manifestações de cidadãos), **convocação de mesários** e **logística de urnas eletrônicas** (só gestão administrativa, sem software da urna nem apuração). Os primeiros sugeridos colidiam com material existente (manutenção predial = exemplo 1 de 04 e 05 §5; capacitações = G01; empréstimo de equipamentos perto de G05 e G06). A diversidade tem de vir do processo concreto, não só do nome do domínio. | Usuário (proposta revisada pelo popper, O3; domínios na consulta 20) |

## Iteração 2: desenho da implementação (consulta 20, 17/11/2026)

| # | Decisão | Origem |
|---|---------|--------|
| D46 | **Ordem.** Implementar a variante, testá-la com testes unitários e exemplos sintéticos conhecidos e fazer o commit como **marco experimental**, sem alegar aprovação. Depois, um subagente `general-intern` com contexto limpo redige os 6 holdouts e as rubricas. Ele recebe as convenções de contagem, o contrato dos critérios, os limites de cobertura e um modelo vazio de gabarito; **não** recebe a implementação, os exemplos de 04 nem os gabaritos G04, G07 e G08. O usuário aprova as rubricas antes de entrarem em `casos.py`. | Usuário (proposta revisada pelo popper) |
| D47 | **Estado do diálogo.** Pendência com pergunta tem `situacao`: `aberta`, `perguntada`, `sem-resposta` ("não sei") ou `resolvida`. Cada lote leva as próximas abertas, até 7 perguntas independentes de um assunto cada (teto provisório); a prévia mostra o número do lote e quantos assuntos faltam. "Não sei" não é repetido sem informação nova. Fim quando não há abertas ou o analista diz "calcular". Sem perguntas, a prévia fecha com "Não identifiquei perguntas adicionais. Confirma a lista para calcular?"; não se inventam perguntas. | Usuário (popper, O1, O4) |
| D48 | **O que se pergunta.** "Muda a contagem" = muda identificação ou classificação de função (inclusive CE × SE), operação de melhoria, fator EFPA, cenários ou cobertura; nunca detalhe que a estimada não usa (TDs etc., salvo para o EFPA). O roteiro do ciclo vale só para etapas ligadas ao processo descrito; sem base para pergunta específica, uma pergunta aberta por etapa. Efeitos financeiros e comprovação ficam como exemplos condicionais; não se acrescenta categoria por omissão futura. | Usuário (popper, O3, O8) |
| D49 | **Respostas.** Incorpora-se só o que foi respondido ("há pagamento" sem dizer se esta aplicação o executa gera pendência mais estreita, não função). Depois de cada resposta, o `check` revalida grupos e `requer`. | Usuário (popper, O2) |
| D50 | **Esquema versão 3.** Pendência ganha `pergunta`, `opcoes` e `situacao`; lista `esclarecimentos` (ID, pendência, pergunta, resposta); pendência resolvida continua na lista; funções e hipóteses apontam esclarecimentos por IDs conferidos pelo script; o resultado final mostra a seção de esclarecimentos. | Usuário (popper, O5) |
| D51 | **Prévia** gerada pelo script (`render --format previa`): funções em termos de negócio com o tipo APF entre parênteses, sem PF nem complexidade, e o lote de perguntas. Contrato: nenhum número nem exportação antes da confirmação; o script pode calcular internamente para validar. | Usuário (popper, O7) |
| D52 | **Evals.** A04, A14 e L02 passam a esperar a prévia; A15 ganha `interativo=nao --`; o K1 aceita execução válida que termina na prévia. Na cobertura, contam todas as pendências do JSON, não só as do primeiro lote. A camada 1 valida só a prévia textual; atualização após respostas, encerramento, metamórfica e caminho com ferramenta continuam condições de aprovação posteriores. | Usuário (popper, O4, O6) |

## Iteração 2: implementação da variante (17/11/2026)

Marco experimental (D46), sem alegar aprovação; nenhuma execução que consome cota.

- `apf.py`: esquema versão 3 (versão 2 recusada); validação do estado das perguntas (situação, lote, teto de 7, `perguntada` só no último lote), dos esclarecimentos e das referências; `render --format previa` (sem PF, complexidade nem totais; só imprime); o resultado final (md, txt, xlsx) recusa pergunta ainda `perguntada`; seção de esclarecimentos e "(ver E1)" na base das funções e nas hipóteses; pendências resolvidas saem da lista de pendências; legenda com "Esclarecimento".
- `SKILL.md`: argumento `interativo` com sinônimos; etapa 3A (roteiro); seção 2A (lotes, respostas, "calcular", ferramenta × texto); política de incerteza e proibições atualizadas. 03 §10: roteiro do ciclo. 05: esquema v3, prévia e campos interativos.
- Evals: `casos.py` com `interativo=nao` nos casos de contagem, metamórficos e A01–A03; A04, A14 e L02 esperam a prévia; A15 com `interativo=nao --`. Verificador com o caminho da prévia (K1 e K2 próprios). `calibracao.py` e fixtures no esquema v3 (muda o hash do juiz; a calibração delta da D43 vai refazer o necessário).
- 129 testes unitários (34 novos), incluindo a relação metamórfica no nível do script. Caso sintético do G04 respondido renderizado em md, txt e xlsx (xlsx relido com openpyxl).
- Pendente: holdouts (D46, `general-intern`), rubrica e juiz da camada 1 com calibração delta, camada 2, checagem com ferramenta.

## Iteração 2: holdouts e juiz da camada 1 (17/11/2026)

- **Holdouts (D45, D46):** o `general-intern` redigiu duas versões. A primeira foi devolvida (consulta 21): textos com convenções de APF embutidas e nenhuma lacuna de etapa obrigatória, só as das regras gerais. A segunda tem lacunas de etapa com teste de admissibilidade escrito no caso (âncora, duas respostas com efeitos diferentes, delimita e não amplia): E2 em H2 (como o resultado da entrega da convocação chega ao sistema) e E3 em H3 (chegada × conferência do retorno); H1 declara que não mede descoberta de etapa. Aprovada pelo usuário com três ajustes (consulta 22): duas decomposições do envio em H2/H2c (SE autônoma, 42–52 / 46 PF, ou absorvido no registro, 37–47 / 41 PF); separações de arquivos e máximos de H3/H3c não obrigatórios; E2/E3 exigidas como pendência com pergunta. Transcritos para `gabaritos-iniciais.md` (seção "Holdouts da iteração 2") e `casos.py` (H1…H3c). Commits `59b9e19` (rascunho) e `7782937`.
- D53 (**juiz da camada 1**, consulta 23, aprovado pelo usuário): instruções próprias para casos com `previa`; S3 sobre o modelo da prévia, sem exigir PF nem cenários; S4 só de ausências, toda obrigatória com `pergunta` que de fato peça o esclarecimento, em qualquer lote; critério novo **R** (pendências redundantes ou proibidas, com ou sem pergunta; redundante = pede confirmar ou repetir o que o texto afirma, ou escolher onde o texto já escolheu; contexto citado e perguntas complementares não são; pergunta mista avaliada pelo trecho que pede resposta); `medidas` relatadas (número de perguntas, genéricas, que não mudam a contagem, redundantes, diagnóstico presente); resultado conjunto S4+R no resumo. Esquema `veredito-previa.schema.json` (R e medidas obrigatórios; sem eles o julgamento é inválido).
- D54 (**G04i, G07i, G08i**): G04, G07 e G08 na camada 1, com o contrato de cada caso fixado em `casos.py` (nota ao juiz), não no gabarito compartilhado. G04i: S4 v2 = origem, alcance de "gerenciar", identificação e dados do servidor, análise ou decisão; cálculo e prestação de contas como diagnóstico; `S4_antigo` (lista do gabarito, regra da iteração 1) reportado fora da aprovação. G07i e G08i: gabarito integral.
- Calibração delta preparada (8 dossiês, acerto exato dos critérios-alvo): P5 (H2 correto, perguntas complementares e contexto citado), P6 (H3 correto, pergunta mista só de contexto), E8 (H2 sem E2 → S4), E10 (H3 com E3 só em `nao_contados` → S4), E12 (E2 sem pergunta → S4), E9 (H2 com repetição efetiva → R), E11 (H2c perguntando a origem dos locais → R), E13 (G04i correto no v2 → só `S4_antigo`). **Não executada**: pede ok do usuário (8 chamadas do Codex).
- 133 testes unitários.

**Calibração delta da camada 1 (`calib-4`, `-5`, `-6`), autorizada pelo usuário:**
- `calib-4`: parada no P5 (1 chamada). S3 reprovado por defeito real do dossiê: pergunta sobre a autonomia do envio sem hipótese correspondente (a pendência não substitui a hipótese) e erros de envio sem processo que os grave. Dossiê corrigido, com as leituras dos AIE explicitadas nas justificativas.
- `calib-5`: P5 acertou; parada no P6 (2 chamadas). S3 reprovado porque a rubrica do H3 descreve a conferência como grupo de duas alternativas e o dossiê a representa como hipótese opcional sem grupo (mesmos cenários); no P5, o juiz aceitara a mesma forma. Consulta 24: frase nova no S3 da prévia (equivalência semântica, só quando a alternativa incorpora uma atividade numa função obrigatória, sem restrições próprias); rubricas e dossiês mantidos; dois testes unitários de equivalência e de dependência (135 testes).
- `calib-6` (`config_hash` `ca1eafd54650bb9c`): **8/8 acertos** com reprovação exata dos critérios-alvo (P5 e P6 aprovados em tudo; E8, E10 e E12 só no S4; E9 e E11 só no R, com o ID da pendência redundante nas medidas; E13 aprovado no v2 e reprovado só no `S4_antigo`). Consumo do Codex nas três: 5 h 89% → 80%; semanal 86% → 85%.

## Rodada `curta-4` (17/11/2026): diagnóstico, reprovada

Versão `ca1eafd54650bb9c` (skill de `451690d`, juiz de `bf2184c`). Autorizada com 22 exec e 14 juízes; parada no K3 do H3 (3ª execução); continuação autorizada **só como diagnóstico** (consulta 26), sem H3c, H1 e H1c (preservados), parada só por cota ou inválida; parada de novo na A01 (inválida). Executadas 17 e julgadas 11. Consumo: Claude 5 h 86% → 75%; Codex 5 h 80% → 70%.

| Caso | K1, K2 | Juiz | Observação |
|---|---|---|---|
| H2 | ok | S3 ✗ | E2 perguntada; o registro posterior da entrega virou `sem-evidencia` (misturado com reenvio não pedido), sem hipótese; absorção do envio citada sem alternativa |
| H2c | ok | S1 ✗ | "consultar a relação de locais para escolher o local" absorvida no registro; a rubrica exige CE (leitura do executor defensável, consulta 26 O3) |
| H3 | ok | K3 ✗, S3 ✗ | Ocorrência como ALI afirmado, sem hipótese (rubrica: proibida); E3 perguntada e hipótese da conferência presente; cobertura completa indevida |
| G04i | ok | S3 ✗ | S4 v2 ok e **S4 antigo ok** (cálculo e prestação de contas presentes); S3: a alternativa "mantidas aqui" exige a consulta (padrão do exemplo 3) e identificação do servidor fixada em premissa |
| G07i | **K2 ✗** | tudo ok | o executor reescreveu o parágrafo inicial da prévia |
| G08i | ok | tudo ok | 3 perguntas, nenhuma proibida |
| A04, A14 | ok | — | |
| L02 | **K2 ✗** | — | "parcial. o pedido" → "parcial. O pedido" (o script gera minúscula depois de ponto) |
| G01, G04, G06, G08, G03b (não interativo) | ok | tudo ok | G04 com S4 antigo completo |
| M03b | ok | — | |
| A01 | inválida | — | arquivo de nome fixo no `/tmp` (`/tmp/apf_dir_portaria.txt`), mesma armadilha da iteração 1 |
| A03, A05, A15 | não executadas | | |

- Descoberta e contenção: S4 e R aprovados nas 6 julgadas da camada 1; nenhuma pergunta redundante, genérica ou sem efeito na contagem. A falha migrou para a **representação** da incerteza em volta das perguntas (S3/S1/K3) e para a **cópia literal da prévia** (K2).
- Regressão do modo não interativo: nenhuma detectada (5 julgados e M03b), com 1 repetição.
- H2, H2c e H3 foram expostos; H3c, H1 e H1c não.
- Registro (consulta 27): "todas as lacunas obrigatórias foram encontradas nas seis execuções julgadas; E2/E3 apareceram nos casos correspondentes". Não se afirma deslocamento causal da falha nem estabilidade da descoberta (1 repetição).

**Decisões do usuário após a `curta-4` (consulta 27), só para rodadas futuras; os resultados da `curta-4` ficam como estão:**
- D55: H2/H2c aceitam também a consulta dos locais como parte do registro da nomeação, com fundamentação (−4 PF nas referências). H3/H3c: ALI separado **como certeza** deixa de ser proibida (K3) e reprova o S3. Nota do G04i: exigir a consulta também na alternativa local segue o exemplo 3 e não reprova; premissa que fixa o que uma pendência declara desconhecido continua sendo incoerência.
- D56: mitigação do K2 no script (não é correção comprovada): cobertura parcial com dois-pontos ("parcial: motivo") no resumo final e na prévia; abertura da prévia encurtada para uma linha. Não se tolera diferença de maiúscula no verificador. Checagem direcionada do K2 (G07i, L02 e G04 não interativo, sem juiz), junto com A01 (repetição da inválida), A03, A05 e A15; calibração delta só de P5 e P6 (a prévia dos dossiês mudou só nessas duas linhas). Representação da incerteza (H2, H3, G04i): sem correção até nova decisão; cada falha é de natureza diferente, e o campo `efeito` foi descartado (repetiria a rota de fuga da D38).

## Rodadas `calib-7` e `k2-previa` (17/11/2026)

Versão `4eb6077f21f4f68d` (commit `5f00974`, com D55 e D56). Consumo: Codex 5 h 68% → 67%; Claude 5 h 73% → 70%.
- `calib-7`: P5 e P6 acertaram (tudo aprovado) com a prévia nova.
- `k2-previa`, sem juiz: **G07i, L02 e G04 (não interativo, saída final) com K1 e K2 ok**; A01 ok (a inválida da `curta-4` repetida); A15 ok; A05 ok depois de corrigir o verificador (falso positivo: `tem_contagem` contava 6 barras e a linha "Chaves" do alerta passou a ter 6 com `interativo=sim|nao`; agora procura linha de tabela; `reverificar` sem cota; 136 testes); A03 r1 inválida pela auditoria (`ls ../../../tmp` de dentro da pasta da skill, que resolve dentro do diretório da execução, mas o auditor recusa qualquer `..`), repetida como r2, ok. As tarefas de juiz de G07i e G04 ficaram pendentes de propósito.
- Mitigação do K2 sem falha nesta amostra (1 repetição; sem conclusão estatística).

## Iteração 2: correção experimental da representação (consultas 28 e 29)

- D57 (usuário, caminho 1): **Etapa 3B** do `SKILL.md`, revisão do modelo em dois sentidos, nos dois modos, com o subsídio e os esclarecimentos como fonte: (1) das certezas para a fonte — conclusões pelas regras a partir de fatos afirmados continuam evidência; suposição que muda a contagem vira hipótese; premissa sem efeito continua premissa; contradição premissa × pendência resolvida pela fonte (se a fonte responde, sai a pendência; se não, sai ou se restringe a premissa); (2) das lacunas para o modelo — a leitura que a fonte já implica e que muda a contagem entra também como hipótese; o que a fonte nem menciona fica pendência sem PF (C1); confirmar antes de usar `sem-evidencia`. Experimento, não mecanismo validado.
- Rodada `ajuste-1`, autorizada: H2, H3, G04i (casos de ajuste, prévia, juiz) com N = 3; controles G08i (prévia), G01 e G06 (não interativo) com N = 1 (preparados com 3 repetições; r2 e r3 dos controles ficam pendentes de propósito). Critério fixado antes: S3 ≥ 2/3 por caso de ajuste; S4 e R 3/3; nenhum K reprovado; controles com todos os critérios aplicáveis aprovados (inclusive K1, K2 e S3). Falha → registrar e consultar, sem correção automática. Resultado favorável = sinal para o próximo teste (holdouts novos), não estabilidade nem generalização. H3c, H1 e H1c seguem sem execução. `runner.py preparar` ganhou `--reps`.
- **Resultado (`config_hash` `7e5e909e6cbc6b96`), experimento reprovado pelo critério:** H2 r1 com S3 ok (a hipótese do registro posterior da entrega apareceu, com EE), mas **K3 ✗** (hipótese nova de CE "consultar mesário no cadastro eleitoral", a partir de "serão consultados"; proibida na rubrica, aplicada corretamente, consulta 30). Parado; continuação diagnóstica curta autorizada (consulta 30): H3 r1 com **S3 ✗** (hipótese nova de AIE de zonas eleitorais, sem apoio no texto) e **S4 ✗** (a pergunta sobre o tratamento das ocorrências não pergunta por quem); G04i r1 aprovado em tudo, inclusive S4 antigo (na `curta-4`, S3 ✗); controles G08i, G01 e G06 aprovados em tudo (sem rebaixamento de evidências nem inflação detectada). K1 e K2 ok nas 6. Consumo: Claude 5 h 68% → 64%; Codex 5 h 65% → 60%. As r2 e r3 ficaram pendentes.
- Leitura (1 repetição por caso; sem conclusão estatística): a 3B removeu as incoerências que mirava em H2 e G04i, mas induziu hipóteses sem apoio no texto em 2 de 3 casos de ajuste (H2, H3); nos controles, nada detectado.
- D58 (usuário, consulta 31): **3B abandonada**; `SKILL.md` revertido ao estado anterior a `c5e6cfe` (base `451690d` + D55/D56); `--reps` do runner mantido. Não se atribui o ganho ao item 1 nem a inflação ao item 2 (rodaram juntos, uma vez). A representação da incerteza (S3) fica como **limitação conhecida** e trabalho separado; não é apagada dos resultados. A reversão não demonstra que a base seja melhor. Próximo: bloco de **descoberta** H2 e H3, N = 5, na versão retomada; critério fixado antes: S4 e R ≥ 4/5 por caso; S3, S1, K3 e medidas relatados; só K1/K2 (verificador), cota ou execução inválida interrompem. H2 e H3 estão expostos: o bloco mede estabilidade, não generalização.

## Bloco de descoberta `descoberta-1` (18/11/2026)

Versão retomada (`config_hash` `4eb6077f21f4f68d`, igual à da `k2-previa`), H2 e H3, N = 5, autorizado (D58). 10 execuções e 10 juízes, nenhuma inválida; K1 e K2 ok em todas. Consumo: Claude 5 h 62% → 55%; Codex 5 h 58% → 51%.

| Caso | S4 | R | S4+R | S3 | S1, K3, S5 | Perguntas |
|---|---|---|---|---|---|---|
| H2 | 5/5 | 5/5 | 5/5 | 2/5 | 5/5 | 8, 7, 7, 4, 9 |
| H3 | 4/5 | 4/5 | 3/5 | 3/5 | 5/5 | 6, 6, 6, 7, 7 |

- **Critério fixado (S4 e R ≥ 4/5 por caso): atendido nos dois.** O resultado conjunto S4+R do H3 é 3/5.
- H3 S4 ✗ (r2): de novo a pergunta sobre o tratamento das ocorrências sem "por quem" (o mesmo da `ajuste-1`: não era efeito da 3B). H3 R ✗ (r5): a pergunta de autonomia das ocorrências ofereceu como alternativa "só vista pela remessa", que o pedido exclui (há lista própria para a seção).
- S3 (limitação conhecida): H2 r2, r3, r5 sem a hipótese do registro posterior da entrega; H3 r3 com ALI de ocorrências afirmado; H3 r5 com AIE de zonas eleitorais sem apoio — o mesmo tipo de inflação da `ajuste-1` aparece sem a 3B, o que enfraquece a atribuição daquela inflação à 3B.
- Medidas: no H2 r1–r2, uma pergunta genérica e uma sem efeito na contagem; nenhuma redundante no H2.
- H2 e H3 estavam expostos: o bloco mede estabilidade da descoberta nestes casos, não generalização.

## Evals do agente: implementação

- D29: desenho revisado (`evals/README.md`), casos L01/L02 e calibração do juiz aprovados pelo usuário.
- Runner em `evals/agente/` (`runner.py`, `casos.py`, `calibracao.py`, `veredito.schema.json`): uma tarefa por chamada, estado por fase, hash da configuração, auditoria de acesso, verificações automáticas fortes, dossiê autocontido do juiz. Rodada curta = 30 execuções do executor e 10 do juiz.
- **Sondagens (17/11/2026, rodadas `sondas-1` e `sondas-2`):**
  - credencial da assinatura (`apiKeySource: none`), modelo `claude-sonnet-5-5`; o consumo cai na cota monitorada;
  - `--restricted` **não** descobre `.claude/skills` do projeto (sondas-1: o executor improvisou uma contagem detalhada sem a skill);
  - D30: perfil do executor fixado em `--setting-sources project --strict-mcp-config`, ferramentas `Read, Write, Edit, Glob, Grep, Bash, Skill` (`--tools` e `--allowedTools`), `--permission-prompts none`, `TMPDIR` dentro do diretório da execução; confinamento pela auditoria do trace (decisão da sessão, registrada; não é fallback automático);
  - com esse perfil, a skill é descoberta e o caso `modo=detalhada` gerou exatamente o alerta especificado, sem ferramentas;
  - nenhum CLAUDE.md nem memória do usuário entra no contexto do executor;
  - juiz: `gpt-6.1-sol` no Codex 0.167.0 responde (esforço high); eventos `--json` no formato `item.completed` / `item.type`.
- Custo das sondagens no executor: US$ 0,07 + 0,04 + 0,02 (estimativa do Claude Code; na assinatura, vale como medida relativa).
- **Calibração do juiz (rodadas `calib-1` e `calib-2`): aprovada.** Em `calib-1`, o juiz acertou o critério-alvo nos 7 dossiês (P1, P2 aprovados; E1→S1, E2→S5, E3→K3, E4→S4, E5→S3). Também reprovou o S3 do E4 apontando um defeito real da **nossa** referência do G04: o AIE de servidor sem transação ligada que o lesse. No P2, com a mesma estrutura, deixou passar, o que mostra variação do juiz em casos de fronteira. Correção: a hipótese do servidor passou a exigir o registro (fixtures, calibração e gabarito G04, revisão 4). Em `calib-2`, P2 e E4 foram rodados de novo: P2 aprovado em tudo, E4 reprovado só no S4. As demais tarefas de `calib-2` ficaram pendentes de propósito (dossiês inalterados ou com alteração irrelevante para o alvo).
- 76 testes unitários passando (inclui o runner com traces simulados).

## Evals do agente: escolhas do usuário

Harness Claude Code (`claude -p`); executor Sonnet 5.5, esforço high; juiz Codex `gpt-6.1-sol` (nome a confirmar), esforço high; rodada curta e depois completa (N = 5); antes de cada execução do executor e de cada chamada do juiz, checar a cota (Claude e Codex) e parar abaixo de 15% em qualquer janela.

## Mudanças após a consulta 5 (popper)

- Cenários coerentes: hipóteses ganharam `requer`; o script escolhe o mínimo e o máximo entre combinações válidas e rejeita, em desenvolvimento, cenário com arquivos e sem transação. O exemplo 3 de 04 passou de 5–11 para 9–15 PF. O gabarito G04 (já aprovado) foi ajustado pelo mesmo motivo: a origem das solicitações virou alternativa excludente (9 a 28).
- Validação robusta: listas obrigatórias, tipos checados antes do uso, fatores não finitos rejeitados; teste de mutação garante que JSON malformado gera erro, nunca exceção.
- `cobertura` (completa/parcial, com motivo) separada da faixa de fator; `avisos` no resumo; aviso automático de total zero.
- Mudança de tipo com TDs desconhecidos aceita faixa (mín. 0,40).
- E-mail: primeiro testar autonomia do processo, depois CE/SE pela lógica.
- Script nunca sobrescreve arquivo (código 3).
- 61 testes unitários passando.

Local da skill: `nesma-apf-estimator/` na raiz deste repositório (decisão da sessão, revogável).
