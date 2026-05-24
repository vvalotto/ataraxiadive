---
title: "US-ADJ-1.4 — Refactoring api: DIP en router + P-08 a composition root"
type: trazabilidad-us
sp: SP-ADJ-01
inc: SP-ADJ-01
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §7
us_id: US-ADJ-1.4
tests_count: null
rf: []
software_items:
  - src/competencia/api/router.py
  - src/competencia/application/_p08_finalizacion.py
test_units: null
origen_tipo: calidad
---

# US-ADJ-1.4 — Refactoring api: DIP en router + P-08 a composition root

## Descripción

Aplica el Principio de Inversión de Dependencias (DIP) en el router de la API y mueve la política P-08 al composition root.

## Capas afectadas

`competencia/api/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-04 | `EventStoreDep: EventStorePort` — el router depende del puerto abstracto, no de la implementación concreta |
| ADJ-05 | Política P-08 (`CompetenciaFinalizada` automático) movida a `src/app.py` (composition root) |

## Principios aplicados

- **DIP**: la capa API no conoce la implementación de SQLiteEventStore
- **SRP**: el router no contiene lógica de política

## Tests

BDD waiver — refactoring arquitectónico. Tests existentes de SP1 pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
