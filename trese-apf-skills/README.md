# Plugin `trese-apf-skills`

Skills de agente para Análise de Pontos de Função (APF) em projetos do TRE/SE. Uso interno, sem distribuição.

As estimativas produzidas pelas skills são insumo de análise, sempre revisado por um analista. Nenhuma delas serve para contratação ou medição.

## Skills

| Skill | Para quê | Estado |
|---|---|---|
| [`trese-apf-aproximacao`](skills/trese-apf-aproximacao/README.md) | estimativa preliminar de tamanho funcional (contagem estimada ou indicativa da NESMA) de pedidos de desenvolvimento ou melhoria, para a análise de viabilidade | experimental |

O README de cada skill descreve como usá-la, como ler o resultado e o que revisar antes de usar o número.

## Instalação

Pelo marketplace do VS Code, pelo utilitário `skills` ou por cópia manual: veja o [README do repositório](../README.md).

## Versão

`0.1.0`. A versão do plugin está em `plugin.json` e no `marketplace.json` da raiz; mudanças em [`CHANGELOG.md`](CHANGELOG.md).

## Conteúdo

| Caminho | O que é |
|---|---|
| `plugin.json` | manifesto do plugin ([agent-plugins.org](https://agent-plugins.org)) |
| `skills/<skill>/` | a skill distribuída: `SKILL.md`, `README.md` (uso), `references/` e `scripts/` |
| `dev/<skill>/` | desenvolvimento da skill: plano, handoff, relatórios e `evals/`; não é carregado pelo agente |
| `CHANGELOG.md` | mudanças por versão |
