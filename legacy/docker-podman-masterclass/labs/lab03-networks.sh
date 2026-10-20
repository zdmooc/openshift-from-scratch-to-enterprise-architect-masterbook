#!/usr/bin/env bash
set -euo pipefail
BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"

echo "[LAB03] Networks (bridge) + DNS between containers"
NET="lab03-net"

# create network
$BIN network create "$NET" >/dev/null 2>&1 || true

$BIN rm -f web-lab03 2>/dev/null || true
$BIN rm -f curl-lab03 2>/dev/null || true

$BIN run -d --name web-lab03 --network "$NET" -p 8083:80 nginx:1.27
$BIN run --name curl-lab03 --network "$NET" --rm curlimages/curl:8.10.1 -sS http://web-lab03:80 >/dev/null

echo "[+] OK: curl reached web-lab03 via container DNS on network $NET"
