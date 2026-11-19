# 05 · JSON canônico, script e saídas

O agente **não** calcula pesos, fatores nem totais e **não** escreve a tabela final à mão. Ele monta o JSON canônico, e o script `scripts/apf.py` valida, calcula e gera as saídas `.md`, `.txt`, `.xlsx` e `.docx`. Assim, todos os formatos mostram sempre os mesmos números.

## 1. Esquema (versão 3)

```json
{
  "versao_esquema": 3,
  "metodo": "estimada | indicativa",
  "tipo_projeto": "desenvolvimento | melhoria",
  "regime_melhoria": "sem-fatores | nesma | null",
  "projeto": {
    "titulo": "nome curto do pedido",
    "fronteira": "o que está dentro e o que está fora",
    "origem_subsidio": "ex.: arquivo pedido-123.pdf; texto do prompt",
    "data": "AAAA-MM-DD"
  },
  "cobertura": {"status": "completa | parcial", "motivo": "obrigatório se parcial | null"},
  "avisos": ["texto que deve aparecer no resumo executivo"],
  "funcoes": [
    {
      "id": "F01",
      "requisito": "trecho do pedido que sustenta a função",
      "nome": "nome da função",
      "tipo": "ALI | AIE | EE | SE | CE",
      "operacao": "I | A | E | null",
      "hipotese": "H1 | null",
      "justificativa": "por que é esta função e este tipo",
      "efpa": null,
      "esclarecimentos": ["E1"]
    }
  ],
  "hipoteses": [
    {"id": "H1", "descricao": "...", "trecho": "palavra ou frase que a implica | null", "grupo": "nome do grupo de alternativas | null", "requer": ["H3"]}
  ],
  "premissas": [{"id": "PR1", "descricao": "..."}],
  "pendencias": [
    {"id": "P1", "descricao": "..."},
    {"id": "P2", "descricao": "...", "pergunta": "pergunta ao analista", "opcoes": ["...", "..."], "situacao": "aberta | perguntada | sem-resposta | resolvida", "lote": 1}
  ],
  "esclarecimentos": [{"id": "E1", "pendencia": "P2 | null", "pergunta": "... | null", "resposta": "o que o analista respondeu", "lote": 1}],
  "nao_contados": [{"item": "...", "categoria": "absorvido | dado-de-codigo | fora-do-escopo | sem-evidencia", "justificativa": "...", "pendencias": ["P1"]}]
}
```

Os campos `pergunta`, `opcoes`, `situacao`, `lote`, a lista `esclarecimentos` e o campo `esclarecimentos` de funções e hipóteses são do modo interativo (SKILL.md, seção 2A). São opcionais: omita-os quando não houver pergunta nem resposta.

Regras que o script verifica (ele recusa o JSON e lista os erros):

- `regime_melhoria` é obrigatório em melhoria e `null` em desenvolvimento.
- `operacao` é obrigatória em melhoria (`I`, `A`, `E`) e `null` em desenvolvimento.
- `metodo: "indicativa"` só aceita ALI/AIE e só em desenvolvimento.
- `hipotese` aponta para um `id` existente. Toda hipótese sem grupo precisa estar ligada a pelo menos uma função (ou ser exigida por outra); o que não muda o total é premissa, não hipótese.
- **Grupo** = alternativas **excludentes, das quais exatamente uma vale** (ex.: o dado é ALI ou AIE). Um grupo tem ao menos duas hipóteses. Hipóteses sem grupo são independentes e opcionais.
- **`requer`** = hipóteses que precisam valer junto (ex.: "contratos lidos de outro sistema" exige "consultar contratos"). Use para que cada cenário seja uma aplicação possível. Uma hipótese pode reunir várias funções (ex.: o ALI e a EE que o mantém).
- **Cenários** (o script calcula): o mínimo é o conjunto coerente de menor total (evidências, uma alternativa por grupo e o que ela exige); o máximo é o de maior total (todas as hipóteses independentes, uma alternativa por grupo e o que for exigido). Combinações que ativam duas alternativas do mesmo grupo são descartadas. Em desenvolvimento estimado, cenário com arquivos e sem nenhuma transação é rejeitado: ligue as hipóteses com `requer`.
- **`cobertura`**: `parcial` quando o subsídio não permite identificar todas as funções afetadas (ex.: melhoria sem baseline, pelo exemplo 7 do EFPA; pedido vago). O motivo aparece no resumo e o total sai marcado como PARCIAL, mesmo que mínimo e máximo coincidam. Cobertura e faixa de fator são incertezas diferentes: registre as duas quando houver.
- **`avisos`**: frases que o resumo executivo deve mostrar (ex.: "pedido só cosmético: no regime nesma valeria 0,25 × peso por transação"). O script acrescenta sozinho o aviso de total zero.
- IDs únicos: `F1`/`F01`…, `H1`…, `PR1`…, `P1`…. As listas `funcoes`, `hipoteses`, `premissas`, `pendencias` e `nao_contados` são obrigatórias, mesmo vazias.
- Item de `nao_contados` com categoria `sem-evidencia` exige `pendencias`: a lista (não vazia, sem repetição) dos IDs das pendências que o cobrem. Nas outras categorias o campo é opcional. Uma pendência pode cobrir vários itens. O script confere só os IDs: cabe a você garantir que as pendências apontadas tratem de **todos** os assuntos do item (ex.: um item "cálculo do valor e prestação de contas" precisa de pendências que perguntem pelos dois). O render acrescenta "(ver P1, P2)" à justificativa; não escreva isso à mão.
- `funcoes` pode ficar vazia só se `nao_contados` explicar o porquê (ex.: pedido só cosmético no regime `sem-fatores`).

**Campos do modo interativo** (o script confere a estrutura e os IDs; o significado é responsabilidade sua):

- **`pergunta`**: só em pendência cuja resposta pode mudar a contagem (SKILL.md, 2A). Pendência sem `pergunta` continua só pendência. `opcoes` (2 a 5 textos curtos) é opcional e só existe com `pergunta`.
- **`situacao`**, obrigatória quando há `pergunta`: `aberta` (ainda não apresentada, sem `lote`); `perguntada` (no lote atual, com `lote`); `sem-resposta` (o analista não soube ou pediu para calcular; mantém o `lote`); `resolvida` (respondida; precisa de um esclarecimento que aponte para ela). A pendência resolvida **continua na lista**: o resultado final a mostra na seção de esclarecimentos, não nas pendências.
- **`lote`**: número do lote em que a pergunta foi apresentada. No máximo 7 perguntas por lote. `perguntada` só pode existir no último lote: antes de abrir um lote novo, registre a resposta de todas as anteriores.
- **`esclarecimentos`**: uma entrada por resposta do analista (`resposta` obrigatória; `pendencia` aponta a pendência respondida, ou `null` se a informação veio sem pergunta). "Não sei" também é registrado, com a pendência em `sem-resposta`.
- **`esclarecimentos` em funções e hipóteses**: os IDs das respostas que sustentam a função ou a hipótese. O render mostra "(ver E1)" na base da função e na hipótese; não escreva isso à mão.
- Item `sem-evidencia` não pode apontar só pendências resolvidas: depois da resposta, ele virou função, foi descartado ou depende de outra pendência.
- A prévia (`--format previa`) recusa o JSON se houver perguntas `aberta` e nenhuma no lote atual. O resultado final (`md`, `txt`, `xlsx`) recusa se ainda houver pergunta `perguntada`.

### Campo `efpa` (só em melhoria, regime `nesma`, operação `A`)

Obrigatório nesses casos e proibido nos demais. Escolha **uma** forma:

| Forma | Quando | Conteúdo |
|---|---|---|
| Cosmética | transação com mudança só de rótulo, layout ou texto | `{"cosmetica": true}` |
| Só mudança de tipo | função de dados que passa de AIE a ALI ou o inverso, sem mudar TDs | `{"mudanca_tipo": true}` (0,40) |
| Mudança de tipo e TDs conhecidos | idem, com TDs alterados contados | `{"mudanca_tipo": true, "td": {...}}` (maior entre 0,40 e a tabela 1) |
| Mudança de tipo e TDs desconhecidos | idem, sabendo que TDs também mudam, sem a proporção | `{"mudanca_tipo": true, "faixa": {"min": "0.40", "max": "1.00", ...}}` (min ≥ 0,40) |
| Números conhecidos (dados) | o pedido permite fixar TDs afetados e originais | `{"td": {"afetados": 1, "originais": 12}}` |
| Números conhecidos (transação) | o pedido permite fixar TDs e ARs afetados e originais | `{"td": {...}, "ar": {"afetados": 2, "originais": 2}}` |
| Faixa | faltam os números | `{"faixa": {"min": "0.25", "max": "0.75", "justificativa": "o que se sabe e o que falta"}}` |

Valores de faixa permitidos: dados `0.25, 0.40, 0.50, 0.75, 1.00`; transações `0.25, 0.50, 0.75, 1.00, 1.25, 1.50` (os valores das tabelas de 02 §4.2). Fatores são texto com ponto decimal. Função de dados alterada sem TD afetado e sem mudança de tipo é rejeitada (EFPA, exemplo 8).

## 2. Comandos

Use o interpretador que passou na verificação de pré-requisito (SKILL.md). `<skill>` é o diretório onde está o `SKILL.md`.

```bash
python3 <skill>/scripts/apf.py check  ARQUIVO.json                # valida; código 1 lista os erros
python3 <skill>/scripts/apf.py render ARQUIVO.json --format md    # imprime a tabela em Markdown
python3 <skill>/scripts/apf.py render ARQUIVO.json --format txt --out ARQUIVO.txt
python3 <skill>/scripts/apf.py render ARQUIVO.json --format md  --out ARQUIVO.md
python3 <skill>/scripts/apf.py render ARQUIVO.json --format xlsx --out ARQUIVO.xlsx
python3 <skill>/scripts/apf.py render ARQUIVO.json --format docx --out ARQUIVO.docx
python3 <skill>/scripts/apf.py render ARQUIVO.json --format previa  # modo interativo: prévia sem PF, só impressa
```

- Grave o JSON de trabalho no diretório criado por `apf.py novo` para a estimativa (SKILL.md, etapa 4), não no projeto do usuário.
- Se `check` falhar, corrija o JSON e rode de novo. Nunca contorne o script calculando à mão.
- O que se mostra ao usuário é a saída de `render --format md` **sem `--out`**, copiada integralmente para a sua mensagem, sem reescrever números nem palavras e sem reordenar linhas. A saída do comando, sozinha, não é vista pelo usuário.
- **Perfis de renderização** (escolhidos pelo script, nunca pelo agente): sem `--out`, o perfil é `chat`; com `--out`, `arquivo`. Os dois têm o mesmo conteúdo, inclusive a legenda, só com os termos que aparecem no resultado e a definição completa de cada um. Diferenças: o `arquivo` traz, depois do Objeto, os campos a preencher Responsável e Participantes; só o `chat` fecha com uma linha que explica como pedir correções (SKILL.md, 2C). A aba *Legenda* da planilha traz também os termos das colunas fixas dela (operação, fator e entrada nos cenários).

## 3. Conteúdo das saídas

As saídas têm as mesmas seções, nesta ordem, depois do título fixo **CÁLCULO DE TAMANHO FUNCIONAL APROXIMADO** e da identificação: **Objeto** (o título do projeto, `projeto.titulo`) e, só nos arquivos, **Responsável** `[NOME DA UNIDADE]` e **Participantes** `[LISTA DE UNIDADES OU SERVIDORES PARTICIPANTES]`, campos fixos que o usuário preenche no arquivo exportado. Não os preencha nem os retire.

1. **Resumo executivo:** tipo de projeto, regime (em melhoria), método, fronteira, origem do subsídio, data, total (ou faixa) com a unidade, rótulo de estimativa híbrida (`nesma`) e aviso da indicativa.
2. **Memória de cálculo:** ID, requisito/história, função, tipo, operação, complexidade, PF (e, no `nesma`, PF base, fator e PFM), base (evidência ou hipótese) e justificativa técnica, com a linha de total.
3. **Hipóteses e cenários:** cada hipótese com trecho, grupo e efeito; cenário mínimo e máximo, com as hipóteses de cada um.
4. **Premissas assumidas.**
5. **Itens não contados:** item, categoria e justificativa.
6. **Esclarecimentos do analista** (só se houver): pergunta e resposta de cada esclarecimento.
7. **Dúvidas de requisito e pendências** (as resolvidas saem daqui; as perguntadas sem resposta trazem o lote). O script fecha a seção com um aviso fixo de que a lista não é exaustiva; ele faz parte da saída e deve ser copiado.
8. **Legenda:** tipos de função, operação, complexidade, pesos, base, cenários, unidades (PF, PF de melhoria, PFM), fatores e esclarecimentos. Só os termos que aparecem no resultado, com a definição completa (na planilha, também os das colunas fixas).

**Prévia** (`--format previa`, modo interativo; nunca exportada): resumo sem total; funcionalidades identificadas em termos de negócio, com o tipo APF entre parênteses e a base (afirmada ou suposta), **sem PF nem complexidade**; suposições e alternativas; itens que não entram na contagem; esclarecimentos já recebidos; perguntas do lote atual, numeradas (com `--canal ferramenta`, só o anúncio do lote: as perguntas vão pela ferramenta, SKILL.md 2A e 2B); outras pendências; aviso de pendências não exaustivas; fecho com a instrução de resposta, válida tanto para resposta por texto quanto pela ferramenta de perguntas (SKILL.md, 2B). Copie-a inteira para a resposta, como o resultado final.

Particularidades:

- **`.txt`:** tabela de colunas alinhadas só com os campos curtos e, abaixo, um detalhamento por função com requisito e justificativa.
- **`.docx`:** gerado a partir do modelo `assets/modelo.docx` (cabeçalho, rodapé, página e estilos); o script troca só o corpo. Identificação e resumo em tabelas sem cabeçalho; a memória de cálculo em tabela com cabeçalho repetido a cada página. Sem o modelo, o script sai com código 2 e não grava nada.
- **`.xlsx`:** abas *Resumo*, *Memória de cálculo*, *Hipóteses e cenários* (se houver), *Premissas e pendências* e *Legenda*. Os valores de cada linha são gravados; os totais são **fórmulas** (`SUMPRODUCT` sobre as colunas de valor e de "entra no cenário"), com o valor já calculado gravado junto, para leitores que não recalculam.

## 4. Nome e local dos arquivos exportados

- Padrão: `estimativa-apf-<slug-do-titulo>-<AAAA-MM-DD>.<ext>` no diretório de trabalho atual do usuário.
- Se o usuário indicar caminho ou nome, use o indicado.
- O script **nunca sobrescreve**: se o arquivo existir, ele sai com código 3 sem alterar nada. Nesse caso, tente o mesmo nome com `-2`, `-3`… Só substitua um arquivo existente se o usuário pedir expressamente, e então apague-o antes, com a confirmação dele.
- Ao final, informe o caminho do arquivo gerado.

## 5. Exemplo completo (Exemplo 1 de 04)

```json
{
  "versao_esquema": 3,
  "metodo": "estimada",
  "tipo_projeto": "desenvolvimento",
  "regime_melhoria": null,
  "projeto": {
    "titulo": "Ocorrências de manutenção predial",
    "fronteira": "novo sistema de ocorrências; estrutura organizacional é externa",
    "origem_subsidio": "texto do prompt",
    "data": "2026-11-17"
  },
  "cobertura": {"status": "completa", "motivo": null},
  "avisos": [],
  "funcoes": [
    {"id": "F01", "requisito": "registra uma ocorrência... registra os atendimentos de cada ocorrência", "nome": "Ocorrência (Atendimento como RLR)", "tipo": "ALI", "operacao": null, "hipotese": null, "justificativa": "dado de negócio mantido; atendimento só existe dentro da ocorrência"},
    {"id": "F02", "requisito": "As unidades vêm do sistema de estrutura organizacional", "nome": "Unidade", "tipo": "AIE", "operacao": null, "hipotese": null, "justificativa": "mantida por outro sistema, lida no registro e no filtro"},
    {"id": "F03", "requisito": "registra uma ocorrência", "nome": "Registrar ocorrência", "tipo": "EE", "operacao": null, "hipotese": null, "justificativa": "mantém Ocorrência"},
    {"id": "F04", "requisito": "pode alterar", "nome": "Alterar ocorrência", "tipo": "EE", "operacao": null, "hipotese": null, "justificativa": "mantém Ocorrência"},
    {"id": "F05", "requisito": "ou cancelar", "nome": "Cancelar ocorrência", "tipo": "EE", "operacao": null, "hipotese": null, "justificativa": "grava situação cancelada"},
    {"id": "F06", "requisito": "registra os atendimentos", "nome": "Registrar atendimento", "tipo": "EE", "operacao": null, "hipotese": null, "justificativa": "mantém o RLR Atendimento"},
    {"id": "F07", "requisito": "a equipe conclui a ocorrência, e o sistema avisa o solicitante por e-mail", "nome": "Concluir ocorrência", "tipo": "EE", "operacao": null, "hipotese": null, "justificativa": "grava situação; o e-mail é parte desta função"},
    {"id": "F08", "requisito": "consulta as ocorrências filtrando por unidade, tipo e situação", "nome": "Consultar ocorrências", "tipo": "CE", "operacao": null, "hipotese": null, "justificativa": "só recuperação, sem cálculo"},
    {"id": "F09", "requisito": "relatório mensal com o tempo médio de atendimento por tipo", "nome": "Relatório de tempo médio por tipo", "tipo": "SE", "operacao": null, "hipotese": null, "justificativa": "cálculo de média"}
  ],
  "hipoteses": [],
  "premissas": [{"id": "PR1", "descricao": "Autenticação pelo login institucional, sem cadastro de usuários no sistema."}],
  "pendencias": [],
  "nao_contados": [
    {"item": "Tipo de ocorrência", "categoria": "dado-de-codigo", "justificativa": "lista fixa de valores válidos"},
    {"item": "Situação da ocorrência", "categoria": "dado-de-codigo", "justificativa": "status"},
    {"item": "Aviso por e-mail", "categoria": "absorvido", "justificativa": "consequência da conclusão, não tratado como requisito próprio"}
  ]
}
```
