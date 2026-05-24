---
title: "US-ADJ-3.2 — Extraer TarjetaAsignacion VO"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
us_id: US-ADJ-3.2
tests_count: null
rf: []
software_items:
  - src/competencia/domain/value_objects/tarjeta_asignacion.py
test_units: null
origen_tipo: calidad
---

# US-ADJ-3.2 — Extraer TarjetaAsignacion VO

## Descripción

Extrae la lógica de asignación de tarjetas a un Value Object dedicado, eliminando lógica condicional dispersa en el aggregate y handlers.

## Capas afectadas

`competencia/domain/`, `competencia/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-02 | VO `TarjetaAsignacion` encapsula: tipo de tarjeta, motivo DQ, penalizaciones acumuladas y cálculo de RP final |

## Motivación

La lógica de tarjetas crecía en el aggregate `Performance`. Extraerla a un VO mejora la cohesión y simplifica los handlers.

## Tests

BDD waiver — refactoring estructural. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
