#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB01] Build + run nginx example"
cd examples/nginx

FILE="Dockerfile"
if [[ "$BIN" == "podman" ]]; then
  FILE="Containerfile"
fi

$BIN build -t hello-nginx:dev -f "$FILE" .
$BIN rm -f hello-nginx 2>/dev/null || true
$BIN run -d --name hello-nginx -p 8080:80 hello-nginx:dev

echo
echo "Open: http://localhost:8080"
echo "Logs:"
$BIN logs --tail=20 hello-nginx || true
