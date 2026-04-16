# DevPulse — Arquivo Diário do Arquiteto

Curadoria diária de notícias técnicas para arquitetos de software e solução, gerada automaticamente por IA e publicada no GitHub Pages.

## Como funciona

O projeto usa uma arquitetura **data-driven**: templates HTML carregam dados de arquivos JSON via `fetch()`.

- **Templates** (`index.html`, `dia.html`): design Apple glassmorphism, sem dados hardcoded
- **Dados** (`data/*.json`): gerados diariamente pelo Claude Cowork
- **Deploy**: push para `main` → GitHub Actions → GitHub Pages

## Categorias cobertas

Segurança, IA & LLMs, Cloud (foco AWS), DevOps, Backend & APIs, Frontend, Bancos de Dados, Linguagens & Tooling, Arquitetura de Software, Arquitetura de Solução.

## Desenvolvimento local

```bash
# Servidor HTTP necessário para fetch() funcionar
python3 -m http.server 8000

# Abrir no browser
open http://localhost:8000
```

## Estrutura

```
index.html          → Arquivo com calendário e edições
dia.html?d=ISO      → Edição completa do dia
data/editions.json  → Índice de todas as edições
data/YYYY-MM-DD.json → Dados de cada dia
skills/             → Skill Cowork para geração diária
```

## Link

[cesarschutz.github.io/noticias-dev-arq](https://cesarschutz.github.io/noticias-dev-arq/)
