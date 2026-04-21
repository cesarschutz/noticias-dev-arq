# CsR News — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages. Primeira versão pública (v1).

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (template HTML único):

```
home.html  → fetch('data/editions.json')  (índice com counts)
           → fetch('data/{ISO}.json')     (edição por data, sob demanda)
index.html → landing pública (hero + catálogo de categorias/ferramentas)
```

O `home.html` é uma SPA single-file (CSS + JS vanilla embutidos) no estilo **"console ops"** — terminal moderno com paleta marine/cyan/violet/amber. Três colunas:
- **Sidebar esquerda (cockpit)**: nav-row (prev/next + data com badge HOJE), 2 botões inline (ler depois, tema), calendário de edições, categorias e ferramentas agrupadas por subgrupo do rail.
- **Main (feed)**: sem hero em home — começa direto nos destaques. Prompt-bar sticky no topo (`csr@console:~/editions/DATA $ cat DATA.json [HOJE]`) muda de cor por contexto (home=amber, cat=cor da categoria, tool=cor do tipo). Cards clicáveis abrem URL em nova aba.
- **Rail (telemetria)**: quote do dia (rotação a cada 25s, 5 por edição), radar de categorias, timeline de edições.

Topbar: logo + status terminal-style à direita (clock, atualizado há Xh, N saved, `?` atalhos). Sem statusbar inferior. Sem frameworks, sem build step.

## Estrutura de Arquivos

```
├── home.html                       # SPA single-file (feed diário)
├── index.html                      # Landing pública (catálogo institucional)
├── assets/
│   └── csr-news-logo.svg           # Logo
├── data/
│   ├── editions.json               # Índice mestre + counts por categoria/ferramenta
│   ├── {YYYY-MM-DD}.json           # Edição completa do dia
│   ├── quotes.json                 # 80+ frases (fixo — nunca recriar)
│   ├── verses.json                 # 120+ versículos (fixo — nunca recriar)
│   ├── java-versions/              # JEPs por versão Java
│   ├── python-versions/            # PEPs por versão Python
│   └── js-versions/                # Features por edição ECMAScript
├── scripts/
│   ├── validate_editions.py        # Valida schema + URLs + duplicatas
│   └── generate_feed.py            # Gera feed.xml
├── skills/
│   └── csr-news-daily.md           # Skill Cowork para geração diária
├── .github/workflows/
│   ├── pages.yml                   # Deploy no GitHub Pages
│   └── validate.yml                # Validação JSON em PRs
├── CLAUDE.md                       # Este arquivo (instruções para Claude)
├── README.md                       # Descrição pública do projeto
├── COMO-FUNCIONA.md                # Documentação user-friendly (como funciona + catálogos)
└── push.sh                         # Script de push (via LaunchAgent local)
```

## Fluxo de Dados

1. **Cowork** roda `skills/csr-news-daily.md` diariamente às 6h BRT.
2. Pesquisa notícias via WebSearch em **16 categorias + 3 linguagens + 25 ferramentas + HN + Lobste.rs + GitHub Trending + engenharia BR**.
3. Monta `data/{date}.json` com sanity checks (URLs específicas, dedup com últimas 7 edições, verificação de links, score explícito para highlights).
4. Atualiza `data/editions.json` com a nova entrada (incluindo `counts_by_category` e `counts_by_tool`).
5. LaunchAgent local detecta mudança em `data/` e roda `push.sh`.
6. GitHub Actions (`pages.yml`) gera `feed.xml` → deploya no GitHub Pages.
7. GitHub Actions (`validate.yml`) valida JSON em PRs.

## Views da SPA

- **home** (default): edição do dia mais recente — highlights (3 cards top-ranqueados por score), feed por categoria, ferramentas/linguagens.
- **cat:{chave}**: agregado de todas as notícias de uma categoria através das edições.
- **tool:{chave}**: feed completo da ferramenta — releases, notícias, tutoriais (seções distintas).
- **deep link**: `?d=YYYY-MM-DD&u=<hash>` abre direto uma notícia.

### Lazy-load inteligente

Ao filtrar por categoria/ferramenta, a SPA usa `counts_by_category` / `counts_by_tool` do `editions.json` para **só baixar** as edições que têm conteúdo daquele filtro.

## Interações

- **Deep link**: URL com `?d=YYYY-MM-DD` preserva a edição aberta.
- **Prev/Next edições**: botões `◀` `▶` ou atalhos `P`/`N`.
- **Botão "→ hoje"**: volta para a edição do dia atual.
- **Filtro**: toolbar tem chip `urgent` (atalho `U`).
- **Ler depois**: bookmark via `localStorage` (`csrn-read-later`). Modal com ordenação e export JSON.
- **Tema dark/light**: toggle na sidebar ou atalho `T`.
- **Modo cards/list**: atalhos `1` (grid multi-coluna) / `2` (lista).
- **Teclado**: `T`, `1`/`2`, `U`, `P`/`N`, `ESC`.
- **Mobile**: sidebar vira hamburger abaixo de 720px.

## Campos estruturados por notícia (v1)

- **`why_it_matters`** — 1 frase obrigatória em cada item de `news[]` e `tools[]`: por que importa para arquiteto sênior. Diferencial v1.
- **`cves: []`** — CVEs citados, renderizados como pills clicáveis para NVD no modal.
- **`severity: "critical|high|medium|low"`** — para itens de segurança.
- **`published_at`** — ISO 8601 do artigo original.
- **`tags: []`** — 2-6 entidades/tecnologias, mostradas como pills.

## JSON Schemas

### `data/editions.json`

```json
{
  "last_generated": "2026-04-17T06:00:00-03:00",
  "editions": [
    {
      "date": "YYYY-MM-DD",
      "summary": "1-2 frases",
      "counts_by_category": { "sec": 3, "ai": 2, "aiops": 3, "cloud": 2 },
      "counts_by_tool": { "cursor": 1, "langfuse": 1, "docker": 1 },
      "highlights": [{ "title": "...", "url": "..." }]
    }
  ]
}
```

### `data/{YYYY-MM-DD}.json`

Raiz: `date`, `weekday`, `formatted_date`, `generated_at` (ISO 8601), `hero_title`, `hero_description`, `highlights[]`, `news[]`, `tools[]`, `quotes[]`, `sources[]`.

Item de `highlights[]`: exatamente 3 itens, selecionados pelo score explícito (FASE 6 da skill). Cópia de item de `news[]` ou `tools[]` + `source_array: "news" | "tools"`.

Item de `news[]`: obrigatórios `category`, `category_label`, `category_icon`, `headline`, `summary`, `why_it_matters`, `source`, `url`, `read_time`. Opcionais: `urgent`, `breaking`, `severity`, `cves[]`, `tags[]`, `published_at`, `image`.

Item de `tools[]`: obrigatórios `tool_key`, `name`, `kind`, `headline`, `why_it_matters`, `source`, `url`. `version` obrigatório quando `kind === "release"`. Opcionais: `icon`, `description`, `published_at`, `image`, `tags`. `kind` ∈ `{release, news, tip, tutorial, curiosity}`.

Hierarquia de `kind` em `tools[]`: `release > news > tutorial > tip > curiosity`. Use `curiosity` apenas como último recurso — máximo 1 por ferramenta por mês.

Array `quotes[]` (5 itens/dia): `text`, `author`, `related_to` (obrigatórios), `context` (opcional). `related_to` ∈ `"cat:<chave>"`, `"tool:<chave>"`, `"general"`.

Schema completo em `skills/csr-news-daily.md`. Validação em `scripts/validate_editions.py` (constantes `CATEGORIES` e `TOOL_KEYS`). Taxonomia única — sem cutoffs históricos.

## Highlights (`highlights[]`)

Cada edição leva **3 destaques** escolhidos pelo **score explícito** (v1):

| Sinal | Pontos |
|---|---|
| `kind === "release"` oficial | +3 |
| Convergência: ≥2 fontes independentes | +2 |
| HN ≥150 pts OU Lobste.rs top 10 OU GitHub Trending daily | +2 |
| Blog de engenharia Tier 1 ou autor canônico | +1 |
| Impacto arquitetural claro (CVE CVSS ≥9, breaking, GA major) | +1 |

Score máximo: +9. Highlights preferem score ≥5; se nenhum chega, top 3 mesmo. Preferir ≥2 categorias distintas — documentar exceção em `hero_description` se necessário.

## Categorias (16)

| Chave | CSS Var | Label | Ícone | Escopo (subcategorias) |
|-------|---------|-------|-------|--------|
| **Transversal** | | | | |
| ai | `--cat-ai` | IA & LLMs | 🤖 | Modelos fundacionais · Pesquisa · Releases OpenAI/Anthropic/Google/Meta/HF · Benchmarks · Papers · Multimodal · AI Safety |
| aiops | `--cat-aiops` | AIOps & Agents | 🧠 | LLMOps · AI Agents & MCP · RAG & Vector DBs · AI Coding em produção · LLM Evals · LLM Observability · Guardrails · Agent Orchestration · Local LLM |
| sec | `--cat-sec` | Segurança & IAM | 🔐 | CVEs & Zero-days · OWASP & AppSec · Zero Trust & Identidade · Passkeys/WebAuthn · Supply Chain (SBOM/SLSA/Sigstore) · **Runtime/Container Security (Trivy)** · AI Security · **Secrets Management (Vault)** · LGPD |
| **Plataforma & Infraestrutura** | | | | |
| cloud | `--cat-cloud` | Cloud | ☁️ | AWS · Azure · GCP · **CDN & Edge (Cloudflare, Fastly)** · Cloud Networking (VPC/peering) · Well-Architected · FinOps multi-cloud |
| devops | `--cat-devops` | DevOps & Plataformas | ⚙️ | Containers & CNCF · GitOps · CI/CD · Progressive Delivery · IaC · IDPs & developer portals · **Edge/Proxies/Protocolos (HTTP/3, QUIC, envoy)** · Developer Productivity |
| obs | `--cat-obs` | Observabilidade & SRE | 📈 | Tracing (OTel) · Métricas · Logs · APM · SLO/SLI & Error Budgets · Incident Management · eBPF & Profiling · Cost Observability · **Capacity Planning & Performance Tuning** |
| **Desenvolvimento** | | | | |
| backend | `--cat-backend` | Backend & Runtimes | 🔧 | Runtimes poliglotas · Web frameworks · Concurrency models · **WebAssembly (Wasmtime/Spin/WASI)** · Build tools · Server-side patterns · Performance engineering |
| data | `--cat-data` | Dados & Streaming | 🗄️ | Relacionais · NoSQL · Streaming (Flink) · Lakehouse (dbt/Iceberg) · **Vector DBs (pgvector, Pinecone)** · CDC · Data Contracts · Data Mesh |
| integ | `--cat-integ` | Integração & Eventos | 🔌 | API Design & API-First · OpenAPI · **API Versioning & Evolution** · **API Gateway & Rate Limiting** · **gRPC & Protocol Buffers** · GraphQL & Federation · AsyncAPI · EDA · Messaging · Schema Evolution · Webhooks & Idempotência |
| testing | `--cat-testing` | Testes & Qualidade | ⚗️ | TDD/BDD · Testing Pyramid · Contract Testing · Chaos Engineering · Performance/Load (k6) · Mutation Testing · AI-assisted testing |
| frontend | `--cat-frontend` | Frontend & Web | 🎨 | Frameworks SPA · Meta-frameworks · RSC & streaming SSR · Web Platform · Design Systems · Core Web Vitals · Edge Rendering · Build Tools (Vite/Bun/Biome) · a11y/i18n |
| **Arquitetura** | | | | |
| design | `--cat-design` | Design & Padrões | 🏛️ | DDD & Bounded Contexts · Padrões GoF/Enterprise · Clean/Hexagonal · C4 Model · ADRs · Refactoring · docs-as-code · **System Design Process (HLD/LLD)** · **Back-of-the-envelope & Capacity Estimation** |
| distarch | `--cat-distarch` | Sist. Distribuídos | 🕸 | Microsserviços · Cloud Native · Resiliência · Service Mesh · Saga/CQRS/ES · Caching · Consistency Models · Durable Execution · Post-mortems · **Stateless vs Stateful** |
| enterprise | `--cat-enterprise` | Arq. Corporativa | 🗺️ | 3 eixos: Estrutura org (Team Topologies, Platform Eng, DevEx/DORA/SPACE); Governança & custos (API Governance, FinOps); Estratégia técnica (Tech Radar) |
| **Fundação** | | | | |
| fundamentals | `--cat-fundamentals` | Fundamentos de Computação | 🧱 | SO · Redes · Estruturas de Dados & Algoritmos · Concorrência & Paralelismo · Memory models · Teoria de filas · Performance de hardware — **sexta = deep dive (2-3 itens, autor canônico)** |
| **Domínio** | | | | |
| fintech | `--cat-fintech` | Fintech & Pagamentos | 💳 | **Cartões & Redes (Visa/Mastercard/Elo)** · **Cooperativas (Unicred/Sicoob/Sicredi)** · Pix/Open Finance/DREX · PCI DSS · Embedded Finance/BaaS · Payment Rails |

### Regras de desempate (pertencimento duplo)

- Service Mesh → `distarch` · Zero Trust → `sec` · Platform Engineering (conceito) → `enterprise` · Backstage/IDPs (produto) → `devops` · Supply Chain → `sec`
- Kafka/Flink (tech) → `data`; EDA (padrão) → `integ` · DDD → `design`; Microsserviços → `distarch`
- OpenAPI/GraphQL → `integ` · **MCP como protocolo → `aiops`**; como contrato API → refs em `integ`
- **AI Agents / LangGraph / LLM em produção → `aiops`**; modelos/pesquisa → `ai`
- **Vector DBs (pgvector, Pinecone) → `data` (casa canônica)**; aplicação em agents → `aiops`
- **LLM Observability (Langfuse, LangSmith) → `aiops`**; AI Security → `sec`
- AWS/Azure/GCP/CDN/Edge/DNS → `cloud`; HTTP/3, QUIC, proxies (nginx/envoy) → `devops`
- **WebAssembly no backend (Wasmtime, Spin, WASI) → `backend`**
- Fundamentos de SO/redes/algoritmos → `fundamentals`

## Conceito fundamental: Categorias, Linguagens, Ferramentas

### Categoria (`CAT`)

Tema editorial **amplo**. Cada categoria tem subcategorias que guiam pesquisa (e populam `tags[]`) mas **não aparecem na UI**.

- Cobertura v1: **sem mínimo obrigatório por categoria** — cats sem sinal do dia podem ficar em 0 itens. Teto 3/cat (até 5 em `urgent:true` ou convergência ≥3 fontes).
- **Mínimo total**: 15 itens/dia em `news[]` (janela ≤24h), 20 (1-3 dias), 25 (>3 dias).
- **Sexta-feira**: `fundamentals` ganha 2-3 itens obrigatórios (1 evergreen canônico).
- Aparecem na sidebar esquerda listadas por grupo editorial.
- View: `cat:{chave}` agrega todas as notícias daquela categoria.

### Subcategoria

Recorte conceitual. **Invisível na UI** — guia queries da skill e popula `tags[]`. Sem cobertura obrigatória diária.

### Linguagem (`group:'lang'` em `TOOLS`)

3 itens imutáveis: `java`, `javascript`, `python`. Entram no pool de rotação dinâmica diária de `tools[]`.

### Ferramenta (`group:'tools'` em `TOOLS`)

Só entra se tem **release notes/changelog identificável**. Conceitos/disciplinas (SRE, DevEx, FinOps, Platform Engineering) **não são ferramentas** — viram subcategorias.

- **Cobertura v1**: **rotação dinâmica** — a skill escolhe **mínimo 10 tools/dia** priorizando (a) releases/news de 3-7 dias, (b) rotação para não repetir últimas 7 edições, (c) fallback com tutorial/deep-dive relacionado de autor canônico. Sem obrigatoriedade fixa por ferramenta.
- Aparecem no rail direito agrupadas por subgrupo.
- View: `tool:{chave}` exibe todos os itens daquela ferramenta.

### Quando me pedirem para adicionar algo novo — perguntar sempre

| Tipo | Quando é | Exemplos |
|---|---|---|
| **Categoria** | Tema editorial amplo, cobre múltiplas tecnologias/padrões | Um "mobile" novo, um "quantum" novo |
| **Subcategoria** | Recorte de categoria existente, conceito/disciplina | "SAML" em `sec`, "TOGAF" em `enterprise`, "Service Mesh" em `distarch` |
| **Ferramenta** | Produto com changelog/release notes identificável | Docker, Kubernetes, Next.js, Langfuse |

**Teste rápido** para decidir ferramenta vs subcategoria: *"Tem URL estável de release notes/changelog?"* — se sim, ferramenta; se não, subcategoria.

---

## Linguagens & Ferramentas monitoradas (28 = 3 linguagens + 25 ferramentas)

Cada item tem `logo` (URL), `group` (rail: `lang` ou `tools`), `subgroup` (subagrupamento visual no rail), `category` (chave de `CAT`) e `kind` no array `TOOLS` em `home.html` (SPA) e em `TOOL_SUBGROUPS` de `index.html` (landing).

> **`group` vs `category`**: `group` define onde o item aparece no rail (`tools` vs `lang`). `category` define filtro editorial. Conceitos independentes.

| Subgrupo rail | `tool_key` | Nome | Categoria editorial |
|---|---|---|---|
| **AI & IDEs** | | | |
| AI & IDEs | `claudecode` | Claude Code | `aiops` |
| AI & IDEs | `cursor` | Cursor IDE | `aiops` |
| AI & IDEs | `intellij` | IntelliJ IDEA | `backend` |
| AI & IDEs | `vscode` | VS Code | `aiops` |
| **Git & CI/CD** | | | |
| Git & CI/CD | `argocd` | Argo CD | `devops` |
| Git & CI/CD | `ghactions` | GitHub Actions | `devops` |
| Git & CI/CD | `github` | GitHub | `devops` |
| **Containers & IaC** | | | |
| Containers & IaC | `docker` | Docker | `devops` |
| Containers & IaC | `kubernetes` | Kubernetes | `devops` |
| Containers & IaC | `terraform` | Terraform | `devops` |
| **Mesh, Proxies & Edge** | | | |
| Mesh, Proxies & Edge | `istio` | Istio | `distarch` |
| Mesh, Proxies & Edge | `nginx` | Nginx | `devops` |
| **Dados & Streaming** | | | |
| Dados & Streaming | `databricks` | Databricks | `data` |
| Dados & Streaming | `postgres` | PostgreSQL | `data` |
| Dados & Streaming | `redis` | Redis | `data` |
| Dados & Streaming | `kafka` | Apache Kafka | `integ` |
| **Obs & Segurança** | | | |
| Obs & Segurança | `dynatrace` | Dynatrace | `obs` |
| Obs & Segurança | `datadog` | Datadog | `obs` |
| Obs & Segurança | `keycloak` | Keycloak | `sec` |
| **Backend & Build** | | | |
| Backend & Build | `gradle` | Gradle | `backend` |
| Backend & Build | `maven` | Apache Maven | `backend` |
| Backend & Build | `springboot` | Spring Boot (+ Spring Cloud) | `backend` |
| **Design & Docs-as-code** | | | |
| Design & Docs-as-code | `structurizr` | Structurizr (C4 + DSL + MCP) | `design` |
| Design & Docs-as-code | `plantuml` | PlantUML | `design` |
| Design & Docs-as-code | `mermaid` | Mermaid | `design` |
| **Linguagens** | | | |
| Linguagens | `java` | Java & JVM | `backend` |
| Linguagens | `javascript` | JavaScript / TS | `frontend` |
| Linguagens | `python` | Python | `backend` |

### Sub-tópicos cobertos em subcategorias (sem `tool_key` dedicado)

| Sub-tópico | Categoria-casa | Notas |
|---|---|---|
| Backstage, Helm, OpenTofu, Envoy | `devops` | IDP, package manager K8s, IaC OSS, proxy L7 |
| MCP, Ollama, Langfuse, LangGraph | `aiops` | Protocolo agents, LLM local, observability, orchestration |
| OpenTelemetry, Prometheus, Grafana | `obs` | Telemetria padrão, métricas, dashboards |
| Trivy, Vault | `sec` | Scanner de CVEs/IaC, secrets management |
| Cloudflare | `cloud` | CDN/Edge/Workers/Zero Trust |
| pgvector, dbt | `data` | Vector DB, analytics engineering |
| Temporal | `distarch` | Durable execution |
| k6, Playwright | `testing` | Load + E2E |
| Next.js, Vite, Bun, Biome | `frontend` | Meta-framework, build tool, runtime JS, lint+format |
| Wasmtime | `backend` | Runtime WebAssembly |

---

## O Que Atualizar Quando

> **Princípio universal**: antes de adicionar QUALQUER item novo (categoria, ferramenta, linguagem), **pesquise as melhores fontes sobre o tema** (WebSearch). Só depois, atualize TODOS os arquivos afetados.
>
> **Fonte de verdade**: este `CLAUDE.md`. Se mudar regra editorial, sincronize os **3 documentos humanos** no mesmo commit: `README.md`, `CLAUDE.md`, `skills/csr-news-daily.md`. Sempre rodar `python3 scripts/validate_editions.py` antes do commit.

### Mapa: o que aparece na tela e de onde vem

| O que aparece na tela | Onde fica no código | O que muda na skill |
|---|---|---|
| **Sidebar — lista de categorias** | `CAT` em `home.html` | Seção "CATEGORIAS E QUERIES" |
| **Sidebar — cor de destaque ao filtrar** | `--cat-{chave}` em `:root` e `[data-theme="light"]` de `home.html` | — |
| **Sidebar — ícone SVG de categoria** | `CAT_ICONS` em `home.html` | — |
| **Rail direito — subgrupos + ferramentas** | `TOOL_SUBGROUPS` + `TOOLS` em `home.html` | Tabela `tool_key` e política de conteúdo indireto |
| **Rail — logo da ferramenta** | campo `logo` em `TOOLS` | — |
| **About page — "N categorias" / "N monitorados"** | `ab-stat-n` em `home.html` | — |
| **Landing `index.html`** | `CATS` + `TOOL_SUBGROUPS` | — |
| **Filtro `cat:{chave}` e `tool:{chave}` via URL** | `CAT` e `TOOLS` em `home.html` | — |
| **Feed diário (home)** | JSON `data/YYYY-MM-DD.json` gerado pela skill | Queries + fontes + regras de cobertura |
| **README — listas de categorias e ferramentas** | `README.md` | — |
| **Validador** | `CATEGORIES` e `TOOL_KEYS` em `validate_editions.py` | — |

**Regra prática**: se mudar taxonomia, percorra todos os campos desta tabela.

---

### Classificar uma adição nova — Claude deve fazer isso PROATIVAMENTE

| Tipo | Compromisso | Onde aparece | Critério principal |
|---|---|---|---|
| **Categoria** | Cobertura flexível (sem mínimo obrigatório); entra na sidebar com cor e ícone | `CAT`, CSS var, `CAT_ICONS`, About page | Tema amplo com notícias de múltiplas fontes; escopo ortogonal às 16 existentes |
| **Ferramenta** | Entra no pool de rotação dinâmica (mín. 10 tools/dia); rail direito com logo | `TOOLS`, rail, About page | Tecnologia/produto com changelog próprio |
| **Linguagem** | Igual à Ferramenta + dados de versão em `data/{lang}-versions/` | Idem + seção dedicada na skill | Linguagem de programação com releases |
| **Sub-categoria / tag** | Aparece em `tags[]` quando há notícia | `tags[]` em `news[]` | Sub-tópico de categoria existente |

Sempre pesquisar melhores fontes (WebSearch) antes de implementar. Nunca implementar silenciosamente.

---

### Alterar o design visual

- Edite `home.html` ou `index.html` (CSS + HTML no mesmo arquivo).
- Dados JSON não precisam mudar.

### Pesquisar fontes antes de adicionar (OBRIGATÓRIO)

1. `"best [tema] blogs" OR "top [tema] resources" site:reddit.com`
2. `"[tema] newsletter" most popular {current_year}`
3. `"[tema] blog" developers OR architects`

Identifique: changelog/blog oficial, blog editorial de referência, sub-tópicos e melhores sites. Adicione fontes na skill (seção "CATEGORIAS E QUERIES" ou tabela de tools).

### Adicionar/remover uma categoria

1. `home.html`: chave em `CAT`, SVG em `CAT_ICONS`, variável `--cat-{chave}` em `:root` e `[data-theme="light"]`.
2. `home.html` About page: stat `N categorias` (linha `ab-stat-n`).
3. `index.html`: adicione em `CATS`.
4. `README.md`: atualize a lista.
5. `CLAUDE.md`: atualize tabela de categorias (esta seção).
6. `skills/csr-news-daily.md`:
   - Seção "CATEGORIAS E QUERIES" (novo bloco)
   - Grupo FASE correto (3A/3B/3C) do FLUXO DE EXECUÇÃO
   - Tabela de chaves válidas
   - Regras de desempate
7. `scripts/validate_editions.py`: adicione a `CATEGORIES`.
8. `COMO-FUNCIONA.md`: atualize catálogo.

### Adicionar/remover uma Ferramenta

1. **Perguntar ao usuário** se é Ferramenta ou sub-tópico de categoria.
2. `home.html`: adicione entrada em `TOOLS` (com `aliases`, `kind`, `category`, `logo`, `group:'tools'`, `subgroup`). Se subgrupo novo, adicione a `TOOL_SUBGROUPS` e à função de render.
3. `home.html` About page: stat `N monitorados`.
4. `index.html`: adicione em `TOOL_SUBGROUPS`.
5. `README.md` / `CLAUDE.md`: atualize tabelas.
6. `skills/csr-news-daily.md`:
   - Tabela `tool_key · Categoria · Changelog` completa
   - Política de conteúdo indireto (tabela)
7. `scripts/validate_editions.py`: adicione a `TOOL_KEYS`.
8. `COMO-FUNCIONA.md`: atualize catálogo.

### Adicionar uma Linguagem de Programação

1. Todos os passos de "Adicionar Ferramenta".
2. `skills/csr-news-daily.md`: seção dedicada de queries.
3. Se tiver versioning relevante: criar `data/{lang}-versions/index.json` e `{lang}-{N}.json` (modelo: `data/java-versions/`).

### Alterar queries de pesquisa

Edite em `skills/csr-news-daily.md` na seção "CATEGORIAS E QUERIES DE PESQUISA".

### Testar localmente

```bash
python3 -m http.server 8000
open http://localhost:8000/home.html
python3 scripts/validate_editions.py
python3 scripts/generate_feed.py
```

## Convenções

- Datas ISO 8601 (`YYYY-MM-DD`) em arquivos e campos `date`/`weekday`.
- `generated_at` e `last_generated` em ISO 8601 completo com timezone (`YYYY-MM-DDTHH:MM:SS-03:00`).
- Conteúdo de texto em português brasileiro.
- Caminhos relativos (funciona no GitHub Pages com subpath).
- JSON com indentação de 2 espaços, emojis em UTF-8 literal.
- `localStorage` usa prefixo `csrn-` (CsR News).
- **`{current_year}`** nas queries da skill é substituído em runtime pelo ano atual.

## Deploy

Push para `main` → GitHub Actions (`pages.yml`) gera `feed.xml` e deploya.
URL: `https://cesarschutz.github.io/noticias-dev-arq/`
RSS: `https://cesarschutz.github.io/noticias-dev-arq/feed.xml`

Workflow com `paths` filter: mudanças só em `.md` não disparam redeploy.
