---
title: "US-6.6.3 — Navegación contextual: redirect post-login y RootRedirect"
type: trazabilidad-us
sp: SP6
inc: INC-6.6
bc: frontend, identidad
estado: cerrada
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §SP6
us_id: US-6.6.3
tests_count: null
rf: []
---

# US-6.6.3 — Navegación contextual: redirect post-login y RootRedirect

## Descripción

Implementa la navegación contextual del sistema: el usuario no autenticado aterriza en el portal público (`/portalapnea`); post-login es redirigido al portal de su rol activo (organizador/juez/atleta). `RootRedirect` maneja el ruteo inicial según estado de autenticación.

## Contenido implementado

- `RootRedirect` — componente de ruteo inicial por estado de autenticación
- Redirect post-login → portal por `rol_activo` del JWT
- `/portalapnea` como landing para visitantes no autenticados

## Estado

✅ Completado · PR #166
