# Handoff — iteração 2 da skill `nesma-apf-estimator` (em andamento)

Para quem retomar a iteração 2. Estado em 18/11/2026, commit `acb85b2` em diante. O histórico completo (decisões, rodadas, consultas ao popper) está no `PLANO.md`, nas seções "Iteração 2: …", "Rodada `curta-4`", "Rodadas `calib-7` e `k2-previa`", "correção experimental da representação" e "Bloco de descoberta `descoberta-1`". Regras de operação, comandos e armadilhas: `HANDOFF.md`.

## Objetivo

Melhorar a **descoberta de lacunas de domínio** em pedidos vagos (o requisito não atendido na iteração 1: S4 do G04). A iteração 1 terminou na versão inicial `38f562b`.

## Estado atual da skill

- **Variante adotada:** modo interativo (`interativo=sim|nao`, padrão `sim`), em que a skill mostra uma **prévia** sem PF (funções em termos de negócio, com o tipo APF entre parênteses) e pergunta em lotes de até 7 só o que muda a contagem; "não sei" vira pendência; "calcular" encerra. Lacunas geradas por um **roteiro do ciclo do processo** (03 §10), nos dois modos. Esquema canônico v3 (situação e lote das perguntas, esclarecimentos com IDs conferidos). Implementação: commit `451690d` (D40–D52).
- Depois disso: D55 (ajustes de rubrica, só para rodadas futuras) e D56 (mitigação do K2 na renderização: "parcial: motivo" e abertura curta da prévia).
- **Etapa 3B (revisão do modelo) foi testada e abandonada** (D57, D58): corrigiu parte da representação, mas induziu hipóteses sem apoio e não atingiu o critério. O `SKILL.md` foi revertido. Configuração dos evals na `descoberta-1`: `4eb6077f21f4f68d`; depois da D63: `20600eb43524d86f`.
- 140 testes unitários (`python3 -m unittest discover -s evals/unit`).

## Decisões (detalhes no `PLANO.md`)

| # | Em uma linha |
|---|---|
| D40–D42 | modo interativo, roteiro do ciclo, ferramenta de perguntas × texto (instrução fechada) |
| D43 | contrato do S4 v2: em pedido de pouco subsídio, obrigatórias só as das regras gerais; as do ciclo são diagnóstico; o contrato antigo é avaliado à parte (G04) |
| D44 | evals: camada 1 (um turno, termina na prévia); camada 2 (diálogo com simulador) só depois; metamórfica não interativo ≡ "não sei" em tudo |
| D45–D46 | holdouts H1–H3c (Ouvidoria, mesários, urnas; pouco, médio, rico; com contrastes), redigidos por `general-intern` de contexto limpo depois do congelamento da variante |
| D47–D52 | estado do diálogo, o que se pergunta, como as respostas entram, esquema v3, prévia, ajustes nos casos de argumentos |
| D53–D54 | juiz da camada 1 (S4 só ausências com pergunta, critério R de perguntas indevidas, medidas, S4+R conjunto); G04i/G07i/G08i com o contrato fixado em `casos.py` |
| D55–D56 | rubricas (H2/H2c aceitam consulta dos locais no registro; H3/H3c: ALI afirmado reprova S3, não K3; nota do G04i) e mitigação do K2 |
| D57–D58 | Etapa 3B testada e abandonada; S3 vira limitação conhecida |
| D59–D60 | S3 aceito como limitação (interativo padrão, experimental); ordem das fases restantes |
| D61–D63 | canal único das perguntas, exportação múltipla, correções pós-resultado, prévia por canal, opções fiéis, `apf.py novo` (experimentais) |

## O que os resultados mostram (e o que não mostram)

- **Calibração do juiz da camada 1:** `calib-6` 8/8 e `calib-7` 2/2.
- **Descoberta (alvo da iteração 2):** `descoberta-1`, H2 e H3 com N = 5: S4 5/5 e 4/5; R 5/5 e 4/5 (critério ≥ 4/5 atendido); S4+R 5/5 e 3/5. Nas 6 julgadas da `curta-4`, todas as lacunas obrigatórias foram encontradas, e G04i/G04 passaram também no S4 do contrato antigo (cálculo e prestação de contas) em 1 repetição.
- **Não mostram generalização:** H2 e H3 já tinham orientado decisões (expostos). Nada sobre camada 2 nem sobre o caminho com ferramenta.
- **Limitação conhecida — representação da incerteza (S3):** H2 2/5 e H3 3/5 no `descoberta-1`. Padrões: lacuna perguntada sem a hipótese que o texto implica; agrupamento tratado como certo; hipóteses sem apoio (CE de eleitor, AIE de zonas). Não foi corrigida; não apagar dos resultados.
- Falha recorrente no H3: a pendência de análise das ocorrências sai sem "por quem" (S4 ✗ em `ajuste-1` r1 e `descoberta-1` r2).
- Regressão do modo não interativo: nenhuma detectada (G01, G04, G06, G08, G03b, M03b; 1 repetição).

## Holdouts

- Expostos: H2, H2c, H3 (e G04, G07, G08 desde a iteração 1).
- **Nunca executados: H3c, H1, H1c.** Preservá-los até haver uma decisão que dependa deles.
- Para uma conclusão independente de generalização, usar esses e/ou holdouts novos, escritos por agente de contexto limpo com a variante congelada (D46), com rubrica aprovada pelo usuário antes de rodar.

## O que falta (ordem aprovada: D59, D60 no `PLANO.md`)

1. ~~**S3**~~: aceito como limitação conhecida (D59); `interativo=sim` segue padrão, marcado como experimental até a fase 3.
2. **Caminho com ferramenta de perguntas:** primeira checagem manual reprovada (lote e exportação em texto); corrigido experimentalmente na D61 (canal único 2B, exportação múltipla, correções pós-resultado 2C); na T2, exportação ok, correção parcial (resultado não copiado), lote de novo em texto; na T3 (D62) o lote veio pela ferramenta, mas com opções criadas e, de novo, sem o resultado da correção no chat; D63 a checar em sessão limpa. Achados laterais registrados no `PLANO.md` (fase 2) para a camada 2 mínima.
3. **Camada 2 mínima** (teste parcial, turnos roteirizados, `--resume` no runner): "não sei; calcular" × modo direto; incorporação dos fatos do H2c no H2 × gabarito do H2c; percurso de dois lotes.
4. **Regressão ampliada do modo direto**, depois da fase 3: G02, G03a, G05, M01, M02, M03a, M04, G01, G06, M03b.
5. **Holdouts** com a variante congelada: H1, H1c, H3c (regras gerais e contenção) e ao menos um holdout novo com etapa ausente obrigatória (descoberta de etapas), rubrica aprovada pelo usuário.
6. **Encerramento:** relatório da iteração 2 e atualização do `RELATORIO`/README; guia de uso da skill (lista de tarefas do projeto).

Cada fase precisa de critério e próxima decisão fixados e de autorização própria antes de executar.

## Lições da iteração 2 (somam-se às da iteração 1)

- Nada de regra em prosa por falha observada; a 3B reproduziu o ciclo (corrige o alvo, cria erro novo).
- Fixar o critério de leitura **antes** de rodar; uma repetição não sustenta causa nem estabilidade.
- Mudança de rubrica depois de ver o resultado só vale para rodadas futuras.
- Dossiês de calibração positivos precisam ser coerentes com as regras da própria skill (o P5 errado custou duas rodadas).
- Custo real: cerca de 1 ponto da janela de 5 h por execução (Claude) e 1 por juiz (Codex).
