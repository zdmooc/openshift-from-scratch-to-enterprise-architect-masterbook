#!/usr/bin/env bash
set -euo pipefail

ENGINE="${ENGINE:-docker}"
COMPOSE_BIN="$(ENGINE="$ENGINE" COMPOSE="${COMPOSE:-auto}" ./scripts/compose.sh)"

echo "[LAB04] Compose stack (postgres + adminer)"
cd compose/stack02-postgres-adminer

# shellcheck disable=SC2086
$COMPOSE_BIN up -d
echo "[+] Adminer: http://localhost:8082"
echo "[+] To stop:"
echo "    $COMPOSE_BIN down"
