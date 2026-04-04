#!/usr/bin/env bash
# run_uat.sh — Ejecuta el UAT completo de SP2 y captura evidencia.
#
# Uso (desde la raíz del proyecto):
#   bash tests/uat/sp2/run_uat.sh
#
# Requiere:
#   - data/competencia.db y data/resultados.db inicializadas (ver README)
#   - uv run fastapi dev src/app.py corriendo en otra terminal
#
# El script verifica que el servidor esté disponible antes de continuar.
#
# Salidas:
#   quality/reports/uat/SP2/capa1-pytest.txt   — Capa 1: salida pytest
#   quality/reports/uat/SP2/uat_ids.json       — IDs generados por el seed
#   quality/reports/uat/SP2/capa2-http.json    — Capa 2: respuestas HTTP

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
UAT_DIR="$ROOT/quality/reports/uat/SP2"
BASE_URL="${UAT_URL:-http://localhost:8000}"

mkdir -p "$UAT_DIR"

echo "========================================"
echo "  UAT SP2 — La Competencia"
echo "========================================"
echo

# ── Capa 1: pytest E2E automatizado ──────────────────────────────────────
echo "[Capa 1] Ejecutando tests E2E automatizados..."
echo

uv run pytest \
    tests/integration/competencia/test_flujo_e2e_inc21.py \
    tests/integration/competencia/test_competencia_finalizada_integration.py \
    tests/integration/resultados/test_calcular_ranking_integration.py \
    -v --tb=short \
    2>&1 | tee "$UAT_DIR/capa1-pytest.txt"

echo
echo "✓ Capa 1 completada → $UAT_DIR/capa1-pytest.txt"
echo

# ── Verificar servidor disponible ─────────────────────────────────────────
echo "[Verificación] Comprobando que el servidor está disponible en $BASE_URL ..."
if ! curl -sf "$BASE_URL/health" > /dev/null; then
    echo
    echo "ERROR: El servidor no responde en $BASE_URL"
    echo "  Levantá el servidor con: uv run fastapi dev src/app.py"
    echo "  Luego volvé a correr este script."
    exit 1
fi
echo "✓ Servidor disponible"
echo

# ── Seed Fase 1: ConfigurarIntervaloOT + RegistrarAP + GenerarGrilla ─────
echo "[Seed Fase 1] Sembrando ConfigurarIntervaloOT + APs + GenerarGrilla..."
echo

uv run python tests/uat/sp2/seed_competencia.py fase1

IDS_FILE="$UAT_DIR/uat_ids.json"
CID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['competencia_id'])")

echo
echo "  competencia_id: $CID"
echo

# ── Capa 2: verificaciones HTTP ───────────────────────────────────────────
echo "[Capa 2] Verificando endpoints HTTP contra $BASE_URL ..."
echo

HTTP_OUTPUT="$UAT_DIR/capa2-http.json"

# Función auxiliar para capturar respuesta HTTP con status
http_get() {
    local label="$1"
    local url="$2"
    local status
    local body
    body=$(curl -s -w '\n{"_status":%{http_code}}' "$url")
    echo "  \"$label\": $body"
}

http_post() {
    local label="$1"
    local url="$2"
    local data="$3"
    local body
    body=$(curl -s -w '\n{"_status":%{http_code}}' \
        -X POST -H "Content-Type: application/json" \
        -d "$data" "$url")
    echo "  \"$label\": $body"
}

{
  echo "{"

  # UAT-2.1: /health
  echo '  "UAT-2.1_health": '
  curl -sf "$BASE_URL/health" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.2: GET estado (pre-confirmar → grilla_confirmada=false)
  echo '  "UAT-2.2_estado_pre_confirmar": '
  curl -sf "$BASE_URL/competencia/$CID/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.3: GET grilla (5 entradas ordenadas por AP desc)
  echo '  "UAT-2.3_grilla": '
  curl -sf "$BASE_URL/competencia/$CID/grilla?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.4: POST confirmar-grilla (nuevo SP2) → 204
  echo '  "UAT-2.4_confirmar_grilla_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" \
    -d "{\"disciplina\": \"STA\"}" \
    "$BASE_URL/competencia/$CID/confirmar-grilla")
  echo "  {\"http_status\": $STATUS, \"esperado\": 204}"
  echo ","

  # UAT-2.5: GET estado (post-confirmar → grilla_confirmada=true)
  echo '  "UAT-2.5_estado_post_confirmar": '
  curl -sf "$BASE_URL/competencia/$CID/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.6: POST iniciar (nuevo SP2) → 204
  echo '  "UAT-2.6_iniciar_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" \
    -d "{\"disciplina\": \"STA\", \"juez_id\": \"juez-uat-sp2\"}" \
    "$BASE_URL/competencia/$CID/iniciar")
  echo "  {\"http_status\": $STATUS, \"esperado\": 204}"
  echo ","

  # UAT-2.7: GET estado (post-iniciar → estado=en_ejecucion)
  echo '  "UAT-2.7_estado_post_iniciar": '
  curl -sf "$BASE_URL/competencia/$CID/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.8: GET andariveles post-iniciar (3 andariveles libres)
  echo '  "UAT-2.8_andariveles_post_iniciar": '
  curl -sf "$BASE_URL/competencia/$CID/andariveles?disciplina=STA&andariveles=3" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'

  echo "}"
} > "$HTTP_OUTPUT.parcial"

echo "✓ Capa 2 parcial completada (pre-ejecución)"
echo

# ── Seed Fase 2: Ejecución multi-andarivel ────────────────────────────────
echo "[Seed Fase 2] Ejecutando flujo multi-andarivel (A, B, C, D, E)..."
echo

uv run python tests/uat/sp2/seed_competencia.py fase2

echo

# ── Capa 2: verificaciones post-ejecución ────────────────────────────────
echo "[Capa 2] Verificando endpoints post-ejecución..."
echo

{
  # Leer el parcial ya generado
  python3 -c "
import json, sys
with open('$HTTP_OUTPUT.parcial') as f:
    content = f.read()
# Remover el cierre '}'
content = content.rstrip().rstrip('}')
print(content)
print(',')
"

  # UAT-2.9: GET events (tipos SP2 presentes)
  echo '  "UAT-2.9_events": '
  curl -sf "$BASE_URL/competencia/$CID/events" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.10: GET progreso (total=5, ejecutadas=4, dns_count=1)
  echo '  "UAT-2.10_progreso": '
  curl -sf "$BASE_URL/competencia/$CID/progreso" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.11: GET ranking (BC Resultados)
  echo '  "UAT-2.11_ranking": '
  curl -sf "$BASE_URL/resultados/$CID/ranking?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'

  echo "}"
} > "$HTTP_OUTPUT"

rm -f "$HTTP_OUTPUT.parcial"

echo "✓ Capa 2 completada → $HTTP_OUTPUT"
echo

# ── Resumen ───────────────────────────────────────────────────────────────
echo "========================================"
echo "  UAT SP2 finalizado"
echo "  Artefactos en: quality/reports/uat/SP2/"
echo "========================================"
echo
echo "Verificaciones manuales pendientes:"
echo "  - capa1-pytest.txt  → todos PASSED"
echo "  - capa2-http.json   → UAT-2.4 status=204, UAT-2.6 status=204"
echo "  - capa2-http.json   → UAT-2.5 grilla_confirmada=true"
echo "  - capa2-http.json   → UAT-2.7 estado=en_ejecucion"
echo "  - capa2-http.json   → UAT-2.9 eventos: IntervaloOTConfigurado, GrillaDeSalidaGenerada,"
echo "                                          GrillaConfirmada, CompetenciaIniciada, CompetenciaFinalizada"
echo "  - capa2-http.json   → UAT-2.10 total=5, ejecutadas=4, dns_count=1"
echo "  - capa2-http.json   → UAT-2.11 ranking 5 entradas, A en posicion 1"
echo
echo "Próximo paso: completar quality/reports/uat/SP2/report.md"
