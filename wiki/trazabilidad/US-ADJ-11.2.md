---
title: "US-ADJ-11.2 — POST/DELETE /auth/usuarios/me/roles + guard no quitar ATLETA"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: identidad
estado: completado
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
---

# US-ADJ-11.2 — POST/DELETE /auth/usuarios/me/roles + guard no quitar ATLETA

## Descripción

API para que un usuario agregue o quite roles en su propio perfil. El guard impide quitar el rol ATLETA (rol base de todo usuario).

## Contenido implementado

- `AgregarRolUsuarioCommand` + handler
- `POST /auth/usuarios/me/roles` — agregar rol
- `DELETE /auth/usuarios/me/roles/{rol}` — quitar rol (con guard ATLETA)

## Estado

✅ Completado · PR #185
