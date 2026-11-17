# 01 · Fundamentos e identificação de funções

Marcações: **[normativa: fonte]** é regra da fonte citada. **[convenção da skill]** é decisão desta skill para estimativa, sem fonte normativa direta. **[adaptação institucional: TRE/SE]** é prática do órgão.

Fontes: *Roteiro de Métricas de Software do SISP 3.0* (2026), que descreve o IFPUG CPM 4.3.1 (citado como "SISP §x"); NESMA, *Early Function Point Analysis* (2015).

## 1. Propósito, tipo de contagem e fronteira

- **Propósito desta skill** [adaptação institucional: TRE/SE]: estimativa preliminar do tamanho funcional de um pedido de solução dirigido à equipe interna de desenvolvimento, como insumo da análise de viabilidade. Não é medição, não é contagem detalhada e não serve para contratação.
- **Tipos de contagem** [normativa: SISP §5.1, item 2]:
  - **Desenvolvimento:** funcionalidades entregues na primeira versão da aplicação, incluindo eventuais funções de conversão de dados (carga inicial ou migração requisitada).
  - **Melhoria:** funcionalidades incluídas, alteradas e excluídas numa aplicação existente, mais eventuais funções de conversão.
- **Fronteira da aplicação** [normativa: SISP §5.1]: limite lógico entre a aplicação medida, seus usuários e as outras aplicações, definido pela **visão do usuário** e não pela implementação. Não se divide a fronteira por equipe, plataforma ou tecnologia. Fronteira mal posicionada duplica transações e arquivos ou conta transferências de dados de forma errada.
- **Como delimitar** [normativa: SISP §5.1, dicas do CPM]: verifique quem mantém cada grupo de dados (o que é mantido por outra aplicação está fora); agrupe processos por área funcional; um diagrama de contexto ajuda.
- **Registro obrigatório:** a fronteira adotada vai para `projeto.fronteira`. Se o pedido não permite decidir se algo está dentro ou fora, essa é uma lacuna que **impede** a contagem: pergunte (ver SKILL.md, política de incerteza).

## 2. Funções de dados (ALI e AIE)

**Definições** [normativa: SISP §5.1, item 3]:

- **ALI (Arquivo Lógico Interno):** grupo de dados logicamente relacionados, reconhecido pelo usuário e **mantido** por um processo elementar da aplicação medida.
- **AIE (Arquivo de Interface Externa):** grupo de dados logicamente relacionados, reconhecido pelo usuário, **mantido por outra aplicação** e apenas referenciado pela aplicação medida. Um AIE é obrigatoriamente um ALI de outra aplicação.

**Teste para decidir ALI × AIE × nada:**

1. É um grupo de dados que o usuário de negócio reconhece (fala dele, consulta, mantém)? Se não, não é função de dados.
2. É **dado de código** (seção 5)? Se sim, não conta.
3. Quem mantém? Se é a aplicação medida, é ALI. Se é outra aplicação e a medida só lê, é AIE.
4. Só é AIE se a aplicação medida **usa** os dados num processo elementar dela (lê para exibir, validar ou calcular). Integração não é sinônimo de AIE: receber dados de outro sistema e gravá-los num ALI próprio é uma EE da aplicação medida, não um AIE [convenção da skill, a partir das definições acima].

**Agrupamento (um arquivo ou vários)** [normativa: SISP §5.1, tabela 1]:

- Um ALI/AIE tem, por padrão, um subgrupo (RLR). Subgrupos adicionais são RLRs do **mesmo** arquivo quando são: subtipos (funcionário assalariado × horista), entidade associativa com atributos não-chave, ou entidade atributiva em relacionamento que não seja 1-1 obrigatório.
- **Decisão prática** [convenção da skill]: uma entidade que não tem significado de negócio sem a principal (itens de um pedido, turmas de um curso, dependentes de um servidor) é RLR do arquivo principal. Uma entidade com ciclo de vida próprio, que o usuário trata como objeto independente ou que sobrevive à exclusão da outra, é arquivo separado. **Dependência referencial não basta**: "reserva precisa de sala" não faz de Reserva um RLR de Sala. Decida pelo que o pedido diz sobre a vida da entidade; se o pedido não diz, registre a escolha como hipótese com o efeito em PF (7 PF por ALI a mais).
- **Histórico** [normativa: SISP §8.2.3]: histórico de estados de um registro é parte do ALI principal, mantido pelas mesmas funções. Só vira ALI independente se for mantido separadamente (por exemplo, sobrevive à exclusão do registro principal). A consulta ao histórico, se pedida, conta como função transacional.
- Na contagem estimada **não se contam DERs nem RLRs** para fins de complexidade: a complexidade é fixa (ver 02). Os conceitos de RLR servem aqui só para decidir quantos arquivos existem.

## 3. Processo elementar

**Definição** [normativa: SISP §8.3]: a menor unidade de atividade significativa para o usuário. É autocontido e deixa o negócio da aplicação num estado consistente.

- Um processo com várias etapas ou telas não se divide: "Incluir empregado" com três abas (dados gerais, endereço, dependentes) é um único processo elementar, porque nenhuma aba isolada é uma transação completa [normativa: SISP §8.3].
- Abas ou telas podem ser processos distintos quando cada uma é autocontida, reconhecida pelo usuário, com requisito e lógica próprios [normativa: SISP §8.3].
- **Unicidade** [normativa: SISP §5.1, item 4; §8.4 c]: cada função transacional é um processo elementar **único**. Dois requisitos que fazem a mesma coisa sobre os mesmos dados, com a mesma lógica, são uma função só. Contar telas, abas ou botões como processos é falha de contagem apontada pela CGU.
- **Operações CRUD** [convenção da skill]: incluir, alterar e excluir são, em regra, processos elementares distintos quando o pedido indica que o usuário os executa separadamente. Não gere as quatro operações automaticamente: conte só as que o pedido menciona ou implica (verbos como "cadastrar", "manter", "gerenciar" podem implicar mais de uma, e então cada uma é **hipótese**, não evidência).

## 4. Funções transacionais (EE, SE, CE)

**Definições** [normativa: SISP §5.1, item 4]:

- **EE (Entrada Externa):** processa dados ou informação de controle que **entram** pela fronteira. Intenção primária: **manter um ou mais ALI** ou **alterar o comportamento do sistema**.
- **CE (Consulta Externa):** envia dados para fora da fronteira com intenção primária de **apresentar** dados por simples recuperação. A lógica **não** tem fórmula matemática, cálculo nem dado derivado; nenhum ALI é mantido e o comportamento do sistema não muda. Uma CE lê ao menos um arquivo.
- **SE (Saída Externa):** envia dados para fora com processamento **além** da recuperação: cálculo, dado derivado, manutenção de ALI ou alteração de comportamento.

**Critérios semânticos para classificar sem contar campos** [convenção da skill, a partir das definições acima]:

| Sinal no pedido | Classificação provável | Cuidado |
|---|---|---|
| "cadastrar", "registrar", "incluir", "alterar", "excluir", "cancelar", "aprovar" (grava algo) | EE | aprovar/cancelar só são EE se gravam mudança de estado; se só exibem, não |
| "parametrizar", "configurar regra" que muda o comportamento | EE | parâmetro que é dado de código não conta (seção 5) |
| "consultar", "visualizar", "listar", "detalhar", "pesquisar com filtros" sem cálculo | CE | se a lista mostra total, média, percentual, contagem ou dado derivado, é SE |
| "relatório com totais", "painel", "indicador", "taxa", "estatística", "gráfico de" | SE | um relatório que só lista registros, sem cálculo, é CE |
| "emitir documento" que grava (ex.: número de protocolo gerado e gravado) | SE (ou EE se a intenção primária é gravar) | decidir pela intenção primária e registrar a justificativa |
| "exportar", "imprimir", "baixar em PDF/CSV" a mesma consulta | **mesma função** | ver 03, múltiplas mídias |
| "notificar por e-mail", "enviar aviso" | **primeiro**, teste se é processo elementar autônomo (§3): disparado por si (agenda, prazo, comando do usuário) e completo sozinho. Se é só consequência de outra operação ("ao concluir, avisa o solicitante"), é parte daquela função. Se for autônomo, classifique pela lógica, como qualquer saída: CE se só recupera e envia; SE se calcula, deriva dados, grava ou muda comportamento | o canal (e-mail, tela, arquivo) não decide o tipo |
| "importar arquivo", "receber dados do sistema X e gravar" | EE | a fonte externa não vira AIE por isso |
| "disponibilizar dados para o sistema X" (API, arquivo) | CE ou SE da aplicação medida (dados saem pela fronteira) | SE se houver cálculo ou dado derivado |

- **Mensagens** [normativa: SISP §5.1, tabela 2]: mensagens de erro, de confirmação e de validação fazem parte da função que as emite; nunca são funções próprias.
- **Navegação** [normativa: SISP §5.1, tabela 2; §8.4]: menus, botões de navegação, paginação e ajudas de navegação não são funções nem dados.
- **Atributos lidos só para processar** [normativa: SISP §5.1, tabela 2]: dados recuperados de um ALI/AIE para validação, sem sair pela fronteira, não criam função nova. Mas o arquivo lido **é** referenciado pela transação, o que importa para o EFPA (ver 02).

## 5. Dados de código (não contam)

[normativa: SISP §8.4.1, a partir do CPM 4.3.1, parte 3, cap. 1]

Dados de código implementam requisitos **não funcionais**: padronizam a entrada, garantem consistência, substituem descrições por códigos. Consequências:

- não são ALI nem AIE;
- não são RLR nem DER de outro arquivo;
- as transações que os mantêm **não** contam;
- não são arquivo referenciado de nenhuma transação.

| Característica | Dado de código | Dado de negócio |
|---|---|---|
| Obrigatoriedade | obrigatório para a área, mas só opcionalmente armazenado como arquivo | obrigatório para a operação da área |
| Origem do requisito | em geral surge da solução, não do requisito do usuário | identificável pelo usuário de negócio |
| Quem mantém | às vezes um técnico de suporte | o usuário de negócio |
| Papel | padroniza e facilita transações que o referenciam | dado principal das transações |
| Dinâmica | essencialmente estático | muito dinâmico, incluído e alterado na operação normal |

Tipos e exemplos de dados de código:

- **Substituição (código + descrição):** UF (sigla, nome), cores, tipos de documento, situação/status.
- **Ocorrência única:** dados da própria organização (nome, endereço).
- **Estáticos:** tabela de elementos químicos, feriados nacionais fixos.
- **Valores default:** valores iniciais de atributos de novos registros.
- **Valores válidos:** lista de valores permitidos para um atributo ("presencial, EaD, híbrida").
- **Faixas válidas:** faixa de telefones permitidos, faixa de temperatura.

**Cuidado** [convenção da skill]: o nome "tabela de domínio" não decide nada. Uma entidade auxiliar com atributos de negócio próprios, mantida rotineiramente pelo usuário de negócio e usada como objeto do processo (ex.: Fornecedor com CNPJ, contato e histórico de fornecimentos; Sala com capacidade e recursos), é dado de negócio. Na dúvida, aplique a tabela acima e registre a decisão em `nao_contados` (categoria `dado-de-codigo`) ou na justificativa do ALI.

## 6. Conversão de dados

[normativa: SISP §5.1, item 6; §7.6]

Cargas iniciais e migrações **requisitadas** no projeto contam como funções de conversão (em geral EE de carga e, se pedidos, relatórios de carga como CE/SE). Elas entram no tamanho do projeto, mas não no tamanho da aplicação depois de implantada. Se o pedido só menciona "aproveitar os dados do sistema antigo" sem detalhe, registre como pendência e, se o efeito for relevante, como hipótese com PF.

[convenção da skill] Na estimativa, registre as funções de conversão com o requisito "conversão de dados" na justificativa, para que fiquem identificáveis na memória de cálculo.
