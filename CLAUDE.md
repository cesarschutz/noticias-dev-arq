# DevPulse — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages.

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (templates HTML):

```
index.html       → fetch('data/editions.json')  → renderiza arquivo com calendário
dia.html?d=ISO   → fetch('data/{ISO}.json')      → renderiza edição completa do dia
```

Templates são HTML estáticos com CSS embutido (design Apple/glassmorphism) e JS vanilla que carrega JSON via `fetch()`. Sem frameworks, sem build step.

## Estrutura de Arquivos

```
├── index.html                 # Template: página arquivo (calendário + edições)
├── dia.html                   # Template: edição diária (notícias + filtros)
├── data/
│   ├── editions.json          # Índice mestre de todas as edições
│   └── {YYYY-MM-DD}.json     # Dados completos de cada dia
├── skills/
│   └── devpulse-daily.md     # Skill Cowork para geração diária
├── CLAUDE.md                  # Este arquivo
├── README.md
├── .nojekyll
└── .github/workflows/pages.yml
```

## Fluxo de Dados

1. **Cowork** roda `skills/devpulse-daily.md` diariamente às 6h BRT
2. Pesquisa notícias via WebSearch em 10 categorias + 11 ferramentas
3. Gera `data/{date}.json` e atualiza `data/editions.json`
4. Commit + push → GitHub Actions deploya no Pages

## JSON Schemas

### `data/editions.json`
```json
{
  "last_generated": "ISO 8601 com timezone",
  "editions": [{ "date": "YYYY-MM-DD", "summary": "...", "highlights": [{ "title": "...", "url": "..." }] }]
}
```

### `data/{YYYY-MM-DD}.json`
Campos principais: `date`, `weekday`, `formatted_date`, `generated_at`, `hero_title`, `hero_description`, `stats`, `top3[]`, `news[]`, `tools[]`, `sources[]`

Cada item de notícia: `category`, `category_label`, `category_icon`, `urgent`, `new`, `star`, `breaking`, `headline`, `summary`, `source`, `url`, `read_time`

Schema completo em `skills/devpulse-daily.md`.

## Categorias

| Chave | CSS Class | Label | Ícone |
|-------|-----------|-------|-------|
| sec | c-sec | Segurança | 🔐 |
| ai | c-ai | IA & LLMs | 🤖 |
| cloud | c-cloud | Cloud | ☁️ |
| devops | c-devops | DevOps | ⚙️ |
| backend | c-backend | Backend | 🔧 |
| frontend | c-frontend | Frontend | 🖥️ |
| db | c-db | Bancos | 🗄️ |
| lang | c-lang | Linguagens | 🛠️ |
| arqsw | c-arqsw | Arq. Software | 🏛️ |
| arqsol | c-arqsol | Arq. Solução | 🗺️ |

## O Que Atualizar Quando

### Alterar o design visual
- Edite `index.html` e `dia.html` (CSS e estrutura HTML)
- Dados JSON não precisam mudar
- Se adicionar/renomear classes CSS de categoria, atualize o mapa `CAT` no JS de `dia.html`

### Adicionar/remover uma categoria
1. Adicione a categoria no mapa `CAT` em `dia.html`
2. Adicione CSS para a nova classe (ex: `.c-novacat{--c1:...;--c2:...}`)
3. Atualize a tabela de categorias em `skills/devpulse-daily.md`
4. Atualize este CLAUDE.md

### Adicionar/remover uma ferramenta monitorada
- Edite a tabela de ferramentas em `skills/devpulse-daily.md`

### Alterar queries de pesquisa
- Edite as queries em `skills/devpulse-daily.md` na seção "Categorias e Queries"

## Convenções

- Datas em ISO 8601 (`YYYY-MM-DD`) nos nomes de arquivo e JSON
- Todo conteúdo de texto em português brasileiro
- Termos técnicos em inglês são aceitáveis
- Caminhos sempre relativos (funciona no GitHub Pages)
- JSON com indentação de 2 espaços
- Desenvolvimento local requer servidor HTTP (`python3 -m http.server`)

## Deploy

Push para `main` → GitHub Actions (`pages.yml`) → GitHub Pages automático.
URL: `https://cesarschutz.github.io/noticias-dev-arq/`
