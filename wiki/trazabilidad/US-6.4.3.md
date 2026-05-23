---
title: "US-6.4.3 — Corregir D-05: imports cross-BC en resultados/api y competencia/api"
type: trazabilidad-us
sp: SP6
inc: INC-6.4
bc: resultados, competencia, registro
estado: cerrada
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §32
us_id: US-6.4.3
tests_count: null
---

# US-6.4.3 — Corregir D-05: imports cross-BC en resultados/api y competencia/api

## Descripción

Corrección de los hallazgos ARCH-02 y AA-03: `resultados/api` y `competencia/api` importaban infraestructura de otros BCs directamente (violación de fronteras). También reduce la dependencia fan-out del BC `registro`.

## Contenido implementado

- `resultados/api` — eliminados imports cross-BC a infraestructura ajena (ARCH-02)
- `competencia/api` — idem (AA-03)
- BC `registro` — reducción de fan-out (D↑)

## Estado

✅ Completado — 2026-05-10 · PR #160
