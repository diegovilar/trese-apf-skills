# skill-apf — `nesma-apf-estimator`

Skill de agente que estima o tamanho funcional (Análise de Pontos de Função, contagem **estimada** ou **indicativa** da NESMA) de pedidos de desenvolvimento ou melhoria de sistemas, como insumo da análise de viabilidade da equipe interna de TI do TRE/SE. Uso interno, sem distribuição.

A estimativa é **preliminar**: não serve para contratação nem medição, e todo resultado precisa da revisão de um analista.

## Para usar

Leia o **[guia de uso](GUIA-DE-USO.md)**: instalação, como chamar, as perguntas da prévia, como ler o resultado e o que revisar antes de usar o número.

Em resumo: copie a pasta `nesma-apf-estimator/` para o diretório de skills do seu ambiente (Claude Code, OpenCode), tenha Python 3.8+ e chame a skill com um pedido que descreva o processo: quem registra, quem decide, o que o sistema guarda ou lê de outro sistema e que consultas são esperadas. No Claude Code:

```
/nesma-apf-estimator A Seção de Gestão de Pessoas precisa de um sistema novo para os pedidos de teletrabalho. O servidor registra o pedido com o período e o plano de trabalho; nome, cargo e lotação vêm do sistema de RH. A chefia imediata aprova ou devolve o pedido, com justificativa. O servidor acompanha a situação dos seus pedidos, e a Seção consulta os pedidos aprovados por unidade e emite um relatório mensal em PDF.
```

Com argumentos, antes de `--`:

```
/nesma-apf-estimator tipo=melhoria melhoria=nesma saida=xlsx -- ./demandas/diarias-prestacao-de-contas.docx
/nesma-apf-estimator interativo=nao saida=md -- ./demandas/requisitos-sistema-de-eventos.md
```

O primeiro estima uma melhoria com os fatores de impacto da NESMA e exporta em planilha; o segundo calcula direto, sem a prévia e os lotes de perguntas, e salva em Markdown. Outros ambientes acionam skills de outro jeito; veja o guia.

## Estado

Em uso experimental. O modo interativo (padrão), com prévia e perguntas antes do cálculo, funcionou nos testes, mas o comportamento em diálogos longos ainda não foi avaliado. Nos testes, a skill às vezes contou hipóteses que o pedido não sustenta e fez perguntas que ampliam o pedido; uma lacuna perguntada nem sempre virou alternativa nos cenários; e a lista de pendências não é exaustiva. Por isso, todo resultado passa pela revisão descrita no guia.

## Conteúdo do repositório

| Caminho | O que é |
|---|---|
| `nesma-apf-estimator/` | a skill: `SKILL.md`, `references/` (regras e convenções de contagem) e `scripts/apf.py` (validação, cálculo e exportação em md, txt e xlsx; só biblioteca padrão) |
| `GUIA-DE-USO.md` | guia para o analista |
| `evals/` | testes do script e avaliações do agente com casos de referência ([evals/README.md](evals/README.md)) |
| `RELATORIO-*.md`, `PLANO.md`, `HANDOFF*.md` | histórico do desenvolvimento: decisões, resultados das avaliações e como retomar o trabalho |

## Testes

```
python3 -m unittest discover -s evals/unit
```

Testes do script: esquema, aritmética, fatores, cenários, renderização, planilha e linha de comando. As avaliações do agente executam a skill com um modelo sobre casos de referência; ver `evals/README.md`.

## Fontes

Roteiro de Métricas de Software do SISP 3.0 (referência técnica subsidiária), NESMA *Early Function Point Analysis* e sua tradução, e NESMA *APF para Melhoria de Software* 2.2.1 (fatores EFPA).
