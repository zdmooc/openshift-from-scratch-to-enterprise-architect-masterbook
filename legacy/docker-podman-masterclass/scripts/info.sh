#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[+] ENGINE=$BIN"
$BIN version || true
echo
echo "[+] Containers:"
$BIN ps || true
echo
echo "[+] Images:"
$BIN images || true
