# Evals da skill `nesma-apf-estimator`

Três camadas, separadas:

| Camada | O que testa | Onde | Como rodar |
|---|---|---|---|
| Unitários | esquema, aritmética, tabelas EFPA, cenários, renderização, xlsx, CLI, consistência entre `references/` e o script | `evals/unit/` | `python3 -m unittest discover -s evals/unit` |
| Interoperabilidade | o `.xlsx` abre e os valores lidos batem | manual + openpyxl/LibreOffice | ver `PLANO.md` (D28) |
| Agente | a skill executada de verdade por um modelo, sobre os gabaritos aprovados | `evals/agente/` | runner abaixo |

Gabaritos aprovados: `evals/gabaritos-iniciais.md` (revisão 4 no G04; G07, holdout, aprovado em 17/11/2026).

## Estrutura do código (após a consulta 7 ao popper)

`execucao.py` (o que o executor recebe; hash de execução), `juiz.py` (o que o juiz recebe; hash do juiz e do dossiê), `verificador.py` (critérios automáticos sobre snapshots congelados; mudar exige só `runner.py reverificar <rodada>`), `runner.py` (orquestração e estado). Como retomar uma rodada: `HANDOFF.md` na raiz.

## Evals do agente (desenho revisado após a consulta 6 ao popper)

### Princípios

- **Uma tarefa por chamada.** A unidade de trabalho do runner é **uma** execução do executor **ou uma** chamada do juiz. O orquestrador lê a cota antes de cada uma (Claude antes do executor, Codex antes do juiz). Abaixo de 15% em qualquer janela (5 horas ou semanal), ou se a leitura da cota falhar, para. Sondagens (perfil de execução, nome do modelo do juiz) também são tarefas e seguem a mesma regra.
- **Retomada por fases.** Cada tarefa tem estado próprio: `executado` → `coletado` → `verificado` → `julgado`. Retomar continua da fase pendente, sem repetir consumo e sem pular julgamento. O checkpoint guarda o hash dos casos, das rubricas, do runner, da configuração e da skill; o runner se recusa a misturar resultados de configurações diferentes.
- **Falha operacional ≠ falha semântica.** Timeout, erro de autenticação, parada por cota, contaminação (acesso indevido) e falha do juiz são registrados como **inválidos**, com o motivo. Nunca contam como aprovação e nunca somem do denominador.

### Perfil de execução do executor (a validar com uma sondagem autorizada)

- Claude Code headless: `claude -p "<invocação>" --model <sonnet 5.5> --effort high --output-format stream-json --verbose --no-session-persistence --setting-sources project --tools Read,Write,Edit,Glob,Grep,Bash --permission-prompts none`, com `cwd` num diretório temporário novo.
- **Sem `--bare`:** esse modo ignora o login OAuth e exige chave de API, o que fugiria da cota monitorada. A sondagem confirma qual credencial e modalidade de consumo estão em uso e se a skill do projeto é descoberta. O perfil validado fica registrado e fixo; não há fallback silencioso.
- `--setting-sources project` evita carregar hooks, plugins e configurações do usuário. A sondagem verifica também se o CLAUDE.md global do usuário entra no contexto e, se entrar, registra isso.
- A cópia da skill vai para `.claude/skills/nesma-apf-estimator/` no diretório temporário. O hash dela é conferido antes e depois de cada execução: se mudou, a execução é inválida.
- **Isolamento por auditoria.** `--tools` restringe as ferramentas disponíveis, mas não confina o Bash. Por isso o runner audita o trace: qualquer leitura, comando ou caminho fora do diretório temporário (exceto o interpretador Python), e qualquer acesso à rede, torna a execução **contaminada** (inválida). Os gabaritos ficam fora do diretório temporário. O que se mede é o **acesso observável**.

### Juiz

- `codex exec -m gpt-6.1-sol -c model_reasoning_effort="high" --ephemeral --skip-git-repo-check --sandbox read-only --json --output-schema <veredito.schema.json> -C <diretório vazio>`.
- **Dossiê autocontido no prompt:** invocação exata, subsídio completo, gabarito e rubrica do caso, convenções aplicáveis (C1 a C4), JSON canônico produzido e resposta final do executor. Nada de outras execuções.
- O trace `--json` do juiz é auditado: comando ou leitura de arquivo invalida o julgamento.
- Para S5 (rastreabilidade), o juiz compara cada trecho citado no JSON com o subsídio original e marca citações inexistentes ou distorcidas.
- **Calibração antes do uso:** o juiz roda sobre dossiês com resultado conhecido, ao menos 2 corretos e 5 com erro plantado: funções trocadas mantendo tipos e total; citação inventada; função proibida contada; pendência obrigatória omitida; cenário impossível com soma correta. Se não acertar todos, o juiz não é usado até ajustarmos o prompt ou a rubrica.

### Critérios automáticos (sem juiz)

| Critério | Verificação |
|---|---|
| K1, estágio 1 | o subsídio vem em **arquivo**; resposta só com o bloco `ALERTA`; nenhum acesso ao arquivo do subsídio; nenhuma chamada a `apf.py`; nenhum arquivo criado; nenhuma contagem na resposta (sem tabela, sem números de PF) |
| K1, estágio 2 | resposta só com `ALERTA`; leitura do subsídio permitida; nenhuma chamada a `apf.py`; nenhum arquivo criado; nenhuma contagem |
| K1, execução válida | houve `apf.py check` e `apf.py render`; sem alerta |
| K2 integridade | o JSON capturado passa em `apf.py check`; o runner reexecuta o renderizador confiável sobre ele e exige que o bloco Markdown inteiro apareça **literalmente** na resposta final (texto operacional só depois, como a pergunta sobre exportação) |
| K2 exportação | com `saida=`: o `.md` e o `.txt` exportados são idênticos ao render confiável; no `.xlsx`, o conteúdo das planilhas (XML) é idêntico ao gerado pelo exportador confiável |
| K4 unidade e rótulo | derivados do JSON pelo script e garantidos pela comparação do K2 |
| S1 pré-filtro | o multiconjunto de pares (tipo, operação) do JSON é igual ao do gabarito (nos casos com total fixo). A correspondência nome a nome fica com o juiz |
| S2 | total (ou mínimo e máximo) igual a um dos aceitos |

### Critérios do juiz

K3 (nenhuma função proibida contada), S1 nome a nome (e por rubrica em G03b e G04), S3 (hipóteses e cenários coerentes), S4 (pendências obrigatórias) e S5 (rastreabilidade contra o subsídio). Veredito em JSON: um booleano por critério, justificativa curta e citação do trecho que a sustenta.

### Casos

- Contagem: G01, G02, G03a, G03b, G04, G05, G06.
- Argumentos: A01–A15 (com A13 em a/b). Os casos que executam usam um pedido curto, para custar pouco. Nos casos de alerta de estágio 1, o subsídio é passado como arquivo, para que a ausência de leitura seja observável.
- Linguagem natural (novos, a validar pelo usuário): L01, prosa com "gere em planilha" → só o pedido de confirmação com `saida=xlsx`, sem executar; L02, prosa só descrevendo um sistema novo → executa com os padrões, sem pedir confirmação.
- Metamórficos, cada par com a sua relação:
  - M01 (G01 parafraseado): mesmo multiconjunto (tipo, operação) e mesmo total.
  - M02 (G01 com uma frase repetida): mesmo multiconjunto e mesmo total.
  - M03 (G01 com `saida=md` × `saida=txt`): mesmo JSON, a menos de textos livres; mesmos valores.
  - M04 (G06 sem as frases do menu e da mensagem): mesmo multiconjunto e mesmo total.
  - M05 (G02 × G03a): mesmo inventário de funções; G03a acrescenta só Cancelar (EE, A); G02 = 20 PF de melhoria; G03a = 14,75 PFM.

### Modo interativo (iteração 2, D40–D52)

- O padrão da skill passou a ser `interativo=sim`. Os casos que testam contagem, metamórficos e argumentos explícitos fixam `interativo=nao`; os casos de alerta ficam como estavam.
- A04, A14 e L02 testam o padrão e terminam na **prévia** (`"previa": True` em `casos.py`). K1: `check` e `render --format previa` no trace, nenhum render final, nada exportado, nenhum número de PF na resposta. K2: a prévia confiável, gerada do JSON escolhido pelo conteúdo, aparece literalmente na resposta. O verificador registra o lote (número, perguntas, abertas restantes).
- **Camada 1** (holdouts e G04/G07/G08 com `interativo=sim`): um turno, o executor sem ferramenta de perguntas, termina na prévia. O juiz avalia as lacunas obrigatórias sobre **todas** as pendências do JSON (não só as do primeiro lote), os contrastes, a redundância e o tamanho do lote. Rubrica e calibração delta ainda por fazer (D43).
- Ainda não implementados: camada 2 (diálogo com `--resume` e demandante simulado), relação metamórfica não interativo ≡ interativo com "não sei" sobre execuções reais, checagem do caminho com ferramenta (com o usuário). A relação metamórfica tem só a versão no nível do script, nos testes unitários.

### Rodadas

1. **Sondagens:** perfil do executor (1 execução curta) e nome do modelo do juiz (1 chamada mínima).
2. **Calibração do juiz:** cerca de 7 chamadas.
3. **Curta:** 1 execução por caso (cerca de 32) e as chamadas do juiz correspondentes (cerca de 12). Serve para achar falhas grosseiras, não para declarar estabilidade.
4. **Completa:** N = 5. Os críticos (K) precisam passar em todas as execuções válidas; os semânticos (S), em pelo menos 4 de 5. Execuções inválidas são relatadas à parte e repetidas.
