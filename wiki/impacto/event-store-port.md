---
title: "Impacto: EventStorePort"
type: impacto
last_updated: "2026-05-23"
sources:
  - wiki/decisiones/ADR-008-event-store-sqlite.md
  - wiki/arquitectura/competencia.md
  - wiki/arquitectura/notificaciones.md
componente: EventStorePort
riesgo: muy_alto
bcs_afectados: [competencia, notificaciones]
tipo: interfaz
---

# Impacto: `EventStorePort`

## Qué es

Puerto de dominio que abstrae el acceso al event store append-only. Definido en `<bc>/domain/ports/event_store_port.py` y implementado en `<bc>/infrastructure/event_store/`.

```python
class EventStorePort(ABC):
    def append(self, stream_id, events, expected_version) -> None: ...
    def load(self, stream_id) -> list[DomainEvent]: ...
    def load_from(self, stream_id, from_version) -> list[DomainEvent]: ...
```

El contrato es idéntico en ambos BCs con Event Sourcing: [[arquitectura/competencia]] y [[arquitectura/notificaciones]]. Cada BC tiene su propio adaptador y su propio SQLite.

## BCs afectados

| BC | Rol | Streams |
|----|-----|---------|
| [[arquitectura/competencia]] | Core Domain — fuente de verdad deportiva | `competencia-{id}`, `performance-{id}` |
| [[arquitectura/notificaciones]] | Generic — ciclo de vida de notificaciones | `notificacion-{id}` |

Los demás BCs (Torneo, Registro, Resultados, Identidad) usan CRUD y no implementan este puerto.

## Esquema subyacente (ADR-008)

```sql
CREATE TABLE events (
    id          TEXT PRIMARY KEY,
    stream_id   TEXT NOT NULL,
    stream_pos  INTEGER NOT NULL,
    event_type  TEXT NOT NULL,
    payload     TEXT NOT NULL,
    metadata    TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    UNIQUE (stream_id, stream_pos)   -- optimistic concurrency
);
```

El constraint `UNIQUE (stream_id, stream_pos)` es la garantía de concurrencia optimista a nivel de DB.

## Riesgo de cambio: muy alto

### Cambiar la firma del puerto

Impacta **ambos BCs con ES** por igual. Un cambio en `append` / `load` / `load_from` requiere:

1. Actualizar la implementación SQLite en `<bc>/infrastructure/event_store/` (×2 BCs).
2. Actualizar todos los handlers de aplicación que invocan el puerto (×N handlers en Competencia, ×M en Notificaciones).
3. Actualizar los tests de integración del adaptador en ambos BCs.

### Cambiar el esquema de la tabla `events`

Riesgo adicional sobre el anterior:

- Requiere migración Alembic en ambos BCs ([[ADR-009-migraciones-por-bc]]).
- El hash SHA-256 de auditoría opera sobre la secuencia canónica de eventos — un cambio de esquema puede romper la reproducibilidad del hash ([[ADR-018-hash-sha256-auditoria]]).
- Los datos históricos no son mutables — cualquier cambio de esquema es aditivo o requiere migración de registros existentes.

### Cambiar la convención de `stream_id`

Afecta todas las lecturas por `stream_id` en ambos BCs. Los stream IDs están hardcodeados en los aggregates y en los tests.

## Qué NO se ve afectado por un cambio en este puerto

- Los BCs CRUD (Torneo, Registro, Resultados, Identidad) — no usan event store.
- Los contratos HTTP de la API — el puerto es interno al BC.
- El contrato del evento `CompetenciaFinalizada` — ese es un evento de dominio de salida, no el esquema del store.

## Componentes C4 L3 — implementaciones concretas

| BC | Componente wiki | Descripción |
|----|----------------|-------------|
| Competencia | [[arquitectura/competencia/event-store-port]] | `EventStorePort` ABC + `SQLiteEventStore`; tabla `events`; `load_from(from_version)` |
| Notificaciones | [[arquitectura/notificaciones/sqlite-notificacion-event-store]] | `SQLiteNotificacionEventStore`; tabla `notificaciones_events`; índice sobre `evento_fuente_id` |

**Diferencia clave entre implementaciones:** Competencia usa `SQLiteEventStore` (tabla `events` con `id TEXT PK`, `stream_pos`, `metadata`, hash SHA-256); Notificaciones usa `SQLiteNotificacionEventStore` (tabla `notificaciones_events` con `id INTEGER PK AUTOINCREMENT`, índice `json_extract` para idempotencia). Son implementaciones independientes — no comparten código de infraestructura.

## Recorrido en el wiki

```
[[ADR-008-event-store-sqlite]]
  → [[arquitectura/competencia/event-store-port]] (implementación Competencia)
  → [[arquitectura/notificaciones/sqlite-notificacion-event-store]] (implementación Notificaciones)
  → [[ADR-001-event-sourcing-competencia]]
  → [[ADR-018-hash-sha256-auditoria]]
  → [[ADR-009-migraciones-por-bc]]
```

## ADRs relacionados

- [[ADR-008-event-store-sqlite]] — esquema de la tabla `events`; convención de stream_id; por qué SQLite
- [[ADR-001-event-sourcing-competencia]] — justificación del ES en el Core Domain
- [[ADR-018-hash-sha256-auditoria]] — hash SHA-256 que opera sobre la secuencia de eventos
- [[ADR-009-migraciones-por-bc]] — política de migraciones Alembic; una migración por BC
