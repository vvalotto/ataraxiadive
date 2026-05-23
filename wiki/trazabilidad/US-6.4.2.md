---
title: "US-6.4.2 — Materializar proyección competencias_por_torneo en CalcularOverallHandler"
type: trazabilidad-us
sp: SP6
inc: INC-6.4
bc: resultados, competencia
estado: cerrada
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §32
us_id: US-6.4.2
tests_count: null
---

# US-6.4.2 — Materializar proyección competencias_por_torneo en CalcularOverallHandler

## Descripción

Corrección del hallazgo ARCH-01: `CalcularOverallHandler` hacía un scan O(n) sobre todas las competencias para encontrar las del torneo. Se materializa la proyección `competencias_por_torneo` para eliminar el scan lineal.

## Contenido implementado

- Proyección `competencias_por_torneo` materializada en BC Resultados
- `CalcularOverallHandler` — usa proyección en lugar de O(n) scan

## Estado

✅ Completado — 2026-05-10 · PR #158
