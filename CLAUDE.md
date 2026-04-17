# DevPulse — Arquivo Diário do Arquiteto

Arquivo de notícias técnicas diárias para arquitetos de software/solução, hospedado no GitHub Pages.

## Arquitetura

O projeto separa **dados** (JSON) de **apresentação** (template HTML único):

```
index.html → fetch('data/editions.json')  (índice com counts)
           → fetch('data/{ISO}.json')     (edição por data, sob demanda)
```

O `index.html` é uma SPA single-file (CSS + JS vanilla embutidos) no estilo **"console ops"** — terminal moderno com paleta marine/cyan/violet/amber. Três colunas:
- **Sidebar esquerda (cockpit)**: nav-row (prev/next + data com badge HOJE), 2 botões inline (ler depois, tema), categorias + ferramentas com contadores X/Y (X=dia atual, Y=total do arquivo).
- **Main (feed)**: sem hero em home — começa direto nos destaques. Prompt-bar sticky no topo (`csr@console:~/editions/DATA $ cat DATA.json [HOJE]`) muda de cor por contexto (home=amber, cat=cor da categoria, tool=cor do tipo). Cards clicáveis abrem URL em nova aba.
- **Rail (telemetria)**: quote do dia (rotação a cada 25s, 5 por edição), radar de categorias, timeline de edições.

Topbar: logo + status terminal-style à direita (clock, atualizado há Xh, N saved, `?` atalhos). Sem statusbar inferior. Sem frameworks, sem build step.

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
2. Pesquisa notícias via WebSearch em 10 categorias + 30 ferramentas + HN + blogs eng + pulso BR
3. Monta `data/{date}.json` com sanity checks (URLs específicas, dedup com últimas 7 edições, diversidade pillars)
4. Atualiza `data/editions.json` com a nova entrada (incluindo `counts_by_category` e `counts_by_tool`)
5. LaunchAgent local detecta mudança em `data/` e roda `push.sh` (retry + log rotativo em `~/Library/Logs/devpulse-push.log`)
6. GitHub Actions (`pages.yml`) gera `feed.xml` → deploya no GitHub Pages
7. GitHub Actions (`validate.yml`) valida JSON em PRs

## Views da SPA

- **home** (default): edição do dia mais recente — hero, pillars (3 cards Java/AWS/DistArch), feed, ferramentas
- **cat:{chave}**: agregado de todas as notícias de uma categoria através das edições
- **tool:{chave}**: feed completo da ferramenta — releases, notícias, dicas, tutoriais e curiosidades (seções distintas)
- **deep link**: `?d=YYYY-MM-DD&u=<hash>` abre direto uma notícia

### Lazy-load inteligente
Ao filtrar por categoria/ferramenta, a SPA usa `counts_by_category` / `counts_by_tool` do `editions.json` para **só baixar** as edições que têm conteúdo daquele filtro. Um loader visual fica no topo do main durante o fetch paralelo. Em background (após boot), todas as edições são pré-aquecidas em cache para busca global.

## Interações

- **Deep link**: URL com `?d=YYYY-MM-DD` preserva a edição aberta. Copiar link de um card usa botão dedicado (copia URL da matéria).
- **Prev/Next edições**: botões `◀` `▶` na sidebar (ou atalhos `P`/`N`) navegam entre edições adjacentes. Em view cat/tool, escondem.
- **Botão "→ hoje"**: aparece na sidebar quando a edição aberta não é a de hoje.
- **Filtro**: toolbar tem chip `urgent` (atalho `U`).
- **Ler depois**: bookmark via `localStorage` (`dpco-read-later`). Modal com ordenação (saved/date/category/urgent), export JSON e clear.
- **Tema dark/light**: toggle na sidebar ou atalho `T`.
- **Modo cards/list**: atalhos `1` (grid multi-coluna) / `2` (lista 1 coluna larga). Ambos com summary completo.
- **Teclado**: `J/K` navegam cards, `O`/`Enter` abrem URL em nova aba, `H` volta pra home, `?` abre atalhos, `ESC` fecha modal.
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

Item de `tools[]`: obrigatórios `tool_key`, `name`, `kind`, `headline`, `source`, `url`. `version` obrigatório quando `kind === "release"`. Opcionais: `icon`, `description`, `published_at`, `image`, `tags`. `kind` ∈ `{release, news, tip, tutorial, curiosity}`.

Array `quotes[]` (5 itens/dia): `text`, `author`, `related_to` (obrigatórios), `context` (opcional). `related_to` ∈ `"cat:<chave>"`, `"tool:<chave>"`, `"general"`.

Schema completo em `skills/devpulse-daily.md`. Validação em `scripts/validate_editions.py`:
- Edições ≥ `2026-04-18` são **strict v1** (tools com `kind`/`tool_key`, imagens, quotes).
- Edições ≥ `2026-04-20` são **strict v2** (taxonomia nova — categorias, ferramentas v2, `pillars[]` com campo `pillar`).

## Pilares (`pillars[]`)

Os três pilares são os destaques fixos do topo de cada edição — um por tema principal:

| `pillar` | Tema | Cor | Ícone |
|---|---|---|---|
| `java` | Java & JVM | `#f89820` | ☕ |
| `aws` | AWS | `#FF9900` | 🔶 |
| `distarch` | Arquitetura Distribuída | `#818cf8` | 🕸 |

Cada pilar substitui o antigo `top3` — visual diferenciado no topo com borda colorida espessa e badge de identificação. Retrocompat: edições antigas com `top3` são renderizadas normalmente.

## Categorias (taxonomia v2 — desde 2026-04-20)

| Chave | CSS Var | Label | Ícone | Escopo |
|-------|---------|-------|-------|--------|
| sec | `--cat-sec` | Segurança & IAM | 🔐 | CVEs, zero-days, Keycloak, Auth0, OIDC, zero-trust |
| ai | `--cat-ai` | IA & LLMs | 🤖 | Modelos, agents, RAG, MCP, AI coding tools |
| aws | `--cat-aws` | AWS | 🔶 | Todos os serviços AWS — Lambda, DynamoDB, SNS, SQS, CloudWatch, etc. |
| devops | `--cat-devops` | DevOps & Plataformas | ⚙️ | K8s, Docker, GitOps, platform engineering, SRE |
| obs | `--cat-obs` | Observabilidade | 📈 | Tracing, logging, metrics, OpenTelemetry, Dynatrace, Datadog |
| data | `--cat-data` | Dados & Streaming | 🗄️ | DB relacional/NoSQL, warehouse, lakehouse, streaming, CDC |
| integ | `--cat-integ` | Integração & Eventos | 🔌 | APIs (REST/GraphQL/gRPC), Kafka, EDA, iPaaS, OpenAPI, schemas |
| backend | `--cat-backend` | Backend & Runtimes | 🔧 | Java/Spring, Go, Node, Rust, JVM, Gradle, Maven, frameworks server-side |
| arqsw | `--cat-arqsw` | Arq. Software | 🏛️ | DDD, padrões, C4, Clean/Hex, microsserviços, ADRs, Whimsical, PlantUML |
| arqsol | `--cat-arqsol` | Arq. Solução | 🗺️ | TOGAF, integração enterprise, landing zones, reference architectures |

**Chaves legadas** (presentes em edições anteriores a 2026-04-20, mapeadas em runtime):
- `cloud` → `aws`, `db` → `data`, `lang` → `backend`, `frontend` → home (removida)

## Ferramentas monitoradas (26, agrupadas por categoria)

Cada ferramenta tem `logo` (URL), `category` (chave de `CAT`) e `kind` (tipo visual) no mapa `TOOLS` em `index.html`. O campo `tool_key` em cada item de `tools[]` do JSON diário garante match exato. Se não houver conteúdo direto, conteúdo indireto do ecossistema da ferramenta é permitido (documentar em `description`).

| Categoria | `tool_key` | Nome |
|---|---|---|
| `arqsw` | `structurizr` | Structurizr |
| `arqsw` | `whimsical` | Whimsical |
| `arqsw` | `plantuml` | PlantUML |
| `ai` | `cursor` | Cursor IDE |
| `ai` | `claudecode` | Claude Code |
| `ai` | `chatgpt` | ChatGPT |
| `ai` | `vscode` | VS Code |
| `ai` | `warp` | Warp Terminal |
| `sec` | `keycloak` | Keycloak |
| `sec` | `owasp` | OWASP |
| `sec` | `snyk` | Snyk |
| `devops` | `docker` | Docker Desktop |
| `devops` | `kubernetes` | Kubernetes |
| `obs` | `dynatrace` | Dynatrace |
| `data` | `postgres` | PostgreSQL |
| `data` | `mysql` | MySQL |
| `data` | `mongocompass` | MongoDB Compass |
| `data` | `dbeaver` | DBeaver |
| `data` | `databricks` | Databricks |
| `integ` | `kafka` | Apache Kafka |
| `integ` | `postman` | Postman |
| `integ` | `openapi` | OpenAPI |
| `backend` | `intellij` | IntelliJ IDEA |
| `backend` | `springboot` | Spring Boot |
| `backend` | `gradle` | Gradle |
| `backend` | `maven` | Apache Maven |

**Ferramentas legadas** (presentes em edições anteriores, ainda navegáveis via deep link): `teams`, `notion`, `c4`, `terraform`, `ghactions`, `grafana`, `cloudwatch`, `lambda`, `dynamodb`, `apigateway`, `sns`, `sqs`, `togaf`.

## O Que Atualizar Quando

### Alterar o design visual
- Edite `index.html` (CSS + HTML no mesmo arquivo)
- Dados JSON não precisam mudar
- Se adicionar/renomear classes CSS de categoria, atualize o mapa `CAT` no JS

### Adicionar/remover uma categoria
1. Consulte as **regras de classificação** abaixo antes de decidir
2. Adicione/remova a chave em `CAT` no JS de `index.html`
3. Adicione/remova variável `--cat-{chave}` em `:root` e `[data-theme="light"]`
4. Atualize a tabela em `skills/devpulse-daily.md` (seção "Categorias e Queries"), neste CLAUDE.md e em `scripts/validate_editions.py` (`CATEGORIES_V2`)
5. Atualize `STRICT_FROM_V2` no validator para a data da primeira edição com a nova taxonomia

### Adicionar/remover uma ferramenta monitorada
1. Consulte as **regras de classificação** abaixo antes de decidir
2. Adicione/remova entrada no array `TOOLS` do JS em `index.html` (com `aliases`, `kind`, `category`, `logo`)
3. Atualize a tabela em `skills/devpulse-daily.md` (seção "FERRAMENTAS MONITORADAS")
4. Atualize a lista de chaves em `skills/devpulse-daily.md` (counts_by_tool + sanity checks)
5. Atualize `TOOL_KEYS_V2` em `scripts/validate_editions.py`

### Como classificar uma adição (ferramenta, categoria ou tag)
1. **Tem site + changelog/releases?** → candidata a `TOOLS`. Deve: ter logo estável; publicar release/news ≥1×/mês; ser relevante para **arquiteto de software/solução** (modelagem, decisão técnica, integração, operação) — chat, e-mail e gestão de tarefas ficam fora; encaixar em **uma** categoria com campo `category` obrigatório.
2. **Tema editorial coerente, não uma ferramenta?** → candidata a `CAT`. Deve: produzir ≥1 notícia/semana; ter fontes reconhecíveis; ter escopo ortogonal às existentes. Se for recorte de categoria existente, vira **tag**.
3. **Genérico ou transversal?** → **tag** em `tags[]`, sem alterar taxonomia.
4. **Remoção**: categoria/ferramenta que precisa de >3 `curiosity`/mês para cumprir cobertura mínima está em zona de morte.
5. **Em dúvida, perguntar** antes de alterar — mudanças têm custo (validator, skill, CSS vars, logos, cutoff).

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
