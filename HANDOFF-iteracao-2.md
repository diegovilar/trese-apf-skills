# Handoff — iteração 2 da skill `nesma-apf-estimator` (encerrada)

Para quem retomar a iteração 2. Estado em 18/11/2026, fim da sessão que fez as consultas 32 a 44 ao popper. O histórico completo (decisões D40–D68, rodadas, consultas) está no `PLANO.md`; as seções desta sessão começam em "Plano de continuação da iteração 2 (consultas 32 a 34)". Regras de operação, comandos e armadilhas: `HANDOFF.md`.

## Próximo passo

**T5 concluído (C1–C6 atendidos, sessão `ses_e0f8024bcffei2fNg5HrMY4Dbu`; ver PLANO.md).** **Iteração 2 encerrada em 18/11/2026, sem aprovação integral** (D71, consulta 56): relatório (`RELATORIO-iteracao-2.md`), `README.md` e `GUIA-DE-USO.md` prontos. Modo interativo continua experimental. Decisão do usuário (D72): **parar aqui**. Nenhuma rodada nem trabalho novo autorizado. Opções futuras registradas: piloto curto em paralelo ao fluxo habitual (recomendado na consulta 57) e iteração 3 (contenção, representação da incerteza), com desenho próprio. Popper da sessão de 18/11 (tarde): `ses_e0fdc0bfbffeasgGVovR3zMH6f` (consultas 45 a 57); numa sessão nova, abra outro e continue da **consulta 58**.

Feito nesta sessão (detalhes no `PLANO.md`, seções "Rodada `regressao-1`" em diante):
- **Fase 4 (`regressao-1`)**: sem regressão grosseira nos casos cobertos (N = 1; G02 reposto pela D69; G07 lacuna declarada).
- **Fase 5**: H4 redigido por agente de contexto limpo (duas devoluções) e aprovado (D70). `holdout-h4` (N = 5): E1 perguntada 5/5, hipótese B 0/5, R 2/5 (juiz inconsistente sobre ambiguidade da rubrica). `holdout-gerais`: H1-r1 ✓; **H1c K3 3/3 ✗** (CE autônoma da equipe como hipótese); H3c-r1 K2 ✗ por procedência (JSON editado após o render), sem juiz. Fase 5 encerrada sem correção da skill (D71); limitações principais: inflação por hipótese, contenção das perguntas, S3.
- `config_hash` atual dos evals: `87654cd6ba3cf1a0` (inclui o H4); a skill não muda desde `0c5a3b3`.

## Objetivo da iteração

Melhorar a **descoberta de lacunas de domínio** em pedidos vagos (o requisito não atendido na iteração 1: S4 do G04). A iteração 1 terminou na versão inicial `38f562b`.

## Estado atual da skill (commit `0c5a3b3` em diante)

- **Modo interativo** (`interativo=sim`, padrão, marcado como experimental na D59): prévia sem PF e perguntas em lotes de até 7; roteiro do ciclo do processo (03 §10) nos dois modos; esquema v3.
- **Canal único das perguntas** (SKILL.md 2B, D61–D63): texto primeiro, pergunta pela ferramenta se houver (senão texto numerado), depois espera; vale para tipo/fronteira, lotes, exportação e correção ambígua. Com ferramenta, a prévia sai com `render --format previa --canal ferramenta` (só anuncia o lote) e a ferramenta recebe as perguntas com texto e opções do JSON (lista vazia quando não há opções).
- **Exportação** de seleção múltipla (`.md`, `.txt`, `.xlsx`, "Nenhum" exclusivo).
- **Correções depois do resultado** (SKILL.md 2C): esclarecimento atualizado no lugar (vale a última resposta; versionamento fica fora da skill), identificação refeita, resultado inteiro de novo e só então exportação (com `saida=`, reexporta direto; sem, pergunta de novo). Linha fixa no chat: "Para solicitar recálculo, informe o item (ID ou descrição) e a correção desejada. Depois, você pode exportar novamente."
- **`apf.py novo`**: diretório de trabalho exclusivo por estimativa (evita colisão de JSON em `/tmp`).
- **Legenda enxuta** em chat, md e txt (só termos usados, definição completa); xlsx com os termos das colunas fixas (D64).
- **K2 por categorias** (D67): conteúdo técnico e avisos obrigatórios literais; frases fixas de orientação com o sentido correto (podem ser adaptadas, não omitidas); `PREVIA_INTRO` retirada.
- 154 testes unitários. `config_hash` atual: `5be257e4fb57843d` (na `descoberta-1` era `4eb6077f21f4f68d`).

## Decisões (detalhes no `PLANO.md`)

| # | Em uma linha |
|---|---|
| D40–D42 | modo interativo, roteiro do ciclo, ferramenta de perguntas × texto |
| D43 | contrato do S4 v2 (pouco subsídio: obrigatórias só as das regras gerais) |
| D44 | evals: camada 1 (prévia); camada 2 (diálogo); metamórfica não interativo ≡ "não sei" |
| D45–D46 | holdouts H1–H3c, redigidos por agente de contexto limpo |
| D47–D52 | estado do diálogo, perguntas, respostas, esquema v3, prévia |
| D53–D54 | juiz da camada 1 (S4 com pergunta, R, medidas); G04i/G07i/G08i |
| D55–D56 | ajustes de rubrica; mitigação do K2 |
| D57–D58 | Etapa 3B testada e abandonada; S3 vira limitação conhecida |
| D59–D60 | S3 aceito como limitação (interativo padrão, experimental); ordem das fases restantes |
| D61–D64 | canal único, exportação múltipla, correções pós-resultado, prévia por canal, opções fiéis, `apf.py novo`, legenda enxuta |
| D65–D67 | camada 2 mínima, linha de correção simplificada, encerramento da camada 2 com limitação, K2 por categorias |
| D68 | fase 4: `regressao-1` especificada e autorizada para a próxima sessão |

## O que os resultados mostram (e o que não mostram)

- **Descoberta (alvo da iteração):** `descoberta-1`, H2 e H3 com N = 5: S4 5/5 e 4/5; R 5/5 e 4/5 (critério atendido); S4+R 5/5 e 3/5. H2/H3 expostos: não mostram generalização.
- **Caminho com ferramenta de perguntas** (checagens manuais T1–T4 no OpenCode, sessões listadas no `PLANO.md`): T1–T3 reprovaram em pontos sucessivos (lote em texto; opções criadas; resultado da correção não copiado); **T4 atendeu todos os critérios** (1 execução: sinal funcional, não estabilidade). T5 manual fica para o fim, com a versão final.
- **Camada 2 mínima** (diálogos roteirizados, sem simulador): `camada2-1` (8 turnos, 1 falha K2) e `camada2-2` (11 turnos, 1 falha K2), contadas separadamente. Em cada uma, a repetição 1 completa atendeu as relações: D2a preservação ("não sei" não muda o modelo), D2b incorporação (juiz H2c aprovado em tudo), D2d correção (−4 PF, só a função certa), D2c segundo lote exercitado (fluxo, não conteúdo). **Critério global N = 3 não atendido**; encerrada com limitação aceita pelo usuário (D67). A metamórfica da D44 (não interativo ≡ "não sei") continua pendente sobre execuções reais.
- **K2:** todas as falhas da iteração foram em frases fixas de orientação reescritas ou omitidas pelo executor, nunca em números, tabelas ou JSON. Daí o K2 por categorias (vale para frente; as reprovações passadas ficam).
- **Limitação conhecida — representação da incerteza (S3):** H2 2/5 e H3 3/5 no `descoberta-1`; nas checagens manuais, o máximo variou (42 × 50 PF) conforme consultas viravam hipótese ou pendência. Não corrigida; não apagar.
- Achados laterais registrados para trabalho futuro (PLANO.md, fase 2 e camada 2): fronteira assumida e não atualizada após respostas; pendência composta marcada como respondida em parte; IDs renumerados na correção; cobertura "parcial" quando o gabarito do H2c considera completa.
- Regressão do modo direto: ainda não medida na versão atual (fase 4).

## Holdouts

- Expostos: H2, H2c, H3 (e G04, G07, G08 desde a iteração 1).
- **Nunca executados: H3c, H1, H1c.** H1, H1c, H3c medem regras gerais e contenção, não descoberta de etapas; para esta, falta ao menos um holdout **novo** com etapa ausente obrigatória (D60), escrito por agente de contexto limpo, rubrica aprovada pelo usuário.

## O que falta (ordem da D60)

1. ~~S3~~: aceito como limitação (D59).
2. ~~Caminho com ferramenta~~: T4 atendeu (D61–D63); T5 manual no fim.
3. ~~Camada 2 mínima~~: encerrada com limitação (D65–D67).
4. ~~Regressão ampliada do modo direto~~: `regressao-1` concluída.
5. ~~Holdouts~~: encerrada com limites (D70, D71).
6. ~~Encerramento~~ (concluído em 18/11): T5 manual (lote, resposta livre, exportação, correção), relatório da iteração 2, `RELATORIO`/README, guia de uso.

Pendências de produto, para depois: correção mostrando só o que mudou (exige IDs estáveis e decidir onde fica o resultado completo quando não se exporta); outras reduções de volume.

## Lições da iteração 2 (somam-se às da iteração 1)

- Nada de regra em prosa por falha observada; a 3B reproduziu o ciclo (corrige o alvo, cria erro novo). Conflitos entre instruções, porém, se corrigem (o passo 3 da 2A × ferramenta).
- O que funcionou contra comportamentos do executor foi **estrutural**: tirar do texto copiado o que o atrai (prévia `--canal ferramenta` sem as perguntas; `apf.py novo`), não reforçar prosa.
- Fixar o critério e a **regra de parada** antes de rodar; uma repetição não sustenta causa nem estabilidade.
- Mudança de rubrica ou de critério depois de ver o resultado só vale para rodadas futuras.
- Contar por rodada e por versão; não somar repetições de versões diferentes.
- Custo medido nesta sessão: cerca de 0,7–1 ponto da janela de 5 h do Claude por turno (com a orquestração) e cerca de 1 ponto do Codex por juiz.
