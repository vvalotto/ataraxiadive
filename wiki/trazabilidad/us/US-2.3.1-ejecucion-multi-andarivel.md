---
title: "US-2.3.1 — Ejecución multi-andarivel"
type: trazabilidad-us
sp: SP2
inc: INC-2.3
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.3.1
tests_count: null
rf:
  - RF-PR-06-competencia-multi-andarivel
software_items:
  - src/competencia/domain/aggregates/competencia.py
test_units:
  - tests/features/US-2.3.1-ejecucion-multi-andarivel.feature
  - tests/integration/competencia/test_andariveles_activos_integration.py
origen_tipo: rf
---

# US-2.3.1 — Ejecución multi-andarivel

## Descripción

Permite que varios atletas compitan en paralelo en andariveles separados, distribuyendo la grilla de salida entre ellos sin conflictos.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PR-06-competencia-multi-andarivel]] | Andariveles simultáneos — varios atletas compiten en paralelo |

## Contenido implementado

- Distribución de atletas en grilla por andarivel (columna)
- Garantía de no conflicto entre andariveles (dos atletas no comparten OT en el mismo andarivel)

## Invariantes aplicadas

- INV-C-05: no pueden existir dos atletas en el mismo andarivel en el mismo OT

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.3.

## Estado

✅ Completado — 2026-03-28
