Distribuição: **Ouvidoria × pouco subsídio**, com recepção e consulta individual; **convocação de mesários × médio**, com preparação, comunicação e registro de presença; **logística administrativa de urnas × rico**, com movimentações, conferência e ocorrências. Os três pedidos foram escritos na voz da área de negócio, não da TI. A revisão retira precisões artificiais e acrescenta duas lacunas de etapa ancoradas no processo: entrada do resultado da entrega da convocação e registro da conferência do retorno das urnas. H1 não serve para medir descoberta obrigatória de etapas além das quatro regras gerais: seu texto não oferece âncora suficiente. Os contrastes são mais informativos que os respectivos holdouts, mas conservam o nível do par. Casos sintéticos para aprovação humana; cenários são referências de cálculo, não totais obrigatórios independentes da interpretação.

## H1 · Manifestações à Ouvidoria (holdout, pouco subsídio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria. A equipe quer gerenciar esses registros, e o cidadão precisa consultar as suas manifestações.

**Informação ausente:** quais operações a equipe espera de “gerenciar”; como identificar o cidadão e obter os dados necessários para vincular suas manifestações; se há análise ou decisão sobre o que foi encaminhado e quem a realiza.

**Regras gerais acionadas:**
- Verbo amplo: “A equipe quer gerenciar esses registros”, sem operações discriminadas.
- Vínculo com pessoa: “o cidadão precisa consultar as suas manifestações”, sem identificador ou origem dos dados.
- Submissão a uma unidade: “manifestações enviadas pelos cidadãos à Ouvidoria”, sem tratamento descrito.
- Origem não afirmada: não se aplica às manifestações, cujo registro na aplicação é solicitado. “Cidadãos” não autoriza inventar um cadastro de pessoas para então oferecer ALI × AIE.

**O que o texto já responde:** há registro das manifestações na aplicação, seu destino é a Ouvidoria e o cidadão consultará as suas. Não há justificativa para perguntar se essas três coisas existem.

**Funções:**
- Obrigatórias (evidência):
  - Manifestações — **ALI**; “registrar no sistema as manifestações”.
  - Registrar manifestação — **EE**; “registrar no sistema”.
  - Consultar as próprias manifestações — **CE**; “o cidadão precisa consultar as suas manifestações”, sem processamento além da recuperação indicado.
- Aceitas como hipótese:
  - Corrigir manifestação — **EE**; “gerenciar”.
  - Cancelar manifestação — **EE**; “gerenciar”; não somar cancelamento e exclusão lógica da mesma operação.
  - Consultar manifestações pela equipe — **CE**; “A equipe quer gerenciar”. Só é adicional se houver uma distinção funcional fundamentada em relação à consulta individual, não apenas outro perfil de acesso.
  - São hipóteses opcionais de operações sobre o ALI obrigatório. Não há grupo de alternativas de origem. Interpretações que apenas renomeiem a mesma operação não são somáveis.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - Analisar, distribuir, deferir, responder ou encerrar atendimento — o verbo genérico não basta para presumir esse fluxo específico; sua existência fica como pendência.
  - ALI de cidadãos ou AIE de cadastro eleitoral, de pessoas ou de identidade — solução para o vínculo ainda não descrita.
  - Avisos, anexos, painel estatístico e migração — não mencionados nem implicados.
  - Arquivo próprio de status fixos, confirmação do registro e navegação — dados de código ou partes de funções, não funções adicionais.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo: registro e consulta individual — **1 ALI × 7 + 1 EE × 4 + 1 CE × 4 = 15 PF**.
- Máximo sem consulta adicional da equipe: incluir correção e cancelamento — **1 ALI × 7 + 3 EE × 4 + 1 CE × 4 = 23 PF**.
- Máximo com consulta funcionalmente distinta da equipe: **1 ALI × 7 + 3 EE × 4 + 2 CE × 4 = 27 PF**.
- Em todos, a EE de registro mantém Manifestações e as consultas leem esse ALI. Não acrescentar cadastro pessoal ou fluxo de resposta para completar o cenário.

**Cobertura:** **parcial**. A faixa cobre operações implicadas por “gerenciar”, não um tratamento ou uma identificação funcional que ainda não foram especificados.

**Pendências obrigatórias (reprovam se ausentes):**
- Quais operações “gerenciar” abrange para a equipe?
- Como o cidadão é identificado e de onde vêm os dados usados para vinculá-lo às suas manifestações?
- Há análise ou decisão sobre as manifestações encaminhadas à Ouvidoria? Por quem?
- **Descoberta de etapas além das quatro regras: nenhuma passou no teste.** A recepção não permite exigir, sem ampliar o pedido, distribuição, resposta, recursos ou prazos. As três perguntas acima decorrem das regras gerais, não demonstram por si só descoberta de etapas do domínio.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Se haverá distribuição, resposta, prazos, anexos ou avisos.
- Como será a autenticação, sem substituir a pergunta sobre identificação funcional.
- Por ser pouco subsidiado, as possibilidades de ciclo ficam aqui e não geram PF.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: se haverá registro no sistema, se o destino é a Ouvidoria ou se o cidadão consultará suas manifestações.
- Não reabrir a origem das manifestações como ALI × AIE.
- Identificação, alcance de “gerenciar” e existência de análise são obrigatórios aqui, mas estarão respondidos em H1c.

**Notas para o juiz:** aceitar máximos de 23 ou 27 PF conforme a fundamentação da consulta pela equipe. Exigir hipóteses com efeito visível nos cenários, não CRUD tratado como evidência. “Quais integrações?” ou “Terá usuários?” não substituem a pergunta explícita sobre identificação do cidadão. Não reprovar por ausência de perguntas sobre etapas sem âncora textual. Este par mede as regras gerais, não o objetivo adicional de descoberta de etapas.

## H1c · Identificação e resposta definidas (contraste de H1, pouco subsídio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos registrar no sistema as manifestações enviadas pelos cidadãos à Ouvidoria, com nome e CPF informados pelo próprio cidadão para identificar quais manifestações são dele na consulta. A equipe da Ouvidoria poderá corrigir o texto e cancelar registros feitos por engano, além de analisar o conteúdo e registrar a resposta final ao cidadão.

**Informação ausente:** nenhuma das três lacunas obrigatórias de H1 permanece. Avisos, anexos e requisitos de autenticação continuam não descritos, mas não são funcionalidades presumidas.

**Regras gerais acionadas:**
- Identificação respondida por nome e CPF informados pelo próprio cidadão.
- Tratamento respondido pela análise da equipe da Ouvidoria e registro da resposta final.
- O verbo amplo foi substituído por operações concretas.
- A origem das manifestações continua local; os dados pessoais são informados no registro, sem requisito de um grupo independente de pessoas.

**O que o texto já responde:** fonte dos dados de identificação, vínculo das manifestações ao cidadão, correção, cancelamento e análise com resposta pela equipe da Ouvidoria.

**Funções:**
- Obrigatórias (evidência):
  - Manifestações — **ALI**; “registrar no sistema as manifestações”, incluindo identificação e resposta.
  - Registrar manifestação — **EE**; “registrar no sistema”.
  - Consultar as próprias manifestações — **CE**; “identificar quais manifestações são dele na consulta”.
  - Corrigir texto — **EE**; “poderá corrigir o texto”.
  - Cancelar manifestação — **EE**; “cancelar registros feitos por engano”.
  - Registrar resposta final — **EE**; “registrar a resposta final ao cidadão”. A análise humana não é outra transação.
- Aceitas como hipótese:
  - Nenhuma adicional necessária. O texto não pede consulta autônoma da equipe com lógica diferente.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - Cadastro de cidadãos ou leitura de cadastro externo — não decorrem de nome e CPF informados na própria manifestação.
  - EE separada de análise, aprovação ou encerramento — não foram pedidas operações autônomas para isso.
  - SE de envio de resposta por e-mail — registrar uma resposta não pede uma notificação independente.
  - Consulta adicional apenas por haver outro perfil; avisos, anexos, painéis e migração — sem suporte.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo = máximo de referência: **1 ALI × 7 + 4 EE × 4 + 1 CE × 4 = 27 PF**.
- Registro, correção, cancelamento e resposta mantêm Manifestações; a CE lê esse ALI. Não há arquivo de pessoas a alimentar.

**Cobertura:** **completa para o escopo expresso**, não para todos os serviços possíveis de uma Ouvidoria.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das lacunas obrigatórias de H1 permanece. Nenhuma lacuna adicional de etapa foi identificada com âncora suficiente.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Segurança e autenticação da consulta; possíveis avisos ou anexos.
- Eventual consulta autônoma da equipe, sem PF enquanto não sustentada.
- Não confundir identificação funcional respondida com suficiência dos mecanismos de segurança.

**Pendências ou perguntas proibidas (contrastes):**
- Como identificar o cidadão ou de onde vêm nome e CPF.
- Quais operações “gerenciar” abrange.
- Se há análise, quem a faz ou se a equipe registra resposta.
- Se as manifestações serão registradas no sistema ou consultadas pelo cidadão.

**Notas para o juiz:** o contraste é mais informativo, embora mantenha “pouco subsídio” como rótulo do par. Não é necessário que ele preserve o total máximo do holdout: a resposta passa de possibilidade não contável a função expressa. Aqui o resultado também é 27 PF, por composição diferente do máximo de H1 com consulta da equipe. Perguntas proibidas reprovam mesmo se registradas fora do primeiro lote.

## H2 · Nomeações e entrega das convocações (holdout, médio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.

**Informação ausente:** quem mantém os locais de votação; o que a área chama de problema de entrega e como essa informação chega ao sistema após o envio. Não há pedido de dispensa, aprovação de nomeação ou tratamento disciplinar de faltas.

**Regras gerais acionadas:**
- Origem não afirmada: “relação de locais de votação, com nome e endereço” não informa o mantenedor.
- Identificação pessoal: respondida por inscrição e nome consultados no cadastro eleitoral.
- Verbo amplo: as operações de preparar nomeações e enviar convocações são detalhadas; não é necessário perguntar genericamente o significado de “preparar”.
- Submissão a uma unidade: não se aplica. O cartório cria nomeações; não há pedido apresentado por mesário.
- A entrada do resultado da entrega é uma lacuna de etapa adicional, não mera repetição da regra sobre origem de um grupo de dados.

**O que o texto já responde:** registro das nomeações, origem da identificação dos mesários, consulta dos locais, envio por e-mail, data de envio na nomeação, relação de problemas de entrega, registro de presença/ausência e lista de ausentes. “Providenciar outro contato” não exige, por si só, um módulo de telefonia ou outro canal de envio.

**Funções:**
- Obrigatórias (evidência):
  - Nomeações — **ALI**; “registrar cada nomeação”, com data de envio e situação de presença.
  - Eleitores — **AIE**; “inscrição e o nome [...] consultados no cadastro eleitoral, que é mantido no sistema eleitoral”. Lido ao registrar a nomeação.
  - Registrar nomeação — **EE**; “O cartório vai registrar cada nomeação”.
  - Consultar locais — **CE**; “consultar a relação de locais de votação, com nome e endereço”.
  - Enviar convocação — **SE**; “enviar as convocações por e-mail” e “a data de envio [...] fique na nomeação”. A saída mantém o ALI, independentemente do canal.
  - Consultar convocações com problema de entrega — **CE**; “uma relação das convocações com problema de entrega”, sem indicadores pedidos.
  - Registrar comparecimento ou ausência — **EE**; “registrará o comparecimento ou a ausência na nomeação”. É uma operação com resultados alternativos.
  - Listar ausentes por local — **CE**; “lista dos mesários marcados como ausentes, por local”. Recupera a ausência registrada, sem inferi-la.
- Aceitas como hipótese:
  - Grupo **L — origem dos locais**, exatamente uma alternativa:
    - **L-externa:** Locais — **AIE**, lido pela CE de consulta dos locais.
    - **L-local:** Locais — **ALI** e uma **EE** mínima para alimentá-lo. Arquivo e mantenedora integram a mesma alternativa.
    - Âncora de ambas: “relação de locais de votação”, sem origem. Não presumir simultaneamente cadastro manual e importação.
  - Grupo **R — resultado da entrega**, alternativas excludentes quanto ao retorno posterior:
    - **R-no-envio:** os problemas são erros conhecidos e guardados durante o envio; sem transação adicional. A SE já obrigatória mantém esse resultado.
    - **R-posterior:** receber e registrar resultados posteriores do serviço de comunicação — uma **EE**, mantendo a situação na nomeação.
    - Âncora: “convocações com problema de entrega”. Não é evidência de integração de retorno, mas sustenta a hipótese com efeito em PF.
  - Se a interpretação fundamentada for registro manual de retorno posterior, aceitar **EE** em lugar da EE de recebimento automático. Não contar ambas sem requisito.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI e AIE de locais simultâneos — origens alternativas.
  - ALI de eleitores ou EE de importação — o pedido descreve consulta externa.
  - AIE do serviço de comunicação só por receber avisos — receber dados e gravá-los em Nomeações não caracteriza leitura de arquivo externo.
  - CE de eleitor apenas para preencher nomeação, EE separada de data de envio ou de erro imediato — leituras e gravações absorvidas pelas funções existentes.
  - Uma EE para presença e outra para ausência; SE de estatísticas só por agrupar por local — não decorrem do texto.
  - Sistema de telefonia, envio por outro canal, dispensa, treinamento, aprovação ou punição por falta — não pedidos.
  - CRUD completo de nomeações ou locais — sem verbo amplo ou enumeração que o sustente.

**Cenários (referência de cálculo, não exigência numérica):**
- Base comum: **1 ALI × 7 + 1 AIE × 5 + 2 EE × 4 + 3 CE × 4 + 1 SE × 5 = 37 PF**.
- Mínimo, L-externa + R-no-envio: base + **1 AIE × 5 = 42 PF**.
- Intermediário, L-externa + R-posterior: base + **1 AIE × 5 + 1 EE × 4 = 46 PF**.
- Máximo, L-local + R-posterior: base + **1 ALI × 7 + 2 EE × 4 = 52 PF**. As duas EE adicionais são alimentação dos locais e retorno da entrega.
- Nomeações é mantido por registro, envio, presença e, quando aplicável, retorno. A situação de falha é gravada na SE de envio ou na EE posterior; a CE de problemas não lê um dado sem origem. Eleitores é lido no registro, e Locais é lido pela consulta, com mantenedora no cenário local.

**Cobertura:** **completa para as interpretações delimitadas nos cenários**, com origem e alcance do retorno ainda abertos. Também aceitar cobertura parcial se a skill explicar que ainda não consegue delimitar os resultados de entrega envolvidos; não aceitar “parcial” como desculpa para omitir funções já expressas ou as alternativas.

**Pendências obrigatórias (reprovam se ausentes):**
- **Regra geral:** quem mantém os locais de votação: a nova aplicação ou outra fonte consultada?
- **Etapa E2 — resultado da entrega:** o que entra na relação de problemas e como o sistema fica sabendo desses problemas? São apenas erros identificados no envio ou também resultados posteriores que precisam ser registrados?
  - **Âncora textual:** “uma relação das convocações com problema de entrega”. Para produzir essa relação, o resultado precisa chegar a Nomeações por algum processo.
  - **Duas respostas plausíveis e consequências:**
    - “Queremos só os e-mails rejeitados na hora do envio; os demais casos continuam fora desse controle.” O resultado é parte da SE de envio já contada; **nenhuma função adicional**.
    - “O serviço de comunicação mandará depois as devoluções e confirmações, e queremos atualizar a situação na nomeação.” Acrescenta **uma EE de recebimento/registro de resultado, 4 PF**; não cria AIE automaticamente.
  - **Por que é necessário delimitar este pedido:** a relação de problemas foi solicitada, mas sua informação de entrada não foi explicada. A pergunta define como uma saída já pedida pode funcionar e se existe processamento posterior ao envio; não oferece um serviço alheio ao escopo.
  - A pergunta só sobre “integrações” não basta. É necessário identificar o retorno da entrega e seu registro; não é obrigatório mencionar tecnologia de callback, API ou protocolo.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autenticação, correção ou cancelamento de nomeações e eventual substituição de mesários.
- Como o cartório executa o outro contato fora do que foi solicitado; não presumir nova função de comunicação.
- Dispensa, treinamento e consequências das ausências pertencem ao domínio, mas não ao escopo apresentado.
- O detalhamento dos resultados do envio pode ser solicitado sem exigir todos os estados possíveis para a estimativa.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: como identificar o mesário ou de onde vêm inscrição e nome.
- Se há envio por e-mail, registro da data, relação de problemas ou registro de presença.
- Se a ausência é calculada a partir de presença não registrada: o texto manda marcar ausências.
- Se há pedidos de dispensa a decidir, como se estivessem mencionados.
- Origem dos locais e mecanismo do resultado da entrega são perguntas necessárias aqui, mas respondidas em H2c.

**Notas para o juiz:** E2 é o objetivo adicional de descoberta de etapa. A primeira resposta do teste restringe “problema de entrega” aos erros observáveis no envio; a segunda inclui um evento posterior. Não transformar essa distinção em dois canais de saída: a função adicional é de entrada. A consulta dos problemas é obrigatória em ambos os cenários. Uma resposta com EE posterior só como pendência, sem hipótese de efeito em PF, perde a distinção implicada pelo texto. Não exigir fases do ciclo eleitoral que o pedido não abrange.

## H2c · Resultado da entrega recebido do serviço (contraste de H2, médio, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos preparar as nomeações dos mesários e enviar as convocações por e-mail. O cartório vai registrar cada nomeação, com o mesário e o local de votação; a inscrição e o nome do mesário serão consultados no cadastro eleitoral, que é mantido no sistema eleitoral. Para escolher o local, o servidor precisa consultar a relação de locais de votação, com nome e endereço, mantida no sistema de locais da Justiça Eleitoral. Queremos que a data de envio da convocação fique na nomeação. Precisamos também de uma relação das convocações com problema de entrega, para o cartório providenciar outro contato. O serviço de comunicação avisará o sistema quando houver devolução do e-mail ou confirmação de entrega, e essas respostas devem atualizar a situação da convocação na nomeação. Depois da eleição, o cartório registrará o comparecimento ou a ausência na nomeação e tirará a lista dos mesários marcados como ausentes, por local.

**Informação ausente:** nenhuma das duas lacunas obrigatórias de H2 permanece. Tecnologias e detalhes operacionais das fontes não são necessários para reabrir a classificação funcional já respondida.

**Regras gerais acionadas:**
- Origem dos locais: respondida por mantenedor externo.
- Identificação do mesário: continua respondida por inscrição e cadastro eleitoral.
- Verbo amplo e submissão a uma unidade: continuam não exigindo perguntas genéricas.
- A etapa E2 foi explicada por retorno posterior do serviço de comunicação, com atualização da nomeação.

**O que o texto já responde:** tudo o que H2 respondia, mais origem dos locais e entrada das devoluções/confirmações após o envio.

**Funções:**
- Obrigatórias (evidência):
  - Nomeações — **ALI**; “registrar cada nomeação”, com situação da convocação e presença.
  - Eleitores — **AIE**; “consultados no cadastro eleitoral, que é mantido no sistema eleitoral”.
  - Locais — **AIE**; “relação de locais [...] mantida no sistema de locais da Justiça Eleitoral”.
  - Registrar nomeação — **EE**; “O cartório vai registrar cada nomeação”.
  - Consultar locais — **CE**; “o servidor precisa consultar a relação de locais”.
  - Enviar convocação — **SE**; “enviar [...] por e-mail” e “a data de envio [...] fique na nomeação”.
  - Receber e registrar resultado da entrega — **EE**; “O serviço de comunicação avisará o sistema [...] e essas respostas devem atualizar a situação”.
  - Consultar convocações com problema — **CE**; “uma relação das convocações com problema de entrega”.
  - Registrar comparecimento ou ausência — **EE**; “registrará o comparecimento ou a ausência na nomeação”.
  - Listar ausentes por local — **CE**; “lista dos mesários marcados como ausentes, por local”.
- Aceitas como hipótese:
  - Nenhuma necessária para os cenários de referência. Os grupos L e R foram resolvidos.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI local de locais e sua alimentação — o pedido esclareceu a consulta à relação mantida externamente.
  - AIE de serviço de comunicação ou ALI separado de comprovantes de entrega apenas porque existem mensagens — o requisito é receber informação e atualizar Nomeações.
  - Duas EE só por haver confirmação e devolução — são resultados alternativos do mesmo processo de recebimento, salvo lógica adicional não descrita.
  - Importação de eleitores, CE autônoma de eleitor para preencher nomeação, gravação de data contada outra vez, presença/ausência duplicadas — mesmos motivos de H2.
  - Funções de outro contato, dispensa, treinamento, substituição e punição — sem requisito.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo = máximo: **1 ALI × 7 + 2 AIE × 5 + 3 EE × 4 + 3 CE × 4 + 1 SE × 5 = 46 PF**.
- Registro, presença e resultado da entrega mantêm Nomeações; o envio também grava nesse ALI. Eleitores é lido no registro e Locais na consulta. O recebimento de mensagens não deixa um AIE fictício sem leitura.

**Cobertura:** **completa para o escopo expresso**. As duas alternativas do holdout agora têm respostas funcionais.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das lacunas obrigatórias de H2 permanece; não pedir de novo o mecanismo de entrada dos resultados.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autenticação e eventual tratamento operacional de mensagens inválidas ou repetidas.
- O outro contato providenciado pelo cartório, sem transformar isso em módulo adicional.
- Outros processos eleitorais continuam fora do pedido apresentado.

**Pendências ou perguntas proibidas (contrastes):**
- Quem mantém os locais ou se é preciso cadastrar a relação na nova aplicação.
- Como o mesário é identificado ou de onde vêm seus dados.
- Se haverá resultados posteriores ao envio, quem os fornece ou se eles atualizam a nomeação.
- Se a relação trata somente de erros imediatos: o retorno posterior está expresso.
- Se há registro da data de envio, de comparecimento/ausência ou lista de problemas.
- Pode haver pergunta técnica sobre o serviço, mas não usá-la para reabrir a existência ou a direção do fluxo já descrito.

**Notas para o juiz:** contraste mais informativo, com o nível “médio” mantido pelo par. Ele responde à origem e à etapa E2 sem acrescentar substituição, dispensa ou outros canais. Locais passa a AIE de evidência e a EE de retorno também passa a evidência; alternativas e perguntas correspondentes devem desaparecer. Não contar uma função para cada valor de resultado.

## H3 · Remessas, retorno e conferência de urnas (holdout, rico, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.
>
> Antes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber.
>
> Também queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas.
>
> A consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.
>
> O acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.

**Informação ausente:** identificação e fonte dos dados dos responsáveis; existência e autoria de análise/decisão sobre ocorrências; como a conferência é registrada em relação à chegada do material. O texto também não resolve totalmente a autonomia lógica dos registros de movimentação e ocorrência, de modo que não se deve impor um único agrupamento de arquivos.

**Regras gerais acionadas:**
- Vínculo pessoal: “identificar os responsáveis por entregar e receber”, sem identificador ou fonte.
- Submissão a uma unidade: ocorrência registrada e aviso à Seção de Logística, sem dizer se a seção analisa ou decide algo.
- Origem: remessas e registros operacionais são registrados na aplicação; urnas continuam no cadastro do sistema nacional. Não há origem em aberto para as urnas.
- Verbo amplo: “organizar” é desenvolvido nas operações seguintes. Não perguntar genericamente o que organizar remessas significa.
- A articulação entre chegada e conferência é uma lacuna de etapa adicional, não a pergunta geral sobre análise das ocorrências.

**O que o texto já responde:** criação, correção e cancelamento de remessas; registro de saída, entrega e retorno; possibilidade de retornos parciais; existência da conferência; ocorrências de transporte e aviso à seção ao registrá-las; consultas, ficha em PDF e quadro quantitativo. A fonte das urnas, a autenticação externa e as exclusões técnicas estão expressas.

**Funções:**
- Obrigatórias (evidência):
  - Remessas — **ALI**; “vai registrar cada remessa com a data prevista, a zona de destino e as urnas”.
  - Urnas — **AIE**; “números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro”. É lido, pelo menos, no registro das urnas da remessa.
  - Registrar remessa — **EE**; “vai registrar cada remessa”.
  - Corrigir remessa — **EE**; “pode corrigir a data ou a relação de urnas”. São atributos da mesma operação, não duas funções.
  - Cancelar remessa — **EE**; “cancelar uma remessa que não será mais realizada”.
  - Registrar saída — **EE**; “registrar a saída efetiva, com a data e as urnas que saíram”.
  - Registrar entrega — **EE**; “depois a entrega à zona, com a data e as urnas recebidas”.
  - Registrar retorno — **EE**; “No retorno ao depósito, serão registradas a data e as urnas que chegaram”.
  - Registrar ocorrência — **EE**; “Também queremos registrar ocorrências de transporte”, inclusive fatos no trajeto, não apenas na conferência.
  - Consultar ocorrências — **CE**; “consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas”.
  - Consultar ficha da remessa — **CE**; “A consulta da remessa deve reunir seus dados e os registros [...] imprimir essa ficha em PDF”.
  - Quadro por zona — **SE**; “quantidades [...] além do saldo que ainda está fora do depósito”. Exige agregação e cálculo.
- Aceitas como hipótese:
  - Grupo **C — registro da conferência**, exatamente uma alternativa:
    - **C-na-chegada:** conferência concluída ao registrar o retorno; não há transação adicional.
    - **C-posterior:** confirmar e registrar a conferência após a chegada — **EE** adicional, mantendo o retorno/remessa.
    - Âncora: “A devolução só deve ser considerada concluída depois da conferência do material”, sem dizer se chegada e conferência geram registros em momentos diferentes.
  - **Agrupamento dos dados internos:** o modelo de referência mais agregado tem um ALI Remessas com itens, movimentações e ocorrências. A consulta reunida não prova, porém, que todos tenham o mesmo ciclo de vida.
    - **G-movimentações:** um ALI Movimentações separado, **+7 PF**, se saída, entrega e retorno forem interpretados como registros de negócio mantidos e conservados com autonomia, não simples histórico da remessa. Âncora: os registros próprios de saída, entrega e devolução.
    - **G-ocorrências:** um ALI Ocorrências separado, **+7 PF**, se a ocorrência for interpretada como objeto acompanhado pela seção com autonomia em relação à remessa. Âncora: registro de ocorrências de transporte e consulta própria pela seção.
    - Cada dimensão é uma escolha excludente entre subgrupo e arquivo separado; as duas separações podem coexistir. São hipóteses de agrupamento, não evidência de três arquivos. Se a leitura for de simples histórico, ele fica no ALI principal.
    - As EE já obrigatórias mantêm os arquivos correspondentes quando separados; não surgem novas EE só por mudar o agrupamento.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI local de urnas e manutenção do cadastro nacional — o mantenedor externo está indicado.
  - Cadastro de responsáveis ou AIE de pessoal — solução da identificação ainda não descrita.
  - Analisar, aprovar ou concluir ocorrência — o aviso à seção não especifica tratamento.
  - Função autônoma de aviso só porque há comunicação à seção — “Ao registrar” descreve consequência do registro.
  - CE adicional de PDF — “imprimir essa ficha” é outra mídia da consulta, sem outro conteúdo ou lógica implicados.
  - Uma EE por retorno parcial ou por urna; arquivos por tabela física ou por status — repetição, detalhe ou implementação não criam funções.
  - Separar ALI sem hipótese de autonomia, ou somar simultaneamente o arquivo e um segundo arquivo que apenas duplica o mesmo grupo lógico.
  - Gestão local de usuários, software de urna, carga de software, votação e apuração — exclusões expressas.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo, agrupamento agregado + C-na-chegada: **1 ALI × 7 + 1 AIE × 5 + 7 EE × 4 + 2 CE × 4 + 1 SE × 5 = 53 PF**.
- Conferência posterior, sem separar arquivos: **1 ALI × 7 + 1 AIE × 5 + 8 EE × 4 + 2 CE × 4 + 1 SE × 5 = 57 PF**.
- Uma separação de arquivo acrescenta **7 PF**; duas acrescentam **14 PF**. Máximo de referência, dois arquivos separados + C-posterior: **3 ALI × 7 + 1 AIE × 5 + 8 EE × 4 + 2 CE × 4 + 1 SE × 5 = 71 PF**.
- No modelo agregado, as sete ou oito EE mantêm Remessas. No separado, registrar/corrigir/cancelar mantém Remessas; saída/entrega/retorno e eventual conferência mantêm Movimentações; registro de ocorrência mantém Ocorrências. AIE Urnas é lido na validação. As consultas e o quadro leem os grupos necessários.
- Esses extremos não incluem identificação ou tratamento de ocorrências ainda não descritos. Não são limite superior de uma solução futura.

**Cobertura:** **parcial**. A conferência e os agrupamentos têm alternativas contabilizadas, mas a fonte da identificação pessoal e o possível tratamento das ocorrências ainda podem introduzir funções sem base suficiente para contá-las.

**Pendências obrigatórias (reprovam se ausentes):**
- **Regra geral:** como são identificados os responsáveis por entregar e receber e de onde vêm os dados deles? Não basta perguntar pelo login do operador.
- **Regra geral:** há análise ou decisão sobre as ocorrências comunicadas à Seção de Logística e quem a realiza?
- **Etapa E3 — conferência do retorno:** o registro de chegada já inclui a conferência ou o material é recebido primeiro e a conferência precisa ser registrada depois? O que marca a devolução como conferida?
  - **Âncora textual:** “No retorno [...] serão registradas a data e as urnas que chegaram” e “A devolução só deve ser considerada concluída depois da conferência do material”.
  - **Duas respostas plausíveis e consequências:**
    - “Quem recebe confere na hora e só registra o retorno depois de conferir.” A EE de retorno já cobre o resultado da conferência; **nenhuma função adicional**.
    - “Anotamos a chegada assim que o material entra, mas outra pessoa confere mais tarde e registra que terminou.” Acrescenta **uma EE de confirmação/registro da conferência, 4 PF**. O número de ALI não muda apenas por isso.
  - **Por que é necessário delimitar este pedido:** a conclusão da devolução foi condicionada à conferência, enquanto o registro de chegada também foi solicitado. É preciso saber se são uma ou duas atividades completas da aplicação para atender ao controle pedido, especialmente com retornos parciais; não se está propondo uma nova fase do transporte.
  - Não perguntar apenas “há conferência?”: sua existência já está afirmada. É necessário distinguir o registro da chegada do registro do resultado da conferência.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autonomia de movimentações e ocorrências: são partes da ficha da remessa ou registros com acompanhamento e conservação próprios? A incerteza deve aparecer nas hipóteses se alterar o agrupamento, mas esta pergunta não é usada como pendência reprovadora de etapa.
- Eventuais anexos, cobrança de atrasos e correção de movimentações já registradas.
- Preparação física anterior e planejamento detalhado de rotas pertencem ao domínio, mas não são etapas exigidas deste pedido.
- Não inventar dúvidas sobre votação ou software de urna para avaliar a parte administrativa.

**Pendências ou perguntas proibidas (contrastes):**
- Mesmo no holdout: quem mantém o cadastro de urnas; se haverá devolução parcial, conferência, ocorrências, consulta pela seção, PDF ou quadro quantitativo.
- Perguntar se existe conferência não substitui E3 e reabre informação respondida.
- Quais operações “organizar” abrange, de forma genérica, ignorando as operações descritas.
- Se haverá gestão local de usuários ou se o pedido inclui software de urna, votação ou apuração.
- A fonte dos responsáveis, a existência de análise e a forma de registrar a conferência ficam respondidas em H3c; a autonomia dos arquivos não.

**Notas para o juiz:** E3 mede descoberta da relação entre duas etapas, além das regras gerais. A conferência física existe, mas isso não prova uma EE autônoma; a hipótese deve depender de quando e como seu resultado é registrado. Aceitar agrupamentos fundamentados, sem impor um “dossiê” único nem premiar ALI por tabela. Os modelos de um a três ALI são referências de interpretações, não licença para qualquer separação: exigir explicação de autonomia, ligação ao texto e mantenedora. Se a leitura for de histórico de estados, aplicar sua inclusão no arquivo principal. Total menor com agrupamento coerente não é subcontagem automática.

## H3c · Conferência posterior e tratamento definidos (contraste de H3, rico, rubrica)

Argumentos: `tipo=desenvolvimento`

> Precisamos de um sistema para organizar as remessas de urnas do depósito às zonas eleitorais e a volta desse material. A Seção de Logística vai registrar cada remessa com a data prevista, a zona de destino e as urnas que seguirão nela. Os números de série devem ser conferidos com a relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro.
>
> Antes da saída, a equipe pode corrigir a data ou a relação de urnas e cancelar uma remessa que não será mais realizada. Precisamos registrar a saída efetiva, com a data e as urnas que saíram, e depois a entrega à zona, com a data e as urnas recebidas. No retorno ao depósito, serão registradas a data e as urnas que chegaram. A devolução só deve ser considerada concluída depois da conferência do material; uma mesma remessa às vezes volta em partes, em dias diferentes. A chegada é anotada assim que as urnas entram no depósito; outro servidor confere o material mais tarde e registra que aquele retorno foi conferido. Em cada saída, entrega e devolução precisamos identificar os responsáveis por entregar e receber. Esses responsáveis são servidores do Tribunal: usaremos a matrícula e o nome que vêm do cadastro de servidores do sistema de pessoal.
>
> Também queremos registrar ocorrências de transporte, como avarias no trajeto e divergências na devolução, com descrição, remessa e urnas envolvidas. Ao registrar uma ocorrência, a Seção de Logística deve ser avisada. A seção precisa consultar uma lista das ocorrências recebidas, com a descrição e as urnas envolvidas. A equipe da seção analisa cada ocorrência e registra sua conclusão para dar o caso por encerrado.
>
> A consulta da remessa deve reunir seus dados e os registros de saída, entrega, devolução e ocorrência. A equipe também precisa imprimir essa ficha em PDF. Para organizar o trabalho, queremos um quadro por zona com as quantidades de urnas que saíram, foram entregues e retornaram, além do saldo que ainda está fora do depósito.
>
> O acesso será pela autenticação institucional que já usamos. Não estamos pedindo cadastro de usuários ou gestão de perfis. O pedido trata apenas das rotinas administrativas de transporte, não de software da urna, carga de software, votação ou apuração.

**Informação ausente:** nenhuma das três lacunas obrigatórias de H3 permanece. A autonomia lógica de movimentações e ocorrências continua não totalmente explicitada; o contraste não a resolveu por precisão artificial.

**Regras gerais acionadas:**
- Identificação respondida por matrícula/nome do cadastro de servidores do sistema de pessoal.
- Análise e responsável respondidos pela equipe da seção, que registra a conclusão.
- Origem das urnas continua respondida; as operações continuam detalhando “organizar”.
- E3 é respondida pela anotação da chegada seguida de conferência posterior por outro servidor, com resultado registrado.

**O que o texto já responde:** tudo o que H3 respondia, mais identificação funcional dos responsáveis, fonte de pessoal, tratamento das ocorrências e autonomia temporal e funcional do registro da conferência.

**Funções:**
- Obrigatórias (evidência):
  - Remessas — **ALI**; “vai registrar cada remessa com a data prevista, a zona de destino e as urnas”.
  - Urnas — **AIE**; “relação de urnas do sistema nacional de logística, que continua responsável por esse cadastro”.
  - Servidores — **AIE**; “matrícula e o nome que vêm do cadastro de servidores do sistema de pessoal”. Leitura para identificar responsáveis nas movimentações.
  - Registrar remessa — **EE**; “vai registrar cada remessa”.
  - Corrigir remessa — **EE**; “pode corrigir a data ou a relação de urnas”.
  - Cancelar remessa — **EE**; “cancelar uma remessa que não será mais realizada”.
  - Registrar saída — **EE**; “registrar a saída efetiva”.
  - Registrar entrega — **EE**; “depois a entrega à zona”.
  - Registrar retorno — **EE**; “No retorno [...] serão registradas a data e as urnas que chegaram” e “A chegada é anotada assim que as urnas entram”.
  - Registrar conferência do retorno — **EE**; “outro servidor confere o material mais tarde e registra que aquele retorno foi conferido”. É atividade completa posterior, não outra tela suposta.
  - Registrar ocorrência — **EE**; “Também queremos registrar ocorrências de transporte”.
  - Registrar conclusão da ocorrência — **EE**; “A equipe da seção analisa cada ocorrência e registra sua conclusão para dar o caso por encerrado”.
  - Consultar ocorrências — **CE**; “consultar uma lista das ocorrências recebidas”.
  - Consultar ficha da remessa — **CE**; “A consulta da remessa deve reunir seus dados e os registros [...] imprimir essa ficha em PDF”.
  - Quadro por zona — **SE**; “quantidades [...] além do saldo que ainda está fora do depósito”.
- Aceitas como hipótese:
  - Permanecem as escolhas **G-movimentações** e **G-ocorrências** de H3: subgrupos de Remessas ou arquivos separados, **+7 PF** por separação fundamentada em autonomia lógica.
  - Conferência mantém o grupo onde estiver o retorno; conclusão mantém o grupo onde estiver a ocorrência. Não acrescentar EE apenas por separar esses grupos.
  - A hipótese C-posterior deixa de ser hipótese: o registro posterior da conferência agora é evidência. Não conservar C-na-chegada nos cenários.
- Proibidas (como função ou hipótese com PF), com o motivo:
  - ALI de servidores ou cadastro local para resolver a identificação — a fonte informada é o cadastro do sistema de pessoal; nenhuma manutenção local foi pedida.
  - CE autônoma de servidores apenas por preencher responsáveis — leitura absorvida pelas EE que usam a identidade.
  - EE extra de análise humana ou outra de encerramento além da conclusão — “registra sua conclusão para dar o caso por encerrado” descreve uma atividade de negócio, não três transações.
  - SE autônoma de aviso à seção, CE extra de PDF, EE por retorno parcial, arquivo por status — mesmos motivos de H3.
  - ALI de urnas, gestão local de usuários e funções de votação/apuração — fonte externa ou exclusão expressa.
  - Arquivos adicionais apresentados como certeza só porque foram citados registros diferentes — agrupamento ainda exige hipótese fundamentada.

**Cenários (referência de cálculo, não exigência numérica):**
- Mínimo, modelo agregado: **1 ALI × 7 + 2 AIE × 5 + 9 EE × 4 + 2 CE × 4 + 1 SE × 5 = 66 PF**.
- Uma separação de arquivo: **73 PF**; duas separações: **3 ALI × 7 + 2 AIE × 5 + 9 EE × 4 + 2 CE × 4 + 1 SE × 5 = 80 PF**.
- As nove EE são remessa, correção, cancelamento, saída, entrega, retorno, conferência, ocorrência e conclusão. Em relação ao mínimo identificável de H3, há **+5 PF** de Servidores, **+4 PF** de conferência posterior e **+4 PF** de conclusão.
- No modelo separado, Remessas é mantido por registro/correção/cancelamento; Movimentações por saída/entrega/retorno/conferência; Ocorrências por registro/conclusão. Nos modelos agregados, as mesmas EE mantêm os respectivos subgrupos. Urnas e Servidores são lidos nas validações e identificações solicitadas.
- Trata-se de desenvolvimento: não contar novamente saída, entrega e retorno só porque agora a fonte de identificação foi esclarecida.

**Cobertura:** **completa para o escopo administrativo expresso, com incerteza de agrupamento contabilizada**. Aceitar cobertura parcial se acompanhada de justificativa específica sobre autonomia dos registros ainda não resolvida; não alegar ausência de identificação, conferência ou tratamento.

**Pendências obrigatórias (reprovam se ausentes):** nenhuma das três de H3 permanece. As respostas sobre fonte dos responsáveis, tratamento e registro posterior da conferência estão no pedido.

**Pendências de diagnóstico (relatadas, não reprovam):**
- Autonomia e conservação de movimentações e ocorrências, para confirmar as alternativas de agrupamento ainda abertas.
- Anexos, cobrança de atraso e correção posterior de movimentações, sem PF por mera plausibilidade.
- Detalhes técnicos das consultas externas não reabrem origem ou existência das fontes.

**Pendências ou perguntas proibidas (contrastes):**
- Como identificar os responsáveis ou de onde vêm matrícula e nome.
- Se há análise das ocorrências, quem a faz ou se a conclusão é registrada.
- Se chegada e conferência são anotadas juntas ou se há registro posterior da conferência: o texto responde que são etapas registradas em momentos distintos.
- Se haverá conferência, devolução parcial, PDF, quadro quantitativo ou gestão local de usuários.
- Quem mantém o cadastro de urnas; se o pedido abrange votação, apuração ou software da urna.
- A pergunta sobre autonomia dos arquivos continua permitida, pois não foi respondida no contraste.

**Notas para o juiz:** contraste mais informativo, com o nível “rico” do par. As inserções respondem somente às lacunas obrigatórias de H3; não fixam o agrupamento dos arquivos. A conferência passa a EE de evidência pela separação entre chegada registrada e resultado posterior registrado, não por ser feita por outro perfil. A conclusão é EE, não SE só por conter um resultado. A origem pessoal é funcional e não deve ser confundida com autenticação. Perguntas proibidas reprovam mesmo em listas secundárias; dúvidas residuais de agrupamento não reprovam.

## Pontos de dúvida para aprovação humana

- **E2 — retorno da entrega:** confirmar que “relação das convocações com problema de entrega” é âncora suficientemente forte para tornar obrigatório esclarecer erros imediatos versus resultados posteriores. As respostas alteram a existência de uma EE, mas a primeira restringe o significado de “problema de entrega”.
- **E3 — chegada e conferência:** confirmar que a distinção entre registrar retorno já conferido e registrar conferência depois é uma lacuna de etapa inequívoca, sem exigir que todo pedido detalhe o momento de cada operação.
- **Agrupamento de H3/H3c:** o texto permite uma ficha reunindo registros sem resolver completamente sua autonomia. Os cenários aceitam um a três ALI, mas cada separação exige hipótese sustentada em objetos de negócio, não tabelas. Confirmar se ambos os desmembramentos são suficientemente fundamentados ou se um deve ficar apenas como diagnóstico sem PF.
- **Consulta da equipe em H1:** mantidos máximos de 23 ou 27 PF, conforme a fundamentação da distinção funcional já aceita na revisão.
- **Cobertura:** H2 admite completa ou parcial fundamentada; H3c também admite justificativa específica de parcialidade pelos agrupamentos, mas não por lacunas já respondidas. Confirmar a preferência de registro do avaliador.
