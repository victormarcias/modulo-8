#!/usr/bin/env bash
set -euo pipefail

echo "Levantando la base de datos..."
docker compose up -d db

echo "Esperando a que la base de datos esté lista..."
until docker compose exec -T db pg_isready -U modulo-8 > /dev/null 2>&1; do
  sleep 1
done

echo "Corriendo tests..."
uv run pytest "$@"
