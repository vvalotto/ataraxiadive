---
title: "US-1.1.1 — Setup: esqueleto BC Competencia"
type: trazabilidad-us
sp: SP1
inc: INC-1.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.1.1
tests_count: null
rf: []
software_items:
  - src/competencia/domain/aggregates/performance.py
  - src/competencia/infrastructure/event_store/sqlite_event_store.py
test_units: null
origen_tipo: setup
---

# US-1.1.1 — Setup: esqueleto BC Competencia

## Contexto

Primera US del proyecto. Establece la estructura inicial del BC Competencia siguiendo el patrón BC-first (ADR-006).

## Contenido implementado

- Esqueleto de `src/competencia/` con capas domain / application / infrastructure / api
- Tabla `events` en SQLite (ADR-008) — Event Store append-only
- Endpoint `/health` — health-check inicial

## RFs cubiertos

Ninguno directamente — US de infraestructura/scaffolding.

## Decisiones arquitectónicas aplicadas

| ADR | Aplicación |
|-----|-----------|
| [[ADR-001]] | Stack tecnológico |
| [[ADR-003]] | Arquitectura hexagonal |
| [[ADR-006]] | Estructura BC-first |
| [[ADR-007]] | SQLite como motor de persistencia |
| [[ADR-008]] | Event Store como tabla `events` append-only |
| [[ADR-009]] | Migraciones Alembic |

## Tests

Sin suite dedicada — validación por smoke test del health-check.

## Estado

✅ Completado — 2026-03-21
