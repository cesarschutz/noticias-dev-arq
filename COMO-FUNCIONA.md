# Como funciona o CsR News

> Documento em linguagem acessível — escrito para pessoas que não são desenvolvedoras mas querem entender o que o sistema faz, de onde vêm as notícias e por que existem as categorias que existem.

---

## 1. O que é o CsR News

**CsR News** é um "jornal técnico diário" escrito por uma Inteligência Artificial. Todo dia de manhã, às 6h da manhã (horário de Brasília), uma IA lê dezenas de sites especializados do mundo da tecnologia, filtra o que é relevante para **arquitetos de software e solução sênior**, e organiza tudo em uma página web fácil de navegar.

Pense num "clipping matinal personalizado" — só que em vez de um editor humano escolher as matérias, quem faz isso é uma IA seguindo regras editoriais bem definidas. O resultado fica publicado em: [cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/).

---

## 2. O que a IA faz todo dia (em 5 passos)

1. **Abre o arquivo do dia anterior** para saber o que já foi noticiado e não repetir.
2. **Pesquisa** em múltiplas fontes confiáveis (blogs oficiais, jornalismo técnico, comunidades técnicas) — cerca de 100-200 buscas diferentes.
3. **Filtra** o que é relevante: CVEs críticos, releases importantes, artigos profundos — deixando de lado clickbait e "top 10 tools".
4. **Classifica** cada notícia por categoria (ex: Segurança, Cloud, IA) e calcula um "score" de importância.
5. **Monta a edição** do dia com até 30 notícias, 10+ releases de ferramentas, 3 destaques (highlights) e 5 citações de autores.

O resultado é publicado automaticamente no site, sem intervenção humana.

---

## 3. De onde vêm as notícias (protocolo de pesquisa)

A IA segue um protocolo rigoroso:

### Níveis de confiança das fontes

| Nível | O que é | Exemplos |
|---|---|---|
| **Tier 1 — Oficial** | Blog/changelog dos fabricantes e bases oficiais de CVEs | `kubernetes.io/blog`, `aws.amazon.com/new`, `anthropic.com/news`, `nvd.nist.gov`, `cisa.gov` |
| **Tier 2 — Autoridade editorial** | Jornalismo técnico reconhecido, autores renomados, newsletters | InfoQ, The New Stack, Martin Fowler, Simon Willison, ByteByteGo, Grafana Blog |
| **Tier 3 — Comunidade** | Engineering blogs de grandes empresas, fóruns técnicos | Netflix TechBlog, Cloudflare Blog, Uber Engineering, GitHub Trending, Reddit r/devops |
| **Evitar** | Marketing disfarçado, "top 10 lists", Medium sem autor | DZone, posts genéricos |

### Sinal social

A IA também monitora o que está pegando nas comunidades:

- **Hacker News** (`news.ycombinator.com`): notícias com 150+ pontos ou 50+ comentários viram candidatas.
- **Lobste.rs** (`lobste.rs`): top 10 do dia, mais técnico que HN.
- **GitHub Trending**: os repositórios em alta do dia (Go, Rust, Python, TypeScript, Java).

### Como evita repetir a mesma notícia

Antes de adicionar qualquer item, a IA verifica **as URLs e manchetes das últimas 7 edições**. Se algo já foi publicado recentemente, é descartado. Se a manchete é muito parecida (similaridade ≥85%), também é descartado. Isso evita você ler a mesma história repetida.

### Como garante que o link funciona

Para os 3 destaques do dia e todas as notícias críticas, a IA faz uma verificação extra: abre o link e confere se a página realmente existe e é sobre o que foi anunciado. Se cair em página de erro, tenta outra fonte antes de descartar.

### Brasil no radar

Além de fontes globais, a IA também lê blogs de engenharia brasileiros: Nubank Tech, iFood Tech, Mercado Livre Tech, Stone Engineering, PicPay Tech, C6 Bank, Inter, Zup Innovation, Globo Engineering, Olist Tech, TabNews. Para fintech, acompanha também Banco Central do Brasil (Pix, Open Finance, DREX) e sites de cooperativismo de crédito.

---

## 4. Catálogo de categorias (16)

Categorias são os "grandes temas" — cada notícia pertence a uma.

### Transversais (tocam tudo)

- **🤖 IA & LLMs (`ai`)** — modelos fundacionais (GPT, Claude, Gemini, Llama), pesquisa em IA, releases de fundação. *Por que existe*: IA é o tema mais transformador da década; qualquer arquiteto precisa acompanhar.
- **🧠 AIOps & Agents (`aiops`)** — como usar IA em produção: agentes (MCP, LangGraph), RAG (Retrieval-Augmented Generation), observabilidade de LLMs (Langfuse), AI Coding (Cursor, Claude Code), guardrails. *Por que existe*: a engenharia de aplicações com IA virou uma disciplina separada da pesquisa em modelos — com ferramentas, padrões e riscos próprios.
- **🔐 Segurança & IAM (`sec`)** — CVEs (vulnerabilidades críticas), Zero Trust, identidade (OIDC/SAML), supply chain (SBOM, SLSA), AI Security. *Por que existe*: segurança é preocupação diária do arquiteto; CVEs não esperam.

### Plataforma & Infraestrutura

- **☁️ Cloud (`cloud`)** — AWS, Azure, Google Cloud, CDN, edge delivery, networking. *Por que existe*: quase tudo hoje roda na nuvem; acompanhar serviços e padrões é essencial.
- **⚙️ DevOps & Plataformas (`devops`)** — Kubernetes, GitOps, CI/CD, IaC (Terraform), Backstage, HTTP/3, proxies (nginx, envoy). *Por que existe*: a "plumbing" que mantém tudo rodando em produção.
- **📈 Observabilidade & SRE (`obs`)** — tracing (OpenTelemetry), métricas, logs, SLO/SLI, incidentes, eBPF. *Por que existe*: você não conserta o que não consegue ver.

### Desenvolvimento

- **🔧 Backend & Runtimes (`backend`)** — Java/Spring, Go, Rust, Node.js, WebAssembly (Wasmtime), performance. *Por que existe*: o coração das aplicações.
- **🗄️ Dados & Streaming (`data`)** — bancos (PostgreSQL, Redis), streaming (Kafka), lakehouse (Databricks, dbt), vector DBs (pgvector). *Por que existe*: dados são o ativo mais valioso; arquitetura de dados é estratégica.
- **🔌 Integração & Eventos (`integ`)** — APIs (REST, GraphQL, gRPC), eventos (EDA, AsyncAPI), webhooks, idempotência. *Por que existe*: sistemas distribuídos só funcionam se se integram bem.
- **⚗️ Testes & Qualidade (`testing`)** — TDD, contract testing, chaos engineering, load testing (k6), frameworks (Playwright, pytest). *Por que existe*: qualidade não é opcional; arquitetos erram muito aqui.
- **🎨 Frontend & Web (`frontend`)** — React/Vue/Svelte, Next.js, Tailwind, Core Web Vitals, edge rendering, mobile cross-platform. *Por que existe*: a ponte com o usuário final; arquitetos full-stack precisam acompanhar.

### Arquitetura

- **🏛️ Design & Padrões (`design`)** — DDD, Clean Architecture, C4 Model, ADRs, refactoring, docs como código. *Por que existe*: bons padrões reduzem dívida técnica.
- **🕸 Sistemas Distribuídos (`distarch`)** — microsserviços, service mesh (Istio), saga/CQRS/event sourcing, consistency models, post-mortems. *Por que existe*: a complexidade real mora nos sistemas distribuídos.
- **🗺️ Arquitetura Corporativa (`enterprise`)** — Team Topologies, Platform Engineering, FinOps, DORA/SPACE, governança. *Por que existe*: estratégia técnica de alto nível, como organizar times e orçamento.

### Fundação

- **🧱 Fundamentos de Computação (`fundamentals`)** — sistemas operacionais, redes (TCP/IP, DNS), algoritmos, concorrência, performance de hardware. *Por que existe*: "moda vem e vai; fundamentos ficam". **Na sexta-feira** essa categoria ganha destaque extra: 2-3 itens obrigatórios, sendo ao menos 1 artigo clássico de autor canônico (Martin Fowler, Martin Kleppmann, Sam Newman, Julia Evans, Brendan Gregg, Dan Luu).

### Domínio

- **💳 Fintech & Pagamentos (`fintech`)** — cartões (Visa, Mastercard, Elo), cooperativas de crédito (Unicred, Sicoob, Sicredi), Pix, Open Finance, DREX, PCI DSS. *Por que existe*: domínio de interesse do autor (arquiteto que trabalha em fintech).

---

## 5. O que são subcategorias

Categorias são amplas (ex: "Segurança"). Dentro de cada uma há **subcategorias** — recortes mais específicos que guiam a pesquisa da IA mas **não aparecem como filtros na tela**. Por exemplo, dentro de `sec` existem: CVEs, OWASP, Zero Trust, Supply Chain, AI Security, Secrets Management.

Essas subcategorias viram **tags** nos cartões (`tags[]`) — pequenas etiquetas que você vê junto com a notícia, indicando as tecnologias citadas.

---

## 6. Catálogo de ferramentas monitoradas (27)

Ferramentas são produtos técnicos com lançamentos regulares (releases, changelogs). Cada uma tem uma página dedicada no site com o histórico de updates.

### AI & IDEs (4)
- **Claude Code** — assistente de programação da Anthropic no terminal.
- **Cursor IDE** — editor de código com IA integrada.
- **IntelliJ IDEA** — IDE Java/Kotlin da JetBrains.
- **VS Code** — editor da Microsoft, padrão de mercado.

### Git & CI/CD (3)
- **Argo CD** — GitOps para Kubernetes.
- **GitHub Actions** — CI/CD do GitHub.
- **GitHub** — plataforma de código (inclui Copilot, Advanced Security).

### Containers & IaC (3)
- **Docker** — padrão de containers.
- **Kubernetes** — orquestração de containers.
- **Terraform** — infraestrutura como código (HashiCorp).

### Mesh, Proxies & Edge (3)
- **Istio** — service mesh.
- **Nginx** — web server e reverse proxy clássico.
- **Cloudflare** — CDN, DNS, Workers, Zero Trust.

### Dados & Streaming (4)
- **Databricks** — lakehouse de dados + IA.
- **PostgreSQL** — banco relacional open-source líder (inclui extensão pgvector para RAG).
- **Redis** — cache in-memory.
- **Apache Kafka** — streaming distribuído.

### Observabilidade & Segurança (4)
- **Dynatrace** — APM enterprise com IA (Davis).
- **Datadog** — observabilidade SaaS unificada.
- **Keycloak** — IAM open-source.
- **Vault** — secrets management (HashiCorp).

### Backend & Build (3)
- **Gradle** — build para JVM.
- **Apache Maven** — build Java clássico.
- **Spring Boot** (+ Spring Cloud) — framework Java líder.

### Design & Docs-as-code (3)
- **Structurizr** — arquitetura como código (C4 + DSL + integração MCP).
- **PlantUML** — diagramas UML como código.
- **Mermaid** — diagramas em Markdown (renderiza nativamente no GitHub).

### Tecnologias cobertas como sub-tópico (sem ferramenta dedicada)

Algumas tecnologias relevantes aparecem como **sub-tópicos** das categorias — a IA busca notícias sobre elas normalmente, mas elas não têm página dedicada no site. Se houver notícia, ela aparece na categoria correspondente, com o nome da tecnologia nas tags do cartão.

- **DevOps**: Backstage, Helm, OpenTofu, Envoy
- **AIOps & Agents**: MCP (Model Context Protocol), Ollama, Langfuse, LangGraph
- **Observabilidade**: OpenTelemetry, Prometheus, Grafana
- **Segurança**: Trivy
- **Dados**: pgvector, dbt
- **Sist. Distribuídos**: Temporal
- **Testes**: k6, Playwright
- **Frontend**: Next.js, Vite, Bun, Biome
- **Backend**: Wasmtime

**Nota sobre rotação**: nem todas as 27 ferramentas aparecem todo dia. A IA escolhe **pelo menos 10 por dia** priorizando aquelas que tiveram releases ou notícias reais nos últimos 3-7 dias. Se sobrar slot, completa com tutoriais ou deep-dives de ferramentas que não apareceram nas últimas 7 edições — rotação para variar a cobertura.

---

## 7. Linguagens (3)

Linguagens funcionam como ferramentas, mas são destacadas à parte:

- **☕ Java & JVM** — Spring, virtual threads, GraalVM, Project Loom/Valhalla.
- **🟨 JavaScript / TypeScript** — Node.js, Deno, Bun, TypeScript, TC39 proposals.
- **🐍 Python** — CPython, PEPs, FastAPI, uv, async, typing.

Essas 3 são foco pessoal do autor — outras linguagens (Go, Rust, C#, Kotlin, Scala) aparecem como notícia em `backend` quando há algo relevante, sem seção dedicada.

---

## 8. Diferenças entre os conceitos

| Conceito | O que é | Compromisso da IA | Aparece como |
|---|---|---|---|
| **Categoria** (16) | Tema editorial amplo | Cobertura flexível — pode ter 0 itens em dias calmos. Total mínimo: 15 itens/dia em toda edição. | Cor, ícone, filtro na sidebar esquerda |
| **Subcategoria** | Recorte específico dentro de uma categoria | Só aparece quando há notícia, como tag | Pequenas etiquetas no cartão (tags) |
| **Linguagem** (3) | Java/JS/Python, com releases próprios | Entra no pool de rotação diária de ferramentas | Logo no rail direito, view dedicada |
| **Ferramenta** (27) | Produto com changelog identificável | Rotação dinâmica — mínimo 10 ferramentas/dia | Logo no rail direito, view dedicada |

**Teste rápido para distinguir ferramenta de subcategoria**: *"Tem site de release notes que posso colar a URL agora?"* — se sim, é ferramenta; se não, é subcategoria.

---

## 9. Como usar a interface

### Página principal (home)

- **Topo**: logo + relógio + botão "ler depois" + atalhos (`?`).
- **Sidebar esquerda**: navegação de edições (calendário), tema claro/escuro, ler depois, categorias, ferramentas.
- **Centro (feed)**: notícias do dia agrupadas por categoria, com os 3 highlights no topo.
- **Rail direita**: frase do dia (rotaciona a cada 25 segundos), radar de categorias, timeline de edições.

### Atalhos de teclado

- `T` — alterna tema claro/escuro
- `1` — modo cartões (grid multi-coluna)
- `2` — modo lista (uma coluna, mais texto)
- `U` — filtro "urgent" (só CVEs críticos, breaking changes)
- `P` / `N` — navegar edição anterior/próxima
- `ESC` — fecha modal

### Filtros

- Clicar em uma categoria na sidebar → vê **todas** as notícias daquela categoria em todas as edições.
- Clicar em uma ferramenta → vê **todas** as releases/news/tutoriais daquela ferramenta.
- Clicar em um CVE dentro de um cartão → abre o CVE no NVD.
- Copiar link de um cartão → copia a URL do artigo original.

### Deep link

URLs com `?d=YYYY-MM-DD` abrem direto uma edição específica. `?d=YYYY-MM-DD&u=<hash>` abre direto uma notícia. Útil para compartilhar.

### Ler depois

Clique no marcador de página num cartão → salva no navegador. Modal com ordenação (por data salva, categoria, urgência), export JSON, limpar tudo.

### Mobile

Abaixo de 720px de largura, a sidebar vira hamburger menu. Tudo responsivo.

---

## 10. Regras editoriais (o que a IA garante todo dia)

- **Mínimo 15 notícias/dia** no total; sem obrigatoriedade por categoria (dias calmos podem ter menos categorias representadas).
- **Mínimo 10 ferramentas/dia** via rotação dinâmica.
- **3 highlights** escolhidos pelo score explícito (release +3, convergência +2, sinal social +2, autoridade +1, impacto +1).
- **Sexta-feira** → `fundamentals` ganha 2-3 itens, sendo ≥1 clássico de autor canônico.
- **Todo item tem `why_it_matters`** — uma frase explicando por que importa para arquiteto sênior (diferencial v1).
- **Sem repetição**: nada que apareceu nas últimas 7 edições entra de novo.
- **Sem clickbait**: manchetes "top N", "N razões", "N ways" são rejeitadas.
- **Diversidade**: nenhum domínio aparece em mais de 3 itens por edição.
- **Consistência**: itens de segurança com `urgent:true` precisam ter `severity` definido.

---

## 11. Proteções de qualidade

- **Validação de links**: os 3 highlights, todos os releases e as 5 notícias top são verificadas individualmente — se o link cai em página 404 ou conteúdo diferente, é substituído antes de publicar.
- **Cascata de imagens**: cada cartão tenta carregar a imagem principal em 5 métodos diferentes (Microlink, og:image, oembed, favicon). Pelo menos o favicon do site sempre aparece — nunca cartão sem imagem.
- **Dedup de manchetes**: similaridade ≥85% com qualquer manchete das últimas 7 edições → descarta.
- **Score explícito**: decisões editoriais auditáveis — qualquer pessoa pode calcular por que um item virou highlight.
- **Checkpoints em disco**: a IA grava progresso em arquivo a cada etapa, evitando perda de trabalho se houver interrupção.

---

## 12. FAQ

**Por que não tem <minha tecnologia favorita>?**
Porque o foco é arquitetura de software/solução (Java, JVM, cloud, K8s, etc.). Tecnologias fora desse eixo (mobile nativo, gamedev, blockchain, DevOps embarcado) podem aparecer como notícia em categorias relevantes, mas não têm ferramenta dedicada. Se você acha que deveria, abra uma issue no GitHub.

**Por que `fintech` como categoria?**
Interesse pessoal do autor (trabalha em fintech). A categoria cobre cartões, cooperativas, Pix, Open Finance, DREX — tópicos específicos do Brasil.

**Como sugiro uma fonte nova?**
Abra issue no GitHub descrevendo: nome do blog/site, URL, por que é relevante, exemplos de conteúdo relevante que ele já publicou. A IA pode ser re-treinada para incluir essa fonte.

**A IA pode errar?**
Sim — principalmente ao classificar categoria em casos ambíguos. Se perceber algo estranho (notícia irrelevante, link quebrado, categoria errada), reporte em issue. O sistema tem "regras de desempate" documentadas para minimizar erros (ex: Service Mesh → `distarch`, MCP como protocolo → `aiops`, etc.).

**Posso assinar por RSS?**
Sim — `feed.xml` na raiz do site. É gerado automaticamente pelo CI.

**O código é aberto?**
Sim. Todo o sistema (site + skill da IA + scripts) está no repositório público no GitHub. A skill é um único arquivo Markdown (`skills/csr-news-daily.md`) com ~1000 linhas de instruções para a IA — você pode ler exatamente como ela decide.

**Por que "v1"?**
Esta é a primeira versão pública. Versões anteriores foram iterações internas de desenvolvimento, não publicadas. A partir daqui, o sistema é estável e o histórico de edições passa a ser preservado.

---

Qualquer dúvida, abra uma issue no GitHub: [cesarschutz/noticias-dev-arq](https://github.com/cesarschutz/noticias-dev-arq).
