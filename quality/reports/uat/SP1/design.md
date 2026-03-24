# Diseño de Pruebas UAT — SP1 "La Performance"

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP1 — La Performance |
| **Baseline** | BL-001 |
| **US cubiertas** | US-1.2.1 a US-1.4.2 |
| **Fecha diseño** | 2026-03-24 |
| **Autor** | Victor Valotto |

---

## Objetivo

Verificar de forma observable que el BC Competencia cumple el DoD de SP1:
5 performances ejecutadas (flujo completo AP → tarjeta), Event Store con traza completa
y Read Models consistentes.

Este UAT genera evidencia para el cierre formal de SP1 y alimenta la retrospectiva de BL-001.

---

## Contexto técnico

En SP1, los **comandos no están expuestos via HTTP** — el router del BC Competencia
expone solo endpoints GET (Read Models + audit log). Los comandos se invocan directamente
por código en la capa Application.

Esto determina la estrategia: **UAT híbrido en dos capas**.

---

## Estrategia

```
Capa 1 — Automatizada (pytest)
  Ejecuta el flujo DoD SP1 completo via Application handlers.
  Verifica invariantes, Event Store y Read Models desde el código.
  Evidencia: salida pytest -v

Capa 2 — HTTP Manual (curl)
  Verifica los 4 endpoints GET del servidor real contra una DB sembrada.
  Confirma que el servidor levanta, la DB persiste y los endpoints responden.
  Evidencia: respuestas JSON capturadas
```

---

## Escenario DoD

5 atletas con disciplina STA (Static Apnea):

| Atleta | AP | Flujo | Tarjeta |
|--------|----|-------|---------|
| A | 60m | AP → Llamar → Resultado 60m → Tarjeta | Blanca |
| B | 40m | AP → Llamar → DNS | — |
| C | 80m | AP → Llamar → Resultado 72m → Tarjeta | Amarilla (sin superficie) |
| D | 50m | AP → Llamar → Resultado 55m → Tarjeta → Corregir 53m | Blanca |
| E | 90m | AP → Llamar → Resultado 90m → Tarjeta | Roja (black-out, dist. 45m) |

---

## Capa 1 — Tests Automatizados

**Archivo:** `tests/integration/competencia/test_flujo_e2e.py`

**Ejecutar:**
```bash
pytest tests/integration/competencia/test_flujo_e2e.py -v
```

| ID | Test | Qué verifica |
|----|------|--------------|
| UAT-1.1 | `test_get_events_retorna_traza_completa` | ≥15 eventos en Event Store |
| UAT-1.2 | `test_get_events_orden_de_secuencia` | Eventos en orden de inserción |
| UAT-1.3 | `test_get_events_campos_obligatorios` | Estructura completa de EventoDTO |
| UAT-1.4 | `test_get_events_incluye_tipos_esperados` | 6 tipos de evento presentes |
| UAT-1.5 | `test_progreso_consistente_con_event_store` | `total=5, ejecutadas=4, dns=1` |
| UAT-1.6 | `test_blackout_con_distancia_en_event_store` | INV-P-10 + distancia serializada |
| UAT-1.7 | `test_get_events_sin_eventos_retorna_lista_vacia` | Robustez: competencia vacía |

**Criterio de aceptación Capa 1:** 7/7 PASSED, 0 FAILED.

---

## Capa 2 — Verificación HTTP

**Setup:**
```bash
# 1. Inicializar DB (si no existe)
uv run alembic upgrade head

# 2. Sembrar flujo DoD en DB real
uv run python tests/uat/sp1/seed_competencia.py

# 3. Levantar servidor (en otra terminal)
uv run fastapi dev src/app.py
```

El seed escribe los IDs en `quality/reports/uat/SP1/uat_ids.json`.

| ID | Endpoint | Verificación | Resultado esperado |
|----|----------|--------------|-------------------|
| UAT-2.1 | `GET /health` | Status + body | `200 {"status": "ok"}` |
| UAT-2.2 | `GET /competencia/{id}/events` | `total_events`, secuencia, tipos | ≥18 eventos ordenados, 6 tipos presentes |
| UAT-2.3 | `GET /competencia/{id}/progreso` | Contadores | `total=5, ejecutadas=4, dns_count=1, completadas=5` |
| UAT-2.4 | `GET /competencia/{id}/performance/proximas` | Lista al final del flujo | `[]` (todos ejecutados) |

**Criterio de aceptación Capa 2:** 4/4 con status 200 y valores esperados.

---

## Invariantes verificados end-to-end

| Invariante | Descripción | Cómo se verifica |
|------------|-------------|------------------|
| INV-P-05 | LlamarAtleta solo si Performance = AnunciadaAP | Flujo secuencial; test UAT-1.1 |
| INV-P-06 | RegistrarResultado solo si Performance = Llamada | Flujo secuencial; test UAT-1.1 |
| INV-P-07 | AsignarTarjeta solo si ResultadoRegistrado previo | Flujo secuencial; test UAT-1.4 |
| INV-P-08 | RegistrarDNS solo si Performance = Llamada | Atleta B; test UAT-1.4 |
| INV-P-09 | Resultado y DNS mutuamente excluyentes | Atleta B (DNS, sin resultado); test UAT-1.5 |
| INV-P-10 | CorregirResultado solo si Performance = Ejecutada | Atleta D post-tarjeta; test UAT-1.6 |

---

## Ejecución automatizada

El script `tests/uat/sp1/run_uat.sh` orquesta Capa 1 + seed + Capa 2 y deposita
todos los artefactos en `quality/reports/uat/SP1/`.

```bash
bash tests/uat/sp1/run_uat.sh
```

---

## Artefactos generados

| Archivo | Contenido |
|---------|-----------|
| `design.md` | Este documento |
| `uat_ids.json` | IDs generados por el seed (competencia + atletas) |
| `capa1-pytest.txt` | Salida completa de pytest -v |
| `capa2-http.json` | Respuestas JSON de los 4 endpoints |
| `report.md` | Reporte de ejecución con resultado final |
