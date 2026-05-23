---
title: "US-5.4.2 — Cambiar contraseña para usuario autenticado"
type: trazabilidad-us
sp: SP5
inc: INC-5.4
bc: identidad
estado: cerrada
fecha_cierre: "2026-04-24"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §24
  - docs/plans/sp5/US-5.4.2-plan.md
us_id: US-5.4.2
tests_count: null
---

# US-5.4.2 — Cambiar contraseña para usuario autenticado

## Descripción

Permite a un usuario autenticado cambiar su propia contraseña. El handler valida la contraseña actual antes de actualizar.

## Contenido implementado

- `CambiarPasswordHandler` — lógica de cambio con validación de contraseña actual
- `POST /auth/cambiar-password` — endpoint autenticado

## Estado

✅ Completado — 2026-04-24 · PR #113
