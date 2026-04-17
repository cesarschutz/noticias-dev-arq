# DevPulse — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages.

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (template HTML único):

```
index.html → fetch('data/editions.json')  (índice com counts)
           → fetch('data/{ISO}.json')     (edição por data, sob demanda)
```

O `index.html` é uma SPA single-file (CSS + JS vanilla embutidos) no estilo **"console ops"** — terminal moderno com paleta marine/cyan/violet/amber. Três colunas: sidebar (categorias + ferramentas), main (feed), rail (telemetria). Sem frameworks, sem build step.

## Estrutura de Arquivos

```
├── index.html                      # SPA single-file
├── assets/
│   └── devpulse-logo.svg           # Logo (usado no boot e topbar)
├── data/
│   ├── editions.json               # Índice mestre + counts por categoria/ferramenta
│   └── {YYYY-MM-DD}.json           # Dados completos de cada dia
├── scripts/
│   ├── validate_editions.py        # Valida schema + URLs + duplicatas
│   └── generate_feed.py            # Gera feed.xml (RSS 2.0) a partir do índice
├── skills/
│   └── devpulse-daily.md           # Skill Cowork para geração diária
├── .github/workflows/
│   ├── pages.yml                   # Deploy no GitHub Pages (gera RSS antes)
│   └── validate.yml                # Validação JSON em PRs
├── CLAUDE.md                       # Este arquivo
├── README.md
├── .gitignore                      # feed.xml é gerado pelo CI, não commitado
├── .nojekyll                       # Desativa Jekyll no GitHub Pages
└── push.sh                         # Script de push (chamado por LaunchAgent local)
```

## Fluxo de Dados

1. **Cowork** roda `skills/devpulse-daily.md` diariamente às 6h BRT
2. Pesquisa notícias via WebSearch em 10 categorias + 11 ferramentas + HN + blogs eng + pulso BR
3. Monta `data/{date}.json` com sanity checks (URLs específicas, dedup com últimas 7 edições, diversidade top3)
4. Atualiza `data/editions.json` com a nova entrada (incluindo `counts_by_category` e `counts_by_tool`)
5. LaunchAgent local detecta mudança em `data/` e roda `push.sh` (retry + log rotativo em `~/Library/Logs/devpulse-push.log`)
6. GitHub Actions (`pages.yml`) gera `feed.xml` → deploya no GitHub Pages
7. GitHub Actions (`validate.yml`) valida JSON em PRs

## Views da SPA

- **home** (default): edição do dia mais recente — hero, top3, feed, ferramentas
- **cat:{chave}**: agregado de todas as notícias de uma categoria através das edições
- **tool:{chave}**: agregado de menções + releases oficiais de uma ferramenta
- **deep link**: `?d=YYYY-MM-DD&u=<hash>` abre direto uma notícia

### Lazy-load inteligente
Ao filtrar por categoria/ferramenta, a SPA usa `counts_by_category` / `counts_by_tool` do `editions.json` para **só baixar** as edições que têm conteúdo daquele filtro. Um loader visual fica no topo do main durante o fetch paralelo. Em background (após boot), todas as edições são pré-aquecidas em cache para busca global.

## Interações

- **Busca global**: `/` ou `Ctrl/Cmd+K` abre modal com input. Indexa headlines + summary + source + tags + CVEs de todas edições carregadas. Resultados com highlight de termos e navegação por setas.
- **Deep link**: abrir uma notícia atualiza a URL com `?d=date&u=hash`. Botão "compartilhar" copia o link. Ao acessar via esse URL, a SPA já abre o modal da notícia.
- **Prev/Next edições**: botões `<` `>` no topbar (ou atalhos `P`/`N`) navegam entre edições adjacentes.
- **Filtro**: toolbar tem chip `urgent` (atalho `U`).
- **Ler depois**: bookmark via `localStorage` (`dpco-read-later`). Modal com ordenação (saved/date/category/urgent), export JSON e clear.
- **Tema dark/light**: toggle na topbar ou atalho `T`.
- **Modo cards/list**: atalhos `1` e `2`.
- **Teclado**: `J/K` navegam cards, `O` ou `Enter` abre, `H` volta pra home do dia atual, `ESC` fecha tudo.
- **Mobile**: sidebar vira hamburger abaixo de 720px.

## Campos estruturados por notícia

Além dos campos básicos, a skill gera (todos opcionais):
- **`cves: []`** — CVEs citados, renderizados como pills clicáveis para NVD no modal.
- **`severity: "critical|high|medium|low"`** — para itens de segurança, granularidade maior que o booleano `urgent`.
- **`published_at`** — ISO 8601 do artigo original (vs. data da edição).
- **`tags: []`** — 2-6 entidades/tecnologias, mostradas como pills nos cards.

## JSON Schemas

### `data/editions.json`
```json
{
  "last_generated": "2026-04-17T06:00:00-03:00",
  "editions": [
    {
      "date": "YYYY-MM-DD",
      "summary": "1-2 frases",
      "counts_by_category": { "sec": 3, "ai": 4, "cloud": 2 },
      "counts_by_tool": { "cursor": 1, "docker": 1 },
      "highlights": [{ "title": "...", "url": "..." }]
    }
  ]
}
```

### `data/{YYYY-MM-DD}.json`
Raiz: `date`, `weekday`, `formatted_date`, `generated_at` (ISO 8601), `hero_title`, `hero_description`, `top3[]`, `news[]`, `tools[]`, `sources[]`.

Item de `top3[]`/`news[]`: obrigatórios `category`, `category_label`, `category_icon`, `headline`, `summary`, `source`, `url`, `read_time`. Opcionais: `urgent`, `new`, `star`, `breaking`, `severity`, `cves[]`, `tags[]`, `published_at`. Só em `top3[]`: `image`.

Item de `tools[]`: `name`, `icon`, `version`, `description`, `url`.

Schema completo em `skills/devpulse-daily.md`. Validação em `scripts/validate_editions.py` (edições ≥ `2026-04-18` são strict; anteriores são lenient para preservar histórico).

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

Microsoft Teams (doc), Notion (doc), IntelliJ IDEA (ide), Cursor IDE (ide), Warp Terminal (ide), MongoDB Compass (db), DBeaver (db), Postman (api), Docker Desktop (devops), Structurizr (arch), C4 Model (arch).

Cada ferramenta tem `kind` que define a cor do border-left no sidebar — IDEs violet, DBs cyan, DevOps amber, APIs green, docs pink, arquitetura teal.

A SPA tenta casar menções em `headline + summary` com os `aliases` do objeto `TOOLS` em `index.html`. Releases oficiais vêm do array `tools[]` do JSON diário.

## O Que Atualizar Quando

### Alterar o design visual
- Edite `index.html` (CSS + HTML no mesmo arquivo)
- Dados JSON não precisam mudar
- Se adicionar/renomear classes CSS de categoria, atualize o mapa `CAT` no JS

### Adicionar/remover uma categoria
1. Adicione a chave em `CAT` no JS de `index.html`
2. Adicione variável `--cat-{chave}` em `:root` e `[data-theme="light"]`
3. Atualize a tabela em `skills/devpulse-daily.md`, neste CLAUDE.md e em `scripts/validate_editions.py` (set `CATEGORIES`)

### Adicionar/remover uma ferramenta monitorada
1. Adicione entrada no array `TOOLS` do JS em `index.html` (com `aliases` e `kind`)
2. Atualize a tabela em `skills/devpulse-daily.md` (changelog URL)
3. Atualize a lista de chaves em `skills/devpulse-daily.md` (counts_by_tool)

### Alterar queries de pesquisa
- Edite em `skills/devpulse-daily.md` na seção "Categorias e Queries"

### Testar localmente
```bash
python3 -m http.server 8000
open http://localhost:8000
# Validação do JSON:
python3 scripts/validate_editions.py
# Gerar feed:
python3 scripts/generate_feed.py
```

## Convenções

- Datas ISO 8601 (`YYYY-MM-DD`) em arquivos e campos `date`/`weekday`
- `generated_at` e `last_generated` em ISO 8601 completo com timezone (`YYYY-MM-DDTHH:MM:SS-03:00`)
- Conteúdo de texto em português brasileiro
- Caminhos relativos (funciona no GitHub Pages com subpath)
- JSON com indentação de 2 espaços, emojis em UTF-8 literal (não escapados)
- `localStorage` usa prefixo `dpco-` (DevPulse Console Ops)

## Deploy

Push para `main` → GitHub Actions (`pages.yml`) gera `feed.xml` e deploya.
URL: `https://cesarschutz.github.io/noticias-dev-arq/`
RSS: `https://cesarschutz.github.io/noticias-dev-arq/feed.xml`

Workflow com `paths` filter: mudanças só em `.md` não disparam redeploy.
