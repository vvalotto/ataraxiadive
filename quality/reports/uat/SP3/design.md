# Diseño de Pruebas UAT — SP3 "El Torneo"

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP3 — El Torneo |
| **Baseline** | BL-003 |
| **US cubiertas** | US-3.1.1 a US-3.5.3 + SP-ADJ-04 |
| **Fecha diseño** | 2026-04-03 |
| **Autor** | Victor Valotto |

---

## Objetivo

Verificar de forma observable que el pipeline completo de SP3 cumple el DoD:
un torneo real creado, atletas inscriptos, competencia STA ejecutada con ranking
segmentado por categoría y overall calculado.

Este UAT usa datos reales del torneo **"Apnea Indoor Buenos Aires 2025"** como oráculo
empírico del dominio (HITO-17). Los APs y RPs son valores reales del evento.

---

## Contexto técnico

SP3 agregó endpoints HTTP en los nuevos BCs:
- **Torneo:** `POST /torneos`, `PUT /torneos/{id}/...` (ciclo de vida + disciplinas/jueces)
- **Identidad:** `POST /auth/registro`, `POST /auth/login`
- **Registro:** `POST /registro/atletas`, `POST /registro/inscripciones`, `GET /torneos/{id}/inscriptos`
- **Resultados:** `GET /resultados/{id}/overall` (nuevo SP3)

Los comandos de ejecución interna de Competencia (ConfigurarIntervaloOT, GenerarGrilla,
RegistrarAP, LlamarAtleta, RegistrarResultado, AsignarTarjeta) siguen siendo Application layer.
Esto mantiene el patrón **UAT híbrido en dos capas**, con mayor superficie HTTP que SP2.

---

## Estrategia

```
Capa 1 — Automatizada (pytest)
  Reutiliza tests de integración e2e existentes:
    - tests/integration/e2e/test_flujo_torneo_competencia.py
    - tests/features/steps/test_US_3_3_2_steps.py (BDD flujo completo)
    - tests/integration/resultados/test_calcular_overall_integration.py
    - tests/integration/resultados/test_calcular_ranking_integration.py
  Evidencia: salida pytest -v

Capa 2 — HTTP (seed + curl al servidor real)
  Pipeline: Identidad → Torneo → Registro → Seed competencia → Competencia → Resultados
  Seed maneja: ConfigurarIntervaloOT + RegistrarAP ×6 + GenerarGrilla + ejecución completa
  HTTP verifica todos los endpoints nuevos de SP3 + Resultados rankin/overall
  Evidencia: respuestas JSON capturadas
```

---

## Dataset origen: Buenos Aires 2025

**Subconjunto seleccionado:** disciplina STA, 6 atletas reales, 4 categorías.

Criterio de selección: cubre SENIOR y MASTER (masculino y femenino), permite verificar
ranking segmentado por categoría (US-ADJ-4.5, RF-PM-05) y overall multi-categoría (US-3.5.x).

| ID UAT | Nombre real | Categoria app | Club | AP (MM:SS) | AP (s) | RP real (s) | Tarjeta UAT |
|--------|-------------|---------------|------|------------|--------|-------------|-------------|
| A | José Enjuto | SENIOR_MASCULINO | FREEDIVING ROSARIO | 02:00 | 120 | 393 | Blanca |
| B | Mauro Almada | SENIOR_MASCULINO | FREEDIVING BUENOS AIRES | 05:00 | 300 | 342 | Blanca |
| C | M. de los Milagros Montangie | SENIOR_FEMENINO | ESC. BUCEO CETACEOS | 03:00 | 180 | 277 | Blanca |
| D | Víctor Valotto | MASTER_MASCULINO | REGATAS SANTA FE | 03:15 | 195 | 273 | Blanca |
| E | Alejandro Alperin | MASTER_MASCULINO | OHANA FREEDIVERS | 04:01 | 241 | 244 | Blanca |
| F | Alina Di Lernia | MASTER_FEMENINO | ESCUELA MARES | 04:00 | 240 | 243 | Blanca |

> Los RPs reales se expresaban como MM:SS.cs en el dataset; se convierten a segundos enteros
> usando `TiempoAP.desde_mmss()` (US-ADJ-4.6). Tarjeta blanca en todos para simplificar ranking.

---

## Escenario DoD

**Grilla STA** — orden ascendente (menor AP primero, política P-01 corregida en US-ADJ-4.2):

| Posición | Atleta | AP (s) | Categoría |
|----------|--------|--------|-----------|
| 1 | A — Enjuto | 120 | SENIOR_MASCULINO |
| 2 | C — Montangie | 180 | SENIOR_FEMENINO |
| 3 | D — Valotto | 195 | MASTER_MASCULINO |
| 4 | F — Di Lernia | 240 | MASTER_FEMENINO |
| 5 | E — Alperin | 241 | MASTER_MASCULINO |
| 6 | B — Almada | 300 | SENIOR_MASCULINO |

**Ranking por categoría esperado post-ejecución:**

| Categoría | Pos | Atleta | RP (s) | En podio |
|-----------|-----|--------|--------|----------|
| SENIOR_MASCULINO | 1 | A — Enjuto | 393 | ✅ |
| SENIOR_MASCULINO | 2 | B — Almada | 342 | ✅ |
| SENIOR_FEMENINO | 1 | C — Montangie | 277 | ✅ |
| MASTER_MASCULINO | 1 | D — Valotto | 273 | ✅ |
| MASTER_MASCULINO | 2 | E — Alperin | 244 | ✅ |
| MASTER_FEMENINO | 1 | F — Di Lernia | 243 | ✅ |

> El atleta B registra el último resultado → dispara `CompetenciaFinalizada` → `CalcularRanking`
> automáticamente (política P-08). El ranking resultante debe coincidir con el orden real del
> dataset de Buenos Aires 2025.

---

## Capa 1 — Tests Automatizados

**Archivos:**
```
tests/integration/e2e/test_flujo_torneo_competencia.py
tests/features/steps/test_US_3_3_2_steps.py
tests/integration/resultados/test_calcular_overall_integration.py
tests/integration/resultados/test_calcular_ranking_integration.py
```

**Ejecutar:**
```bash
pytest tests/integration/e2e/test_flujo_torneo_competencia.py \
       tests/features/steps/test_US_3_3_2_steps.py \
       tests/integration/resultados/test_calcular_overall_integration.py \
       tests/integration/resultados/test_calcular_ranking_integration.py -v
```

| ID | Archivo | Qué verifica |
|----|---------|--------------|
| UAT-1.1 | test_flujo_torneo_competencia.py::test_flujo_completo_inscripcion_ap_grilla | Pipeline Torneo→Registro→Competencia (grilla generada con torneo_id) |
| UAT-1.2 | test_flujo_torneo_competencia.py::test_atleta_sin_ap_no_aparece_en_grilla | Atleta inscripto sin AP no aparece en grilla |
| UAT-1.3 | test_flujo_torneo_competencia.py::test_multiples_atletas_ordenados_por_ap_ascendente | Grilla STA orden ascendente (P-01 corregido) |
| UAT-1.4 | test_US_3_3_2_steps.py::test_flujo_completo | BDD: Torneo → Registro → Competencia completo |
| UAT-1.5 | test_US_3_3_2_steps.py::test_atleta_sin_ap | BDD: inscripto sin AP excluido de grilla |
| UAT-1.6 | test_US_3_3_2_steps.py::test_orden_ap | BDD: orden ascendente verificado |
| UAT-1.7 | test_calcular_ranking_integration.py | Ranking segmentado por categoría (US-ADJ-4.5) |
| UAT-1.8 | test_calcular_overall_integration.py | Overall calculado con política P-09 |

**Criterio de aceptación Capa 1:** todos PASSED, 0 FAILED.

---

## Capa 2 — Verificación HTTP

### Setup

```bash
# 1. Sembrar flujo completo en DB real
uv run python tests/uat/sp3/seed_sp3.py

# 2. Levantar servidor (en otra terminal)
uv run fastapi dev src/app.py
```

El seed escribe los IDs en `quality/reports/uat/SP3/uat_ids.json`.

### Endpoints verificados

| ID | BC | Endpoint | Método | Verificación | Resultado esperado |
|----|----|---------|---------|--------------|--------------------|
| UAT-2.1 | — | `/health` | GET | Servidor disponible | `200 {"status": "ok"}` |
| UAT-2.2 | Identidad | `/auth/registro` | POST | Registrar organizador | `201` |
| UAT-2.3 | Identidad | `/auth/login` | POST | Login → JWT token | `200 {"access_token": ...}` |
| UAT-2.4 | Torneo | `/torneos` | POST | Crear torneo BA 2025 | `201 {"torneo_id": ...}` |
| UAT-2.5 | Torneo | `/torneos/{id}/disciplinas` | PUT | Asignar STA | `200` |
| UAT-2.6 | Torneo | `/torneos/{id}/disciplinas/STA/juez` | PUT | Asignar juez UAT | `200` |
| UAT-2.7 | Torneo | `/torneos/{id}/abrir-inscripcion` | PUT | Estado → INSCRIPCION | `200` |
| UAT-2.8 | Registro | `/registro/atletas` | POST ×6 | Registrar 6 atletas reales | `201 ×6` |
| UAT-2.9 | Registro | `/registro/inscripciones` | POST ×6 | Inscribir en STA con torneo_id | `201 ×6` |
| UAT-2.10 | Registro | `/torneos/{id}/inscriptos` | GET | 6 atletas inscritos en STA | `200 [6 items]` |
| UAT-2.11 | Competencia | `/competencia` | POST | Crear competencia STA con torneo_id | `200 {"competencia_id": ...}` |
| UAT-2.12 | Competencia | `/competencia/{id}/grilla` | GET | 6 entradas en orden ascendente | pos.1=Enjuto(120s), pos.6=Almada(300s) |
| UAT-2.13 | Competencia | `/competencia/{id}/confirmar-grilla` | POST | 204 No Content | GrillaConfirmada en Event Store |
| UAT-2.14 | Competencia | `/competencia/{id}/iniciar` | POST | 204 No Content | CompetenciaIniciada en Event Store |
| UAT-2.15 | Competencia | `/competencia/{id}/estado` | GET | Post-iniciar | `estado=en_ejecucion` |
| UAT-2.16 | Competencia | `/competencia/{id}/progreso` | GET | Post-ejecución completa | `total=6, ejecutadas=6, dns_count=0` |
| UAT-2.17 | Competencia | `/competencia/{id}/events` | GET | Tipos de eventos SP3 | CompetenciaFinalizada presente |
| UAT-2.18 | Resultados | `/resultados/{id}/ranking?disciplina=STA` | GET | Ranking por categoría | 4 categorías con posiciones correctas |
| UAT-2.19 | Resultados | `/resultados/{torneo_id}/overall` | GET | Overall calculado | Todos los atletas presentes |
| UAT-2.20 | Torneo | `/torneos/{id}` | GET | Estado final del torneo | `estado=EJECUCION` |

**Criterio de aceptación Capa 2:** 20/20 con status esperado y valores correctos.

---

## Invariantes verificados end-to-end

| Invariante | Descripción | Cómo se verifica |
|------------|-------------|-----------------|
| INV-T-01 | Torneo transita estados en secuencia (CREADO→INSCRIPCION→EJECUCION) | UAT-2.7 → UAT-2.20 |
| INV-A-05 | Atleta con `club` obligatorio | UAT-2.8 (todos pasan club) |
| INV-D-01 | Acrónimos disciplinas = estándar AIDA (DBF, SPE) | Dataset + enum corregido |
| INV-P-01 | Grilla STA en orden ascendente (menor AP primero) | UAT-2.12 pos.1=Enjuto(120s) |
| INV-R-01 | Ranking segmentado por categoría (sin mezcla) | UAT-2.18 (4 secciones) |
| P-08 | CompetenciaFinalizada → CalcularRanking automático | UAT-2.17 → UAT-2.18 |
| P-09 | Overall incluye atletas de todas las categorías | UAT-2.19 (6 atletas) |
| RF-PM-05 | Rankings por categoría y género | UAT-2.18 (SENIOR_M, SENIOR_F, MASTER_M, MASTER_F) |

---

## Verificaciones de datos reales

Los resultados de UAT-2.18 deben coincidir con los resultados oficiales del torneo BA 2025:

| Categoría | Pos UAT | Atleta | RP UAT (s) | RP Real (dataset) | ¿Coincide? |
|-----------|---------|--------|------------|-------------------|------------|
| SENIOR_MASCULINO | 1 | Enjuto | 393 | 06:33.05 = 393s | ✅ |
| SENIOR_MASCULINO | 2 | Almada | 342 | 05:42.09 = 342s | ✅ |
| SENIOR_FEMENINO | 1 | Montangie | 277 | 04:37.14 = 277s | ✅ |
| MASTER_MASCULINO | 1 | Valotto | 273 | 04:32.98 = 273s | ✅ |
| MASTER_MASCULINO | 2 | Alperin | 244 | 04:04.38 = 244s | ✅ |
| MASTER_FEMENINO | 1 | Di Lernia | 243 | 04:02.56 = 243s | ✅ |

---

## Artefactos generados

| Archivo | Contenido |
|---------|-----------|
| `design.md` | Este documento |
| `uat_ids.json` | IDs generados por el seed (torneo + atletas + competencia) |
| `capa1-pytest.txt` | Salida completa de pytest -v |
| `capa2-http.json` | Respuestas JSON de los 20 endpoints |
| `report.md` | Reporte de ejecución con resultado final |
