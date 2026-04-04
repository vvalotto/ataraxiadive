#!/usr/bin/env bash
# run_uat.sh — Ejecuta el UAT completo de SP3 y captura evidencia.
#
# Uso (desde la raíz del proyecto):
#   bash tests/uat/sp3/run_uat.sh
#
# Requiere:
#   - DBs data/*.db inicializadas (se crean automáticamente al levantar el servidor)
#   - uv run fastapi dev src/app.py corriendo en otra terminal
#
# El script verifica que el servidor esté disponible antes de continuar.
#
# Salidas:
#   quality/reports/uat/SP3/capa1-pytest.txt   — Capa 1: salida pytest
#   quality/reports/uat/SP3/uat_ids.json       — IDs generados por el seed
#   quality/reports/uat/SP3/capa2-http.json    — Capa 2: respuestas HTTP (20 checks)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
UAT_DIR="$ROOT/quality/reports/uat/SP3"
BASE_URL="${UAT_URL:-http://localhost:8000}"

mkdir -p "$UAT_DIR"

echo "========================================"
echo "  UAT SP3 — El Torneo"
echo "  Datos: Buenos Aires 2025 (HITO-17)"
echo "========================================"
echo

# ── Capa 1: pytest E2E automatizado ──────────────────────────────────────────
echo "[Capa 1] Ejecutando tests E2E automatizados..."
echo

uv run pytest \
    tests/integration/e2e/test_flujo_torneo_competencia.py \
    tests/features/steps/test_US_3_3_2_steps.py \
    tests/integration/resultados/test_calcular_overall_integration.py \
    tests/integration/resultados/test_calcular_ranking_integration.py \
    -v --tb=short \
    2>&1 | tee "$UAT_DIR/capa1-pytest.txt"

echo
echo "✓ Capa 1 completada → $UAT_DIR/capa1-pytest.txt"
echo

# ── Verificar servidor disponible ────────────────────────────────────────────
echo "[Verificación] Comprobando servidor en $BASE_URL ..."
if ! curl -sf "$BASE_URL/health" > /dev/null; then
    echo
    echo "ERROR: El servidor no responde en $BASE_URL"
    echo "  Levantá el servidor con: uv run fastapi dev src/app.py"
    echo "  Luego volvé a correr este script."
    exit 1
fi
echo "✓ Servidor disponible"
echo

# ── Seed Fase 1: Torneo + Registro + Competencia hasta GenerarGrilla ─────────
echo "[Seed Fase 1] Sembrando Torneo + Registro + Competencia..."
echo

uv run python tests/uat/sp3/seed_sp3.py fase1

IDS_FILE="$UAT_DIR/uat_ids.json"
TORNEO_ID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['torneo_id'])")
CID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['competencia_id'])")

echo
echo "  torneo_id      : $TORNEO_ID"
echo "  competencia_id : $CID"
echo

# ── Capa 2: verificaciones HTTP pre-ejecución ─────────────────────────────────
echo "[Capa 2] Verificando endpoints HTTP pre-ejecución..."
echo

HTTP_OUTPUT="$UAT_DIR/capa2-http.json"

# ── Obtener JWT: registrar usuario UAT (ADMIN) y hacer login ─────────────────
UAT_EMAIL="uat-admin@uat-sp3.test"
UAT_PASS="uat-admin-pass-sp3"
curl -s -o /dev/null \
  -X POST -H "Content-Type: application/json" \
  -d "{\"nombre\": \"Admin UAT SP3\", \"email\": \"$UAT_EMAIL\", \"password\": \"$UAT_PASS\", \"rol\": \"ADMIN\"}" \
  "$BASE_URL/auth/registro"

JWT_TOKEN=$(curl -sf \
  -X POST -H "Content-Type: application/json" \
  -d "{\"email\": \"$UAT_EMAIL\", \"password\": \"$UAT_PASS\"}" \
  "$BASE_URL/auth/login" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# También registrar un usuario ATLETA para verificar endpoints de registro
UAT_ATLETA_EMAIL="uat-atleta@uat-sp3.test"
UAT_ATLETA_PASS="uat-atleta-pass-sp3"
curl -s -o /dev/null \
  -X POST -H "Content-Type: application/json" \
  -d "{\"nombre\": \"Atleta UAT SP3\", \"email\": \"$UAT_ATLETA_EMAIL\", \"password\": \"$UAT_ATLETA_PASS\", \"rol\": \"ATLETA\"}" \
  "$BASE_URL/auth/registro"
ATLETA_TOKEN=$(curl -sf \
  -X POST -H "Content-Type: application/json" \
  -d "{\"email\": \"$UAT_ATLETA_EMAIL\", \"password\": \"$UAT_ATLETA_PASS\"}" \
  "$BASE_URL/auth/login" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

AUTH="Authorization: Bearer $JWT_TOKEN"
ATLETA_AUTH="Authorization: Bearer $ATLETA_TOKEN"

{
  echo "{"

  # UAT-2.1: /health
  echo '  "UAT-2.1_health": '
  curl -sf "$BASE_URL/health" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.2: POST /auth/registro (organizador — status only)
  echo '  "UAT-2.2_auth_registro_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" \
    -d '{"nombre": "Org UAT SP3", "email": "org@uat-sp3.test", "password": "uat-sp3-pass", "rol": "ORGANIZADOR"}' \
    "$BASE_URL/auth/registro")
  echo "  {\"http_status\": $STATUS, \"esperado\": \"201 o 409 si ya existe\"}"
  echo ","

  # UAT-2.3: POST /auth/login (token en respuesta)
  echo '  "UAT-2.3_auth_login": '
  curl -sf \
    -X POST -H "Content-Type: application/json" \
    -d "{\"email\": \"$UAT_EMAIL\", \"password\": \"$UAT_PASS\"}" \
    "$BASE_URL/auth/login" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.4: GET /torneos/{id} (estado del torneo creado)
  echo '  "UAT-2.4_torneo_estado": '
  curl -sf "$BASE_URL/torneos/$TORNEO_ID" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.5: GET /torneos/{id}/disciplinas
  echo '  "UAT-2.5_torneo_disciplinas": '
  curl -sf "$BASE_URL/torneos/$TORNEO_ID/disciplinas" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.6: GET /torneos (lista de torneos)
  echo '  "UAT-2.6_torneos_lista_count": '
  COUNT=$(curl -sf "$BASE_URL/torneos" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
  echo "  {\"total_torneos\": $COUNT}"
  echo ","

  # UAT-2.7: PUT /torneos/{id}/abrir-inscripcion (ya está abierto — transition error esperado)
  echo '  "UAT-2.7_torneo_ya_inscripcion_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X PUT -H "$AUTH" "$BASE_URL/torneos/$TORNEO_ID/abrir-inscripcion")
  echo "  {\"http_status\": $STATUS, \"nota\": \"ya abierto en seed — transition error esperado\"}"
  echo ","

  # UAT-2.8: POST /registro/atletas (verificar endpoint con token ATLETA)
  ATLETA_HTTP_ID_1=$(python3 -c "import uuid; print(uuid.uuid4())")
  echo '  "UAT-2.8_registrar_atleta_http_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" -H "$ATLETA_AUTH" \
    -d "{\"atleta_id\": \"$ATLETA_HTTP_ID_1\", \"nombre\": \"Test\", \"apellido\": \"HTTP\", \"email\": \"test.http@uat.test\", \"fecha_nacimiento\": \"1995-06-15\", \"categoria\": \"SENIOR_MASCULINO\", \"club\": \"CLUB HTTP TEST\"}" \
    "$BASE_URL/registro/atletas")
  echo "  {\"http_status\": $STATUS, \"esperado\": 201}"
  echo ","

  # UAT-2.9: POST /registro/inscripciones (inscribir atleta HTTP)
  ATLETA_HTTP_ID_2=$(python3 -c "import uuid; print(uuid.uuid4())")
  curl -s -o /dev/null \
    -X POST -H "Content-Type: application/json" -H "$ATLETA_AUTH" \
    -d "{\"atleta_id\": \"$ATLETA_HTTP_ID_2\", \"nombre\": \"Test2\", \"apellido\": \"HTTP2\", \"email\": \"test2.http@uat.test\", \"fecha_nacimiento\": \"1996-07-20\", \"categoria\": \"SENIOR_FEMENINO\", \"club\": \"CLUB HTTP TEST\"}" \
    "$BASE_URL/registro/atletas"
  echo '  "UAT-2.9_inscribir_atleta_http_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" -H "$ATLETA_AUTH" \
    -d "{\"atleta_id\": \"$ATLETA_HTTP_ID_2\", \"torneo_id\": \"$TORNEO_ID\", \"disciplinas\": [\"STA\"]}" \
    "$BASE_URL/registro/inscripciones")
  echo "  {\"http_status\": $STATUS, \"esperado\": 201}"
  echo ","

  # UAT-2.10: GET /registro/torneos/{id}/inscriptos
  echo '  "UAT-2.10_inscriptos": '
  curl -sf -H "$AUTH" "$BASE_URL/registro/torneos/$TORNEO_ID/inscriptos" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.11: POST /competencia — crear competencia vía HTTP (standalone)
  echo '  "UAT-2.11_crear_competencia_http_status": '
  NEW_CID=$(python3 -c "import uuid; print(uuid.uuid4())")
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" \
    -d "{\"competencia_id\": \"$NEW_CID\", \"disciplina\": \"DNF\", \"intervalo_minutos\": 7, \"configurado_por\": \"uat-http\"}" \
    "$BASE_URL/competencia")
  echo "  {\"http_status\": $STATUS, \"esperado\": 201}"
  echo ","

  # UAT-2.12: GET /competencia/{id}/grilla (seed competencia STA)
  echo '  "UAT-2.12_grilla_sta": '
  curl -sf "$BASE_URL/competencia/$CID/grilla?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.13: POST /competencia/{id}/confirmar-grilla → 204
  echo '  "UAT-2.13_confirmar_grilla_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" -H "$AUTH" \
    -d '{"disciplina": "STA"}' \
    "$BASE_URL/competencia/$CID/confirmar-grilla")
  echo "  {\"http_status\": $STATUS, \"esperado\": 204}"
  echo ","

  # UAT-2.14: GET /competencia/{id}/estado (post-confirmar)
  echo '  "UAT-2.14_estado_post_confirmar": '
  curl -sf "$BASE_URL/competencia/$CID/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.14b: PUT /torneos/{id}/cerrar-inscripcion (transición previa a EJECUCION)
  curl -s -o /dev/null \
    -X PUT -H "$AUTH" "$BASE_URL/torneos/$TORNEO_ID/cerrar-inscripcion"

  # UAT-2.15: PUT /torneos/{id}/iniciar-ejecucion
  echo '  "UAT-2.15_torneo_iniciar_ejecucion_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X PUT -H "$AUTH" "$BASE_URL/torneos/$TORNEO_ID/iniciar-ejecucion")
  echo "  {\"http_status\": $STATUS, \"esperado\": 200}"
  echo ","

  # UAT-2.16: POST /competencia/{id}/iniciar → 204
  echo '  "UAT-2.16_iniciar_status": '
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" -H "$AUTH" \
    -d "{\"disciplina\": \"STA\", \"juez_id\": \"juez-uat-sp3\"}" \
    "$BASE_URL/competencia/$CID/iniciar")
  echo "  {\"http_status\": $STATUS, \"esperado\": 204}"

  echo "}"
} > "$HTTP_OUTPUT.pre"

echo "✓ Capa 2 pre-ejecución guardada"
echo

# ── Seed Fase 2: Ejecución completa ──────────────────────────────────────────
echo "[Seed Fase 2] Ejecutando 6 performances STA (datos BA 2025)..."
echo

uv run python tests/uat/sp3/seed_sp3.py fase2

echo

# ── Capa 2: verificaciones post-ejecución ────────────────────────────────────
echo "[Capa 2] Verificando resultados post-ejecución..."
echo

{
  python3 -c "
import json, sys
with open('$HTTP_OUTPUT.pre') as f:
    content = f.read().rstrip().rstrip('}')
print(content)
print(',')
"

  # UAT-2.17: GET /competencia/{id}/estado (post-ejecución → Finalizada)
  echo '  "UAT-2.17_estado_post_ejecucion": '
  curl -sf "$BASE_URL/competencia/$CID/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.18: GET /competencia/{id}/progreso
  echo '  "UAT-2.18_progreso": '
  curl -sf "$BASE_URL/competencia/$CID/progreso" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.19: GET /resultados/{id}/ranking?disciplina=STA (por categoría)
  echo '  "UAT-2.19_ranking_por_categoria": '
  curl -sf "$BASE_URL/resultados/$CID/ranking?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # UAT-2.20: GET /resultados/{torneo_id}/overall
  echo '  "UAT-2.20_overall": '
  curl -sf "$BASE_URL/resultados/$TORNEO_ID/overall" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'

  echo "}"
} > "$HTTP_OUTPUT"

rm -f "$HTTP_OUTPUT.pre"

echo "✓ Capa 2 completada → $HTTP_OUTPUT"
echo

# ── Resumen ───────────────────────────────────────────────────────────────────
echo "========================================"
echo "  UAT SP3 finalizado"
echo "  Artefactos en: quality/reports/uat/SP3/"
echo "========================================"
echo
echo "Verificaciones manuales pendientes:"
echo "  - capa1-pytest.txt  → todos PASSED (UAT-1.1 a UAT-1.8)"
echo "  - capa2-http.json   → UAT-2.3 access_token presente"
echo "  - capa2-http.json   → UAT-2.4 torneo estado=INSCRIPCION, disciplinas=[STA]"
echo "  - capa2-http.json   → UAT-2.10 inscriptos: al menos 6 entradas con STA"
echo "  - capa2-http.json   → UAT-2.12 grilla: pos.1=Enjuto(120s), pos.6=Almada(300s)"
echo "  - capa2-http.json   → UAT-2.13 status=204"
echo "  - capa2-http.json   → UAT-2.16 status=204"
echo "  - capa2-http.json   → UAT-2.17 estado=Finalizada"
echo "  - capa2-http.json   → UAT-2.18 total=6, ejecutadas=6, dns_count=0"
echo "  - capa2-http.json   → UAT-2.19 ranking: 4 categorías con posiciones correctas"
echo "                         SENIOR_M: Enjuto(393) pos.1, Almada(342) pos.2"
echo "                         SENIOR_F: Montangie(277) pos.1"
echo "                         MASTER_M: Valotto(273) pos.1, Alperin(244) pos.2"
echo "                         MASTER_F: Di Lernia(243) pos.1"
echo "  - capa2-http.json   → UAT-2.20 overall: 6 atletas"
echo
echo "Próximo paso: completar quality/reports/uat/SP3/report.md"
