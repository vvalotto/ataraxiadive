---
title: "US-6.6.1 — Endpoint público GET /torneos sin autenticación"
type: trazabilidad-us
sp: SP6
inc: INC-6.6
bc: torneo
estado: completado
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §SP6
  - docs/plans/sp6/US-6.6.1-plan.md
---

# US-6.6.1 — Endpoint público GET /torneos sin autenticación

## Descripción

Expone el listado de torneos sin requerir autenticación, habilitando el portal público. El endpoint filtra torneos en estado `CANCELADO` y mantiene el mismo contrato que el endpoint autenticado.

## Contenido implementado

- `GET /torneos` — sin `Authorization` header requerido; filtra `EstadoTorneo.CANCELADO`
- Tests de integración HTTP: 200 sin token, sin cancelados, campos del portal público

## Estado

✅ Completado — 2026-05-10
