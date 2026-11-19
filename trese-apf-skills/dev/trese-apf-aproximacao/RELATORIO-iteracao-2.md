# Relatório final — iteração 2 da skill `trese-apf-aproximacao`

> Registro histórico: referências de caminhos podem refletir a estrutura anterior à reorganização de 19/11/2026; veja o mapa na D73 do `PLANO.md`.

18/11/2026. Iteração **encerrada** por decisão do usuário (D71), **sem aprovação integral**: o alvo da iteração teve sinal favorável, mas a contenção (perguntas e hipóteses indevidas) não foi demonstrada e há limitações conhecidas (ver "Resultado dos evals"). Skill congelada no estado do commit `0c5a3b3`. Detalhes, decisões (D40–D71) e todas as rodadas em `PLANO.md`; relatório anterior em `RELATORIO-iteracao-1.md`. Documentação de uso: `README.md` e `GUIA-DE-USO.md`.

## Objetivo

Melhorar a **descoberta de lacunas de domínio** em pedidos vagos: o critério não atendido na iteração 1 era o S4 do G04 ("Como servidor, quero gerenciar minhas solicitações de diárias"), em que a skill deixava de registrar partes do processo que o pedido silencia.

## O que mudou na skill

- **Modo interativo** (`interativo=sim`, padrão): a skill mostra uma **prévia** sem PF (funções em termos de negócio e lacunas) e faz perguntas ao analista em lotes de até 7. As respostas viram esclarecimentos que atualizam o modelo; "não sei" deixa a pendência sem resposta; "calcular" encerra as perguntas. `interativo=nao` mantém o fluxo direto da iteração 1.
- **Roteiro do ciclo do processo** (03 §10), nos dois modos: entrada, dados de terceiros, análise ou decisão, o que vem depois, cálculos, consultas, avisos e dados existentes. O roteiro só gera pendências e perguntas, nunca funções.
- **Canal único das perguntas**: com ferramenta de perguntas no harness, a prévia só anuncia o lote e as perguntas vão pela ferramenta com o texto e as opções do JSON; sem ela, vão numeradas no texto.
- **Correções depois do resultado**: o analista indica o item e a correção; o esclarecimento é atualizado, o resultado inteiro é refeito e a exportação é perguntada de novo (com `saida=`, reexporta direto); arquivos anteriores preservados.
- **Exportação** de seleção múltipla (`.md`, `.txt`, `.xlsx`); legenda só com os termos usados (no xlsx, também os das colunas fixas).
- `apf.py novo`: diretório de trabalho exclusivo por estimativa.
- Esquema canônico versão 3 (estado das perguntas e esclarecimentos).

| Arquivo | Tamanho |
|---|---:|
| `trese-apf-aproximacao/SKILL.md` | 19,3 kB |
| `references/01-fundamentos-e-identificacao.md` | 12,3 kB |
| `references/02-regras-nesma.md` | 8,6 kB |
| `references/03-casos-de-borda-e-convencoes.md` | 15,6 kB |
| `references/04-exemplos-praticos.md` | 11,2 kB |
| `references/05-saida-e-legenda.md` | 16,0 kB |
| `scripts/apf.py` | 76,5 kB |

Texto da skill (SKILL.md e references): cerca de 12,9 mil palavras. Fontes: as mesmas da iteração 1.

## Resultado dos evals

Executor `claude-sonnet-5-5` via Claude Code; juiz Codex `gpt-6.1-sol`, recalibrado para a prévia (camada 1). **154 testes unitários** passando. Cada número abaixo vale para a rodada e a versão indicadas no `PLANO.md`; repetições de versões diferentes não foram somadas.

**Descoberta (alvo da iteração).**
- Casos de ajuste H2 e H3 (`descoberta-1`, N = 5): S4 (lacunas obrigatórias perguntadas) 5/5 e 4/5; R (sem perguntas indevidas) 5/5 e 4/5. Critério atendido, mas os dois casos estavam expostos: mede estabilidade neles, não generalização.
- **Holdout novo H4** (eliminação de documentos em papel; redigido por agente de contexto limpo, aprovado pelo usuário antes de rodar; `holdout-h4`, N = 5): a etapa-alvo (registro de resultados parciais com o lote aberto) foi **perguntada em 5/5**. É um **sinal de transferência** da descoberta de uma etapa para um domínio novo, num padrão de lacuna próximo ao do H3; não demonstra descoberta de etapas em geral.
- G04 (o caso da iteração 1): no modo direto, S4 aprovado na `regressao-1`, versão final, 1 execução. Na camada 1, o G04i passou no S4 v2 e no contrato antigo uma vez na `curta-4` e uma vez na `ajuste-1`, ambas em versões anteriores; não foi julgado na versão final. Nada disso prova que a limitação da iteração 1 foi superada.

**Contenção — não demonstrada.**
- H4: R **2/5** e S4+R **2/5** (sem recontagem). As reprovações vêm de perguntas sobre o que acontece com lotes retidos, cálculo de saldo e correção de registros. O juiz tratou de forma diferente perguntas equivalentes (aprovou no r1, reprovou no r3 e no r4), sobre um ponto em que a rubrica distingue mal "não contar" de "não perguntar"; duas reprovações são defensáveis (opção que contraria a origem em papel; pergunta que amplia o pedido).
- H1c (contraste com as lacunas obrigatórias do H1 respondidas): **K3 reprovado em 3/3**. A skill contou, como hipótese, uma consulta autônoma da equipe que o pedido não sustenta: **inflação por hipótese sistemática** neste caso. H1 (pouco subsídio): aprovado em tudo (N = 1).
- H3c: sem medida. A única execução reprovou no K2 por procedência (o executor editou o JSON depois de renderizar a prévia) e não foi julgada.

**Representação da incerteza (S3) — limitação conhecida (D59).** Alternativas que a pergunta deixa em aberto nem sempre viram hipótese com efeito nos cenários: H4 0/5; H2 2/5 e H3 3/5 na `descoberta-1`. Uma tentativa de correção por regra em prosa (etapa 3B) foi abandonada (D58): com ela apareceram hipóteses sem apoio no texto, embora o mesmo tipo de inflação tenha reaparecido sem ela.

**Modo direto — sem regressão grosseira detectada** (`regressao-1`, N = 1): G01–G06, G08, M01–M04, A03 e as relações M01–M05 aprovados. G07 ficou de fora (lacuna declarada). Não demonstra estabilidade.

**Diálogo e caminho com ferramenta.**
- Camada 2 mínima (diálogos roteirizados): preservação com "não sei", incorporação de respostas, correção e segundo lote funcionaram na primeira repetição de cada rodada; o critério N = 3 não foi atendido por falhas de cópia de frases fixas (K2) e a camada foi encerrada com limitação (D67).
- Checagens manuais no OpenCode: T1–T3 reprovaram em pontos sucessivos, corrigidos de forma estrutural. **T4 atendeu os critérios da D61–D63** (lote pela ferramenta com opções fiéis, diretório único, exportação múltipla, resultado corrigido no chat antes da exportação). **T5 atendeu os critérios C1–C6** fixados antes (também resposta livre, "não sei", hashes dos arquivos preservados e correção com −4 PF nos dois extremos). Uma execução cada: sinal funcional, não estabilidade. O T5 **não testou contenção**: apareceu uma consulta autônoma da chefia como hipótese, da mesma família do H1c, não julgada.

**Cópia literal (K2).** Até a D67, as falhas foram alterações ou omissões do executor em trechos fixos de orientação; desde então, essas frases são verificadas pelo sentido, e o conteúdo técnico continua exigindo cópia literal. Depois disso, o H3c-r1 falhou por procedência (JSON alterado depois do render).

## Limitações conhecidas

1. **Contenção**: a skill pode contar como hipótese funções que o pedido não sustenta (H1c 3/3) e fazer perguntas que ampliam o pedido ou que a rubrica considera indevidas (R do H4 2/5).
2. **Representação da incerteza (S3)**: uma lacuna perguntada nem sempre vira alternativa nos cenários; o máximo pode variar conforme a lacuna vira hipótese ou só pendência.
3. **Descoberta**: evidência em casos expostos e num único holdout novo, com padrão próximo a um caso de ajuste.
4. Achados menores sem correção: fronteira assumida sem perguntar; IDs renumerados em correções; perguntas do lote reordenadas na ferramenta.

O modo interativo continua **experimental** (D59, D67): a camada 2 foi encerrada com o critério N = 3 não atendido, e a estabilidade do diálogo não foi medida.

## Condição de uso

Igual à da iteração 1, reforçada: a lista de pendências **não é exaustiva**, e as hipóteses e o máximo do intervalo precisam de revisão. Antes de usar a estimativa na análise de viabilidade, um analista revisa os requisitos, os fluxos do domínio e cada hipótese contada. Toda saída traz o aviso.

## Pendente

- Trabalho futuro, se houver iteração 3, com desenho próprio e não por regra em prosa: contenção de hipóteses e perguntas; representação da incerteza; correção mostrando só o que mudou (exige IDs estáveis); a metamórfica "não interativo ≡ não sei" sobre execuções reais; H3c e H1 com N > 1.
- Diretórios de execução dos evals em `/private/tmp/apf-evals` e cópias do T5 em `/tmp/t5`: os snapshots necessários estão em `evals/agente/resultados/` (fora do git); a remoção fica a critério do usuário.
