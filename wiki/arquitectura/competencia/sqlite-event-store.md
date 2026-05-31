---
title: "Competencia — Adapter SQLiteEventStore"
type: arquitectura-componente
bc: competencia
capa: infrastructure
tipo_componente: adapter
responsabilidad: "Implementación concreta del EventStorePort sobre SQLite — re-export desde shared.infrastructure"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-007, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/competencia/infrastructure/event_store/sqlite_event_store.py
  - src/shared/infrastructure/event_store/sqlite_event_store.py
us_origen:
  - US-1.1.1-setup-esqueleto-bc-competencia
  - US-3.3.1-torneo-id-opcional-en-competencia-para-overall
  - US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por
  - US-ADJ-3.3-refactorizar-build-app-constante-event-type
  - US-ADJ-3.7-proyeccion-competencias-por-torneo-o-n-o-1
tests:
  - tests/features/US-3.3.1-torneo-id-competencia.feature
  - tests/integration/competencia/test_torneo_id_integration.py
---

# Adapter SQLiteEventStore (Competencia)

## Responsabilidad

Implementación concreta de [[event-store-port]] sobre SQLite. El archivo de este BC es solo un re-export desde `shared.infrastructure` — la fuente canónica vive en `shared/`.

## Base de datos

`competencia.db` — archivo SQLite dedicado al BC Competencia (ADR-007: persistencia por BC).

## Tabla `events`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Autoincrement |
| `stream_id` | TEXT | Identificador del stream (`competencia-*` o `performance-*`) |
| `event_type` | TEXT | Nombre del evento (`APRegistrado`, `GrillaDeSalidaGenerada`, etc.) |
| `payload` | TEXT | JSON del payload del evento |
| `sequence` | INTEGER | Número de secuencia dentro del stream |
| `occurred_at` | TEXT | Timestamp ISO 8601 |

## Comportamiento

- **Append-only:** nunca se actualiza ni elimina un evento
- **`load(stream_id)`:** retorna eventos ordenados por `sequence`
- **`ConcurrencyError`:** se levanta si se detecta conflicto de secuencia (optimistic locking básico)

## Migración

`src/competencia/infrastructure/migrations/versions/0001_create_events_table.py` — crea la tabla `events` (Alembic, ADR-009).

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Es la implementación de [[event-store-port]]
- Usado por [[handler-utils]] para todas las escrituras y lecturas de streams

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/infrastructure/event_store/sqlite_event_store.py` | Implementación SQLite del EventStorePort |
| `src/shared/infrastructure/event_store/sqlite_event_store.py` | Implementación SQLite del EventStorePort |
