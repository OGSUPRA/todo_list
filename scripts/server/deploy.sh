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

print_failure_diagnostics() {
  docker compose ps || true
  docker logs --tail 200 todo_postgres || true
}

cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

docker compose config >/dev/null

# Clear only dangling build cache and unreferenced layers before deploy.
docker builder prune -f || true
docker image prune -f || true

# Pull required runtime images with retries instead of building on the VPS.
retry 4 15 docker compose pull postgres api web

# Lightweight default deploy for very small VPS.
# Extra tools can be enabled later when the server is stronger:
# docker compose --profile admin-tools up -d pgadmin
# docker compose --profile monitoring up -d prometheus grafana loki promtail postgres-exporter cadvisor node-exporter
if ! retry 3 15 docker compose up -d --no-build --remove-orphans; then
  print_failure_diagnostics
  exit 1
fi
