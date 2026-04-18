# CsR News — Arquivo Diário do Arquiteto

Curadoria diária de notícias técnicas para arquitetos de software e solução, gerada automaticamente por IA e publicada no GitHub Pages.

## Como funciona

Arquitetura **data-driven**: um template HTML único carrega dados de arquivos JSON via `fetch()`.

- **SPA** (`index.html`): console ops single-file — topbar + sidebar + main + rail. Dark/light, cards/list, busca global, deep links.
- **Dados** (`data/*.json`): gerados diariamente pela skill `skills/csr-news-daily.md`
- **RSS** (`feed.xml`): gerado pelo CI antes do deploy
- **Deploy**: push para `main` → GitHub Actions → GitHub Pages

## Funcionalidades

- Filtrar por **categoria** ou **assunto fixo** (agrega todas as edições, lazy-load inteligente)
- **Prev/Next entre edições**: botões `◀` `▶` ou `P`/`N`
- **Botão "→ hoje"**: atalho visual para voltar à edição do dia atual
- **Calendário na sidebar**: navegação por mês com destaque nas datas com edição disponível
- **Prompt-bar sticky** no topo do main mostra contexto atual (edição/categoria/assunto) estilo terminal
- **Ler depois**: salvar, ordenar, exportar JSON
- **Cards clicáveis direto**: clique abre URL em nova aba; bookmark, copy, CVEs inline
- **Teclado**: `T` tema, `1`/`2` modo, `U` filtro urgent, `P`/`N` prev/next edição
- **RSS**: assine em `feed.xml`

## Categorias cobertas

Segurança & IAM · IA & LLMs · AWS · DevOps & Plataformas · Observabilidade · Dados & Streaming · Integração & Eventos · Backend & Runtimes · **Testes & Qualidade** · Design & Padrões · Arq. Corporativa · Sist. Distribuídos · Fintech & Pagamentos.

## Assuntos fixos monitorados

**Tópicos**: API-First · Cloud Native · CVEs & Vulnerabilidades · DDD · Event-Driven · Microsserviços · OWASP · Resiliência

**Ferramentas — AI & IDEs**: Cursor IDE · Claude Code · ChatGPT · VS Code · IntelliJ IDEA

**Ferramentas — Git & CI/CD**: Argo CD · GitHub Actions · Git · GitHub · Helm

**Ferramentas — Containers & Infra**: Docker · Istio · Kubernetes · AWS Lambda · Terraform

**Dados & Integração**: PostgreSQL · MySQL · Databricks · Amazon DynamoDB · Apache Kafka · OpenAPI · Redis

**Backend & Design**: Spring Boot · Spring Cloud · Quarkus · Gradle · Apache Maven · Structurizr

**Segurança & Obs**: CVEs & Vulnerabilidades · Keycloak · OWASP · Dynatrace · Grafana

**Linguagens & Runtimes**: Java & JVM · JavaScript / TS · Python

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
assets/                      → Logo
data/editions.json           → Índice + counts por categoria/assunto
data/YYYY-MM-DD.json         → Dados de cada dia
data/java-versions/          → JEPs por versão Java (11–atual)
data/python-versions/        → PEPs por versão Python (3.8–atual)
data/js-versions/            → Features por edição ECMAScript (ES2015–atual)
data/quotes.json             → Frases de autores técnicos (gerado na 1ª execução)
data/verses.json             → Versículos de Jesus em PT-BR (gerado na 1ª execução)
skills/csr-news-daily.md     → Skill para geração diária
scripts/validate_editions.py → Validador de schema + URLs + duplicatas
scripts/generate_feed.py     → Gerador RSS 2.0
.github/workflows/           → CI (deploy + validação)
```

## Link

[cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/) · [RSS](https://cesarschutz.github.io/noticias-dev-arq/feed.xml)
