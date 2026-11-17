# Plano — skill `nesma-apf-estimator`

Estado: **construção, etapa 6 (evals do agente)**. Etapas 1 a 5 concluídas: fontes, gabaritos, esquema e cálculo, references/ e SKILL.md, renderizadores e exportador (61 testes unitários; xlsx validado com openpyxl, LibreOffice e Excel).
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
