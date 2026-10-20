#!/usr/bin/env bash
set -euo pipefail

ENGINE="${ENGINE:-docker}"

if [[ "$ENGINE" == "docker" ]]; then
  BIN="docker"
elif [[ "$ENGINE" == "podman" ]]; then
  BIN="podman"
else
  echo "ENGINE must be docker or podman (got: $ENGINE)" >&2
  exit 1
fi

if ! command -v "$BIN" >/dev/null 2>&1; then
  echo "Engine binary not found: $BIN" >&2
  exit 1
fi

echo "$BIN"
