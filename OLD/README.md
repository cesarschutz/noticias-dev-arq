# CsR News — Arquivo Diário do Arquiteto

Curadoria diária de notícias técnicas para arquitetos de software e solução, gerada automaticamente por IA e publicada no GitHub Pages. Primeira versão pública (v1).

## Como funciona

Arquitetura **data-driven**: templates HTML carregam dados de arquivos JSON via `fetch()`.

- **SPA** (`home.html`): console ops single-file — topbar + sidebar + main + rail. Dark/light, cards/list, busca global, deep links.
- **Landing** (`index.html`): página institucional com catálogo de categorias e ferramentas.
- **Dados** (`data/*.json`): gerados diariamente pela skill `skills/csr-news-daily.md`.
- **RSS** (`feed.xml`): gerado pelo CI antes do deploy.
- **Deploy**: push para `main` → GitHub Actions → GitHub Pages.

## Diferencial v1

Cada notícia e release traz o campo **`why_it_matters`** — uma frase explicando por que aquilo importa para um arquiteto sênior. Além disso, os destaques diários são escolhidos por um **score explícito** (release oficial, convergência de fontes, sinal social, autoridade da fonte, impacto arquitetural), e ferramentas entram via **rotação dinâmica** (mínimo 10/dia, priorizando updates reais dos últimos 3-7 dias).

## Funcionalidades

- Filtrar por **categoria**, **linguagem** ou **ferramenta** (agrega todas as edições, lazy-load inteligente).
- **Prev/Next entre edições**: botões `◀` `▶` ou `P`/`N`.
- **Botão "→ hoje"**: atalho visual para voltar à edição do dia atual.
- **Calendário na sidebar**: navegação por mês com destaque nas datas com edição.
- **Prompt-bar sticky** no topo do main mostra contexto atual (edição/categoria/ferramenta).
- **Ler depois**: salvar, ordenar, exportar JSON.
- **Cards clicáveis direto**: clique abre URL em nova aba; bookmark, copy, CVEs inline.
- **Teclado**: `T` tema, `1`/`2` modo, `U` filtro urgent, `P`/`N` prev/next edição.
- **RSS**: assine em `feed.xml`.

## Categorias cobertas (16)

Segurança & IAM · IA & LLMs · **AIOps & Agents** (novo) · **Cloud** (AWS/Azure/GCP) · DevOps & Plataformas · Observabilidade & SRE · Backend & Runtimes · Dados & Streaming · Integração & Eventos · Testes & Qualidade · Frontend & Web · Design & Padrões · Sist. Distribuídos · Arq. Corporativa · **Fundamentos de Computação** (sexta-feira = deep dive) · Fintech & Pagamentos.

Cada categoria tem subcategorias internas (guiam pesquisa e populam `tags[]`, mas não aparecem na UI).

## Linguagens monitoradas (3)

Java & JVM · JavaScript / TS · Python.

## Ferramentas monitoradas (25, só com release notes identificáveis)

**AI & IDEs**: Claude Code · Cursor IDE · IntelliJ IDEA · VS Code

**Git & CI/CD**: Argo CD · GitHub Actions · GitHub

**Containers & IaC**: Docker · Kubernetes · Terraform

**Mesh, Proxies & Edge**: Istio · Nginx

**Dados & Streaming**: Databricks · PostgreSQL · Redis · Apache Kafka

**Obs & Segurança**: Dynatrace · Datadog · Keycloak

**Backend & Build**: Gradle · Apache Maven · Spring Boot (+ Spring Cloud)

**Design & Docs-as-code**: Structurizr · PlantUML · Mermaid

> **Sub-tópicos cobertos via subcategoria** (não têm ferramenta dedicada, mas aparecem em notícias da categoria correspondente): Backstage, Helm, OpenTofu, Envoy (em `devops`) · MCP, Ollama, Langfuse, LangGraph (em `aiops`) · OpenTelemetry, Prometheus, Grafana (em `obs`) · Trivy, Vault (em `sec`) · Cloudflare (em `cloud`) · pgvector, dbt (em `data`) · Temporal (em `distarch`) · k6, Playwright (em `testing`) · Next.js, Vite, Bun, Biome (em `frontend`) · Wasmtime (em `backend`).

## Desenvolvimento local

```bash
# fetch() requer servidor HTTP, não file://
python3 -m http.server 8000
open http://localhost:8000/home.html

# Validar schemas dos JSONs
python3 scripts/validate_editions.py

# Gerar RSS localmente
python3 scripts/generate_feed.py
```

## Estrutura

```
home.html                     → SPA (feed diário)
index.html                    → landing (catálogo institucional)
assets/                       → logo
data/editions.json            → índice + counts por categoria/ferramenta
data/YYYY-MM-DD.json          → edição de cada dia
data/java-versions/           → JEPs por versão Java
data/python-versions/         → PEPs por versão Python
data/js-versions/             → features por edição ECMAScript
data/quotes.json              → frases de autores (fixo, 80+)
data/verses.json              → versículos em PT-BR (fixo, 120+)
skills/csr-news-daily.md      → skill para geração diária
scripts/validate_editions.py  → validador de schema + URLs + duplicatas
scripts/generate_feed.py      → gerador RSS 2.0
.github/workflows/            → CI (deploy + validação)
CLAUDE.md                     → instruções para Claude
COMO-FUNCIONA.md              → documentação user-friendly
```

## Link

[cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/) · [RSS](https://cesarschutz.github.io/noticias-dev-arq/feed.xml)
