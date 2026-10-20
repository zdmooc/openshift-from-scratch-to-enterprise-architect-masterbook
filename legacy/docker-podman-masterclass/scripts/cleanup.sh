#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[+] Stopping/removing demo containers if any..."
$BIN rm -f hello-nginx 2>/dev/null || true
$BIN rm -f hello-flask 2>/dev/null || true

echo "[+] Removing demo images..."
$BIN rmi -f hello-nginx:dev 2>/dev/null || true
$BIN rmi -f hello-flask:dev 2>/dev/null || true

echo "[+] Done."
