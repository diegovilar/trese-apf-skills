# Guia de uso — skill `nesma-apf-estimator`

Para o analista de TI do TRE/SE que precisa de uma estimativa de tamanho funcional na análise de viabilidade de um pedido de sistema. Não é preciso saber Análise de Pontos de Função para usar a skill, mas é preciso revisar o que ela entrega (ver "Antes de usar o número").

## Para que serve, e para que não serve

A skill faz uma **estimativa preliminar** de pontos de função (PF) pelo método da NESMA, a partir do pedido como ele está: uma história de usuário, um parágrafo, um documento de requisitos. Ela lista as funções que identificou, separa o que o pedido afirma do que ela supôs, calcula um intervalo (mínimo e máximo) e diz o que ficou faltando.

Não serve para contratação, medição de entrega nem contagem detalhada. Não aplica fórmulas contratuais do SISP. O resultado é insumo de viabilidade, sempre revisado por um analista.

## Requisitos e instalação

- Um ambiente de agente que carregue skills (Claude Code, OpenCode ou equivalente).
- **Python 3.8 ou superior** na máquina. Sem Python, a skill para e avisa: nada é calculado de cabeça.
- As regras e o cálculo não dependem de internet: todo o conhecimento está na pasta da skill e a skill não pesquisa na web. Isso não quer dizer que o pedido fique na sua máquina: o agente pode usar um modelo remoto, conforme o seu ambiente.

Instalação: copie a pasta `nesma-apf-estimator/` deste repositório, inteira, para o diretório de skills do seu ambiente. Exemplos: `.claude/skills/` do projeto ou `~/.claude/skills/` no Claude Code; `~/.config/opencode/skills/` no OpenCode. Um link para a pasta, em vez da cópia, também serve quando o ambiente o reconhece (é o caso do OpenCode usado nas checagens). Não altere os arquivos da pasta: os números vêm do script `scripts/apf.py`, que depende das referências como estão.

## Como chamar

O jeito mais simples é acionar a skill e colar o pedido, ou indicar o arquivo:

```
/nesma-apf-estimator Como servidor, quero gerenciar minhas solicitações de diárias.
/nesma-apf-estimator -- ./pedido.pdf
```

A forma de acionar depende do ambiente: `/nesma-apf-estimator` no Claude Code; `$nesma-apf-estimator` no OpenChamber (a forma usada nas checagens manuais); no OpenCode V2, `@nesma-apf-estimator` (veja a documentação do seu cliente). Também dá para pedir em linguagem natural ("estime os pontos de função deste pedido: ...").

Para mudar o padrão, ponha argumentos **no início**, no formato `chave=valor`, e termine com `--` antes do pedido:

```
tipo=melhoria melhoria=nesma saida=xlsx -- ./pedido-alteracao.docx
```

| Chave | Valores | Padrão | Quando usar |
|---|---|---|---|
| `modo` | `estimada`, `indicativa` | `estimada` | `indicativa` só em desenvolvimento, para uma ordem de grandeza grosseira: conta só os arquivos lógicos (na pesquisa da NESMA, desviou até cerca de 50% da contagem detalhada em alguns casos; não é limite garantido de erro) |
| `tipo` | `desenvolvimento`, `melhoria` | inferido do pedido | quando o pedido não deixa claro se o sistema é novo ou já existe |
| `melhoria` | `sem-fatores`, `nesma` | `sem-fatores` | em melhoria: `sem-fatores` soma o peso cheio de cada função incluída, alterada ou excluída (PF de melhoria); `nesma` aplica os fatores de impacto da NESMA (resultado em PFM) |
| `saida` | `md`, `txt`, `xlsx` | perguntar no fim | para exportar direto, sem a pergunta (também depois de cada correção) |
| `interativo` | `sim`, `nao` | `sim` | `nao` calcula direto, sem a prévia e os lotes de perguntas |

Argumento errado (chave desconhecida, valor fora da lista, falta do `--`) gera um **alerta** e nada é executado. Corrija e chame de novo. Se você pedir uma configuração em linguagem natural ("gere em planilha", "sem perguntas"), a skill mostra a chamada equivalente e pede confirmação antes de rodar.

## O que acontece numa estimativa (modo interativo, padrão)

1. **Tipo e fronteira.** Se o pedido não diz se o sistema é novo ou já existe, ou não permite saber o que pertence ao sistema medido, a skill pergunta antes de tudo.
2. **Prévia.** A skill mostra as funções que identificou, em termos do negócio e com o tipo APF entre parênteses, o que ela supôs e o que ficou de fora, **ainda sem pontos de função**. Junto vem um lote de até 7 perguntas sobre o que pode mudar a contagem: quem mantém os dados, o que um verbo amplo como "gerenciar" abrange, como uma pessoa é identificada, se há análise ou decisão, o que acontece depois.
3. **Suas respostas.** Responda pela ferramenta de perguntas do ambiente (se houver) ou por texto, pelo número da pergunta. Você pode:
   - escolher uma opção ou **escrever a resposta com suas palavras**;
   - dizer **"não sei"**: a pergunta fica como pendência e não volta, e nenhuma função é acrescentada por causa dela (as hipóteses que o próprio pedido sustenta continuam);
   - dizer **"calcular"** a qualquer momento da prévia: as perguntas restantes dos lotes ficam como pendências e a skill calcula. Isso não dispensa as perguntas de tipo e fronteira do passo 1.

   Cada resposta vira um esclarecimento, que aparece no resultado. Respostas podem abrir um novo lote de perguntas.
4. **Resultado.** A skill mostra a estimativa completa: resumo com o intervalo, memória de cálculo por função, hipóteses e cenários, premissas, itens não contados, esclarecimentos, pendências e legenda.
5. **Exportação.** A skill pergunta se você quer o resultado em `.md`, `.txt`, `.xlsx` (pode escolher mais de um) ou nenhum. Os arquivos vão para o diretório de trabalho atual, com o nome `estimativa-apf-<título>-<data>.<ext>`. Um arquivo existente nunca é sobrescrito: o novo ganha o sufixo `-2`, `-3`...
6. **Correções.** Depois do resultado, peça a correção informando o item (ID ou descrição) e o que muda, por exemplo: "Correção: não existe cancelamento; o servidor só altera a solicitação enquanto não houver decisão da chefia." A skill atualiza o esclarecimento, refaz a identificação, mostra o resultado inteiro de novo e pergunta outra vez sobre a exportação (com `saida=` na chamada, reexporta direto). Os arquivos anteriores continuam como estavam (e ficam desatualizados). Se a correção for ambígua, ela pergunta antes de recalcular.

Com `interativo=nao`, a skill pula a prévia e os lotes de perguntas: calcula direto e põe todas as lacunas na lista de pendências. Ainda pergunta tipo e fronteira, se for indispensável, e oferece a exportação.

## Como ler o resultado

- **Total ou faixa.** Quando há hipóteses (o que o pedido sugere sem afirmar), o resultado traz um mínimo e um máximo; sem hipóteses, um total único. Não existe "total provável". A faixa cobre só os cenários modelados, não o projeto inteiro: o que ficou em pendência ou fora da cobertura não está nela.
- **Base de cada função:** *evidência* (o pedido afirma), *hipótese* (o pedido sugere, com o trecho citado) ou *pendência* (nem afirma nem sugere; não conta).
- **Cobertura parcial** quer dizer que o pedido não permite identificar todas as funções. Quanto mais vago o pedido, mais provável.
- **Unidades:** PF em desenvolvimento; em melhoria, PF de melhoria (`sem-fatores`) ou PFM (`nesma`, rotulada como estimativa híbrida). PFM não se compara com PF.
- **Pendências:** o que você precisaria confirmar com a área demandante. A lista termina com o aviso de que **não é exaustiva**.

## Antes de usar o número

Revise sempre. As limitações abaixo foram medidas nos testes da skill (`RELATORIO-iteracao-2.md`):

- **Hipóteses a mais.** A skill às vezes conta como hipótese uma função que o pedido não sustenta, como uma consulta separada para outro perfil (por exemplo, "consultar para a chefia decidir"). Confira cada hipótese que entra no máximo: o trecho citado realmente implica uma função própria?
- **Perguntas a mais.** Algumas perguntas podem ampliar o pedido (sugerir um cálculo ou uma operação que ninguém pediu) ou repetir o que o texto já diz. Se você sabe que aquilo não faz parte do pedido, diga isso com todas as letras ("o sistema não calcula saldo"); se não sabe, responda "não sei". Também pode dizer "calcular" e deixar as restantes como pendência.
- **Lacunas não perguntadas.** A lista de pendências não é exaustiva. Leia o fluxo do processo e pergunte-se o que falta, sobretudo nas etapas depois da decisão.
- **Alternativas só como pendência.** Uma dúvida que a skill perguntou nem sempre aparece como alternativa nos cenários; então o intervalo pode não refletir as duas respostas possíveis. Se a resposta for relevante, responda à pergunta ou peça a correção.
- **Fronteira.** A skill às vezes assume a fronteira do sistema sem perguntar. Confira a linha "Fronteira da aplicação" no resumo.
- Em correções, os IDs das funções podem mudar de número. Refira-se aos itens também pela descrição.

O modo interativo é **experimental**: as duas checagens manuais completas (T4 e T5) atenderam aos respectivos critérios, uma vez cada, mas a estabilidade em diálogos longos não foi medida.

## Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `ALERTA: argumentos inválidos` | corrija a chamada conforme o alerta (formato e chaves estão nele) |
| alerta de Python não encontrado | instale Python 3.8+ e tente de novo |
| a skill parou perguntando tipo ou fronteira | responda; ela não estima sem isso |
| o resultado não mostra a tabela, só um resumo | peça para mostrar o resultado completo do script; a skill deve copiá-lo inteiro |
| quero substituir um arquivo exportado | apague-o você mesmo ou peça explicitamente; por padrão a skill cria `-2`, `-3`... |
| o pedido é de data warehouse, IA, app multiplataforma, portal estático | fora da cobertura: a skill conta só a parte transacional e declara o resto como limitação |
