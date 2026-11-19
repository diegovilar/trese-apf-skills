# 02 · Regras NESMA: estimada, indicativa e melhoria

Fontes: NESMA, *Early Function Point Analysis* (2015) e a tradução autorizada da FATTO, *Contagem Antecipada de Pontos de Função*; NESMA, *APF para Melhoria de Software* 2.2.1 (tradução PT, 2010; citado como "EFPA §x"); SISP 3.0 §5.1 (tabela de contribuição do CPM 4.3.1).

Todas as contas são feitas pelo script `scripts/apf.py`. Este arquivo explica as regras para que o agente classifique corretamente e preencha o JSON. **O agente não soma nem multiplica.**

## 1. Os três métodos da NESMA

[normativa: NESMA, Early FPA]

| Método | O que se identifica | Complexidade | Uso nesta skill |
|---|---|---|---|
| Detalhada | todas as funções (ALI, AIE, EE, SE, CE), com DERs, RLRs e ALRs | calculada por função | **não usada** |
| **Estimada** (*high level*) | todas as funções (ALI, AIE, EE, SE, CE) | **fixa**: dados = Baixa, transações = Média | **padrão** [adaptação institucional: TRE/SE] |
| Indicativa | só as funções de dados (ALI, AIE) | não se aplica | modo opcional (`modo=indicativa`) |

A estimada difere da detalhada **só** na complexidade, que é pré-definida em vez de calculada. A identificação das funções segue as mesmas regras (ver 01).

## 2. Contagem estimada

[normativa: NESMA, Early FPA; pesos da tabela 6 do CPM 4.3.1, SISP §5.1]

| Tipo | Complexidade fixa | PF |
|---|---|---|
| ALI | Baixa | 7 |
| AIE | Baixa | 5 |
| EE | Média | 4 |
| SE | Média | 5 |
| CE | Média | 4 |

- Não há fator de ajuste (VAF): o resultado é PF não ajustado.
- **Exatidão** [normativa: NESMA, Early FPA]: na pesquisa da NESMA com cerca de 100 aplicações, a estimada não teve diferença estatisticamente significativa em relação à detalhada. Isso vale para a contagem bem feita a partir de requisitos suficientes; a qualidade da estimativa depende da qualidade do subsídio.

## 3. Contagem indicativa

[normativa: NESMA, Early FPA]

**Tamanho indicativo (PF) = 35 × nº de ALI + 15 × nº de AIE**

- Supõe, em média, 3 EE (incluir, alterar, excluir), 2 SE e 1 CE para cada ALI, e 1 SE e 1 CE para cada AIE.
- Serve quando só se conhece o modelo de dados (entidades), como numa macroestimativa de estudo técnico preliminar.
- **Aviso obrigatório na saída** (o script inclui): na pesquisa da NESMA, a indicativa desviou até cerca de 50% da detalhada em alguns casos. É uma observação da pesquisa, não um limite garantido de erro. Em aplicações com mais ou menos saídas que a média, os multiplicadores 35 e 15 podem não se aplicar.
- **Só em desenvolvimento** [convenção da skill]: a fórmula estima o tamanho de uma aplicação a partir dos arquivos e não fornece as funções transacionais alteradas que uma melhoria exige. `modo=indicativa` com `tipo=melhoria` é rejeitado (estágio 1 da validação).
- As regras de identificação de ALI/AIE e de dados de código (01) valem igualmente.

## 4. Projetos de melhoria

Uma função de dados é **alterada** quando mudam seus tipos de dados (inclusão, exclusão ou mudança de atributos) por alteração de regra de negócio [normativa: SISP §7.3]. Uma transação é **alterada** quando mudam seus tipos de dados, os arquivos que referencia ou sua lógica de processamento [normativa: SISP §7.3, a partir do CPM 4.3.1]. **Incluída** é a função nova; **excluída** é a função retirada da aplicação.

Mudança só de nome de um atributo, sem efeito funcional, não é alteração: nem a função de dados nem a transação são contadas [normativa: EFPA, exemplo 8].

A skill tem dois regimes, escolhidos por `melhoria=`.

### 4.1 Regime `sem-fatores` (padrão)

[convenção da skill; padrão definido pelo usuário]

- Cada função incluída, alterada ou excluída entra com o peso cheio da estimada (7/5/4/5/4), sem fator.
- Unidade: **PF de melhoria** (soma simples). Não é PFM da NESMA.
- **Quais transações contam como alteradas (convenção C4)** [convenção da skill, com apoio no SISP §7.3]: só as que têm mudança nos **próprios** dados, nos arquivos que referencia (**passa a ler ou deixa de ler** um arquivo) ou na própria lógica. Uma transação que continua usando um arquivo que mudou, sem nenhum efeito nos dados ou na lógica dela, **não** conta como alterada neste regime.

### 4.2 Regime `nesma` (EFPA)

[normativa: EFPA §2.3, §3.2–3.6, exemplos 3, 6, 7, 8, 9, 11]

- O tamanho é expresso em **PFM (pontos de função de melhoria)**, unidade distinta de PF. Nunca chame o resultado de PF.
- **PFM de cada função = PF da função × fator de impacto.** O PF da alterada é o tamanho **depois** da alteração; na estimada, o peso fixo do tipo.
- **PFM total = soma dos PFM** de incluídas, excluídas e alteradas.
- Rótulo obrigatório (o script inclui): **"estimativa híbrida: pesos NESMA estimada + fatores EFPA"**. O EFPA foi escrito para a contagem detalhada; combinar com pesos estimados é uma adaptação, e a própria NESMA ressalva que o método não foi validado cientificamente.

**Fatores firmes** (o script aplica):

| Situação | Fator |
|---|---|
| Função incluída | 1,00 |
| Função excluída | 0,40 |
| Função de dados que só muda de tipo (AIE → ALI ou ALI → AIE) | 0,40 (se também mudam TDs, vale o maior entre 0,40 e o fator da tabela 1; sem a proporção de TDs, faixa de 0,40 até o máximo compatível) |
| Transação com alteração só cosmética (nenhum TD nem AR alterado: rótulo, cabeçalho, layout, texto de mensagem) | 0,25 |

**Tabela 1: função de dados alterada** (% de TDs alterados = TDs incluídos + alterados + excluídos, dividido pelo número original de TDs):

| % de TDs | ≤ 1/3 | ≤ 2/3 | ≤ 100% | > 100% |
|---|---|---|---|---|
| Fator | 0,25 | 0,50 | 0,75 | 1,00 |

**Tabela 2: transação alterada** (linhas: % de ARs afetados; colunas: % de TDs afetados; cada percentual é relativo ao número original da transação):

| % ARs \ % TDs | ≤ 2/3 | ≤ 100% | > 100% |
|---|---|---|---|
| ≤ 1/3 | 0,25 | 0,50 | 0,75 |
| ≤ 2/3 | 0,50 | 0,75 | 1,00 |
| ≤ 100% | 0,75 | 1,00 | 1,25 |
| > 100% | 1,00 | 1,25 | 1,50 |

Regras para contar TDs e ARs afetados:

- TDs afetados = incluídos + alterados + excluídos (exemplo 10: 2 + 1 + 3 = 6).
- **AR afetado** = arquivo incluído, excluído **ou alterado** entre os que a transação referencia. Se um arquivo usado pela transação muda, ele conta como AR afetado **mesmo que a transação não use os TDs alterados**, e a transação **entra** no escopo da melhoria (exemplo 7). Essa é a principal diferença de seleção em relação ao regime `sem-fatores`.
- Os percentuais podem passar de 100% quando se acrescentam TDs ou ARs.

**Quando o subsídio não traz os números** (o caso comum numa estimativa):

- Se o pedido **declara** os TDs e ARs originais e os afetados (ou dá informação suficiente para fixar a linha e a coluna da tabela), informe `td` e `ar` no JSON e o script calcula o fator.
- Se não declara, **não invente números nem um valor central**. Informe no JSON uma **faixa** (`efpa.faixa.min` e `efpa.faixa.max`) com os fatores da tabela compatíveis com o que se sabe, e explique na justificativa da faixa o que se sabe e o que falta. Exemplos:
  - transação que passa a ler um arquivo novo (e nenhum outro arquivo dela muda), com número original de arquivos desconhecido: um AR afetado sobre 3 ou mais originais dá ≤ 1/3; sobre 2, dá 50% (≤ 2/3); sobre 1, dá 100%. Com % de TD ≤ 2/3, o fator vai de 0,25 a 0,75. Diga exatamente essas condições na justificativa; se também um arquivo que ela já lia for alterado, são 2 ARs afetados e a faixa muda;
  - sem nenhuma informação: a faixa é a tabela inteira (dados 0,25 a 1,00; transações 0,25 a 1,50). Reconheça a amplitude em vez de estreitá-la sem base.
- Sem baseline, também não se sabe **quais outras transações** usam os arquivos alterados e entrariam pelo exemplo 7. Declare `cobertura` como `parcial`, com esse motivo, e registre a baseline como pendência. A faixa (fator desconhecido) e a cobertura parcial (funções desconhecidas) são incertezas diferentes: uma pode existir sem a outra.

## 5. Unidades e rótulos na saída

| Situação | Unidade | Observação |
|---|---|---|
| Desenvolvimento, estimada | PF | não ajustado |
| Desenvolvimento, indicativa | PF | com aviso de desvio |
| Melhoria, `sem-fatores` | PF de melhoria | soma simples |
| Melhoria, `nesma` | PFM | rótulo de estimativa híbrida; total como faixa quando houver fator em faixa |

Em qualquer situação, `cobertura: parcial` marca o total como PARCIAL no resumo.
