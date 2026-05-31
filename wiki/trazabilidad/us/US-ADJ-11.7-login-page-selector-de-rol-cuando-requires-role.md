---
title: "US-ADJ-11.7 — LoginPage: selector de rol cuando requires_role_selection"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: frontend, identidad
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.7
tests_count: null
rf: []
---

# US-ADJ-11.7 — LoginPage: selector de rol cuando requires_role_selection

## Descripción

Actualiza el login para soportar el flujo multi-rol de [[US-ADJ-11.1-usuario-roles-list-rol-jwt-rol-activo-login-condicional]]: cuando el backend devuelve `requires_role_selection: true`, el frontend muestra un selector de rol antes de completar el login. Si el usuario tiene un solo rol, el token se emite directamente.

## Contenido implementado

- `LoginPage` — selector de rol condicional
- `loginApi(rolElegido?)` — pasa `rol_activo` al backend cuando el usuario elige

## Estado

✅ Completado · PR #191
