#!/usr/bin/env bash
# Скачать ролик-образец (Instagram Reels, TikTok, YouTube Shorts) для разбора.
#   bash scripts/download.sh <ссылка> <папка> [браузер]
# Instagram без входа часто отвечает «login required»: тогда yt-dlp берёт куки
# из вашего браузера (по умолчанию chrome; можно safari, firefox, edge, brave).
# Ролик нужен только как образец для разбора — в свой ролик чужие кадры, голос и лицо не идут.
set -euo pipefail
URL="${1:?ссылка на ролик}"; OUT="${2:-work/src}"; BROWSER="${3:-chrome}"
mkdir -p "$OUT"
command -v yt-dlp >/dev/null || { echo "Нет yt-dlp: pip install -U yt-dlp (или brew install yt-dlp)"; exit 1; }
TPL="$OUT/%(uploader_id)s_%(id)s.%(ext)s"
if ! yt-dlp -q --no-warnings -f "b[ext=mp4]/b" -o "$TPL" "$URL"; then
  echo "Без входа не отдали — пробую с куками браузера $BROWSER"
  yt-dlp -q --no-warnings --cookies-from-browser "$BROWSER" -f "b[ext=mp4]/b" -o "$TPL" "$URL"
fi
ls -la "$OUT"
