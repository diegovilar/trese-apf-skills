# Handoff — skill `nesma-apf-estimator`

Para retomar o trabalho em outra sessão (humana ou de agente). Leia também o `PLANO.md`, que guarda todas as decisões (D1 a D30) e o andamento.

## Onde estamos

**A iteração 1 foi encerrada em 17/11/2026 como versão inicial** (commit `38f562b`), com o S4 do G04 não atendido e revisão humana obrigatória das lacunas (ver `RELATORIO-iteracao-1.md` e a seção "Encerramento da iteração 1" do `PLANO.md`). **Nenhuma fase que consome cota está autorizada.** Para a próxima iteração, use `HANDOFF-iteracao-2.md`; deste arquivo valem só as regras de operação, os comandos, a arquitetura e as armadilhas abaixo.

- Testes unitários: `python3 -m unittest discover -s evals/unit` (95 passando).
- Histórico das rodadas (curta-3, fumaça, completa-1 a -5, calib-3, diag-1, k2-aviso): `PLANO.md`.
- Popper da sessão de encerramento: `ses_e15628079ffehR54kQzwIQFPNZ` (consultas 9 a 18). Numa sessão nova, abra outro e numere a partir da consulta 19.

## Regras que valem (combinadas com o usuário)

1. **Não executar nada que consuma cota sem o ok do usuário para a fase.** Nenhuma fase está autorizada depois do encerramento da iteração 1.
2. **Antes de cada tarefa que consome cota, ler a cota** (ferramenta de uso do OpenChamber, `providerId` `claude` para o executor e `codex` para o juiz). Se qualquer janela (5 h ou semanal) estiver **abaixo de 15%**, ou a leitura falhar, **parar** e avisar o usuário. Esta sessão de orquestração também consome a cota do Claude.
3. **Uma tarefa por chamada** (`proxima` → ler cota → `executar`).
4. Recomendações e decisões com consequência passam pelo **popper** (subagente de segunda opinião) antes de chegar ao usuário. Um popper só funciona a partir da sessão que o abriu: **abra um novo** (`/use-popper`, padrão com proposta), mande na abertura o objetivo, o `PLANO.md`, este arquivo e o `HANDOFF-iteracao-2.md`, e numere as consultas a partir de 19. O usuário prefere ver só a posição final, depois do retorno do popper, com o bloco "Revisão do popper" ao fim.
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

Siga a seção "Primeiras decisões a levar ao usuário" do `HANDOFF-iteracao-2.md`. Antes, confira `python3 -m unittest discover -s evals/unit` (95 testes) e `git log --oneline | head -3`.
