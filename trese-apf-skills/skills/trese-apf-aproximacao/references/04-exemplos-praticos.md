# 04 · Exemplos práticos

Quatro exemplos completos: pedido → raciocínio → memória de cálculo. Os totais foram calculados com `scripts/apf.py`. Os exemplos ilustram as regras de 01 a 03; não são modelos para copiar: cada pedido real precisa da própria análise.

---

## Exemplo 1 · Desenvolvimento: mestre-detalhe, consulta filtrada e relatório gerencial

**Pedido**

> Sistema para a Seção de Manutenção Predial registrar ocorrências. Qualquer servidor registra uma ocorrência informando unidade, local, tipo (elétrica, hidráulica, civil, refrigeração) e descrição, e pode alterar ou cancelar a ocorrência enquanto ela não for atendida. A equipe de manutenção registra os atendimentos de cada ocorrência (data, técnico, providência). Um atendimento só existe dentro de uma ocorrência. Quando o problema é resolvido, a equipe conclui a ocorrência, e o sistema avisa o solicitante por e-mail. As unidades vêm do sistema de estrutura organizacional. A chefia consulta as ocorrências filtrando por unidade, tipo e situação, e emite um relatório mensal com o tempo médio de atendimento por tipo.

**Raciocínio**

1. *Tipo e fronteira:* desenvolvimento; a fronteira é o novo sistema de ocorrências. A estrutura organizacional está fora (é mantida por outro sistema).
2. *Dados:* Ocorrência é dado de negócio mantido aqui (ALI). Atendimento "só existe dentro de uma ocorrência": é RLR de Ocorrência, não um ALI separado (01 §2). Unidade é lida de outro sistema e usada no registro e no filtro (AIE). Tipo de ocorrência é lista fixa de valores válidos e situação é status: dados de código (01 §5).
3. *Transações:* registrar, alterar e cancelar ocorrência (3 EE, todas afirmadas). Registrar atendimento (EE). Concluir ocorrência grava a situação (EE). O aviso por e-mail é consequência da conclusão e não é tratado como requisito próprio: é parte da EE de conclusão (01 §4). A consulta com filtros só recupera dados (CE). O relatório calcula tempo médio (SE).
4. *Não contados:* tipo e situação (dados de código); e-mail (absorvido na EE de conclusão).
5. *Pendências:* nenhuma impede a contagem. Ficaria pendente se o pedido mencionasse "alterar atendimento", que não aparece.

**Memória de cálculo**

| ID | Função identificada | Tipo | Complexidade | PF | Base | Justificativa técnica |
|---|---|---|---|---:|---|---|
| F01 | Ocorrência (Atendimento como RLR) | ALI | Baixa | 7 | evidência | dado de negócio mantido; atendimento sem significado fora da ocorrência |
| F02 | Unidade (estrutura organizacional) | AIE | Baixa | 5 | evidência | mantida por outro sistema, lida no registro e no filtro |
| F03 | Registrar ocorrência | EE | Média | 4 | evidência | mantém Ocorrência |
| F04 | Alterar ocorrência | EE | Média | 4 | evidência | "pode alterar" |
| F05 | Cancelar ocorrência | EE | Média | 4 | evidência | grava situação cancelada |
| F06 | Registrar atendimento | EE | Média | 4 | evidência | mantém o RLR Atendimento |
| F07 | Concluir ocorrência | EE | Média | 4 | evidência | grava situação; o e-mail é parte desta função |
| F08 | Consultar ocorrências com filtros | CE | Média | 4 | evidência | só recuperação |
| F09 | Relatório mensal de tempo médio por tipo | SE | Média | 5 | evidência | cálculo de média |
| | **Total** | | | **41 PF** | | |

---

## Exemplo 2 · Melhoria: regra nova, campo novo e leitura de sistema externo

**Pedido**

> No sistema de Requisição de Materiais, já em produção: (a) incluir o campo "centro de custo" na requisição, informado no registro e exibido na consulta da requisição; (b) ao registrar a requisição, verificar no sistema de Orçamento, mantido pela Secretaria de Orçamento, se a unidade tem saldo disponível e bloquear o registro se não tiver. Hoje o sistema de Requisição não lê nada do sistema de Orçamento.

**Raciocínio comum aos dois regimes**

1. *Tipo e fronteira:* melhoria no sistema de Requisição; o sistema de Orçamento está fora.
2. *Dados:* Requisição ganha um atributo por regra de negócio (ALI alterado). Saldo orçamentário da unidade é grupo lógico mantido pelo Orçamento e passa a ser lido (AIE incluído; o pedido diz que hoje nada é lido de lá).
3. *Transações:* Registrar requisição muda dados (novo campo), arquivos (passa a ler o saldo) e lógica (bloqueio): alterada. Consultar requisição exibe o novo campo: alterada.
4. *Pendências:* outras transações que usam a requisição (alterar, listar, relatórios) não são descritas. Centro de custo foi tratado como atributo digitado; se for lista de outro sistema, muda a análise.

**Regime `sem-fatores` (padrão)**

| ID | Função identificada | Tipo | Op. | PF | Base |
|---|---|---|---|---:|---|
| F01 | Requisição | ALI | A | 7 | evidência |
| F02 | Saldo orçamentário (Orçamento) | AIE | I | 5 | evidência |
| F03 | Registrar requisição | EE | A | 4 | evidência |
| F04 | Consultar requisição | CE | A | 4 | evidência |
| | **Total** | | | **20 PF de melhoria** | |

Outras transações que só leem a Requisição, sem mudar, não contam neste regime (convenção C4).

**Regime `nesma` (EFPA), sem baseline no pedido**

O pedido não informa quantos TDs e ARs cada função tinha. Pelas tabelas de 02 §4.2:

- *Requisição (ALI):* 1 TD novo sobre um número original desconhecido. Com 3 ou mais TDs originais, ≤ 1/3 dá 0,25; com 2, 50% dá 0,50; com 1, 100% dá 0,75. Faixa de 0,25 a 0,75.
- *Registrar (EE):* 2 ARs afetados (Requisição alterada e Saldo novo) sobre um número original desconhecido (ao menos 1, a Requisição): de > 100% (1 original) a ≤ 1/3 (6 ou mais). 1 TD novo: coluna ≤ 2/3, ou ≤ 100% se a função tivesse 1 só TD. Faixa de 0,25 a 1,25.
- *Consultar (CE):* 1 AR afetado (Requisição alterada) sobre ao menos 1 original: de 100% a ≤ 1/3. Coluna ≤ 2/3 ou ≤ 100%. Faixa de 0,25 a 1,00.

| ID | Função identificada | Tipo | Op. | PF base | Fator | PFM | Base |
|---|---|---|---|---:|---:|---:|---|
| F01 | Requisição | ALI | A | 7 | 0,25–0,75 | 1,75–5,25 | evidência |
| F02 | Saldo orçamentário (Orçamento) | AIE | I | 5 | 1,00 | 5,00 | evidência |
| F03 | Registrar requisição | EE | A | 4 | 0,25–1,25 | 1,00–5,00 | evidência |
| F04 | Consultar requisição | CE | A | 4 | 0,25–1,00 | 1,00–4,00 | evidência |
| | **Total** | | | | | **8,75–19,25 PFM** | |

Leitura correta do resultado: estimativa híbrida, sem valor central, com **cobertura parcial**. Pelo exemplo 7 do EFPA, toda outra transação que use a Requisição também entraria, e o pedido não diz quais são: o total vale só para as funções identificadas, e a baseline da aplicação vai para as pendências. São duas incertezas diferentes. A largura da faixa vem dos fatores desconhecidos: com os números de TDs e ARs, o fator de cada função fica determinado. A cobertura parcial vem das funções desconhecidas.

---

## Exemplo 3 · Requisito ambíguo de backlog

**Pedido**

> Como gestor de contratos, quero acompanhar os contratos da minha unidade.

**Raciocínio**

1. *Tipo:* o usuário informou `tipo=desenvolvimento`. Sem isso, a skill perguntaria, porque o texto não diz se o sistema existe (lacuna que impede a contagem).
2. *Fronteira:* não se sabe se os contratos são mantidos por este sistema ou lidos de outro. Isso não impede a contagem, mas cria **alternativas excludentes**: Contrato é ALI (mantido aqui) **ou** AIE (lido de outro sistema). Exatamente uma das duas vale: hipóteses H1 e H2 no mesmo grupo.
3. *Coerência de cada alternativa:* um ALI só existe se algum processo da aplicação o mantém, e um AIE só existe se algum processo o lê (01 §2). Por isso H1 inclui, além do ALI, a função mínima que o mantém (registrar contrato), e as duas alternativas **exigem** a consulta (H3). Sem essas ligações, o cenário mínimo seria "um AIE que ninguém lê", que não é uma aplicação possível; o script rejeita esse caso.
4. *Transações:* "acompanhar" implica ao menos consultar os contratos (hipótese H3, CE). Não implica alertar vencimentos nem emitir relatórios: são pendências, sem PF (convenção C1).
5. *Nenhuma função é evidência pura*: o pedido só afirma o objeto (contratos) e a intenção (acompanhar).

**Hipóteses**

| ID | Hipótese | Trecho | Grupo | Exige | Efeito |
|---|---|---|---|---|---:|
| H1 | Contratos mantidos por este sistema, com registro | "contratos da minha unidade" | origem dos contratos | H3 | +11 PF |
| H2 | Contratos lidos de outro sistema | "contratos da minha unidade" | origem dos contratos | H3 | +5 PF |
| H3 | Acompanhar inclui consultar os contratos | "acompanhar" | — | — | +4 PF |

**Memória de cálculo**

| ID | Função identificada | Tipo | PF | Base |
|---|---|---|---:|---|
| F01 | Contrato (mantido aqui) | ALI | 7 | H1 |
| F02 | Registrar contrato | EE | 4 | H1 |
| F03 | Contrato (lido de outro sistema) | AIE | 5 | H2 |
| F04 | Consultar contratos da unidade | CE | 4 | H3 |

- **Cenário mínimo:** 9 PF (H2 e a consulta que ela exige, H3).
- **Cenário máximo:** 15 PF (H1 e H3).
- **Cobertura:** parcial; o pedido não permite saber se há outras funções.
- **Pendências:** de onde vêm os contratos; quais operações "acompanhar" abrange (só consultar, ou também alterar e encerrar contratos); se precisa de alertas de vencimento, relatórios ou indicadores; como "minha unidade" é determinada.

Para a viabilidade, este resultado diz sobretudo que o pedido ainda não tem conteúdo suficiente: a resposta útil é a lista de pendências, e não o número.

---

## Exemplo 4 · Contagem indicativa

**Pedido** (`modo=indicativa`)

> Sistema para a Seção de Estágio gerir os estagiários do tribunal: dados do estagiário, instituições de ensino conveniadas (com dados do convênio) e termos de compromisso. Cada estagiário pode ter vários termos ao longo do tempo, e os termos são guardados mesmo depois do desligamento. A unidade de lotação vem do sistema de estrutura organizacional e o supervisor é um servidor cujos dados vêm do RH. A situação do estágio é uma de: ativo, suspenso, desligado.

**Raciocínio:** Estagiário e Instituição de ensino são dados de negócio mantidos (ALI): o pedido diz que a seção os gere e separa explicitamente o que vem de outros sistemas (unidade e servidor), o que afirma a origem local do resto. Termo de compromisso sobrevive ao desligamento e tem vida própria (ALI separado, 01 §2). Unidade e Servidor são lidos de outros sistemas (AIE). Situação do estágio é dado de código.

| ID | Função identificada | Tipo | PF |
|---|---|---|---:|
| F01 | Estagiário | ALI | 35 |
| F02 | Instituição de ensino | ALI | 35 |
| F03 | Termo de compromisso | ALI | 35 |
| F04 | Unidade (estrutura organizacional) | AIE | 15 |
| F05 | Servidor (RH) | AIE | 15 |
| | **Total** | | **135 PF** |

Aviso que acompanha o resultado: na pesquisa da NESMA, a indicativa desviou até cerca de 50% da detalhada em alguns casos. Se os processos do pedido já forem conhecidos, a contagem estimada é preferível.
