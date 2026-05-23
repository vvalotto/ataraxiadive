---
title: "US-ADJ-1.1 — Refactoring domain: ot_programado + event_handlers + snake_case"
type: trazabilidad-us
sp: SP-ADJ-01
inc: SP-ADJ-01
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §7
us_id: US-ADJ-1.1
tests_count: null
---

# US-ADJ-1.1 — Refactoring domain: ot_programado + event_handlers + snake_case

## Descripción

Ajuste técnico post-SP2 sobre la capa `domain/` del BC Competencia. Resuelve issues ADJ-03, ADJ-06, ADJ-08 detectados en revisión de calidad.

## Capas afectadas

`competencia/domain/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-03 | `@property ot_programado` — encapsula cálculo del Official Top programado |
| ADJ-06 | `_event_handlers` registrados en `__init__` (patrón consistente con ES) |
| ADJ-08 | Renombrar `registrarAP` → `registrar_ap` (snake_case PEP-8) |

## Motivación

Correcciones de estilo y encapsulamiento detectadas en revisión post-SP2. No cambian comportamiento observable.

## Tests

BDD waiver — refactoring interno sin comportamiento nuevo. Tests existentes de SP1 pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
