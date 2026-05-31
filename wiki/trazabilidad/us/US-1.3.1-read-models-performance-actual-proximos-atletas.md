---
title: "US-1.3.1 — Read Models: PerformanceActual, ProximosAtletas, ProgresoCompetencia"
type: trazabilidad-us
sp: SP1
inc: INC-1.3
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.3.1
tests_count: 174
rf:
  - RF-EJ-05-cronometraje-manual-por-juez
software_items:
  - src/competencia/application/queries/obtener_performance_actual.py
test_units:
  - tests/features/US-1.3.1-interfaz-juez.feature
  - tests/integration/competencia/test_api_interfaz_juez.py
origen_tipo: rf
---

# US-1.3.1 — Read Models

## Descripción

Construye los modelos de lectura necesarios para que el juez opere en tiempo real durante la competencia.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-05-cronometraje-manual-por-juez]] | Cronometraje manual — juez ingresa el tiempo |

## Read Models implementados

| Modelo | Propósito |
|--------|-----------|
| `PerformanceActual` | Estado actual del atleta en turno (AP, tiempo transcurrido, estado) |
| `ProximosAtletas` | Lista de atletas que compiten a continuación según grilla |
| `ProgresoCompetencia` | Porcentaje de avance de la disciplina (atletas completados / total) |

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.3.1 | ✅ |
| **Total acumulado** | **174 tests (97.53%)** |

## Estado

✅ Completado — 2026-03-23
