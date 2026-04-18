#!/usr/bin/env bash
# run_uat.sh — UAT SP4: checks HTTP automáticos del flujo de performance.
#
# Uso (desde la raíz del proyecto):
#   bash tests/uat/sp4/run_uat.sh
#
# Precondición:
#   - seed_sp4.py ya ejecutado (crea las DBs y los IDs)
#   - Backend corriendo: uv run fastapi dev src/app.py
#
# Salidas:
#   quality/reports/uat/SP4/uat_ids.json      — IDs del seed (ya existe)
#   quality/reports/uat/SP4/capa1-http.json   — verificaciones HTTP automáticas
#   quality/reports/uat/SP4/checklist.md      — checklist listo para capa 2 manual

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
UAT_DIR="$ROOT/quality/reports/uat/SP4"
BASE_URL="${UAT_URL:-http://localhost:8000}"
IDS_FILE="$UAT_DIR/uat_ids.json"

echo
echo "========================================================"
echo "  UAT SP4 — Flujo de Performance (Capa 1: HTTP)"
echo "========================================================"
echo

# ── Verificar seed ejecutado ──────────────────────────────────────────────────
if [[ ! -f "$IDS_FILE" ]]; then
    echo "ERROR: $IDS_FILE no encontrado."
    echo "  Ejecutá primero: uv run python tests/uat/sp4/seed_sp4.py"
    exit 1
fi

TORNEO_ID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['torneo_id'])")
CID_DNF=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['competencia_dnf_id'])")
CID_STA=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['competencia_sta_id'])")
JUEZ_EMAIL=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['juez_email'])")
JUEZ_PASS=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['juez_password'])")

echo "  torneo_id      : $TORNEO_ID"
echo "  competencia_dnf: $CID_DNF"
echo "  competencia_sta: $CID_STA"
echo "  juez_email     : $JUEZ_EMAIL"
echo

# ── Verificar servidor ────────────────────────────────────────────────────────
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

# ── Obtener JWT ───────────────────────────────────────────────────────────────
echo "[Auth] Obteniendo JWT para juez..."
JWT_RESPONSE=$(curl -sf \
    -X POST -H "Content-Type: application/json" \
    -d "{\"email\": \"$JUEZ_EMAIL\", \"password\": \"$JUEZ_PASS\"}" \
    "$BASE_URL/auth/login")
JWT_TOKEN=$(echo "$JWT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
AUTH="Authorization: Bearer $JWT_TOKEN"
echo "✓ JWT obtenido"
echo

# ── Capa 1: verificaciones HTTP ───────────────────────────────────────────────
echo "[Capa 1] Ejecutando checks HTTP..."
echo

HTTP_OUTPUT="$UAT_DIR/capa1-http.json"

{
  echo "{"

  # ── UAT-1.1: /health ─────────────────────────────────────────────────────
  echo '  "UAT-1.1_health": '
  curl -sf "$BASE_URL/health" | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.2: Login juez ───────────────────────────────────────────────────
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST -H "Content-Type: application/json" \
    -d "{\"email\": \"$JUEZ_EMAIL\", \"password\": \"$JUEZ_PASS\"}" \
    "$BASE_URL/auth/login")
  echo '  "UAT-1.2_login_juez": '
  echo "  {\"http_status\": $STATUS, \"esperado\": 200, \"token_presente\": true}"
  echo ","

  # ── UAT-1.3: GET /torneos — torneo en EJECUCION visible ──────────────────
  echo '  "UAT-1.3_torneos": '
  TORNEOS=$(curl -sf "$BASE_URL/torneos")
  TORNEO_ESTADO=$(echo "$TORNEOS" | python3 -c "
import sys, json
t = json.load(sys.stdin)
match = next((x for x in t if x['torneo_id'] == '$TORNEO_ID'), None)
print(match['estado'] if match else 'NOT_FOUND')
")
  echo "  {\"torneo_id\": \"$TORNEO_ID\", \"estado\": \"$TORNEO_ESTADO\", \"esperado\": \"EJECUCION\"}"
  echo ","

  # ── UAT-1.4: GET /competencia?torneo_id=... ───────────────────────────────
  echo '  "UAT-1.4_competencias_del_torneo": '
  curl -sf "$BASE_URL/competencia?torneo_id=$TORNEO_ID" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.5: Estado competencia DNF ──────────────────────────────────────
  echo '  "UAT-1.5_estado_dnf": '
  curl -sf "$BASE_URL/competencia/$CID_DNF/estado?disciplina=DNF" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.6: Estado competencia STA ──────────────────────────────────────
  echo '  "UAT-1.6_estado_sta": '
  curl -sf "$BASE_URL/competencia/$CID_STA/estado?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.7: Grilla DNF — 10 atletas en orden ────────────────────────────
  echo '  "UAT-1.7_grilla_dnf": '
  curl -sf "$BASE_URL/competencia/$CID_DNF/grilla?disciplina=DNF" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.8: Grilla STA — 3 atletas en orden ─────────────────────────────
  echo '  "UAT-1.8_grilla_sta": '
  curl -sf "$BASE_URL/competencia/$CID_STA/grilla?disciplina=STA" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'
  echo ","

  # ── UAT-1.9: Performance actual DNF — R01 Jorge en Llamada ───────────────
  echo '  "UAT-1.9_performance_actual_dnf": '
  ACTUAL=$(curl -sf "$BASE_URL/competencia/$CID_DNF/performance/actual" || echo "null")
  echo "  $ACTUAL"
  echo ","

  # ── UAT-1.10: Progreso DNF — 4 atletas avanzados ─────────────────────────
  echo '  "UAT-1.10_progreso_dnf": '
  curl -sf "$BASE_URL/competencia/$CID_DNF/progreso" \
    | python3 -m json.tool --indent 2 | sed 's/^/  /'

  echo "}"
} > "$HTTP_OUTPUT"

echo "✓ Capa 1 completada → $HTTP_OUTPUT"
echo

# ── Verificar estados esperados ───────────────────────────────────────────────
echo "[Verificación] Chequeando estados esperados..."

DNF_ESTADO=$(python3 -c "
import json
data = json.load(open('$HTTP_OUTPUT'))
print(data.get('UAT-1.5_estado_dnf', {}).get('estado', 'N/A'))
")
STA_ESTADO=$(python3 -c "
import json
data = json.load(open('$HTTP_OUTPUT'))
print(data.get('UAT-1.6_estado_sta', {}).get('estado', 'N/A'))
")
GRILLA_DNF_COUNT=$(python3 -c "
import json
grilla = json.load(open('$HTTP_OUTPUT')).get('UAT-1.7_grilla_dnf', [])
print(len(grilla) if isinstance(grilla, list) else 'N/A')
")
GRILLA_STA_COUNT=$(python3 -c "
import json
grilla = json.load(open('$HTTP_OUTPUT')).get('UAT-1.8_grilla_sta', [])
print(len(grilla) if isinstance(grilla, list) else 'N/A')
")

echo
printf "  %-40s %s\n" "UAT-1.3 torneo.estado == EJECUCION" "$([ "$TORNEO_ESTADO" = "EJECUCION" ] && echo "✓ OK" || echo "✗ FALLO (got: $TORNEO_ESTADO)")"
printf "  %-40s %s\n" "UAT-1.5 DNF.estado == EnEjecucion"  "$([ "$DNF_ESTADO" = "EnEjecucion" ] && echo "✓ OK" || echo "✗ FALLO (got: $DNF_ESTADO)")"
printf "  %-40s %s\n" "UAT-1.6 STA.estado == EnEjecucion"  "$([ "$STA_ESTADO" = "EnEjecucion" ] && echo "✓ OK" || echo "✗ FALLO (got: $STA_ESTADO)")"
printf "  %-40s %s\n" "UAT-1.7 grilla DNF tiene 10 atletas" "$([ "$GRILLA_DNF_COUNT" = "10" ] && echo "✓ OK" || echo "✗ FALLO (got: $GRILLA_DNF_COUNT)")"
printf "  %-40s %s\n" "UAT-1.8 grilla STA tiene 3 atletas"  "$([ "$GRILLA_STA_COUNT" = "3" ] && echo "✓ OK" || echo "✗ FALLO (got: $GRILLA_STA_COUNT)")"
echo

# ── Generar checklist ─────────────────────────────────────────────────────────
CHECKLIST="$UAT_DIR/checklist.md"

cat > "$CHECKLIST" << CHECKLIST_EOF
# Checklist UAT SP4 — Flujo de Performance (Capa 2 Manual)

**Generado:** $(date "+%Y-%m-%d %H:%M")
**Frontend:** http://localhost:5173
**Login:** $JUEZ_EMAIL / $JUEZ_PASS

---

## Setup previo

- [ ] Frontend corriendo: \`cd frontend && npm run dev\`
- [ ] Backend corriendo en puerto 8000
- [ ] Abrir http://localhost:5173 en Chrome/Safari (modo móvil en DevTools)
- [ ] Hacer login con el usuario juez

---

## Competencia DNF

**Cómo acceder:** Login → /juez/disciplinas → seleccionar DNF → grilla → tocar atleta

### E-01 — DNS (Diego Vega, AP=40m)
*Verifica el flujo de No Se Presenta*

- [ ] Atleta aparece en grilla con estado AnunciadaAP
- [ ] Paso 1: botón "LLAMAR ATLETA" visible y funcional
- [ ] Paso 2: aparece opción "DNS — NO SE PRESENTA"
- [ ] Al confirmar DNS: pantalla de completado muestra "DNS REGISTRADO"
- [ ] Botón "SIGUIENTE ATLETA" navega de vuelta a grilla

---

### E-02 — BKO mid-performance (Laura Romero, AP=50m)
*Verifica el blackout durante la performance*

- [ ] Llegar al paso 4 (performance en curso)
- [ ] Botón "BKO — BLACK-OUT" visible
- [ ] Al presionar BKO: aparece formulario StepBKO con selector RP (metros.centímetros) y motivo DQ
- [ ] Ingresar metros=25, centímetros=50
- [ ] Seleccionar motivo: BKO SUBACUÁTICO (requiere campo distancia blackout)
- [ ] Ingresar distancia blackout (ej: 20.00)
- [ ] Botón CONFIRMAR habilitado solo cuando todos los campos están completos
- [ ] Al confirmar: pantalla completada muestra "TARJETA ROJA"
- [ ] Botón CANCELAR vuelve al paso 4 limpiando los campos

---

### E-03 — Blanca simple (Carlos Ibañez, AP=60m)
*Flujo dorado completo: paso 1 → paso 6*

- [ ] Flujo completo paso 1 (llamar) → paso 2 (confirmar) → paso 3 (OT) → paso 4 (performance) → paso 5 (RP)
- [ ] Paso 5: ingresar metros=58, centímetros=00
- [ ] Paso 6: tres botones de tarjeta sin texto, con colores (blanco, rojo, amarillo)
- [ ] Seleccionar BLANCA: selector resaltado en verde
- [ ] No aparece selector de motivo DQ
- [ ] Botón CONFIRMAR TARJETA habilitado
- [ ] Pantalla completada muestra marca y "TARJETA BLANCA"

---

### E-04 — Blanca con penalizaciones (Ana Flores, AP=70m)
*Verifica el selector de penalizaciones*

- [ ] Llegar al paso 6 con tarjeta BLANCA seleccionada
- [ ] Aparece sección de penalizaciones con 4 tipos
- [ ] Agregar 1 penalización "Sin contacto pared": contador sube a 1
- [ ] Agregar 1 penalización "Fuera de carril": contador sube a 1
- [ ] Resumen muestra "2 penalizaciones · −6m"
- [ ] Botón quitar (−) reduce el contador; no puede bajar de 0
- [ ] Al confirmar: pantalla completada muestra "TARJETA BLANCA CON PENALIZACIONES" y "2 penalizaciones"

---

### E-05 — Roja DQ estándar (Roberto Chen, AP=80m)
*Verifica el selector de motivo DQ sin distancia*

- [ ] Paso 6: seleccionar ROJA
- [ ] Aparece selector de motivo DQ
- [ ] Seleccionar "PROTOCOLO SUPERFICIE" (no requiere distancia)
- [ ] Campo distancia blackout NO aparece
- [ ] Botón CONFIRMAR habilitado con motivo seleccionado
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### E-06 — Roja BKO post-performance (Patricia Ruiz, AP=90m)
*Verifica distancia blackout obligatoria*

- [ ] Paso 6: seleccionar ROJA
- [ ] Seleccionar "BKO SUPERFICIE": aparece campo "Distancia blackout"
- [ ] Botón CONFIRMAR deshabilitado hasta completar distancia
- [ ] Ingresar distancia=15.00
- [ ] Botón CONFIRMAR se habilita
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### E-07 — Resolver revisión → Blanca (Martin Acosta, ya en EnRevision)
*Resume: atleta ya tiene tarjeta amarilla asignada*

- [ ] En grilla: atleta aparece con estado EnRevision
- [ ] Al seleccionarlo: flow inicia directo en **paso 7** (no pasa por 1-6)
- [ ] Pantalla muestra "TARJETA AMARILLA · Resolución pendiente"
- [ ] Botón "RESOLVER → BLANCA" disponible
- [ ] Al seleccionar Blanca: no aparece selector de motivo DQ
- [ ] Botón CONFIRMAR RESOLUCIÓN habilitado
- [ ] Pantalla completada muestra "TARJETA BLANCA"

---

### E-08 — Resolver revisión → Roja (Silvia Casas, ya en EnRevision)
*Resume: atleta ya tiene tarjeta amarilla asignada*

- [ ] Flow inicia en **paso 7**
- [ ] Seleccionar "RESOLVER → ROJA": aparece selector de motivo DQ
- [ ] Seleccionar motivo DQ (ej: INFRACCIÓN TÉCNICA)
- [ ] Botón CONFIRMAR habilitado con motivo seleccionado
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### R-01 — Resume en paso 2 (Jorge Mendez, ya Llamada)
*Verifica que el flow retoma el estado correcto*

- [ ] En grilla: atleta aparece con estado Llamada
- [ ] Al seleccionarlo: flow inicia directo en **paso 2** (Confirmar presencia)
- [ ] Paso 1 (Llamada) NO aparece (ya fue ejecutado)
- [ ] Continuar flujo normal desde paso 2

---

### R-02 — Resume en paso 6 (Claudia Rios, ya ResultadoRegistrado)
*Verifica que el flow retoma el estado correcto*

- [ ] En grilla: atleta aparece con estado ResultadoRegistrado
- [ ] Al seleccionarlo: flow inicia directo en **paso 6** (Tarjeta)
- [ ] Pasos 1-5 NO aparecen
- [ ] AtletaCard muestra el RP ya registrado (125m)
- [ ] Continuar desde paso 6

---

## Competencia STA

**Cómo acceder:** Login → /juez/disciplinas → seleccionar STA → grilla → tocar atleta

### T-01 — DNS STA (Javier Herrera, AP=120s)
*Verifica DNS en disciplina de tiempo*

- [ ] Flow normal hasta paso 2
- [ ] AtletaCard muestra "AP: 2:00 min" (no en metros)
- [ ] Confirmar DNS → completado "DNS REGISTRADO"

---

### T-02 — BKO STA mid-performance (Carolina Espinoza, AP=180s)
*Verifica BKO sin selector de metros (STA usa tiempo)*

- [ ] Llegar al paso 4
- [ ] Presionar "BKO — BLACK-OUT"
- [ ] StepBKO **NO** muestra el selector RP (metros/centímetros) — es STA
- [ ] Solo aparece: selector de motivo DQ
- [ ] Seleccionar BKO SUBACUÁTICO
- [ ] Botón CONFIRMAR habilitado solo con motivo (sin necesidad de metros ni distancia)
- [ ] Confirmar → "TARJETA ROJA"

---

### T-03 — Blanca STA (Fernando Bravo, AP=240s)
*Verifica el flujo de tiempo completo*

- [ ] Paso 3: texto "Las vías respiratorias del atleta entran en contacto con el agua"
- [ ] Botón VÍAS RESPIRATORIAS EN AGUA (en lugar de "ATLETA INICIA")
- [ ] Paso 5: selector RP de tiempo (minutos + segundos, no metros)
- [ ] Ingresar 4 minutos, 05 segundos
- [ ] Paso 6: confirmar BLANCA
- [ ] Pantalla completada muestra "4:05 min"

---

## Hallazgos de UI

Documentar aquí cualquier problema encontrado durante el walk-through:

$(cat "$ROOT/tests/uat/sp4/hallazgos-smoke-test.md" 2>/dev/null || echo "(ninguno previo)")

---

*Generado automáticamente por run_uat.sh — $(date)*
CHECKLIST_EOF

echo "✓ Checklist generado → $CHECKLIST"
echo

# ── Resumen ───────────────────────────────────────────────────────────────────
echo "========================================================"
echo "  Capa 1 completada"
echo "========================================================"
echo
echo "  Artefactos:"
echo "    $HTTP_OUTPUT"
echo "    $CHECKLIST"
echo
echo "  Para la Capa 2 (manual):"
echo "    1. Levantá el frontend : cd frontend && npm run dev"
echo "    2. Abrí el checklist   : $CHECKLIST"
echo "    3. Ejecutá cada escenario en http://localhost:5173"
echo
