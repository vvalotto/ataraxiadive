---
title: "US-1.4.1 — AsignarTarjeta roja + black-out con distancia"
type: trazabilidad-us
sp: SP1
inc: INC-1.4
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.4.1
tests_count: 189
rf:
  - RF-EJ-07-registro-black-out-distancia
software_items:
  - src/competencia/domain/aggregates/performance.py
test_units:
  - tests/features/US-1.4.1-blackout-con-distancia.feature
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/performance-aggregate
---

# US-1.4.1 — AsignarTarjeta roja + black-out con distancia

## Descripción

Extiende el manejo de tarjeta roja para incluir el caso específico de black-out (pérdida de conocimiento bajo el agua). El black-out registra el hecho y la distancia alcanzada antes de la pérdida de conciencia.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-07-registro-black-out-distancia]] | Black-out registra el hecho y la distancia alcanzada |

## Comando principal

`AsignarTarjeta` — extendido para `MotivoDQ.BKO_SUBACUATICO` y `BKO_SUPERFICIE`

## Invariantes aplicadas

- INV-P-07: tarjeta roja es DQ inmediata
- INV-P-11: una sola tarjeta por performance

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.4.1 | ✅ |
| **Total acumulado** | **189 tests (97.57%)** |

## Estado

✅ Completado — 2026-03-23
