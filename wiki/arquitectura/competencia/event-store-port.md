---
title: "Competencia — Port EventStorePort"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: port
responsabilidad: "Contrato append-only de persistencia de eventos; re-export desde shared.domain"
interfaces_out: []
adr_refs: [ADR-001, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/ports/event_store_port.py
  - src/shared/domain/ports/event_store_port.py
---

# Port EventStorePort (Competencia)

## Responsabilidad

Re-export del contrato canónico `EventStorePort` definido en `shared.domain`. En el BC Competencia este puerto es la **única salida de escritura de datos de dominio** — ambos aggregates (`Competencia` y `Performance`) escriben exclusivamente a través de él.

> La fuente canónica de la interfaz está en `shared/`. Ver [[event-store-port]] en la sección de Impacto para el análisis de riesgo de cambio.

## Operaciones del contrato

| Método | Descripción |
|--------|-------------|
| `append(stream_id, event_type, payload)` | Agrega un evento al stream. Append-only. |
| `load(stream_id)` | Carga todos los eventos de un stream en orden. |

## Stream IDs en este BC

| Stream | Aggregate |
|--------|-----------|
| `competencia-{competencia_id}` | [[competencia-aggregate]] |
| `performance-{competencia_id}-{participante_id}-{disciplina}` | [[performance-aggregate]] |

## Implementación concreta

[[sqlite-event-store]] — re-export de `shared.infrastructure`. Usa `competencia.db` como archivo SQLite con tabla `events`.

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

## Consumidores en este BC

- [[handler-utils]] — `persistir_eventos_pendientes()` usa este port para escribir
- [[performances-ap-port]] (adaptador) — `PerformancesAPAdapter` lee streams para reconstruir performances
- [[performances-estado-port]] (adaptador) — idem para estado completo

## Riesgo

Componente de muy alto impacto transversal. Ver análisis completo en [[event-store-port]] (wiki/impacto/).

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/ports/event_store_port.py` | Puerto abstracto EventStorePort (append-only) |
| `src/shared/domain/ports/event_store_port.py` | Puerto abstracto EventStorePort (append-only) |
