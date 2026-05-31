---
title: "US-ADJ-8.2 — SP-ADJ-08: selector de grilla filtrado y transición a premiación"
type: trazabilidad-us
sp: SP-ADJ-08
inc: SP-ADJ-08
bc: torneo, competencia
estado: cerrada
fecha_cierre: "2026-04-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §22
  - docs/plans/sp-adj-08/PLAN-SP-ADJ-08.md
us_id: US-ADJ-8.2
tests_count: null
rf: []
software_items:
  - src/torneo/application/commands/transicionar_torneo.py
test_units:
  - tests/features/US-ADJ-8.2-restringir-operaciones-torneo-fase.feature
  - tests/integration/torneo/test_ejecucion_precondicion.py
origen_tipo: calidad
---

# US-ADJ-8.2 — SP-ADJ-08: selector de grilla filtrado y transición a premiación

## Descripción

Resolución de hallazgos UAT-5.2-02, 05, 07: el selector de grilla se filtra por `GET /torneos/{id}/disciplinas`; la transición `Pasar a premiacion` se habilita solo cuando todas las competencias esperadas están en estado `Finalizada`.

## Contenido implementado

- `TorneoCompetenciasPage` — selector de grilla filtrado por disciplinas del torneo
- `AccionesPanel` — precondición de todas-finalizadas para `Pasar a premiacion`

## Estado

✅ Completado — 2026-04-22 · PR #107
