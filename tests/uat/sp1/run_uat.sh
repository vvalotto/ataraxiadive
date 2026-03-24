#!/usr/bin/env bash
# run_uat.sh — Ejecuta el UAT completo de SP1 y captura evidencia.
#
# Uso (desde la raíz del proyecto):
#   bash tests/uat/sp1/run_uat.sh
#
# Requiere:
#   - uv run fastapi dev src/app.py corriendo en background (o levantado aparte)
#   - data/competencia.db ya inicializada (uv run alembic upgrade head)
#
# Salidas:
#   quality/reports/uat/SP1/capa1-pytest.txt   — Capa 1: salida pytest
#   quality/reports/uat/SP1/capa2-http.json    — Capa 2: respuestas HTTP

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
UAT_DIR="$ROOT/quality/reports/uat/SP1"
BASE_URL="${UAT_URL:-http://localhost:8000}"

mkdir -p "$UAT_DIR"

echo "========================================"
echo "  UAT SP1 — La Performance"
echo "========================================"
echo

# ── Capa 1: pytest E2E automatizado ──────────────────────────────────────
echo "[Capa 1] Ejecutando tests E2E automatizados..."
echo

uv run pytest tests/integration/competencia/test_flujo_e2e.py \
    -v --tb=short \
    2>&1 | tee "$UAT_DIR/capa1-pytest.txt"

echo
echo "✓ Capa 1 completada → $UAT_DIR/capa1-pytest.txt"
echo

# ── Seed: sembrar DB real ─────────────────────────────────────────────────
echo "[Seed] Sembrando data/competencia.db con el flujo DoD SP1..."
echo

uv run python tests/uat/sp1/seed_competencia.py

IDS_FILE="$UAT_DIR/uat_ids.json"
CID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['competencia_id'])")

echo
echo "  competencia_id: $CID"
echo

# ── Capa 2: verificación HTTP ─────────────────────────────────────────────
echo "[Capa 2] Verificando endpoints HTTP contra $BASE_URL ..."
echo "  (el servidor debe estar corriendo: uv run fastapi dev src/app.py)"
echo

HTTP_OUTPUT="$UAT_DIR/capa2-http.json"

{
  echo "{"

  # UAT-2.1: /health
  echo '  "UAT-2.1_health": '
  curl -sf "$BASE_URL/health" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.2: /events
  echo '  "UAT-2.2_events": '
  curl -sf "$BASE_URL/competencia/$CID/events" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.3: /progreso
  echo '  "UAT-2.3_progreso": '
  curl -sf "$BASE_URL/competencia/$CID/progreso" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.4: /performance/proximas
  echo '  "UAT-2.4_proximas": '
  curl -sf "$BASE_URL/competencia/$CID/performance/proximas" | python3 -m json.tool --indent 2 | sed 's/^/  /'

  echo "}"
} > "$HTTP_OUTPUT"

echo "✓ Capa 2 completada → $HTTP_OUTPUT"
echo

# ── Resumen ───────────────────────────────────────────────────────────────
echo "========================================"
echo "  UAT SP1 finalizado"
echo "  Artefactos en: quality/reports/uat/SP1/"
echo "========================================"
echo
echo "Próximo paso: completar quality/reports/uat/SP1/report.md"
