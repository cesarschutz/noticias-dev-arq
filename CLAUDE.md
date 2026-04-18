# CsR News — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages.

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (template HTML único):

```
index.html → fetch('data/editions.json')  (índice com counts)
           → fetch('data/{ISO}.json')     (edição por data, sob demanda)
```

O `index.html` é uma SPA single-file (CSS + JS vanilla embutidos) no estilo **"console ops"** — terminal moderno com paleta marine/cyan/violet/amber. Três colunas:
- **Sidebar esquerda (cockpit)**: nav-row (prev/next + data com badge HOJE), 2 botões inline (ler depois, tema), calendário de edições, categorias e assuntos fixos agrupados por grupo do rail.
- **Main (feed)**: sem hero em home — começa direto nos destaques. Prompt-bar sticky no topo (`csr@console:~/editions/DATA $ cat DATA.json [HOJE]`) muda de cor por contexto (home=amber, cat=cor da categoria, tool=cor do tipo). Cards clicáveis abrem URL em nova aba.
- **Rail (telemetria)**: quote do dia (rotação a cada 25s, 5 por edição), radar de categorias, timeline de edições.

Topbar: logo + status terminal-style à direita (clock, atualizado há Xh, N saved, `?` atalhos). Sem statusbar inferior. Sem frameworks, sem build step.

## Estrutura de Arquivos

```
├── index.html                      # SPA single-file
├── assets/
│   └── csr-news-logo.svg           # Logo (usado no boot e topbar)
├── data/
│   ├── editions.json               # Índice mestre + counts por categoria/assunto fixo
│   ├── {YYYY-MM-DD}.json           # Dados completos de cada dia
│   ├── quotes.json                 # 80+ frases de autores técnicos (gerado na 1ª execução)
│   ├── verses.json                 # 120+ versículos de Jesus em PT-BR (gerado na 1ª execução)
│   ├── java-versions/
│   │   ├── index.json              # Índice de versões Java (atualizado a cada execução)
│   │   └── java-{N}.json           # JEPs e detalhes — Java 11 até atual
│   ├── python-versions/
│   │   ├── index.json              # Índice de versões Python
│   │   └── python-{N}.json         # PEPs e detalhes — Python 3.8 até atual
│   └── js-versions/
│       ├── index.json              # Índice de versões ECMAScript
│       └── js-es{YYYY}.json        # Features — ES2015 até atual
├── scripts/
│   ├── validate_editions.py        # Valida schema + URLs + duplicatas
│   └── generate_feed.py            # Gera feed.xml (RSS 2.0) a partir do índice
├── skills/
│   └── csr-news-daily.md           # Skill Cowork para geração diária
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

1. **Cowork** roda `skills/csr-news-daily.md` diariamente às 6h BRT
2. Pesquisa notícias via WebSearch em 13 categorias + 37 tópicos + HN + blogs eng + pulso BR
3. Monta `data/{date}.json` com sanity checks (URLs específicas, dedup com últimas 7 edições, diversidade pillars)
4. Atualiza `data/editions.json` com a nova entrada (incluindo `counts_by_category` e `counts_by_tool`)
5. LaunchAgent local detecta mudança em `data/` e roda `push.sh` (retry + log rotativo em `~/Library/Logs/csr-news-push.log`)
6. GitHub Actions (`pages.yml`) gera `feed.xml` → deploya no GitHub Pages
7. GitHub Actions (`validate.yml`) valida JSON em PRs

## Views da SPA

- **home** (default): edição do dia mais recente — hero, pillars (3 cards Java/AWS/DistArch), feed, assuntos fixos
- **cat:{chave}**: agregado de todas as notícias de uma categoria através das edições
- **tool:{chave}**: feed completo do assunto fixo — releases, notícias, dicas, tutoriais e curiosidades (seções distintas)
- **deep link**: `?d=YYYY-MM-DD&u=<hash>` abre direto uma notícia

### Lazy-load inteligente
Ao filtrar por categoria/assunto fixo, a SPA usa `counts_by_category` / `counts_by_tool` do `editions.json` para **só baixar** as edições que têm conteúdo daquele filtro. Um loader visual fica no topo do main durante o fetch paralelo. Em background (após boot), todas as edições são pré-aquecidas em cache para busca global.

## Interações

- **Deep link**: URL com `?d=YYYY-MM-DD` preserva a edição aberta. Copiar link de um card usa botão dedicado (copia URL da matéria).
- **Prev/Next edições**: botões `◀` `▶` na sidebar (ou atalhos `P`/`N`) navegam entre edições adjacentes. Em view cat/tool, escondem.
- **Botão "→ hoje"**: aparece na sidebar quando a edição aberta não é a de hoje.
- **Filtro**: toolbar tem chip `urgent` (atalho `U`).
- **Ler depois**: bookmark via `localStorage` (`csrn-read-later`). Modal com ordenação (saved/date/category/urgent), export JSON e clear.
- **Tema dark/light**: toggle na sidebar ou atalho `T`.
- **Modo cards/list**: atalhos `1` (grid multi-coluna) / `2` (lista 1 coluna larga). Ambos com summary completo.
- **Teclado**: `T` tema, `1`/`2` modo cards/list, `U` filtro urgent, `P`/`N` prev/next edição, `ESC` fecha modal.
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
Raiz: `date`, `weekday`, `formatted_date`, `generated_at` (ISO 8601), `hero_title`, `hero_description`, `pillars[]`, `news[]`, `tools[]`, `sources[]`.

Item de `pillars[]`: obrigatórios `pillar` (`java`|`aws`|`distarch`), `category`, `category_label`, `category_icon`, `headline`, `summary`, `source`, `url`, `read_time`, `image`. Exatamente 3 itens, um por pilar.

Item de `news[]`: obrigatórios `category`, `category_label`, `category_icon`, `headline`, `summary`, `source`, `url`, `read_time`. Opcionais: `urgent`, `breaking`, `severity`, `cves[]`, `tags[]`, `published_at`, `image`.

Item de `tools[]`: obrigatórios `tool_key`, `name`, `kind`, `headline`, `source`, `url`. `version` obrigatório quando `kind === "release"`. Opcionais: `icon`, `description`, `published_at`, `image`, `tags`. `kind` ∈ `{release, news, tip, tutorial, curiosity}`. **Nunca omitir `kind`** — não há fallback no render.

Dois perfis de assunto fixo no campo `kind`:
- **Ferramenta com release** (structurizr, cursor, docker, kubernetes, postgres, kafka, springboot…): prioridade `release > news > tutorial > tip > curiosity`. Use `release` quando nova versão saiu na janela; se não, use `news`/`tip`/`tutorial`.
- **Tema/domínio** (cve, owasp, openapi, java, javascript, python): prioridade `news > tutorial > tip > release > curiosity`. `release` só para versões de linguagem/spec (ex: JDK 25, ECMAScript 2025); o dia-a-dia é `news` e `tip`.

Array `quotes[]` (5 itens/dia): `text`, `author`, `related_to` (obrigatórios), `context` (opcional). `related_to` ∈ `"cat:<chave>"`, `"tool:<chave>"`, `"general"`.

Schema completo em `skills/csr-news-daily.md`. Validação em `scripts/validate_editions.py`:
- Edições ≥ `2026-04-18` são **strict v1** (tools com `kind`/`tool_key`, imagens, quotes).
- Edições ≥ `2026-04-20` são **strict v2** (taxonomia nova — categorias, ferramentas v2, `pillars[]` com campo `pillar`).

### `data/java-versions/index.json`
```json
{
  "last_updated": "2026-04-17T06:00:00-03:00",
  "latest_ga": "24",
  "versions": [
    { "version": "21", "release_date": "2023-09-19", "lts": true, "oracle_support_until": "2031-09", "jep_count": 15 },
    { "version": "17", "release_date": "2021-09-14", "lts": true, "oracle_support_until": "2029-09", "jep_count": 14 }
  ]
}
```
Ordenado do mais recente para o mais antigo. Atualizado pela skill a cada execução (só muda se houver versão nova GA).

### `data/java-versions/java-{N}.json`
```json
{
  "version": "21",
  "release_date": "2023-09-19",
  "lts": true,
  "oracle_support_until": "2031-09",
  "summary": "Descrição geral da versão em PT-BR.",
  "links": [
    { "label": "Release Notes", "url": "https://openjdk.org/projects/jdk/21/" },
    { "label": "Baeldung: What's new", "url": "https://www.baeldung.com/java-lts-21-new-features" }
  ],
  "jeps": [
    {
      "number": 444,
      "title": "Virtual Threads",
      "status": "Standard",
      "description": "2-3 linhas em PT-BR explicando o que muda e por que importa para o arquiteto.",
      "url": "https://openjdk.org/jeps/444"
    }
  ]
}
```
`status` ∈ `Standard | Preview | Incubator | Removed`. Gerado na 1ª execução (Java 11–24) e auto-atualizado quando nova versão GA é detectada.

## Pilares (`pillars[]`)

Os três pilares são os destaques fixos do topo de cada edição — um por tema principal:

| `pillar` | Tema | Cor | Ícone |
|---|---|---|---|
| `java` | Java & JVM | `#f89820` | ☕ |
| `aws` | AWS | `#FF9900` | 🔶 |
| `distarch` | Arquitetura Distribuída | `#818cf8` | 🕸 |

Cada pilar substitui o antigo `top3` — visual diferenciado no topo com borda colorida espessa e badge de identificação. Retrocompat: edições antigas com `top3` são renderizadas normalmente.

## Categorias (taxonomia v3 — desde 2026-04-19)

| Chave | CSS Var | Label | Ícone | Escopo |
|-------|---------|-------|-------|--------|
| **Transversal / Hot** | | | | |
| ai | `--cat-ai` | IA & LLMs | 🤖 | Modelos, agents, RAG, MCP, AI coding tools |
| sec | `--cat-sec` | Segurança & IAM | 🔐 | CVEs, zero-days, Keycloak, Auth0, OIDC, zero-trust; SBOM, Sigstore, SLSA, supply chain; Vault, secrets mgmt; Falco, Trivy, container security |
| **Plataforma & Infraestrutura** | | | | |
| aws | `--cat-aws` | AWS | 🔶 | Todos os serviços AWS — Lambda, DynamoDB, SNS, SQS, CloudWatch, etc. |
| devops | `--cat-devops` | DevOps & Plataformas | ⚙️ | K8s, Docker, GitOps, Argo CD, Istio, platform engineering, SRE |
| obs | `--cat-obs` | Observabilidade | 📈 | Tracing, logging, metrics, OpenTelemetry, Dynatrace, Datadog; SLO/SLI/error budgets; eBPF, profiling contínuo; incident management, on-call, post-mortems |
| **Desenvolvimento** | | | | |
| backend | `--cat-backend` | Backend & Runtimes | 🔧 | Java/Spring, Go, Node, Rust, JVM, Gradle, Maven, frameworks server-side |
| data | `--cat-data` | Dados & Streaming | 🗄️ | DB relacional/NoSQL, warehouse, lakehouse, streaming, CDC |
| integ | `--cat-integ` | Integração & Eventos | 🔌 | APIs (REST/GraphQL/gRPC), Kafka, EDA, iPaaS, OpenAPI, schemas |
| testing | `--cat-testing` | Testes & Qualidade | ⚗️ | TDD, BDD, testing pyramid, unit/integration/E2E, contract testing (Pact), mutation testing, chaos engineering, performance/load, property-based testing, CI test strategy, frameworks (JUnit, pytest, Jest, Playwright, Cypress, Vitest) |
| **Arquitetura** | | | | |
| design | `--cat-design` | Design & Padrões | 🏛️ | DDD, padrões, C4, Clean/Hex, ADRs, Structurizr, refactoring |
| distarch | `--cat-distarch` | Sist. Distribuídos | 🕸 | Microsserviços, cloud-native, service mesh, CQRS, saga, post-mortems |
| enterprise | `--cat-enterprise` | Arq. Corporativa | 🗺️ | TOGAF, integração enterprise, landing zones, reference architectures; Team Topologies, Conway's Law; IDP/Backstage, developer portal; FinOps, cloud governance; API governance, API strategy |
| **Domínio** | | | | |
| fintech | `--cat-fintech` | Fintech & Pagamentos | 💳 | Cartões de crédito, Visa, cooperativas de crédito, Pix, Open Finance, DREX, PCI DSS, payment rails |

**Chaves legadas** (mapeadas em runtime para a nova taxonomia):
- `cloud` → `aws`, `db` → `data`, `lang` → `backend`, `frontend` → home (removida)
- `arqsw` → `design`, `arqsol` → `enterprise`

## Conceito fundamental: Categorias vs. Tópicos

Esta distinção é crítica — afeta como a skill pesquisa, como o JSON é gerado e como a SPA exibe o conteúdo.

### Categorias (`CAT`)
Temas editoriais **amplos**. Cada categoria abrange múltiplas tecnologias, padrões e sub-tópicos. Em `sec`, por exemplo, podem aparecer CVEs, Keycloak, Auth0, OWASP, SAML, zero-trust — qualquer coisa do universo de segurança.

- Cobertura: **mínimo 1, máximo 3 itens por categoria por edição** (em `news[]` + `pillars[]` combinados).
- Se não houver notícia recente: usa evergreen clássico/importante, sem repetir URLs de edições anteriores.
- Não é garantido que **todo sub-tópico** de uma categoria apareça todo dia — isso é normal. O que importa é que a categoria como um todo tenha cobertura.
- Aparecem na sidebar listadas por chave.
- View: `cat:{chave}` agrega TODAS as notícias daquela categoria através das edições.

### Tópicos (`TOOLS` no código, `tool_key` no JSON)
Tecnologias ou temas **específicos** monitorados. A skill busca conteúdo recente para cada um — se não houver, pula.

- Cobertura mínima: **1 item obrigatório por tópico, todos os 37, sem exceção**.
- Se não encontrar conteúdo fresco para um tópico: usar evergreen clássico/importante daquele tópico, sem repetir URLs de edições anteriores.
- Aparecem no rail (coluna direita) agrupados em 3 seções: Tópicos, Ferramentas, Linguagens.
- View: `tool:{chave}` exibe TODOS os itens daquele tópico através das edições (releases, news, tips, tutoriais, curiosidades — seções distintas).
- O campo JSON se chama `tool_key` (nome técnico histórico que permanece no schema). O conceito é "tópico".

### Quando me pedirem para adicionar algo novo — perguntar sempre

**Antes de adicionar qualquer coisa nova**, perguntar ao usuário:

> *"Isso deve ser um **Tópico** (monitorado diariamente, sempre aparece em `tools[]`, tem view dedicada no rail) ou deve ser coberto apenas como **sub-tópico de uma Categoria** existente (aparece em `news[]` quando houver notícia, sem compromisso diário)?"*

A diferença prática:
- **Tópico**: Git, Kafka, Kubernetes — tecnologias que queremos SEMPRE cobertas, com pelo menos 1 item/dia, com logo no rail e view dedicada.
- **Sub-tópico de categoria**: "SAML" dentro de `sec`, "TOGAF" dentro de `enterprise` — aparecem quando há notícia, sem cobertura obrigatória diária.

Se o usuário não souber a diferença, explique e aguarde a decisão antes de modificar qualquer arquivo.

---

## Tópicos monitorados (37, agrupados por grupo do rail)

Cada tópico tem `logo` (URL), `group` (grupo do rail), `category` (chave de `CAT` — para filtro editorial) e `kind` (tipo visual) no mapa `TOOLS` em `index.html`. O campo `tool_key` em cada item de `tools[]` do JSON diário garante o match exato. Se não houver conteúdo direto, conteúdo indireto do ecossistema é obrigatório (documentar em `description`).

> **Distinção importante**: `group` define onde o tópico aparece no rail (`subjects` = temas conceituais, `tools` = produtos de software, `lang` = linguagens). `category` define em qual filtro editorial o item de notícia aparece — são conceitos independentes.

| Grupo do rail | `tool_key` | Nome | Categoria editorial |
|---|---|---|---|
| **Tópicos** (alfabético) | | | |
| Tópicos | `cloudnative` | Cloud Native | `distarch` |
| Tópicos | `cve` | CVEs & Vulnerabilidades | `sec` |
| Tópicos | `ddd` | DDD | `design` |
| Tópicos | `microservices` | Microsserviços | `distarch` |
| Tópicos | `owasp` | OWASP | `sec` |
| **Ferramentas — AI & Produtividade** (alfabético) | | | |
| Ferramentas | `chatgpt` | ChatGPT | `ai` |
| Ferramentas | `claudecode` | Claude Code | `ai` |
| Ferramentas | `cursor` | Cursor IDE | `ai` |
| Ferramentas | `intellij` | IntelliJ IDEA | `backend` |
| Ferramentas | `postman` | Postman | `integ` |
| Ferramentas | `vscode` | VS Code | `ai` |
| Ferramentas | `warp` | Warp Terminal | `ai` |
| **Ferramentas — DevOps & Infra** (alfabético) | | | |
| Ferramentas | `argocd` | Argo CD | `devops` |
| Ferramentas | `docker` | Docker | `devops` |
| Ferramentas | `ghactions` | GitHub Actions | `devops` |
| Ferramentas | `git` | Git | `devops` |
| Ferramentas | `github` | GitHub | `devops` |
| Ferramentas | `helm` | Helm | `devops` |
| Ferramentas | `istio` | Istio | `devops` |
| Ferramentas | `kubernetes` | Kubernetes | `devops` |
| Ferramentas | `terraform` | Terraform | `devops` |
| **Ferramentas — Dados & Integração** (alfabético) | | | |
| Ferramentas | `databricks` | Databricks | `data` |
| Ferramentas | `kafka` | Apache Kafka | `integ` |
| Ferramentas | `mysql` | MySQL | `data` |
| Ferramentas | `openapi` | OpenAPI | `integ` |
| Ferramentas | `postgres` | PostgreSQL | `data` |
| Ferramentas | `redis` | Redis | `data` |
| **Ferramentas — Backend, Design, Seg & Obs** (alfabético) | | | |
| Ferramentas | `dynatrace` | Dynatrace | `obs` |
| Ferramentas | `grafana` | Grafana | `obs` |
| Ferramentas | `gradle` | Gradle | `backend` |
| Ferramentas | `keycloak` | Keycloak | `sec` |
| Ferramentas | `maven` | Apache Maven | `backend` |
| Ferramentas | `springboot` | Spring Boot | `backend` |
| Ferramentas | `structurizr` | Structurizr | `design` |
| **Linguagens** (alfabético) | | | |
| Linguagens | `java` | Java & JVM | `backend` |
| Linguagens | `javascript` | JavaScript / TS | `backend` |
| Linguagens | `python` | Python | `backend` |

**Tópicos legados** (presentes em edições anteriores, ainda navegáveis via deep link, mas não monitorados ativamente): `teams`, `notion`, `c4`, `cloudwatch`, `lambda`, `dynamodb`, `apigateway`, `sns`, `sqs`, `togaf`, `dbeaver`, `mongocompass`, `whimsical`, `plantuml`.

## O Que Atualizar Quando

> **Princípio universal**: antes de adicionar QUALQUER item novo (categoria, tópico, linguagem), **pesquise os melhores sites sobre o tema** (ver protocolo abaixo). Só depois, atualize TODOS os arquivos listados.
>
> **Fonte de verdade**: este `CLAUDE.md`. Se mudar qualquer regra editorial (cobertura, taxonomia, schema), sincronize os **3 documentos humanos** no mesmo commit: `README.md`, `CLAUDE.md`, `skills/csr-news-daily.md`. Divergência entre eles é bug — sempre rodar `python3 scripts/validate_editions.py` antes do commit.

### Mapa: o que aparece na tela e de onde vem

Toda mudança em categorias, tópicos, linguagens ou links de pesquisa impacta múltiplos lugares ao mesmo tempo. Use este mapa para não esquecer nenhum:

| O que aparece na tela | Onde fica no código | O que muda na skill |
|---|---|---|
| **Sidebar esquerda — lista de categorias** | `CAT` em `index.html` (chave, label, ícone emoji) | Seção "Categorias e Queries" + fontes |
| **Sidebar — cor de destaque ao filtrar** | `--cat-{chave}` em `:root` e `[data-theme="light"]` de `index.html` | — |
| **Sidebar — ícone SVG de categoria** | `CAT_ICONS` em `index.html` (path SVG) | — |
| **Rail direito — grupos Tópicos/Ferramentas/Linguagens** | `TOOL_GROUPS` e array `TOOLS` em `index.html` | Seção "TÓPICOS MONITORADOS" + conteúdo indireto |
| **Rail — logo de tópico/ferramenta** | campo `logo` na entrada `TOOLS` de `index.html` | — |
| **About page — "N categorias"** | hardcoded em `index.html` (`ab-stat-n`) | Contagens em MODO NORMAL e PRIMEIRA EXECUÇÃO |
| **About page — "N tópicos"** | hardcoded em `index.html` (`ab-stat-n`) | Idem |
| **Prompt-bar sticky (cor por contexto)** | calculado via `CAT[key]` e `TOOLS[key]` em `index.html` | — |
| **Filtro `cat:{chave}` e `tool:{chave}` via URL** | `CAT` e `TOOLS` em `index.html` | — |
| **Feed diário (home)** | JSON `data/YYYY-MM-DD.json` gerado pela skill | Queries, fontes, cobertura obrigatória |
| **README — lista de categorias e tópicos** | `README.md` (seções "Categorias cobertas" e "Assuntos fixos") | — |
| **Validador** | `CATEGORIES_V{n}` e `TOOL_KEYS_V{n}` em `validate_editions.py` | — |

**Regra prática**: se mudar qualquer coisa nesta tabela — seja na skill, seja no JSON, seja na taxonomia — percorra a coluna "Onde fica no código" e atualize todos os campos afetados em `index.html` e nos demais arquivos. Não existe mudança "só na skill" que não tenha reflexo visual.

---

### Classificar uma adição nova — Claude deve fazer isso PROATIVAMENTE

**Toda vez que o usuário mencionar algo novo que possa ser adicionado ao projeto** (uma ferramenta, tecnologia, tema, linguagem, blog, framework — qualquer coisa), Claude deve **imediatamente**:

1. **Propor a classificação** explicando as diferenças e recomendando qual se aplica:

   | Tipo | Compromisso | Onde aparece | Critério principal |
   |---|---|---|---|
   | **Categoria** | 1 item/dia obrigatório no feed, aparece na sidebar esquerda com cor e ícone | `CAT`, CSS var, `CAT_ICONS`, sidebar, About page | Tema amplo com ≥1 notícia/semana de múltiplas fontes; escopo ortogonal às 13 categorias existentes |
   | **Tópico** | 1 item/dia obrigatório em `tools[]`, aparece no rail direito com logo e view dedicada | `TOOLS`, rail, About page | Tecnologia/produto com changelog próprio, ≥1 release/mês, relevante para arquiteto |
   | **Linguagem** | Igual ao Tópico + dados de versão em `data/{lang}-versions/` | Idem + seção dedicada de fontes na skill | Linguagem de programação com releases e ecossistema próprios |
   | **Sub-categoria / tag** | Aparece em `tags[]` quando há notícia — sem compromisso diário | `tags[]` em `news[]` | Sub-tópico de categoria existente (ex: "SAML" dentro de `sec`); não precisa de cobertura diária garantida |

2. **Pesquisar as melhores fontes** sobre o tema (ver protocolo "Pesquisar fontes antes de adicionar" abaixo) antes de qualquer implementação.

3. **Aguardar confirmação** do usuário antes de modificar qualquer arquivo.

Nunca implemente silenciosamente sem passar pela classificação. Se o usuário não souber a diferença, explique e apresente os impactos de cada opção.

---

### Alterar o design visual
- Edite `index.html` (CSS + HTML no mesmo arquivo)
- Dados JSON não precisam mudar
- Se adicionar/renomear classes CSS de categoria, atualize `CAT` e `CAT_ICONS` no JS

### Pesquisar fontes antes de adicionar (OBRIGATÓRIO)

**Toda vez que um novo Tópico, Categoria ou Linguagem for adicionado**, ANTES de implementar, faça uma pesquisa real (WebSearch) para identificar as melhores fontes:

1. `"best [tema] blogs" OR "top [tema] resources" site:reddit.com`
2. `"[tema] newsletter" most popular 2024 OR 2025`
3. `"[tema] blog" developers OR architects`

Com os resultados, identifique:
- O **changelog/blog oficial** (release notes, announcements do vendor)
- O **blog editorial de referência** (#1 mais citado pela comunidade)
- **Sub-tópicos do tema** e os melhores sites para cada um

Adicione essas fontes na seção correspondente da skill (`skills/csr-news-daily.md`):
- **Categorias**: bloco de sub-tópicos com sites preferidos em "Fontes de alta reputação"
- **Tópicos/Ferramentas**: tabela de changelogs (seção "TÓPICOS MONITORADOS") + queries específicas (seção "CATEGORIAS E QUERIES")
- **Linguagens**: seção "Linguagens de Programação — fontes por tópico" + queries dedicadas

**Os sites são sugestões e preferências** — se não encontrar conteúdo nos sites preferidos, pesquise em outros. Qualidade sempre prevalece sobre a fonte. Fontes genéricas (Medium sem autor, "top 10 tools") nunca como fontes primárias.

### Adicionar/remover uma categoria

> **PESQUISA DE FONTES ANTES** — ver protocolo acima.

1. Consulte as **regras de classificação** abaixo antes de decidir
2. `index.html`: adicione chave em `CAT`, SVG path em `CAT_ICONS`, variável `--cat-{chave}` em `:root` e `[data-theme="light"]`
3. `index.html` **About page**: atualize o stat hardcoded `"N categorias"` (linha com `ab-stat-n`)
4. `README.md`: atualize a lista de categorias cobertas (seção "Categorias cobertas")
5. `CLAUDE.md`: atualize a tabela de categorias (esta seção)
6. `skills/csr-news-daily.md`:
   - Seção "Categorias e Queries" (novo bloco de queries)
   - Fontes na seção "Fontes de alta reputação" (bloco por categoria)
   - **Grupo FASE correto** do FLUXO DE EXECUÇÃO — FASE 3A (`sec`/`ai`/`aws`/`devops`), FASE 3B (`obs`/`data`/`integ`/`backend`/`testing`) ou FASE 3C (`design`/`enterprise`/`distarch`/`fintech`): adicione/remova a categoria na linha do grupo correto
   - Lista literal das 13 categorias em `news[]` cobertura obrigatória (perto do FASE 3A/3B/3C)
   - Distribuição de quotes por categoria (protocolo MODO PRIMEIRA EXECUÇÃO)
7. `scripts/validate_editions.py`: adicione à constante `CATEGORIES_V{n}` e incremente `STRICT_FROM_V{n}` para a data da primeira edição com a nova taxonomia
8. Se **removida**: adicione à seção "Chaves legadas" em `CLAUDE.md` e ao `LEGACY_CAT_MAP` em `index.html` se houver edições antigas com a chave

### Adicionar/remover um Tópico

> **PESQUISA DE FONTES ANTES** — ver protocolo acima.

1. **Perguntar ao usuário** se é Tópico ou sub-tópico de categoria (ver seção "Conceito fundamental" acima)
2. `index.html`: adicione entrada no array `TOOLS` (com `aliases`, `kind`, `category`, `logo`, `group` = `subjects`/`tools`/`lang`)
3. `index.html` **About page**: atualize o stat hardcoded `"N tópicos"` (linha com `ab-stat-n`)
4. `README.md`: atualize a lista de assuntos fixos monitorados (seção "Assuntos fixos monitorados")
5. `CLAUDE.md`: atualize a tabela de tópicos monitorados (esta seção abaixo)
6. `skills/csr-news-daily.md`:
   - Tabela de changelogs em "TÓPICOS MONITORADOS" com changelog oficial e fontes
   - Tabela de conteúdo indireto (seção "Conteúdo indireto" / "Ecossistema como fallback")
   - Distinção "Ferramentas com release" vs "Temas/domínios" (hierarquia de `kind` em FASE 5A)
   - **Grupo FASE correto** do FLUXO DE EXECUÇÃO — FASE 5A (Assuntos+AI: `cloudnative`/`cve`/`ddd`/`microservices`/`owasp`/`chatgpt`/`claudecode`/`cursor`/`intellij`/`postman`/`vscode`/`warp`), FASE 5B (DevOps), FASE 5C (Dados+Integ), FASE 5D (Backend+Obs+Seg+Design), FASE 5E (Linguagens): adicione/remova o tópico na linha do grupo correto
   - **4 locais** onde a lista de `tool_key` aparece: sanity check FASE 7, whitelist evergreen FASE 5A, schema `counts_by_tool`, Regras de Qualidade #14
   - Queries específicas em "CATEGORIAS E QUERIES DE PESQUISA"
7. `scripts/validate_editions.py`: adicione a `TOOL_KEYS_V{n}`
8. Se **removido**: mova para "Tópicos legados" na tabela abaixo

### Adicionar uma Linguagem de Programação

> **PESQUISA DE FONTES ANTES** — ver protocolo acima. Linguagens têm mais peso: precisam de changelog oficial, blog de release, newsletter dedicada, tutoriais e fontes por sub-tópico (performance, web, async, tooling).

1. Todos os passos de "Adicionar Tópico" acima
2. `skills/csr-news-daily.md`: adicione seção dedicada em "Linguagens de Programação — fontes por tópico" com fontes top-tier
3. Se a linguagem tiver versioning relevante para arquitetos: criar `data/{lang}-versions/index.json` e `{lang}-{N}.json` (modelo: `data/java-versions/`)

### Como classificar uma adição (Tópico, Categoria ou tag)

**Sempre perguntar ao usuário qual dos três tipos é antes de implementar.**

1. **Tópico** → array `TOOLS` + campo `tool_key` no JSON. Critérios: tem site/changelog próprio; produz conteúdo ≥1×/mês; relevante para arquiteto; encaixa em uma categoria. Compromisso: skill busca conteúdo TODOS OS DIAS.
2. **Categoria** (`CAT`) → tema editorial amplo. Critérios: produz ≥1 notícia/semana de múltiplas fontes; escopo ortogonal às existentes. Se for recorte de categoria existente (ex.: "SAML" dentro de `sec`), vira **tag**, não categoria.
3. **Tag** → `tags[]` em `news[]`. Tópicos transversais que aparecem esporadicamente. Não muda taxonomia.
4. **Remoção**: Tópico/categoria que precisa de >3 `curiosity`/mês para cobertura mínima → avaliar substituição.
5. **Em dúvida, perguntar** antes de implementar — mudanças têm custo (validator, skill, CSS vars, cutoff).

### Alterar queries de pesquisa
- Edite em `skills/csr-news-daily.md` na seção "Categorias e Queries"

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
- `localStorage` usa prefixo `csrn-` (CsR News)

## Deploy

Push para `main` → GitHub Actions (`pages.yml`) gera `feed.xml` e deploya.
URL: `https://cesarschutz.github.io/noticias-dev-arq/`
RSS: `https://cesarschutz.github.io/noticias-dev-arq/feed.xml`

Workflow com `paths` filter: mudanças só em `.md` não disparam redeploy.
