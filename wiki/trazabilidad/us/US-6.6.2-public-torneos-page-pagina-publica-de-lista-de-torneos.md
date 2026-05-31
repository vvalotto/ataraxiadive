---
title: "US-6.6.2 — PublicTorneosPage: página pública de lista de torneos"
type: trazabilidad-us
sp: SP6
inc: INC-6.6
bc: frontend, torneo
estado: cerrada
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §SP6
  - docs/plans/sp6/US-6.6.1-plan.md
us_id: US-6.6.2
tests_count: null
rf: []
---

# US-6.6.2 — PublicTorneosPage: página pública de lista de torneos

## Descripción

Primera pantalla del portal público de AtaraxiaDive: lista de torneos accesible sin login. Incluye rename de la ruta `/torneos` → `/portalapnea` para evitar conflicto con el proxy Vite.

## Contenido implementado

- `PublicTorneosPage` — lista de torneos sin autenticación
- Ruta `/portalapnea` — renombrada desde `/torneos` (fix conflicto proxy Vite)
- Consume [[US-6.6.1-endpoint-publico-get-torneos-sin-autenticacion-endpoint-publico-get-torneos-sin-autenticacion]] (`GET /torneos` público)

## Estado

✅ Completado · PR #165
