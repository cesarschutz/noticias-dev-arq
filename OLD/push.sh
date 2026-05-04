#!/bin/bash
# CsR News — Commit e push de novas edições
# Rode após o Cowork gerar os JSONs:
#   cd ~/Downloads/noticias-arq && ./push.sh
#
# Pode ser chamado por LaunchAgent. Log em ~/Library/Logs/csr-news-push.log com rotação simples.
# NOTA: Se renomear o Label do LaunchAgent local, rodar: launchctl unload/load do .plist em ~/Library/LaunchAgents/

set -u
cd "$(dirname "$0")" || exit 1

LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/csr-news-push.log"
mkdir -p "$LOG_DIR"

# Rotação simples: se > 1MB, arquiva
if [ -f "$LOG_FILE" ] && [ "$(wc -c <"$LOG_FILE")" -gt 1048576 ]; then
  mv "$LOG_FILE" "$LOG_FILE.1"
fi

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"; }

log "─── CsR News push iniciado ───"

# Verifica se há mudanças em data/
if git diff --quiet data/ && git diff --cached --quiet data/ && [ -z "$(git ls-files --others --exclude-standard data/)" ]; then
  log "✓ Nenhuma alteração em data/ — nada para enviar."
  exit 0
fi

# Detecta a data da edição mais recente
LATEST=$(ls -1 data/2*.json 2>/dev/null | sort -r | head -1 | sed 's|data/||;s|\.json||')
if [ -z "$LATEST" ]; then
  log "✗ Nenhum arquivo de edição encontrado em data/"
  exit 1
fi
log "→ Edição detectada: $LATEST"

git add data/
if ! git commit -m "feat: CsR News edição de $LATEST" >>"$LOG_FILE" 2>&1; then
  log "✗ Falha no commit (veja log acima)"
  exit 1
fi

# Retry com backoff: 3 tentativas
MAX_TRIES=3
DELAY=5
for try in $(seq 1 $MAX_TRIES); do
  log "→ Tentativa $try/$MAX_TRIES: git push"
  if git push origin main >>"$LOG_FILE" 2>&1; then
    log "✓ Push concluído com sucesso"
    exit 0
  fi
  log "⚠ Tentativa $try falhou. Aguardando ${DELAY}s…"
  sleep "$DELAY"
  DELAY=$((DELAY * 2))
done

log "✗ Push falhou após $MAX_TRIES tentativas. Verifique conexão e autenticação."
exit 1
