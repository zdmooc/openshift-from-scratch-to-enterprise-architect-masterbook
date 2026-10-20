#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB09] Sécurité de base : non-root + read-only (quand possible)"

echo "[+] Show that flask container runs as non-root"
$BIN ps --filter name=hello-flask --format "table {{.Names}}	{{.Image}}	{{.Status}}" || true
echo

echo "[+] Try running nginx with read-only fs (tmpfs for /var/cache/nginx may be needed depending image)"
$BIN rm -f ro-nginx 2>/dev/null || true
set +e
$BIN run -d --name ro-nginx --read-only -p 8086:80 nginx:1.27
RC=$?
set -e
if [[ $RC -ne 0 ]]; then
  echo "As expected, read-only may fail; fix with tmpfs mounts:"
  $BIN run -d --name ro-nginx --read-only     --tmpfs /var/cache/nginx:rw,noexec,nosuid,size=64m     --tmpfs /var/run:rw,noexec,nosuid,size=16m     -p 8086:80 nginx:1.27
fi

echo "Open: http://localhost:8086"
