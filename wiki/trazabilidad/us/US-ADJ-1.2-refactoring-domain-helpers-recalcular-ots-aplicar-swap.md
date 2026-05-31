---
title: "US-ADJ-1.2 — Refactoring domain: helpers _recalcular_ots + _aplicar_swap_posicion"
type: trazabilidad-us
sp: SP-ADJ-01
inc: SP-ADJ-01
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §7
us_id: US-ADJ-1.2
tests_count: null
rf: []
software_items:
  - src/competencia/domain/aggregates/performance.py
test_units: null
origen_tipo: calidad
---

# US-ADJ-1.2 — Refactoring domain: helpers _recalcular_ots + _aplicar_swap_posicion

## Descripción

Extrae lógica compleja del aggregate `Competencia` a métodos privados de apoyo, mejorando OCP y SRP.

## Capas afectadas

`competencia/domain/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-01 | `_recalcular_ots()` — helper privado para recálculo de Official Tops tras ajuste de grilla |
| ADJ-02 | `_aplicar_swap_posicion()` — helper privado para intercambio de posiciones en la grilla |

## Principios aplicados

- **OCP**: el aggregate delega comportamiento a métodos especializados sin modificar la interfaz pública
- **SRP**: cada helper tiene una única responsabilidad

## Tests

BDD waiver — refactoring estructural. Tests existentes de SP1 pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
