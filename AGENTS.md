# AGENTS.md

Convenções permanentes deste repositório, para pessoas e agentes. O estado de trabalho de cada skill (o que está autorizado, rodadas, hashes, como retomar) fica no `HANDOFF.md` dela, não aqui.

## O que é

Marketplace e plugin `trese-apf-skills`: skills de agente para Análise de Pontos de Função em projetos do TRE/SE. Uso interno. Documentos, código comentado e mensagens das skills em português.

## Estrutura

```
marketplace.json                    marketplace de plugins do VS Code
skills.sh.json                      caminho das skills para o utilitário `skills`
trese-apf-skills/
├── plugin.json                     manifesto do plugin (agent-plugins.org)
├── CHANGELOG.md
├── README.md                       o plugin e a lista de skills
├── skills/<skill>/                 a skill como é instalada: SKILL.md, README.md (uso), references/, scripts/
└── dev/<skill>/                    desenvolvimento: PLANO.md, HANDOFF.md, RELATORIO-*.md, evals/
```

- O nome da pasta é o nome da skill (`name` no `SKILL.md`) e é o mesmo em `skills/` e `dev/`.
- Só o que a skill precisa em uso vai para `skills/<skill>/`. Plano, relatórios, testes e evals vão para `dev/<skill>/`.
- O `README.md` dentro de `skills/<skill>/` é copiado sozinho com a skill na instalação: referências a arquivos fora da pasta da skill usam a URL do repositório (<https://github.com/diegovilar/trese-apf-skills>), não link relativo. Ele descreve só o uso; instalação fica no `README.md` da raiz.

## Skill nova

1. Crie `trese-apf-skills/skills/<skill>/` e `trese-apf-skills/dev/<skill>/` com o mesmo nome.
2. Acrescente a skill às tabelas do `README.md` da raiz e do `trese-apf-skills/README.md`, e registre-a no `CHANGELOG.md`.
3. Confira a descoberta com `npx skills add . --list` (não instala).

## Versão

A versão do plugin é a mesma em `trese-apf-skills/plugin.json`, no `marketplace.json` (entrada do plugin) e no topo do `CHANGELOG.md`. Mudou uma, mude as três.

## Desenvolvimento de uma skill

- Comece pelo `trese-apf-skills/dev/<skill>/HANDOFF.md`: regras de operação (cota, autorização, segunda opinião) e retomada são específicas de cada skill e valem acima deste arquivo.
- Comandos de desenvolvimento rodam a partir de `trese-apf-skills/dev/<skill>/` (por exemplo, `python3 -m unittest discover -s evals/unit`).
- Não reescreva resultados brutos de evals (`evals/agente/resultados/`, fora do git): são registro, mesmo quando citam nomes ou caminhos antigos.
- Documentos históricos (planos, relatórios, handoffs encerrados) não são reescritos para acompanhar mudanças de estrutura: acrescente uma nota e registre a mudança como decisão no `PLANO.md`.
- Na `trese-apf-aproximacao`, mudar a skill (qualquer arquivo em `skills/<skill>/`, inclusive o README) ou os arquivos de execução e juiz dos evals muda o `config_hash`: rodadas preparadas antes não continuam.
