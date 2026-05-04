# CSR News — dados fixos v2

Arquivos para salvar em `data/dados_fixos`.

Esses JSONs foram montados como tabelas fixas para o projeto evoluir para o modelo:

**notícia + contexto + aprendizado + decisão técnica**.

## Arquivos

- `autores_referencia.json`
- `canais_video.json`
- `categorias.json`
- `consultas_pesquisa.json`
- `ferramentas.json`
- `fontes_preferidas.json`
- `grupos_categorias.json`
- `grupos_ferramentas.json`
- `linguagens.json`
- `manifesto.json`
- `regras_editoriais.json`
- `subcategorias.json`
- `tipos_conteudo.json`

## Observações

- Mantive os IDs atuais das categorias do frontend: `ai`, `aiops`, `sec`, `cloud`, etc.
- Mantive as 34 ferramentas que aparecem em `nova-home.html`/`index.html`.
- Mantive as 3 linguagens: Java, JavaScript/TypeScript e Python.
- `consultas_pesquisa.json` concentra as queries da skill, para no futuro a skill ler do arquivo em vez de ter tudo hardcoded no prompt.
- `subcategorias.json` foi gerado a partir dos escopos da skill, mais os subtópicos monitorados indiretamente.
- Os links oficiais das ferramentas que não estavam na skill foram preenchidos com URLs oficiais/changelog conhecidas para começar; você pode ajustar depois.

