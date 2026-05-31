---
title: "ADR-001: Event Sourcing en Competencia"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-001-event-sourcing-competencia.md
estado: Aceptada
fecha: 2026-03-14
bcs_afectados: [competencia]
rnf_refs:
  - RNF-01-confiabilidad-persistencia-event-sourcing
---

# ADR-001: Event Sourcing en Competencia

## Decisión

Event Sourcing para los aggregates `Performance` y `Competencia` del BC [[competencia]]. Los BCs de soporte (Torneo, Registro, Resultados, Identidad) usan CRUD estándar.

## Por qué

- Los resultados de un torneo oficial son disputables ante la FAAS.
- Un `UPDATE` de performance destruye la historia — no se puede saber qué había antes ni quién lo cambió.
- Las correcciones del juez deben dejar rastro explícito (`MarcaCorregida` con motivo), no sobreescribir.

## Consecuencias vigentes

- El estado de cada performance se **deriva** de una secuencia inmutable de eventos. El Read Model es una proyección.
- Las correcciones son **eventos adicionales**, nunca modificaciones.
- El event store es la fuente de verdad; el Read Model es reconstruible desde cero.
- El hash SHA-256 al cerrar una disciplina (ver [[ADR-018-hash-sha256-auditoria]]) es posible gracias a que los eventos son inmutables y ordenados.
- Las proyecciones deben ser **idempotentes** — riesgo de desincronización si falla la proyección.

## Aggregates bajo Event Sourcing

| Aggregate | Stream ID | BC |
|-----------|-----------|-----|
| `Performance` | `performance-{performance_id}` | [[competencia]] |
| `Competencia` | `competencia-{competencia_id}` | [[competencia]] |
| `Notificacion` | `notificacion-{notificacion_id}` | [[notificaciones]] (ver [[ADR-017-notificaciones-event-sourcing]]) |

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — define qué BCs usan ES vs CRUD
- [[ADR-008-event-store-sqlite]] — implementación concreta del event store
- [[ADR-017-notificaciones-event-sourcing]] — extensión de ES a Notificaciones
- [[ADR-018-hash-sha256-auditoria]] — integridad criptográfica sobre el event store
