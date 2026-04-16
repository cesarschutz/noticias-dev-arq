#!/bin/bash
# DevPulse — Commit e push de novas edições
# Rode após o Cowork gerar os JSONs:
#   cd ~/Downloads/noticias-arq && ./push.sh

cd "$(dirname "$0")" || exit 1

# Verifica se há mudanças em data/
if git diff --quiet data/ && git diff --cached --quiet data/ && [ -z "$(git ls-files --others --exclude-standard data/)" ]; then
  echo "✓ Nenhuma alteração em data/ — nada para enviar."
  exit 0
fi

# Detecta a data da edição mais recente
LATEST=$(ls -1 data/2*.json 2>/dev/null | sort -r | head -1 | sed 's|data/||;s|\.json||')

if [ -z "$LATEST" ]; then
  echo "✗ Nenhum arquivo de edição encontrado em data/"
  exit 1
fi

echo "→ Nova edição detectada: $LATEST"

# Stage, commit, push
git add data/
git commit -m "feat: DevPulse edição de $LATEST"
git push origin main

if [ $? -eq 0 ]; then
  echo "✓ Push realizado com sucesso!"
else
  echo "✗ Falha no push. Verifique sua conexão e autenticação."
  exit 1
fi
