#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB08] Registry (local) demo"
echo "This lab uses a local registry container on port 5000."

$BIN rm -f registry-lab08 2>/dev/null || true
$BIN run -d --name registry-lab08 -p 5000:5000 registry:2

echo "[+] Tag and push hello-nginx image (build first if needed)"
if ! $BIN image inspect hello-nginx:dev >/dev/null 2>&1; then
  echo "Image hello-nginx:dev missing, running lab01 first..."
  ENGINE="$ENGINE" ./labs/lab01-build-run.sh >/dev/null
fi

$BIN tag hello-nginx:dev localhost:5000/hello-nginx:dev
$BIN push localhost:5000/hello-nginx:dev

echo "[+] Pull back:"
$BIN rmi localhost:5000/hello-nginx:dev 2>/dev/null || true
$BIN pull localhost:5000/hello-nginx:dev

echo "[+] Done."
