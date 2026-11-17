# Relatório final — iteração 1 da skill `nesma-apf-estimator`

17/11/2026. Versão inicial, encerrada por decisão do usuário com um critério de aceitação **não atendido** (ver "Resultado dos evals"). Detalhes e decisões em `PLANO.md`; próxima iteração em `HANDOFF-iteracao-2.md`.

## O que a skill faz

Estimativa preliminar de tamanho funcional (NESMA estimada; indicativa por argumento; melhoria sem fatores ou com fatores EFPA) para pedidos de solução dirigidos à equipe interna do TRE/SE, como insumo da análise de viabilidade. Não serve para contratação nem para medição. O agente identifica as funções e monta um JSON canônico. O script `apf.py` (só stdlib) valida, calcula e gera as saídas em md, txt ou xlsx.

## Arquivos

| Arquivo | Tamanho |
|---|---:|
| `nesma-apf-estimator/SKILL.md` | 12,1 kB |
| `references/01-fundamentos-e-identificacao.md` | 12,3 kB |
| `references/02-regras-nesma.md` | 8,6 kB |
| `references/03-casos-de-borda-e-convencoes.md` | 12,8 kB |
| `references/04-exemplos-praticos.md` | 11,2 kB |
| `references/05-saida-e-legenda.md` | 12,5 kB |
| `scripts/apf.py` | 58,7 kB |

Texto da skill (SKILL.md e references): cerca de 10,8 mil palavras. Esquema canônico: versão 2.

## Fontes

| Fonte | Versão | Uso |
|---|---|---|
| Roteiro de Métricas de Software do SISP | 3.0 (Portaria SGD/MGI nº 3.656/2026) | referência técnica subsidiária, sem fórmulas contratuais |
| NESMA, *Early Function Point Analysis* | 2015-07-15 (EN) | pesos da estimada e da indicativa |
| NESMA, *Contagem Antecipada de Pontos de Função* | tradução autorizada da anterior (FATTO) | idem |
| NESMA, *APF para Melhoria de Software* | 2.2.1 (PT, 2010) | fatores EFPA |

As cópias de trabalho em `/tmp/apf-fontes` foram removidas. O `PLANO.md` registra a URL completa só do guia EFPA (FATTO); para as demais fontes, registra apenas o site de origem (gov.br, site da NESMA, FATTO).

## Resultado dos evals

- **Testes unitários do script:** 95 passando (esquema, aritmética, fatores, cenários, renderização nos três formatos, robustez).
- **Interoperabilidade do xlsx:** na etapa 5, abriu no Excel sem reparo (D28). A versão final (esquema 2 e aviso) foi lida de novo com LibreOffice e openpyxl em 17/11/2026, com as cinco abas, o aviso e o vínculo "(ver P1)"; no Excel, não foi reaberta.
- **Evals do agente** (executor `claude-sonnet-5-5` via Claude Code; juiz Codex `gpt-6.1-sol`, calibrado):
  - **Critério não atendido:** S4 (pendências obrigatórias) do G04, pedido de uma frase. Na versão imediatamente anterior ao aviso D39 (com D38, rodada `completa-5`), a pendência "prestação de contas" faltou em 2 de 5 execuções do bloco; numa delas faltou também o cálculo do valor. A versão final (D39) não foi reavaliada pelo juiz; a limitação é conhecida e continua valendo. Nenhuma rodada completa (N = 5) foi aprovada com uma versão congelada.
  - **Sem regressão detectada** no diagnóstico `diag-1` (1 repetição): G01, G02, G03a, G03b, G05, G06, metamórficos M01–M04, exportação xlsx (A03) e relações M01–M05. Isso não demonstra estabilidade.
  - G07 e G08, casos originalmente reservados para medir transferência e depois incorporados à regressão, passaram em todos os critérios nas execuções feitas dos blocos das `completa-4` e `-5`.
  - O aviso fixo (D39) foi copiado sem alteração pelo executor em G01 e G04 (`k2-aviso`, K2 ok).

## Condição de uso

A lista de pendências **não é exaustiva**. Antes de usar a estimativa na análise de viabilidade, um analista revisa os requisitos e os fluxos específicos do domínio. Toda saída da skill traz esse aviso. O usuário aceitou essa condição para a versão inicial.

## Pendente

- Instalação no harness de uso: com o usuário (D11).
- Diretórios de execução dos evals em `/private/tmp/apf-evals` (cerca de 13 MB): os snapshots necessários já estão em `evals/agente/resultados/`; a remoção fica a critério do usuário.
- Iteração 2: descoberta de lacunas de domínio (roteiro do ciclo do processo ou modo entrevista), em `HANDOFF-iteracao-2.md`.
