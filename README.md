# skill-apf — `nesma-apf-estimator`

Skill de agente que estima o tamanho funcional (Análise de Pontos de Função, contagem **estimada** ou **indicativa** da NESMA) de pedidos de desenvolvimento ou melhoria de sistemas, como insumo da análise de viabilidade da equipe interna de TI do TRE/SE. Uso interno, sem distribuição.

A estimativa é **preliminar**: não serve para contratação nem medição, e todo resultado precisa da revisão de um analista.

## Para usar

Leia o **[guia de uso](GUIA-DE-USO.md)**: instalação, como chamar, as perguntas da prévia, como ler o resultado e o que revisar antes de usar o número.

Em resumo: copie a pasta `nesma-apf-estimator/` para o diretório de skills do seu ambiente (Claude Code, OpenCode), tenha Python 3.8+ e chame a skill com o pedido. No Claude Code:

```
/nesma-apf-estimator Como servidor, quero gerenciar minhas solicitações de diárias.
```

Outros ambientes acionam skills de outro jeito; veja o guia.

## Estado

**Iteração 2 encerrada** (18/11/2026), sem aprovação integral. A skill está congelada no estado do commit `0c5a3b3`. O modo interativo (padrão) é experimental. Limitações conhecidas: hipóteses e perguntas a mais (contenção não demonstrada), alternativas que nem sempre viram cenário e lista de pendências não exaustiva. Ver [RELATORIO-iteracao-2.md](RELATORIO-iteracao-2.md).

## Conteúdo do repositório

| Caminho | O que é |
|---|---|
| `nesma-apf-estimator/` | a skill: `SKILL.md`, `references/` (regras e convenções de contagem) e `scripts/apf.py` (validação, cálculo e exportação em md, txt e xlsx; só biblioteca padrão) |
| `GUIA-DE-USO.md` | guia para o analista |
| `evals/` | testes unitários, gabaritos e o runner dos evals do agente ([evals/README.md](evals/README.md)) |
| `evals/T5-roteiro.md` | roteiro da checagem manual final do modo interativo |
| `RELATORIO-iteracao-1.md`, `RELATORIO-iteracao-2.md` | resultado de cada iteração |
| `PLANO.md` | todas as decisões (D1–D71), rodadas de avaliação e consultas |
| `HANDOFF.md`, `HANDOFF-iteracao-2.md` | como retomar o trabalho: regras de operação, comandos, armadilhas e próximo passo |

## Testes

```
python3 -m unittest discover -s evals/unit
```

154 testes do script (esquema, aritmética, fatores, cenários, renderização, xlsx, CLI). Os evals do agente (executor Claude Sonnet via Claude Code, juiz Codex) consomem cota e só rodam com autorização; ver `HANDOFF.md`.

## Fontes

Roteiro de Métricas de Software do SISP 3.0 (referência técnica subsidiária), NESMA *Early Function Point Analysis* e sua tradução, e NESMA *APF para Melhoria de Software* 2.2.1 (fatores EFPA). Detalhes em `RELATORIO-iteracao-1.md`.
