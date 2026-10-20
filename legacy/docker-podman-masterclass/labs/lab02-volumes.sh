#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB02] Volumes (named volume) with postgres"
VOL="pgdata-lab02"

# create volume
if [[ "$BIN" == "docker" ]]; then
  $BIN volume create "$VOL" >/dev/null
else
  $BIN volume create "$VOL" >/dev/null
fi

$BIN rm -f pg-lab02 2>/dev/null || true
$BIN run -d --name pg-lab02   -e POSTGRES_PASSWORD=example   -v ${VOL}:/var/lib/postgresql/data   -p 5432:5432   postgres:16

echo "[+] Waiting a few seconds..."
sleep 3

echo "[+] Show volume:"
$BIN volume inspect "$VOL" | head -n 30 || true

echo "[+] Cleanup container (keep volume):"
$BIN rm -f pg-lab02
echo "Volume kept: $VOL"
