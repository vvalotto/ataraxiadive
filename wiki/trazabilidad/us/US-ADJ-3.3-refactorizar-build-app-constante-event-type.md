---
title: "US-ADJ-3.3 — Refactorizar build_app() + constante event type"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: competencia, resultados
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
us_id: US-ADJ-3.3
tests_count: null
rf: []
software_items:
  - src/competencia/infrastructure/event_store/sqlite_event_store.py
test_units: null
origen_tipo: calidad
componentes_wiki: []
---

# US-ADJ-3.3 — Refactorizar build_app() + constante event type

## Descripción

Refactoriza la función `build_app()` del composition root para reducir su complejidad y extrae los tipos de evento del Event Store como constantes nombradas.

## Capas afectadas

`src/app.py`, `resultados/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-03 | `build_app()` descompuesta — cada BC se registra de forma independiente y declarativa |
| ADJ-04 | Tipos de evento del Event Store extraídos como constantes (eliminan strings literales en handlers) |
| SOLID-04 | SRP en el composition root: wiring de cada BC separado |

## Tests

BDD waiver — refactoring del composition root. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
