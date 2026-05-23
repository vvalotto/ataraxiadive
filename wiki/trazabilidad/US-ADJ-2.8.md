---
title: "US-ADJ-2.8 — Refactoring api: DIP fix EventStoreDep tipado como puerto abstracto"
type: trazabilidad-us
sp: SP-ADJ-02
inc: SP-ADJ-02-code
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §8
us_id: US-ADJ-2.8
tests_count: null
---

# US-ADJ-2.8 — Refactoring api: DIP fix EventStoreDep tipado como puerto abstracto

## Descripción

Corrige la dependencia del router hacia el Event Store: el tipo de la dependencia inyectada pasa de la clase concreta al puerto abstracto.

## Capas afectadas

`competencia/api/router.py`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| B-05 | `get_event_store() -> EventStorePort` — retorna el tipo abstracto |
| D-04 | `EventStoreDep = Annotated[EventStorePort, ...]` — anotación de tipo correcta en FastAPI DI |

## Principios aplicados

- **DIP**: la API depende de la abstracción (`EventStorePort`), no de `SQLiteEventStore`
- Complementa [[US-ADJ-1.4]] que inició el DIP en el router

## Tests

BDD waiver — fix de tipado y arquitectura. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
