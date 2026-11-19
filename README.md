# trese-apf-skills

Skills de agente para Análise de Pontos de Função (APF) em projetos de TI do TRE/SE, empacotadas como o plugin [`trese-apf-skills`](trese-apf-skills/README.md). Uso interno, sem distribuição.

| Skill | Para quê | Estado |
|---|---|---|
| [`trese-apf-aproximacao`](trese-apf-skills/skills/trese-apf-aproximacao/README.md) | estimativa preliminar de tamanho funcional (contagem estimada ou indicativa da NESMA) de pedidos de desenvolvimento ou melhoria, para a análise de viabilidade | experimental |

Como usar cada skill, ler o resultado e revisá-lo: README da skill (link na tabela).

## Requisitos

- Um ambiente de agente que carregue skills: VS Code (chat com plugins de agente), Claude Code, OpenCode ou equivalente.
- **Python 3.8 ou superior** na máquina: os cálculos são feitos por script, nunca pelo modelo.
- Acesso a este repositório, <https://github.com/diegovilar/trese-apf-skills>.

## Instalação

Três caminhos; escolha um.

### VS Code, como marketplace de plugins

O repositório é um marketplace de plugins (`marketplace.json` na raiz) com um plugin, `trese-apf-skills`, que traz todas as skills.

1. Abra o editor de customizações do chat (comando **Chat: Open Customizations**), vá em **Browse**, abra o menu de fontes e escolha **Configure Marketplaces** → **Add Marketplace**. Informe `diegovilar/trese-apf-skills`.
2. Volte a **Browse**, escolha esse marketplace e instale o plugin `trese-apf-skills`.

Outra forma de adicionar o marketplace: abrir o link `vscode://chat-plugin/add-marketplace?ref=diegovilar%2Ftrese-apf-skills`. Os plugins de agente precisam estar habilitados (`chat.plugins.enabled`). Para atualizar, use **Chat: Update Plugins**. Detalhes: [Agent plugins in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins).

O `marketplace.json` serve ao VS Code; os outros ambientes usam um dos caminhos abaixo.

### Utilitário `skills`

O [`skills`](https://github.com/vercel-labs/skills) (Node.js 22.20 ou superior) instala skills de um repositório em vários agentes. Ele encontra as skills deste repositório pelo `skills.sh.json` da raiz.

```bash
# listar as skills disponíveis, sem instalar
npx skills add diegovilar/trese-apf-skills --list

# instalar todas, no projeto atual, escolhendo os agentes interativamente
npx skills add diegovilar/trese-apf-skills --skill '*'

# instalar uma skill, para o usuário (todos os projetos), num agente específico
npx skills add diegovilar/trese-apf-skills --skill trese-apf-aproximacao -g -a claude-code
```

Por padrão a instalação é no projeto atual; `-g` instala para o usuário. Para atualizar: `npx skills update`. Nomes dos agentes e diretórios de cada um: [documentação do `skills`](https://github.com/vercel-labs/skills/blob/HEAD/docs/commands.md).

### Cópia manual

Copie a pasta da skill, inteira, de `trese-apf-skills/skills/<skill>/` para o diretório de skills do seu ambiente. Exemplos:

| Ambiente | Projeto | Usuário |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |

Para outros ambientes, veja a documentação de cada um. Um link simbólico para a pasta, em vez da cópia, também serve quando o ambiente o reconhece. Não altere os arquivos da skill.

## Estrutura do repositório

| Caminho | O que é |
|---|---|
| `marketplace.json` | marketplace de plugins do VS Code |
| `skills.sh.json` | onde o utilitário `skills` procura as skills |
| `trese-apf-skills/` | o plugin: `plugin.json`, `CHANGELOG.md`, [`README.md`](trese-apf-skills/README.md) |
| `trese-apf-skills/skills/<skill>/` | cada skill, como é instalada |
| `trese-apf-skills/dev/<skill>/` | desenvolvimento de cada skill: plano, handoff, relatórios e evals |
| `AGENTS.md`, `CLAUDE.md` | convenções para quem (pessoa ou agente) trabalha no repositório |

## Desenvolvimento

Convenções do repositório: [`AGENTS.md`](AGENTS.md). Cada skill tem o seu diretório de desenvolvimento, com um `HANDOFF.md` que diz como retomar o trabalho. Para a `trese-apf-aproximacao`, os testes do script e do runner dos evals rodam assim:

```bash
cd trese-apf-skills/dev/trese-apf-aproximacao
python3 -m unittest discover -s evals/unit
```

As avaliações do agente (executam a skill com um modelo sobre casos de referência) estão descritas em `trese-apf-skills/dev/trese-apf-aproximacao/evals/README.md`.
