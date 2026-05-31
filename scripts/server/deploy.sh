#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

retry() {
  local attempts="$1"
  local delay_seconds="$2"
  shift 2

  local attempt=1
  until "$@"; do
    if [[ "$attempt" -ge "$attempts" ]]; then
      return 1
    fi
    attempt=$((attempt + 1))
    sleep "$delay_seconds"
  done
}

cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

docker compose config >/dev/null

# Clear only dangling build cache and unreferenced layers before deploy.
docker builder prune -f || true
docker image prune -f || true

# Pull the only required external runtime image for the lightweight profile with retries.
if ! docker image inspect postgres:16-alpine >/dev/null 2>&1; then
  retry 4 15 docker pull postgres:16-alpine
fi

# Lightweight default deploy for very small VPS.
# Extra tools can be enabled later when the server is stronger:
# docker compose --profile admin-tools up -d pgadmin
# docker compose --profile monitoring up -d prometheus grafana loki promtail postgres-exporter cadvisor node-exporter
retry 3 15 docker compose up -d --build --remove-orphans --pull never
