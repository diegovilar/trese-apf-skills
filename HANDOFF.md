# Handoff — skill `nesma-apf-estimator`

Para retomar o trabalho em outra sessão (humana ou de agente). Leia também o `PLANO.md`, que guarda todas as decisões (D1 a D68) e o andamento.

## Onde estamos

**Iteração 2 em andamento** (estado e próximos passos: `HANDOFF-iteracao-2.md`). A iteração 1 foi encerrada em 17/11/2026 como versão inicial (`38f562b`; `RELATORIO-iteracao-1.md`). Fases 4 e 5 concluídas em 18/11 (D68–D71). **Próximo: T5 manual pelo usuário (`evals/T5-roteiro.md`) e encerramento da iteração 2.** Nenhuma rodada de eval está autorizada. Deste arquivo valem as regras de operação, os comandos, a arquitetura e as armadilhas abaixo.

- Testes unitários: `python3 -m unittest discover -s evals/unit` (154 passando).
- Histórico das rodadas (iteração 1: curta-3, fumaça, completa-1 a -5, calib-1 a -3, diag-1, k2-aviso; iteração 2: calib-4 a -8, curta-4, k2-previa, ajuste-1, descoberta-1, sonda-c2, camada2-1, camada2-2; checagens manuais T1–T4 no OpenCode): `PLANO.md`.
- Poppers: iteração 1, `ses_e15628079ffehR54kQzwIQFPNZ` (consultas 9 a 18); iteração 2, `ses_e141aaae0ffeuGbrEAhpELk1I3` (consultas 19 a 31), `ses_e119daa1effePIY2FtgGWuHA2q` (consultas 32 a 44) e `ses_e0fdc0bfbffeasgGVovR3zMH6f` (consultas 45 a 54). Numa sessão nova, abra outro e numere a partir da **consulta 55**.

## Regras que valem (combinadas com o usuário)

1. **Não executar nada que consuma cota sem o ok do usuário para a fase.** Nenhuma rodada está autorizada agora.
2. **Antes de cada tarefa que consome cota, ler a cota** (ferramenta de uso do OpenChamber, `providerId` `claude` para o executor e `codex` para o juiz). Se qualquer janela (5 h ou semanal) estiver **abaixo de 15%**, ou a leitura falhar, **parar** e avisar o usuário. Esta sessão de orquestração também consome a cota do Claude.
3. **Uma tarefa por chamada** (`proxima` → ler cota → `executar`).
4. Recomendações e decisões com consequência passam pelo **popper** (subagente de segunda opinião) antes de chegar ao usuário. Um popper só funciona a partir da sessão que o abriu: **abra um novo** (`/use-popper`, padrão com proposta), mande na abertura o objetivo, o `PLANO.md`, este arquivo e o `HANDOFF-iteracao-2.md`, e continue a numeração das consultas a partir da última registrada no `PLANO.md`. O usuário prefere ver só a posição final, depois do retorno do popper, com o bloco "Revisão do popper" ao fim.
5. Respostas ao usuário em português, curtas, sem concordar por reflexo.

## Comandos

```bash
# próxima tarefa pendente (JSON: tarefa, consome = claude|codex)
python3 evals/agente/runner.py proxima curta-3
# (ler a cota do provedor indicado em "consome"; parar se < 15%)
python3 evals/agente/runner.py executar curta-3 <tarefa>
python3 evals/agente/runner.py status curta-3
python3 evals/agente/runner.py comparar curta-3          # metamórficos, sem cota
python3 evals/agente/runner.py reverificar curta-3       # reavalia execuções com o verificador atual, sem cota
python3 evals/agente/runner.py repetir <rodada> <tarefa>  # cria a repetição de uma execução inválida
python3 evals/agente/runner.py preparar <rodada> curta --casos H2,H3 --reps 5    # casos e repetições escolhidos
python3 evals/agente/runner.py preparar <rodada> calibracao --casos P5,P6        # só os dossiês indicados
python3 evals/agente/runner.py preparar <rodada> dialogo --casos D2a --reps 1     # camada 2 (um turno por tarefa)
python3 evals/agente/runner.py limpar-sessoes <rodada>    # camada 2: guarda e apaga as sessões do Claude
```

- Tarefas de uma rodada podem ser executadas fora da ordem de `proxima` (`executar <rodada> <tarefa>`); as não executadas ficam pendentes e devem ser registradas no `PLANO.md`.
- Camada 2 (`casos.DIALOGOS`): cada turno é uma tarefa dependente da anterior, mesmo workspace e mesma sessão (`--session-id` no turno 1, `--resume` depois, sem `--no-session-persistence`); snapshot por turno; turno inválido não se repete (prepare o diálogo inteiro de novo); relações entre turnos em `comparar`; rode `limpar-sessoes` ao fim.
- Casos com `"previa": True` (camada 1) terminam na prévia: o verificador usa K1/K2 próprios e o juiz usa `INSTRUCOES_JUIZ_PREVIA` e `veredito-previa.schema.json` (R e medidas obrigatórios; `S4_antigo` só no G04i).

## Arquitetura dos evals (após a consulta 7 ao popper)

| Arquivo | Papel | Hash |
|---|---|---|
| `evals/agente/execucao.py` | perfil do Claude Code, invocação, ambiente do executor | **execução** (com a skill e `casos.py`) |
| `evals/agente/juiz.py` | instruções, dossiê e CLI do juiz (Codex `gpt-6.1-sol`, esforço high) | **juiz** (com `calibracao.py`, schema e gabaritos); cada julgamento guarda também o hash do dossiê |
| `evals/agente/verificador.py` | critérios automáticos, auditoria, snapshot, procedência do JSON | **verificador**: mudar não invalida execuções; rodar `reverificar` |
| `evals/agente/runner.py` | orquestração, estado, checkpoint, `reverificar`, migração | fora dos hashes |
| `evals/agente/casos.py` | casos derivados dos gabaritos | execução |

- Cada execução é **congelada** em `resultados/<rodada>/<tarefa>/snapshot/` (diretório da execução sem a skill, temporários criados na janela, manifesto com hashes). A verificação lê só o snapshot e o trace.
- O JSON canônico é escolhido pelo **conteúdo**: o render confiável dele precisa estar contido na saída do `apf.py render --format md` registrada no trace. Ambiguidade reprova.
- `reverificar` mantém o veredito do juiz só se o dossiê reconstruído for idêntico; senão, a tarefa de juiz volta a pendente e o veredito anterior fica no histórico.
- Migração (`reverificar --migrar-de <commit>`) só é aceita se, desde o commit, mudaram apenas `runner.py`, `verificador.py`, testes e documentação. `execucao.py` e `juiz.py` foram aceitos uma única vez, na migração da `curta-3`, por serem extração idêntica do runner (comparação de AST registrada no `PLANO.md`).
- Perfil do executor: `claude -p` com `--setting-sources project --strict-mcp-config`, ferramentas `Read, Write, Edit, Glob, Grep, Bash, Skill`, `--permission-prompts none`, `--effort high`, modelo `claude-sonnet-5-5`, credencial da assinatura. `--restricted` **não** serve (não descobre skills do projeto).

## Armadilhas já encontradas

- O `mktemp` do executor ignora o `TMPDIR` passado: os JSONs vão para `/var/folders/.../T` ou `/tmp`. O verificador lida com isso pela janela de tempo + procedência por conteúdo. O `apf.py novo` (D63) respeita o `TMPDIR` e cria o diretório dentro do workspace nos evals.
- O executor às vezes encadeia comandos (`echo $D && check && render`): a saída do render vem precedida de outras linhas.
- O executor pode quebrar linhas longas ao copiar a tabela (quebra suave do Markdown): o verificador compara a prosa com espaços normalizados, mas exige cada linha de tabela idêntica e na mesma ordem.
- O juiz varia em casos de fronteira (calibração, PLANO.md): uma reprovação isolada do juiz deve ser lida junto com a justificativa.
- Resultados brutos (`evals/agente/resultados/`) ficam fora do git (`.gitignore`); o resumo de cada rodada vai para o `PLANO.md`.
- O executor às vezes grava arquivo de **nome fixo** no `/tmp` (ex.: `/tmp/apf_dir_portaria.txt`): a auditoria invalida a execução (correto: outra execução poderia lê-lo). Repetir com `repetir`.
- A auditoria recusa **qualquer `..`** em comandos, mesmo quando o caminho resolve dentro do diretório da execução (ex.: `ls ../../../tmp` de dentro da pasta da skill). Conservador de propósito; repetir a execução.
- O executor tende a **"corrigir"** frases fixas de orientação ao copiá-las (abertura da prévia, linha de correção: "exportada" → "exportado"). Desde a D67, o K2 é por categorias: conteúdo e avisos literais; orientação com o sentido correto (verificado por termos, `ORIENTACAO` no verificador), sem omissão; a abertura da prévia saiu do script. Se reaparecer em conteúdo, olhar primeiro o render, não acrescentar prosa.
- Na ferramenta de perguntas do OpenCode, o campo `options` é obrigatório no esquema, mas aceita lista vazia (só resposta livre); sem instrução, o executor **inventa** opções (T3).
- Em correções, o executor pode **renumerar IDs** de funções (T4), o que quebra referências do analista ao resultado anterior. Não corrigido.
- As sessões manuais no OpenCode/OpenChamber podem ser lidas pelo banco `~/.local/share/opencode/opencode.db`, tabela `session_message` (`data` em JSON, por `session_id`); `session.messages` do OpenChamber só traz texto.
- A skill instalada no harness do usuário é um **link** para o repositório: não mude a skill enquanto uma sessão manual dele estiver em curso.
- `tem_contagem` (alertas) procura números de PF ou linha de tabela; antes contava barras soltas e deu falso positivo com `interativo=sim|nao` na linha "Chaves" (corrigido na `k2-previa`).
- Mudar `calibracao.py`, `juiz.py`, os esquemas ou os gabaritos muda o hash do juiz: a rodada em curso não continua; abrir outra (ex.: `calib-4` → `-5` → `-6`).

## Para começar a próxima sessão

Comece pela seção "Próximo passo" do `HANDOFF-iteracao-2.md` (rodada `regressao-1`, autorizada). Antes, abra o popper (consulta 45) e confira `python3 -m unittest discover -s evals/unit` (154 testes), `git log --oneline | head -3` e se a configuração dos evals continua `5be257e4fb57843d` (D67; a anterior, `4eb6077f21f4f68d`, é a da `descoberta-1`) (`python3 -c "import sys; sys.path.insert(0,'evals/agente'); import runner; print(runner.config_hash())"`).
