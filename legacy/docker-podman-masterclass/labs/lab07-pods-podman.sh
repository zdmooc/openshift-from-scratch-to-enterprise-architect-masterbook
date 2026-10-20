#!/usr/bin/env bash
set -euo pipefail

BIN="$(ENGINE="${ENGINE:-docker}" ./scripts/engine.sh)"
if [[ "$BIN" != "podman" ]]; then
  echo "[LAB07] Skipped: this lab is for Podman pods (ENGINE=podman)."
  exit 0
fi

echo "[LAB07] Podman pods (Kubernetes mindset)"
POD="lab07-pod"

podman pod rm -f "$POD" 2>/dev/null || true
podman pod create --name "$POD" -p 8085:80

podman run -d --pod "$POD" --name nginx-in-pod nginx:1.27

echo "Open: http://localhost:8085"
podman pod ps
podman ps --pod
