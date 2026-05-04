# CSR News

Jornal técnico pessoal para arquitetos sêniores e devs experientes. Tom: jornalístico, descontraído, sem clickbait. O usuário é o Cesar — ele já sabe o que é um LLM, um Kafka, um service mesh. Não explique o básico, vá direto ao ponto.

---

## Como agir por tipo de pedido

**Pedido visual / estrutural em `nova-home.html`**
→ Invocar agente `frontend-tinker`. Ele sabe ler os tokens e fazer edits respeitando o design system.

**Pedido de ajuste na skill diária (`skills/csr-news-daily.md`)**
→ Invocar agente `skill-keeper`. Ele lê o arquivo completo antes de tocar em qualquer coisa.

**Nova fonte ou `source_key`**
→ Editar `data/sources.json` E propor atualização simultânea na skill (tabela "FONTES PREFERIDAS" + "Fontes não-óbvias").

**Correção manual de uma edição (`data/*.json`)**
→ Salvar `data/editions.json` **primeiro**, depois `data/{YYYY-MM-DD}.json` (esse último dispara o LaunchAgent de push).

**Novo padrão / regra / decisão surgida na conversa**
→ Ao final, oferecer salvar. Destinos possíveis: este `CLAUDE.md` (padrão amplo), um agente em `.claude/agents/` (tarefa especializada), ou a skill (se afetar geração de edição — ver seção Pacto abaixo).

---

## Nunca fazer

- Tirar screenshot. O Cesar abre `nova-home.html` no browser e avisa.
- Modificar `data/quotes.json` — é gerenciado manualmente por ele.
- Rodar `git push` — LaunchAgent externo (`push.sh`) cuida disso.
- Executar a skill — ela roda no **Claude Cowork**, não aqui. Aqui a gente só edita.
- Mexer em `.claude/settings.local.json`.
- Commitar `.secrets` (tem `YOUTUBE_API_KEY`).

---

## Mapa de arquivos

| Arquivo / Pasta | O que é |
|---|---|
| `nova-home.html` | SPA principal — CSS + HTML + JS **tudo inline**, ~8300 linhas. Nunca fragmentar sem ordem explícita. |
| `index.html` | Versão legada. Mexer só se pedido. |
| `data/editions.json` | Índice mestre: `last_generated` + array `editions[]`. Salvar antes do arquivo diário. |
| `data/{YYYY-MM-DD}.json` | Edição do dia. Schema definido na skill (FASE 1). Salvar por último. |
| `data/sources.json` | Fonte de verdade para `source_key`. Nunca usar campo livre — sempre chave daqui. |
| `data/quotes.json` | **Não tocar.** Gerenciado manualmente. |
| `data/img/` | Mascotes e robôs (PNGs). |
| `assets/csr-news-logo.svg` | Logo. |
| `skills/csr-news-daily.md` | Skill diária — fonte de verdade para fases, queries, schema, hierarquia de `kind`, canais YouTube, cascata de imagem. Precisou de detalhe editorial? Abrir esse arquivo. |
| `.secrets` | `YOUTUBE_API_KEY`. No `.gitignore`. |

---

## Design tokens — `nova-home.html`

O bloco `:root` fica aprox. nas linhas 14–60. Sempre ler antes de propor valor hardcoded.

```
/* Light */
--bg: #f5f5f7      --bg-alt: #ffffff     --surface: #ffffff
--text: #1d1d1f    --text-2: rgba(0,0,0,0.56)
--accent: #0071e3  --link: #0066cc
--shadow: rgba(0,0,0,0.22) 3px 5px 30px 0px
--shadow-s: rgba(0,0,0,0.08) 0 2px 8px 0
--sw: 240px  --nh: 48px  --r: 8px  --rl: 12px  --rp: 980px

/* Dark  →  [data-theme="dark"] + @media prefers-color-scheme: dark */
--bg: #000000   --accent: #2997ff
```

Tipografia: `var(--ff-display)` (títulos), `var(--ff-text)` (corpo), `var(--ff-quote)` (Newsreader, para quotes).
Animações: usar `--ease-spring` ou `--ease-out`. Durações: `--tr-fast`, `--tr-base`, `--tr-slow`.

---

## Pacto da skill diária

Se qualquer decisão da conversa mudar um dos itens abaixo, **propor** atualização em `skills/csr-news-daily.md` antes de fechar. Sempre perguntar antes de editar — o arquivo tem ~1376 linhas e é crítico.

- Categorias de news ou queries de busca
- Fontes (tabelas Tier, fontes especializadas)
- `tool_key` ou hierarquia de `kind`
- Política de imagem (cascata FASE 5C)
- Schema de campos (`news[]`, `tools[]`, `highlights[]`, `videos[]`)
- Fases de execução (0–7), sanity checks, checks `jq`
- Canais autorizados de YouTube
- Volume mínimo, janela de busca, regras de blocklist

---

## Padrões editoriais (resumo — detalhes na skill)

- Anti-clickbait: sem "top N", "N razões", "N ways".
- Fontes: Tier 1 (oficial) > Tier 2 (autores canônicos) > Tier 3 (comunidade). Tabela completa na skill.
- Sexta-feira: `fundamentals` recebe 2–3 itens, ≥1 evergreen canônico.
- Blocklist: nunca repetir URL das últimas 7 edições.

---

## Auto-atualização deste arquivo

Quando a conversa firmar um novo padrão, regra, decisão técnica ou nomenclatura, **perguntar ao Cesar se quer salvar** e propor o edit correspondente aqui (ou no destino correto). Não esperar ele pedir.

---

## Agentes disponíveis

| Agente | Quando invocar |
|---|---|
| `frontend-tinker` | Qualquer mudança em `nova-home.html` |
| `skill-keeper` | Qualquer mudança em `skills/csr-news-daily.md` |
