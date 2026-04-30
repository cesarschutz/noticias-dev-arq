# CsR News — edições de demonstração

Este pacote simula como a futura skill pode gerar dados em `/data/edicoes`.

## Estrutura raiz

- `estado_execucao.json`: controle da última execução bem-sucedida.
- `execucoes.json`: histórico de runs.
- `indice_edicoes.json`: índice das edições publicadas.
- `ed_0001/`, `ed_0002/`, `ed_0003/`: três edições simuladas.

## Estrutura por edição

- `edicao.json`: metadados editoriais da edição.
- `itens.json`: notícias, guias, alertas e fundamentos.
- `aprendizados.json`: blocos “aprenda com esta notícia”.
- `relacionamentos.json`: vínculos com ferramentas, linguagens, tags, vídeos e aprendizados.
- `links_fontes.json`: links usados como fonte.
- `destaques.json`: 3 destaques da edição.
- `videos_edicao.json`: vídeos curados para a edição.
- `quotes_edicao.json`: citações selecionadas.
- `validacao.json`: resultado de validação da geração.
- `visao_publica.json`: visão agregada para facilitar consumo pelo frontend.

## Observação

O volume está menor que uma edição final de produção para facilitar inspeção.
A ideia é validar o modelo de dados antes de alterar a skill e o frontend.
