#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB10] Debug : inspect / logs / exec"

echo "[+] Containers:"
$BIN ps

echo
echo "[+] Inspect hello-flask (if running):"
$BIN inspect hello-flask 2>/dev/null | head -n 40 || echo "hello-flask not running"

echo
echo "[+] Exec into hello-nginx (if running):"
if $BIN ps --format '{{.Names}}' | grep -q '^hello-nginx$'; then
  $BIN exec -it hello-nginx sh -lc "nginx -v && ls -la /usr/share/nginx/html | head"
else
  echo "hello-nginx not running"
fi
