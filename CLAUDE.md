# DevPulse — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages.

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (template HTML único):

```
index.html → fetch('data/editions.json')  (índice)
           → fetch('data/{ISO}.json')     (edição por data, sob demanda)
```

O `index.html` é uma SPA single-file (CSS + JS vanilla embutidos) no estilo **"console ops"** — terminal moderno com paleta marine/cyan/violet/amber. Três colunas: sidebar (categorias + ferramentas), main (feed), rail (telemetria). Sem frameworks, sem build step.

## Estrutura de Arquivos

```
├── index.html                 # SPA: topbar, sidebar, main feed, rail, statusbar, modal reader
├── assets/
│   ├── devpulse-logo.svg      # Logo (usado no boot e topbar)
│   └── console-texture.svg    # Textura legada (não referenciada no CSS atual)
├── data/
│   ├── editions.json          # Índice mestre de todas as edições
│   └── {YYYY-MM-DD}.json      # Dados completos de cada dia
├── skills/
│   └── devpulse-daily.md      # Skill Cowork para geração diária
├── CLAUDE.md                  # Este arquivo
├── README.md
├── .nojekyll                  # Desativa Jekyll no GitHub Pages
├── push.sh                    # Script chamado pelo LaunchAgent local
└── .github/workflows/pages.yml
```

## Fluxo de Dados

1. **Cowork** roda `skills/devpulse-daily.md` diariamente às 6h BRT
2. Pesquisa notícias via WebSearch em 10 categorias + 11 ferramentas
3. Gera `data/{date}.json` e atualiza `data/editions.json`
4. Um LaunchAgent local detecta a mudança em `data/` e roda `push.sh`
5. GitHub Actions (`pages.yml`) deploya no GitHub Pages

## Views da SPA

A SPA tem 3 tipos de view:

- **home** (default): mostra a edição do dia mais recente — hero prompt, top3 destaques, feed do dia, ferramentas do dia
- **cat:{chave}**: agregado de todas as notícias de uma categoria através de todas as edições indexadas, agrupadas por data
- **tool:{chave}**: agregado de todas as menções a uma ferramenta (em news + tools), com releases oficiais em destaque

Ao clicar em uma categoria/ferramenta na sidebar, a SPA faz lazy-load de todas as edições via `fetch` paralelo e cache em memória.

## Interações

- **Ler depois**: marcador único do usuário (bookmark). Botão na topbar abre modal com lista salva. Persiste em `localStorage` (`dpco-read-later`).
- **Marcação de não lido**: dot visual (amber/cyan) no card. Some automaticamente ao abrir o modal reader da notícia. Persiste em `localStorage` (`dpco-read`).
- **Dia lido**: cada edição ganha marca de "visitada" ao ser aberta (`dpco-read-days`).
- **Tema**: dark (default) / light, toggle no topbar (`dpco-theme`).
- **Modos de feed**: cards / list (`dpco-mode`).
- **Atalhos**: `1`/`2` alternam modo, `B` abre ler depois, `Esc` fecha modal e datepicker.

## JSON Schemas

### `data/editions.json`
```json
{
  "last_generated": "ISO 8601 com timezone",
  "editions": [
    { "date": "YYYY-MM-DD", "summary": "...", "highlights": [{ "title": "...", "url": "..." }] }
  ]
}
```

### `data/{YYYY-MM-DD}.json`
Campos principais: `date`, `weekday`, `formatted_date`, `generated_at`, `hero_title`, `hero_description`, `top3[]`, `news[]`, `tools[]`, `sources[]` (opcional).

Cada item de `top3`/`news`: `category`, `category_label`, `category_icon`, `urgent`, `new`, `star`, `breaking`, `headline`, `summary`, `source`, `url`, `read_time`. Apenas em `top3` pode haver `image` (og:image para exibição no modal reader).

Cada item de `tools`: `name`, `icon`, `version`, `description`, `url`.

Schema completo em `skills/devpulse-daily.md`.

> **Nota**: o campo `stats` (total/categories/tools/urgent/new) é gerado pela skill por compatibilidade mas **não é consumido** pela SPA atual — a SPA calcula tudo dinamicamente. Pode ser omitido sem quebrar nada.

## Categorias

| Chave | CSS Var | Label | Ícone |
|-------|---------|-------|-------|
| sec | `--cat-sec` | Segurança | 🔐 |
| ai | `--cat-ai` | IA & LLMs | 🤖 |
| cloud | `--cat-cloud` | Cloud | ☁️ |
| devops | `--cat-devops` | DevOps | ⚙️ |
| backend | `--cat-backend` | Backend | 🔧 |
| frontend | `--cat-frontend` | Frontend | 🖥️ |
| db | `--cat-db` | Bancos | 🗄️ |
| lang | `--cat-lang` | Linguagens | 🛠️ |
| arqsw | `--cat-arqsw` | Arq. Software | 🏛️ |
| arqsol | `--cat-arqsol` | Arq. Solução | 🗺️ |

## Ferramentas monitoradas (11)

Microsoft Teams, Notion, IntelliJ IDEA, Cursor IDE, Warp Terminal, MongoDB Compass, DBeaver, Postman, Docker Desktop, Structurizr, C4 Model.

A SPA tenta casar menções em `headline + summary` com os `aliases` definidos no objeto `TOOLS` em `index.html`. Releases oficiais vêm do array `tools[]` do JSON diário.

## O Que Atualizar Quando

### Alterar o design visual
- Edite `index.html` (CSS + HTML no mesmo arquivo)
- Dados JSON não precisam mudar
- Se adicionar/renomear classes CSS de categoria, atualize o mapa `CAT` no JS

### Adicionar/remover uma categoria
1. Adicione a chave em `CAT` no JS de `index.html`
2. Adicione variável `--cat-{chave}` em `:root` e `[data-theme="light"]`
3. Atualize a tabela de categorias em `skills/devpulse-daily.md` e neste CLAUDE.md

### Adicionar/remover uma ferramenta monitorada
1. Adicione entrada no array `TOOLS` do JS em `index.html` (com `aliases` para matching)
2. Atualize a tabela de ferramentas em `skills/devpulse-daily.md`

### Alterar queries de pesquisa
- Edite as queries em `skills/devpulse-daily.md` na seção "Categorias e Queries"

## Convenções

- Datas em ISO 8601 (`YYYY-MM-DD`) nos nomes de arquivo e no JSON
- Todo conteúdo de texto em português brasileiro; termos técnicos em inglês são aceitáveis
- Caminhos sempre relativos (funciona no GitHub Pages com subpath)
- JSON com indentação de 2 espaços
- Desenvolvimento local requer servidor HTTP: `python3 -m http.server 8000`
- `localStorage` usa prefixo `dpco-` (DevPulse Console Ops)

## Deploy

Push para `main` → GitHub Actions (`pages.yml`) → GitHub Pages.
URL: `https://cesarschutz.github.io/noticias-dev-arq/`
