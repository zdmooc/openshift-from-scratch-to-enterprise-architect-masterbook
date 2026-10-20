#!/usr/bin/env bash
set -euo pipefail

BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"
if [[ "$BIN" != "podman" ]]; then
  echo "[LAB06] Skipped: this lab is for Podman (ENGINE=podman)."
  exit 0
fi

echo "[LAB06] Rootless Podman quick checks"
echo "[+] podman info (look for rootless=true)"
podman info | head -n 60 || true

echo
echo "[+] Rootless ports note:"
echo "Depending on your setup, binding <1024 may require extra config; use 808x ports for labs."
