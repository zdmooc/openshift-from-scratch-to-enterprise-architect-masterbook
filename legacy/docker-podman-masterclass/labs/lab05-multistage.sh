#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB05] Build flask demo (non-root + healthcheck)"
cd examples/flask

FILE="Dockerfile"
if [[ "$BIN" == "podman" ]]; then
  FILE="Containerfile"
fi

$BIN build -t hello-flask:dev -f "$FILE" .
$BIN rm -f hello-flask 2>/dev/null || true
$BIN run -d --name hello-flask -e ENGINE="$BIN" -p 8084:8080 hello-flask:dev

echo "Open: http://localhost:8084/"
