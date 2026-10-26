#!/usr/bin/env bash
# Screenshot an HTML/SVG preview with headless Chrome.
#   shot.sh preview.html preview.png [width] [height] [scale]
# scale=2 gives a retina PNG for reading fine text.
set -euo pipefail

IN="${1:?usage: shot.sh <input.html> <out.png> [width] [height] [scale]}"
OUT="${2:?missing out.png}"
W="${3:-2100}"
H="${4:-2260}"
S="${5:-2}"

CHROME="${CHROME:-}"
if [ -z "$CHROME" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v google-chrome || true)" \
           "$(command -v chromium || true)"; do
    [ -x "$c" ] && CHROME="$c" && break
  done
fi
[ -n "$CHROME" ] || { echo "no Chrome/Chromium found; set CHROME=path"; exit 1; }

"$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
  --force-device-scale-factor="$S" --window-size="$W,$H" \
  --screenshot="$OUT" "file://$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")" >/dev/null 2>&1

[ -s "$OUT" ] || { echo "screenshot failed"; exit 1; }
echo "shot: $OUT (${W}x${H} @${S}x, $(du -h "$OUT" | cut -f1))"
