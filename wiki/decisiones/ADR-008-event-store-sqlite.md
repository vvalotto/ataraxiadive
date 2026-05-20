---
title: "ADR-008: Event Store como tabla append-only en SQLite"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-008-event-store-sqlite.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [competencia, notificaciones]
---

# ADR-008: Event Store como tabla append-only en SQLite

## Decisión

El Event Store se implementa como tabla `events` append-only en el SQLite de cada BC con ES.

## Esquema vigente

```sql
CREATE TABLE events (
    id          TEXT PRIMARY KEY,           -- UUID del evento
    stream_id   TEXT NOT NULL,              -- "<aggregate_type>-<aggregate_id>"
    stream_pos  INTEGER NOT NULL,           -- posición 0-based dentro del stream
    event_type  TEXT NOT NULL,
    payload     TEXT NOT NULL,              -- JSON serializado
    metadata    TEXT NOT NULL DEFAULT '{}', -- causation_id, correlation_id
    created_at  TEXT NOT NULL,              -- ISO-8601 UTC
    UNIQUE (stream_id, stream_pos)          -- optimistic concurrency
);
```

## Convención de stream_id

```
competencia-{competencia_id}
performance-{performance_id}
notificacion-{notificacion_id}
```

## Puerto en el dominio

```python
class EventStorePort(ABC):
    def append(self, stream_id, events, expected_version) -> None: ...
    def load(self, stream_id) -> list[DomainEvent]: ...
    def load_from(self, stream_id, from_version) -> list[DomainEvent]: ...
```

El adaptador SQLite implementa este puerto en `<bc>/infrastructure/event_store/`.

## Por qué no EventStoreDB o NATS

- EventStoreDB: licencia restrictiva (ESL). Descartado.
- NATS JetStream: sin concepto de stream por agregado ni optimistic concurrency nativo.
- Para el volumen de AtaraxiaDive (~500 eventos/torneo, 4 torneos/año) SQLite es suficiente.

## Consecuencias vigentes

- El constraint `UNIQUE (stream_id, stream_pos)` garantiza optimistic concurrency a nivel de DB.
- Las proyecciones se actualizan en el mismo comando (no por subscripción reactiva).
- Append-only por convención arquitectónica — no hay endpoint ni comando para eliminar o modificar eventos.
- El puerto es el punto de extensión: si se quiere experimentar con NATS JetStream solo cambia el adaptador.

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — por qué Event Sourcing en Competencia
- [[ADR-007-sqlite-persistencia-bc]] — el SQLite donde vive el event store
- [[ADR-018-hash-sha256-auditoria]] — integridad criptográfica calculada sobre la tabla events
