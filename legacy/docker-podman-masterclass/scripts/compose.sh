#!/usr/bin/env bash
set -euo pipefail

ENGINE="${ENGINE:-docker}"
PREFERRED="${COMPOSE:-auto}"

if [[ "$ENGINE" == "docker" ]]; then
  if command -v docker >/dev/null 2>&1; then
    # Prefer 'docker compose' (v2)
    echo "docker compose"
    exit 0
  fi
fi

# Podman side
if [[ "$PREFERRED" == "podman-compose" || "$PREFERRED" == "auto" ]]; then
  if command -v podman-compose >/dev/null 2>&1; then
    echo "podman-compose"
    exit 0
  fi
fi

# Fallback: docker compose if available
if command -v docker >/dev/null 2>&1; then
  echo "docker compose"
  exit 0
fi

echo "No compose tool found (need docker compose or podman-compose)" >&2
exit 1
