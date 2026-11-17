# Handoff — skill `nesma-apf-estimator`

Para retomar o trabalho em outra sessão (humana ou de agente). Leia também o `PLANO.md`, que guarda todas as decisões (D1 a D30) e o andamento.

## Onde estamos

- A skill está construída em `nesma-apf-estimator/` (SKILL.md, `references/` 01–05, `scripts/apf.py`). O usuário aprovou o conteúdo; a instalação em harness é com ele.
- Testes unitários: `python3 -m unittest discover -s evals/unit` (88 passando).
- Evals do agente: **rodada curta `curta-3` concluída.**
- A `curta-3` terminou (resultado no `PLANO.md`). Falha: erro de transcrição da legenda em 2 de 19 respostas. Mitigação aplicada (D32: perfil `chat` com legenda contextual).
- Fumaça `fumaca-1` concluída em 17/11/2026: K2 7/7; juiz reprovou o G04 em S1, S3 e S4 (falta o grupo de origem; mínimo 0 PF). Resumo e consulta 9 no `PLANO.md`.
- `completa-1` parada no G04 depois de 3 repetições (reprovação inevitável). Skill reforçada (D33), holdout G07 criado (D34). Ver `PLANO.md`.
- `completa-2`: primeiro bloco parado no S4 do G04 (pendência sobre os dados do servidor). Skill ajustada (D36).
- `completa-3`: bloco reprovado no S4 do G07 (homologação, 3/5). Contrato do S4 mantido; D37, G08 e S4 pelo significado (ver `PLANO.md`).
- **Autorizado pelo usuário em 17/11/2026:** calibração delta `calib-3` (só `calib-P3`, `calib-E6`, `calib-P4`, `calib-E7`); se o juiz acertar os 4, o primeiro bloco da `completa-4` (G04, G07 e G08, r1 a r5, chamados pelo nome), com a mesma regra de parada. Se a calibração errar, parar e levar ao usuário. O resto da `completa-4` pede novo ok.
- Popper desta sessão: `ses_e15628079ffehR54kQzwIQFPNZ` (consultas 9 em diante); numa sessão nova, abra outro e continue a numeração.

## Regras que valem (combinadas com o usuário)

1. **Não executar nada que consuma cota sem o ok do usuário para a fase.** Fases: sondagens, calibração, rodada curta e fumaça (feitas); `completa-1` (parada no G04); `completa-2` (parada no S4 do G04); `completa-3` (bloco reprovado no S4 do G07); `calib-3` e bloco G04/G07/G08 da `completa-4` (**autorizados**).
2. **Antes de cada tarefa que consome cota, ler a cota** (ferramenta de uso do OpenChamber, `providerId` `claude` para o executor e `codex` para o juiz). Se qualquer janela (5 h ou semanal) estiver **abaixo de 15%**, ou a leitura falhar, **parar** e avisar o usuário. Esta sessão de orquestração também consome a cota do Claude.
3. **Uma tarefa por chamada** (`proxima` → ler cota → `executar`).
4. Recomendações e decisões com consequência passam pelo **popper** (subagente de segunda opinião) antes de chegar ao usuário. A sessão anterior do popper (`ses_e166880bdffeQatE857gIDKXkq`, 8 consultas) só funciona a partir da sessão que a abriu: **abra um popper novo** (`/use-popper`, padrão com proposta) e, na abertura, mande o contexto: objetivo da skill, `PLANO.md` (decisões D1–D32 e as revisões das consultas 1 a 8) e este handoff. Numere as consultas a partir de 9, para manter a continuidade com o `PLANO.md`. O usuário prefere ver só a posição final, depois do retorno do popper, com o bloco "Revisão do popper" ao fim.
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
```

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

- O `mktemp` do executor ignora o `TMPDIR` passado: os JSONs vão para `/var/folders/.../T` ou `/tmp`. O verificador lida com isso pela janela de tempo + procedência por conteúdo.
- O executor às vezes encadeia comandos (`echo $D && check && render`): a saída do render vem precedida de outras linhas.
- O executor pode quebrar linhas longas ao copiar a tabela (quebra suave do Markdown): o verificador compara a prosa com espaços normalizados, mas exige cada linha de tabela idêntica e na mesma ordem.
- O juiz varia em casos de fronteira (calibração, PLANO.md): uma reprovação isolada do juiz deve ser lida junto com a justificativa.
- Resultados brutos (`evals/agente/resultados/`) ficam fora do git (`.gitignore`); o resumo de cada rodada vai para o `PLANO.md`.

## Para começar a próxima sessão

1. Ler `HANDOFF.md` e `PLANO.md` (seções "Decisões fechadas", "Evals do agente" e "Rodada curta: andamento").
2. Abrir o popper novo (regra 4).
3. Conferir: `python3 -m unittest discover -s evals/unit` (87 testes) e `git log --oneline | head -3` (último commit esperado: o deste handoff).
4. Rodar a fumaça: `preparar fumaca-1 curta --casos M02,M03b,G03a,G03b,G04,G05,G06`; depois, tarefa a tarefa, `proxima` → ler cota → `executar`. São 7 execuções e 5 juízes.
5. Analisar (`status fumaca-1`; diffs de K2, se houver), registrar no `PLANO.md`, consultar o popper e só então pedir ao usuário o ok da rodada completa.

