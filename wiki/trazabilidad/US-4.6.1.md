---
title: "US-4.6.1 — ObtenerAuditLog por performance"
type: trazabilidad-us
sp: SP4
inc: INC-4.6
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §17
us_id: US-4.6.1
tests_count: null
---

# US-4.6.1 — ObtenerAuditLog por performance

## Descripción

Expone el historial completo de eventos de una performance específica, permitiendo al organizador auditar cada acción registrada por el juez.

## Decisiones cubiertas

PLAN-SP4 §INC-4.6 · ADR-001 · ADR-008

## Contenido implementado

- Query `ObtenerAuditLog` — lee el Event Store por `(competencia_id, atleta_id)`
- `GET /competencia/{competencia_id}/performances/{atleta_id}/audit-log`
- Respuesta cronológica con: `sequence`, `tipo`, `timestamp`, `datos`
- Acceso restringido a roles `organizador` / `admin`

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/application (ObtenerAuditLog) | ✅ |
| integration/competencia | ✅ |

## Estado

✅ Completado — 2026-04-18
