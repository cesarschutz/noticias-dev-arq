# DevPulse — Arquivo Diário do Arquiteto

Curadoria diária de notícias técnicas para arquitetos de software e solução, gerada automaticamente por IA e publicada no GitHub Pages.

## Como funciona

Arquitetura **data-driven**: um template HTML único carrega dados de arquivos JSON via `fetch()`.

- **SPA** (`index.html`): console ops single-file — topbar + sidebar (10 categorias + 11 ferramentas) + main (feed) + rail (telemetria) + statusbar. Dark/light toggle.
- **Dados** (`data/*.json`): gerados diariamente pela skill `skills/devpulse-daily.md`
- **Deploy**: push para `main` → GitHub Actions → GitHub Pages

## Funcionalidades

- Filtrar por **categoria** ou **ferramenta** na sidebar esquerda (agrega todas as edições)
- **Ler depois**: salvar matérias para consumo posterior (persistido no navegador)
- **Modal reader**: abre a matéria em popup central; marca como lida automaticamente
- **Modos**: cards (grid) ou list (índice compacto)
- **Calendário**: navegar entre edições via date picker no topbar

## Categorias cobertas

Segurança · IA & LLMs · Cloud (foco AWS) · DevOps · Backend & APIs · Frontend · Bancos de Dados · Linguagens & Tooling · Arquitetura de Software · Arquitetura de Solução.

## Ferramentas monitoradas

Microsoft Teams · Notion · IntelliJ IDEA · Cursor IDE · Warp Terminal · MongoDB Compass · DBeaver · Postman · Docker Desktop · Structurizr · C4 Model.

## Desenvolvimento local

```bash
# fetch() requer servidor HTTP, não file://
python3 -m http.server 8000
open http://localhost:8000
```

## Estrutura

```
index.html               → SPA (template único)
assets/                  → Logo e texturas
data/editions.json       → Índice de todas as edições
data/YYYY-MM-DD.json     → Dados de cada dia
skills/devpulse-daily.md → Skill Cowork para geração diária
```

## Link

[cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/)
