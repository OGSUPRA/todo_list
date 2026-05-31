#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$ROOT_DIR"

cp -n .env.example .env || true

docker compose config >/dev/null

# Clear only dangling build cache and unreferenced layers before deploy.
docker builder prune -f || true
docker image prune -f || true

# Lightweight default deploy for very small VPS.
# Extra tools can be enabled later when the server is stronger:
# docker compose --profile admin-tools up -d pgadmin
# docker compose --profile monitoring up -d prometheus grafana loki promtail postgres-exporter cadvisor node-exporter
docker compose up -d --build --remove-orphans
