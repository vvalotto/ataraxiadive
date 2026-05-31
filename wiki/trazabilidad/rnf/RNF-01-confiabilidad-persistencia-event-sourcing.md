---
title: "RNF-01 — Confiabilidad: persistencia y reconstrucción de estado"
type: trazabilidad-rnf
rnf_id: RNF-01
atributo: Confiabilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-001-event-sourcing-competencia
  - ADR-008-event-store-sqlite
bcs_afectados:
  - competencia
  - notificaciones
---

# RNF-01 — Confiabilidad

**Driver:** cada performance es un evento único e irrepetible. Un dato perdido no puede reconstruirse.

| Atributo | Valor |
|---|---|
| Pérdida de datos al registrar una performance | Inaceptable |
| Confirmación visual al juez tras cada registro | Requerida |
| Reconstrucción del estado desde log | Requerida |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-001-event-sourcing-competencia]] — Event Sourcing como garantía de reconstrucción y persistencia inalterable
- [[decisiones/ADR-008-event-store-sqlite]] — esquema append-only de la tabla `events`; concurrencia optimista

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
