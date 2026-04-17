# DevPulse — Arquivo Diário do Arquiteto

Curadoria diária de notícias técnicas para arquitetos de software e solução, gerada automaticamente por IA e publicada no GitHub Pages.

## Como funciona

Arquitetura **data-driven**: um template HTML único carrega dados de arquivos JSON via `fetch()`.

- **SPA** (`index.html`): console ops single-file — topbar + sidebar + main + rail + statusbar. Dark/light, cards/list, busca global, deep links.
- **Dados** (`data/*.json`): gerados diariamente pela skill `skills/devpulse-daily.md`
- **RSS** (`feed.xml`): gerado pelo CI antes do deploy
- **Deploy**: push para `main` → GitHub Actions → GitHub Pages

## Funcionalidades

- Filtrar por **categoria** ou **ferramenta** (agrega todas as edições, lazy-load inteligente)
- **Busca global**: `/` ou `Ctrl/Cmd+K` — indexa headlines, summary, fonte, tags e CVEs
- **Deep link**: `?d=YYYY-MM-DD&u=<hash>` abre uma notícia específica
- **Prev/Next**: botões ou `P`/`N` navegam entre edições
- **Ler depois**: salvar, ordenar, exportar JSON
- **Modal reader**: abre a matéria, CVEs clicáveis, tags, botão compartilhar
- **Teclado**: `J`/`K` navega, `O` abre, `T` tema, `1`/`2` modo, `U` filtro urgent
- **Calendário** no topbar com navegação por setas
- **RSS**: assine em `feed.xml`

## Categorias cobertas

Segurança · IA & LLMs · Cloud · DevOps · Backend & APIs · Frontend · Bancos de Dados · Linguagens & Tooling · Arquitetura de Software · Arquitetura de Solução.

## Ferramentas monitoradas

Microsoft Teams · Notion · IntelliJ IDEA · Cursor IDE · Warp Terminal · MongoDB Compass · DBeaver · Postman · Docker Desktop · Structurizr · C4 Model.

## Desenvolvimento local

```bash
# fetch() requer servidor HTTP, não file://
python3 -m http.server 8000
open http://localhost:8000

# Validar schemas dos JSONs
python3 scripts/validate_editions.py

# Gerar RSS localmente
python3 scripts/generate_feed.py
```

## Estrutura

```
index.html                   → SPA (template único)
assets/                      → Logo e texturas
data/editions.json           → Índice + counts por categoria/ferramenta
data/YYYY-MM-DD.json         → Dados de cada dia
skills/devpulse-daily.md     → Skill Cowork para geração diária
scripts/validate_editions.py → Validador de schema + URLs + duplicatas
scripts/generate_feed.py     → Gerador RSS 2.0
.github/workflows/           → CI (deploy + validação)
```

## Link

[cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/) · [RSS](https://cesarschutz.github.io/noticias-dev-arq/feed.xml)
