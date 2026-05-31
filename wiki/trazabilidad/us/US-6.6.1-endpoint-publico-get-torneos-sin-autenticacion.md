---
title: "US-6.6.1 — Endpoint público GET /torneos sin autenticación"
type: trazabilidad-us
sp: SP6
inc: INC-6.6
bc: torneo
estado: cerrada
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §SP6
  - docs/plans/sp6/US-6.6.1-plan.md
us_id: US-6.6.1
tests_count: null
rf: []
software_items:
  - src/torneo/api/router.py
test_units:
  - tests/features/US-6.6.1-endpoint-publico-torneos.feature
  - tests/integration/torneo/test_torneos_publicos_api.py
origen_tipo: plataforma
---

# US-6.6.1 — Endpoint público GET /torneos sin autenticación

## Descripción

Expone el listado de torneos sin requerir autenticación, habilitando el portal público. El endpoint filtra torneos en estado `CANCELADO` y mantiene el mismo contrato que el endpoint autenticado.

## Contenido implementado

- `GET /torneos` — sin `Authorization` header requerido; filtra `EstadoTorneo.CANCELADO`
- Tests de integración HTTP: 200 sin token, sin cancelados, campos del portal público

## Estado

✅ Completado — 2026-05-10
