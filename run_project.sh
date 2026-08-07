#!/usr/bin/env bash
set -euo pipefail

echo "Levantando contenedores (db + app)..."
docker compose up -d --build

echo "Esperando a que la base de datos esté lista..."
until docker compose exec -T db pg_isready -U modulo-8 > /dev/null 2>&1; do
  sleep 1
done

echo "Aplicando migraciones..."
docker compose exec -T app uv run alembic upgrade head

echo ""
echo "Listo. API corriendo en:"
echo "  http://localhost:8000"
echo "  Docs (Swagger): http://localhost:8000/docs"
