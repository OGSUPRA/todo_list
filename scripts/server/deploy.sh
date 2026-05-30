#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$ROOT_DIR"

cp -n .env.example .env || true

docker compose --profile monitoring config >/dev/null
docker compose --profile monitoring pull postgres pgadmin prometheus grafana loki promtail postgres-exporter cadvisor node-exporter || true
docker compose --profile monitoring up -d --build --remove-orphans
