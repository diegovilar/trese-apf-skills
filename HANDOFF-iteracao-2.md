# Handoff — iteração 2 da skill `nesma-apf-estimator`

Para quem for retomar a skill depois da versão inicial (iteração 1, encerrada em 17/11/2026). Leia também o `PLANO.md` (decisões D1–D39 e o histórico das rodadas) e o `HANDOFF.md` (regras de operação dos evals, arquitetura e armadilhas). Este arquivo trata só do que a iteração 2 precisa decidir e testar.

## Objetivo da iteração 2

Melhorar a **descoberta de lacunas de domínio** em pedidos vagos, o requisito que a versão inicial não atendeu. O contrato do S4 continua o mesmo: todas as pendências obrigatórias do gabarito precisam aparecer, avaliadas pelo significado (decisão do usuário na consulta 12).

## Ponto de partida (versão inicial)

- Base técnica: commit `38f562b` (esquema canônico versão 2 e aviso fixo de pendências não exaustivas, D39). Os commits seguintes da iteração 1 são só documentação.
- Os resultados brutos (`evals/agente/resultados/`) ficam fora do git. Para retomar em outro ambiente, preserve essa pasta separadamente; sem ela, só restam os resumos do `PLANO.md`.
- **Não atendido:** S4 do G04. A pendência "prestação de contas" faltou em 4 de 9 execuções desde a D37; o cálculo do valor faltou em pelo menos 2 delas (`completa-4` r3 e `completa-5` r4). Esses resultados são das versões com D37 e D38; a D39 (aviso) só passou pela checagem direcionada do K2, sem juiz.
- **Passou nos blocos ou diagnósticos mais recentes:** G07 e G08 (blocos das `completa-4` e `-5`); G01, G02, G03a, G03b, G05, G06, M01–M04, A03 e as relações M01–M05 no `diag-1`, com 1 repetição. Isso mostra ausência de regressão detectada, **não** estabilidade: nenhuma rodada completa foi aprovada com uma versão congelada.
- O que foi observado nos blocos recentes (`completa-4`, versão com D37; `completa-5`, com D38): as pendências que decorrem de regra geral da skill (origem dos dados, D33; alcance do verbo amplo, D33; pessoa ligada ao registro, D36; análise ou decisão sobre registros submetidos, D37) e os contrastes do G08 (não perguntar o que o pedido responde).
- Condição de uso aceita pelo usuário: revisão humana obrigatória das lacunas antes de usar a estimativa na análise de viabilidade.

## Lições da iteração 1 (não repetir)

- Cinco iterações de "regra nova em prosa para a pendência que faltou" resolveram cada alvo e fizeram aparecer outra lacuna. Não continue nesse ciclo: escolha um desenho e teste-o com holdout.
- A D37 (pendência específica de análise ou decisão) parece ter tomado o lugar da pendência ampla que antes cobria aprovação, cálculo e prestação de contas. É hipótese, não causa comprovada.
- A D38 (vínculo obrigatório entre item `sem-evidencia` e pendência) garante consistência de IDs, não de significado, e tem rota de fuga: o executor pode tirar o item da lista.
- G04 e G07 já orientaram correções e não são mais holdout. G08 foi escrito antes de rodar, mas também já foi visto. Toda variante nova precisa de pelo menos um **holdout novo**, com rubrica aprovada pelo usuário antes da primeira execução, e de contrastes (o que **não** perguntar).

## Variantes a avaliar

Não fixe a sintaxe de argumento antes de decidir a variante.

1. **Roteiro do ciclo do processo nas pendências** (sem mudar a D15). Antes de fechar as pendências, a skill percorre um roteiro genérico. Candidato, ainda não decidido: entrada do registro, análise ou decisão, o que vem depois da decisão (pagamento, prestação de contas, arquivamento, recurso), dados de terceiros, cálculos, relatórios e notificações. Ela pergunta só o que o pedido não responde. Risco: lista longa e genérica, com perguntas redundantes. Medir também o excesso.
2. **Modo entrevista opcional**, guiado pelo mesmo roteiro. Antes de estimar, a skill faz perguntas abertas ao demandante ("o que acontece depois da concessão?") e usa as respostas na estimativa. As respostas podem encolher a faixa ou ampliá-la, se revelarem funções novas. Muda a D15 (hoje só se pergunta quando a lacuna impede definir fronteira ou tipo) e precisa da decisão do usuário. O modo atual continua valendo quando só há um documento e ninguém para responder.

Consulta 17 ao popper: a entrevista pode ajudar porque perguntas abertas revelam etapas que o modelo não anteciparia, mas não foi testada. Nada nos resultados mostra que o modelo falharia do mesmo jeito numa conversa.

## Como avaliar

- **Variante 1:** mesmos critérios de hoje (K1–K4, S1–S5) sobre G04, G07, G08 e um ou mais holdouts novos. Acrescente uma medida de perguntas redundantes ou genéricas, com a definição aprovada antes.
- **Variante 2:** desenho novo de eval. Mesmo pedido inicial → perguntas da skill → respostas controladas (roteiro de respostas por caso, escrito antes) → estimativa final. Medir a cobertura das lacunas, as perguntas redundantes, o esforço do demandante (número de perguntas) e o efeito na estimativa, sem pressupor que ela diminua. O S4 não pode ser aplicado literalmente: cada aspecto obrigatório do gabarito precisa estar **resolvido pela resposta e refletido na estimativa**, ou continuar explicitamente pendente; exigir a pendência de algo já respondido seria erro do critério. O runner atual roda `claude -p` sem diálogo: será preciso simular o demandante (outro agente com o roteiro de respostas) ou usar sessões com várias mensagens. Respostas simuladas servem para o teste controlado; a utilidade real se confirma depois, com pessoas.
- O juiz foi recalibrado para o S4 pelo significado (`calib-3`). Critério novo pede calibração delta própria.

## Operação e custo (dados da iteração 1)

- Regras do `HANDOFF.md` continuam valendo: ok do usuário por fase, leitura de cota antes de cada tarefa (parar abaixo de 15%), uma tarefa por chamada, popper para recomendações (abra um novo e continue a numeração a partir da consulta 19).
- Bloco de 3 casos × 5 repetições (15 execuções + 15 juízes): cerca de 8 pontos da janela de 5 h do Claude e 7 do Codex. Rodada completa: 220 tarefas.
- Bloco com parada antecipada (qualquer K, ou o mesmo S reprovado 2 vezes no mesmo caso) evitou gastar rodadas inteiras já reprovadas.
- Execução inválida: `runner.py repetir <rodada> <tarefa>`.
- Resultados brutos de todas as rodadas em `evals/agente/resultados/` (fora do git), úteis como linha de base.

## Primeiras decisões a levar ao usuário

1. Qual variante testar primeiro (ou as duas, comparadas).
2. Se a variante 2 for escolhida: mudar a D15 e como simular o demandante.
3. O holdout novo e seus contrastes, com rubrica aprovada antes de rodar.
