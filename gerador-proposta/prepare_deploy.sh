#!/usr/bin/env bash
# Copia modelo + slots do vault para proposal_app/data/ (pacote Railway sem GitHub).
set -euo pipefail

APP_ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA="$APP_ROOT/data"
SKILL_ROOT="$(cd "$APP_ROOT/.." && pwd)"
VAULT="$(cd "$SKILL_ROOT/../../.." && pwd)"
UNISANTA="$VAULT/01 - Propostas/Unisanta"
ASSETS="$UNISANTA/assets"

mkdir -p "$DATA/assets" "$DATA/geradas"

copy_req() {
  local src="$1" dest="$2"
  if [[ ! -f "$src" ]]; then
    echo "ERRO: arquivo obrigatório não encontrado: $src" >&2
    exit 1
  fi
  cp -f "$src" "$dest"
  echo "  OK  $(basename "$src") ($(du -h "$dest" | awk '{print $1}'))"
}

echo "Empacotando assets em $DATA"
copy_req "$UNISANTA/Modelo-Proposta-Tecnica-v1.0-variaveis.pptx" \
  "$DATA/Modelo-Proposta-Tecnica-v1.0-variaveis.pptx"
copy_req "$UNISANTA/Modelo-Proposta-Tecnica-v1.0-slots.json" \
  "$DATA/Modelo-Proposta-Tecnica-v1.0-slots.json"

# Modelo original (fallback se precisar reparametrizar)
if [[ -f "$ASSETS/Modelo-Proposta Tecnica v1.0.pptx" ]]; then
  copy_req "$ASSETS/Modelo-Proposta Tecnica v1.0.pptx" \
    "$DATA/assets/Modelo-Proposta Tecnica v1.0.pptx"
fi

# Opcionais
[[ -f "$UNISANTA/UNS001-26-vigia-valores.json" ]] && \
  cp -f "$UNISANTA/UNS001-26-vigia-valores.json" "$DATA/" && \
  echo "  OK  UNS001-26-vigia-valores.json"
[[ -f "$ASSETS/logo-nph.png" ]] && \
  cp -f "$ASSETS/logo-nph.png" "$DATA/assets/" && \
  echo "  OK  logo-nph.png"

# Tipos / pacotes de proposta
if [[ -f "$APP_ROOT/data/packages.json" ]]; then
  echo "  OK  packages.json (já em data/)"
elif [[ -f "$UNISANTA/packages.json" ]]; then
  cp -f "$UNISANTA/packages.json" "$DATA/" && echo "  OK  packages.json"
fi
mkdir -p "$DATA/packages"
if [[ -d "$UNISANTA/packages" ]]; then
  cp -f "$UNISANTA/packages/"*.pptx "$DATA/packages/" 2>/dev/null || true
fi
if [[ -d "$APP_ROOT/data/packages" ]]; then
  # keep local package templates
  echo "  OK  packages/ ($(ls "$DATA/packages" 2>/dev/null | wc -l | tr -d ' ') pptx)"
fi

# Marker para paths.py
touch "$DATA/.bundled"

TOTAL=$(du -sh "$DATA" | awk '{print $1}')
echo "Pronto. Pacote data/: $TOTAL"
echo "Próximo: railway up  (ou docker build)"
