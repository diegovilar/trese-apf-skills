# T5 — checagem manual final do modo interativo (fase 6, D71)

> Registro histórico: referências de caminhos podem refletir a estrutura anterior à reorganização de 19/11/2026; veja o mapa na D73 do `PLANO.md`.

Checagem manual, no OpenCode/OpenChamber, do caminho completo do modo interativo com a skill congelada (`trese-apf-aproximacao/` sem mudanças desde `0c5a3b3`). Uma execução: **sinal funcional, não estabilidade**. Um sucesso aqui não apaga as reprovações da fase 5. Critérios e respostas fixados antes da execução; a sessão é lida depois pelo banco do OpenCode.

## Preparação

- Sessão **nova e limpa**, modelo `claude-sonnet-5-5` (variante high), como no T1–T4.
- Conferir que a skill instalada é o link para este repositório e que nada nela mudou desde `0c5a3b3` (`git diff 0c5a3b3 -- trese-apf-aproximacao` vazio).
- Não mexer no repositório durante a sessão.

## Roteiro

1. Enviar: `$trese-apf-aproximacao -- Como servidor, quero gerenciar minhas solicitações de diárias`
2. Tipo do projeto (se perguntado): opção **Desenvolvimento (novo)**. Fronteira (se perguntada): responder só "sistema novo de diárias" (os dados do RH ficam reservados para a pergunta de identificação).
3. Lote de perguntas: responder **por assunto**. Se uma pergunta juntar dois assuntos, combinar as respostas. Assunto não listado: **Não sei**.

| Assunto | Resposta | Como responder |
|---|---|---|
| Origem das solicitações | Registradas e guardadas neste sistema | opção (ou texto equivalente, se não houver opção) |
| Alcance de "gerenciar" | Registrar, alterar, cancelar e consultar | opção (ou texto) |
| Identificação e dados do servidor | "O servidor é identificado pela matrícula do login; nome, cargo e lotação vêm do sistema de RH, que continua mantendo esses dados." | **resposta livre** (digitar, mesmo se houver opção parecida) |
| Análise ou decisão | A chefia imediata aprova ou devolve a solicitação, e o sistema registra a decisão | opção (ou texto) |
| O que acontece depois da decisão (pagamento, prestação de contas etc.) | **Não sei** | opção "Não sei" ou texto |
| Cálculo do valor | O valor é só informado | opção (ou texto) |
| Qualquer outro | **Não sei** | |

   Se identificação ou pós-decisão só aparecerem num lote seguinte, responder esse lote pela tabela antes de dizer **calcular**; depois disso, responder **calcular**. Se a skill pedir confirmação para calcular, confirmar. **Não oferecer fatos espontaneamente:** se a identificação ou o pós-decisão não forem perguntados, o caminho fica **não exercitado** (registrado; o T5 não tem aprovação integral).
4. Exportação: escolher **.md** e **.xlsx**.
   **Pausa:** antes do passo 5, avisar a sessão de orquestração, que registra o caminho e o hash do JSON, do `.md` e do `.xlsx` (estado anterior à correção) e confere que "cancelar" é EE contada nos dois extremos. Só então seguir.
5. Correção, como mensagem nova depois do resultado: `Correção: não existe cancelamento; o servidor só pode alterar a solicitação enquanto não houver decisão da chefia.`
6. Exportação depois da correção: **Nenhum**.

## Critérios (fixados antes)

| # | Critério | Aprova se |
|---|---|---|
| C1 | Canal das perguntas | tipo (e fronteira, se perguntada) pela ferramenta; prévia inteira no chat, sem PF nem exportação antes de calcular, renderizada com `--canal ferramenta` e, **na mesma resposta**, depois dela, chamada da ferramenta com as perguntas `perguntada` do lote, com texto e opções idênticos aos do JSON (lista vazia quando o JSON não tem `opcoes`), conferido por script |
| C2 | Respostas incorporadas | resposta livre registrada no esclarecimento (paráfrase fiel aceita); **AIE de dados de servidores do RH** no modelo, com uso justificado por ao menos uma função identificada e ligado ao esclarecimento; pendência de identificação `resolvida`. "Não sei": resposta registrada, pendência `sem-resposta`, nenhuma função ou hipótese fundada nela. Nenhuma pergunta respondida volta a ser perguntada |
| C3 | Diretório de trabalho | `apf.py novo` uma vez; o mesmo caminho em todos os comandos, inclusive na correção; nenhum arquivo de nome fixo em `/tmp` |
| C4 | Resultado no chat | resultado do `render --format md` copiado sem alterar conteúdo, tabelas, totais, pendências e avisos; linha de correção presente com o sentido certo (K2 por categorias, D67) |
| C5 | Exportação | pela ferramenta, seleção múltipla; `.md` e `.xlsx` gerados do mesmo JSON; `.md` igual ao resultado do chat, sem a linha de correção; `.xlsx` abre (openpyxl) com os mesmos totais |
| C6 | Correção | com "cancelar" confirmado antes como EE nos dois extremos (pausa): EE de cancelamento retirada, **−4 PF nos dois extremos**, alteração mantida com a restrição da chefia registrada, nenhuma outra mudança funcional; se a correção substitui a resposta sobre "gerenciar", o esclarecimento existente é atualizado no lugar (novo só se não corresponder a uma pendência); **resultado inteiro no chat antes da pergunta de exportação**; "Nenhum" não gera arquivo novo; `.md` e `.xlsx` anteriores com os hashes da pausa |

Não comparar totais absolutos com o T4 (as respostas mudaram de propósito). Observações registradas sem reprovar: fronteira assumida sem perguntar; IDs renumerados na correção (T4); variação dos totais por representação da incerteza (S3); número de perguntas e de lotes.

## Leitura da sessão

Banco `~/.local/share/opencode/opencode.db`, tabela `session_message` (`data` em JSON, por `session_id`); entradas e saídas da ferramenta de perguntas em `content[].name == "question"` (`metadata.answers`).
