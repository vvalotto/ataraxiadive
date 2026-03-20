# ADR-008: Event Store implementado como tabla append-only en SQLite

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-001 (Event Sourcing en Competencia), ADR-005 (ES en Notificaciones), ADR-007 (SQLite por BC) |

---

## Contexto

ADR-001 decidió Event Sourcing para el BC Competencia. ADR-005 extendió
esa decisión al BC Notificaciones por razones de idempotencia. Ambos BCs
necesitan un mecanismo de persistencia para sus streams de eventos.

La arquitectura de referencia propuso una tabla de eventos en PostgreSQL
como event store, descartando EventStoreDB por el bajo volumen (~500
eventos/torneo). La decisión de ADR-007 de adoptar SQLite obliga a revisar
esta elección.

**Alternativas evaluadas para event store dedicado:**

- **EventStoreDB:** producto especializado con streams por agregado,
  subscriptions y projections nativas. Licencia restrictiva en versiones
  recientes (ESL — no libre para todos los usos). Descartado por riesgo
  de licenciamiento.
- **NATS JetStream:** messaging + streams persistentes, Apache 2.0,
  binario único. No es ES-first: no tiene concepto de stream por agregado
  ni optimistic concurrency nativo. Interesante para comunicación entre
  BCs — evaluable en SP3.
- **Redpanda / Kafka:** diseñados para streaming analytics y alto throughput.
  No tienen modelo de stream por agregado. Sobrecarga operacional injustificada
  para esta escala.

---

## Decisión

Se implementa el Event Store como **tabla append-only en el archivo SQLite
del BC** (Competencia y Notificaciones), usando el esquema canónico de
Event Sourcing.

### Esquema de la tabla `events`

```sql
CREATE TABLE events (
    id          TEXT PRIMARY KEY,          -- UUID del evento
    stream_id   TEXT NOT NULL,             -- "<aggregate_type>-<aggregate_id>"
    stream_pos  INTEGER NOT NULL,          -- posición dentro del stream (0-based)
    event_type  TEXT NOT NULL,             -- nombre del tipo de evento
    payload     TEXT NOT NULL,             -- JSON serializado del evento
    metadata    TEXT NOT NULL DEFAULT '{}',-- causation_id, correlation_id, etc.
    created_at  TEXT NOT NULL,             -- ISO-8601 UTC

    UNIQUE (stream_id, stream_pos)         -- garantía de optimistic concurrency
);

CREATE INDEX idx_events_stream ON events (stream_id, stream_pos);
```

### Convención de stream_id

```
competencia-{competencia_id}    ← aggregate Competencia
performance-{performance_id}    ← aggregate Performance
notificacion-{notificacion_id}  ← aggregate Notificacion
```

### Optimistic concurrency

Al escribir un evento, se verifica la versión esperada del stream:

```python
# Pseudocódigo del adaptador
def append(stream_id: str, events: list[Event], expected_version: int) -> None:
    current = self._get_stream_version(stream_id)
    if current != expected_version:
        raise ConcurrencyError(stream_id, expected_version, current)
    for i, event in enumerate(events):
        self._insert(stream_id, expected_version + 1 + i, event)
```

El constraint `UNIQUE (stream_id, stream_pos)` actúa como red de seguridad
a nivel de DB en caso de condición de carrera.

### Puerto en el dominio

El dominio no conoce SQLite. Define el puerto:

```python
# <bc>/domain/ports/event_store_port.py
from abc import ABC, abstractmethod
from <bc>.domain.events import DomainEvent

class EventStorePort(ABC):

    @abstractmethod
    def append(
        self,
        stream_id: str,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None: ...

    @abstractmethod
    def load(self, stream_id: str) -> list[DomainEvent]: ...

    @abstractmethod
    def load_from(self, stream_id: str, from_version: int) -> list[DomainEvent]: ...
```

El adaptador SQLite implementa este puerto en `<bc>/infrastructure/event_store/`.

---

## Justificación

### Por qué no un producto dedicado ahora

Un event store dedicado (EventStoreDB, NATS JetStream) agrega un componente
de infraestructura que requiere operación, configuración y mantenimiento.
Para el volumen de AtaraxiaDive (~500 eventos por torneo, 4 torneos al año)
el beneficio operacional no justifica ese costo.

SQLite con una tabla bien estructurada provee:
- Streams por agregado (convención de `stream_id`)
- Optimistic concurrency (constraint UNIQUE + verificación explícita)
- Append-only real (sin UPDATE ni DELETE en el código — reforzable con trigger)
- Reconstrucción de agregados (`load(stream_id)`)
- Lecturas de proyecciones (`load_from(stream_id, version)`)

Todo lo que necesita Event Sourcing a esta escala.

### Puerto como contrato evolutivo

El puerto `EventStorePort` es el punto de extensión. Si en SP3 se quiere
experimentar con NATS JetStream (Apache 2.0, sin problemas de licencia),
solo hay que implementar un nuevo adaptador que satisfaga el mismo contrato.

El dominio y la capa de aplicación no cambian. Ese es el experimento:
¿cuánto cambia cuando se reemplaza el event store?

---

## Consecuencias

**Positivas:**
- Sin dependencias externas adicionales (SQLite ya decidido en ADR-007)
- Tests de integración del event store con SQLite en memoria (`:memory:`)
- Migración futura al alcance del puerto: solo cambia el adaptador
- Append-only reforzable con trigger SQLite si se requiere mayor garantía

**Negativas / trade-offs:**
- Sin subscriptions nativas (proyecciones se actualizan en el mismo comando,
  no por subscripción reactiva)
- Sin projections declarativas (se implementan como queries sobre la tabla)
- Escalabilidad limitada si el volumen crece varios órdenes de magnitud

**Condición de escape:**
Evaluar reemplazo del adaptador por NATS JetStream si se requiere:
- Comunicación reactiva entre BCs basada en eventos (pub/sub)
- Subscriptions a streams desde múltiples consumidores
- Separación del bus de eventos del almacenamiento

---

## Notas del Experimento

La implementación del puerto `EventStorePort` con dos adaptadores distintos
(SQLite en SP1, candidato en SP3) es un caso de prueba directo de la
arquitectura hexagonal. La retrospectiva de BL-002 documentará:

1. ¿Qué cambió dentro de `infrastructure/event_store/`?
2. ¿Qué NO cambió en `domain/` y `application/`?
3. ¿El puerto fue suficiente o hubo fugas de abstracción?

Este dato alimenta directamente RQ1 del experimento IEDD.
