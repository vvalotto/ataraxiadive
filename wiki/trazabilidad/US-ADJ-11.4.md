---
title: "US-ADJ-11.4 — Entidad Juez + JuezRepositoryPort + endpoints /registro/jueces/me"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: registro
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.4
tests_count: null
---

# US-ADJ-11.4 — Entidad Juez + JuezRepositoryPort + endpoints /registro/jueces/me

## Descripción

Introduce la entidad `Juez` en BC Registro con su puerto de repositorio. Expone endpoints para que el usuario con rol Juez gestione su propio perfil de juez.

## Contenido implementado

- Entidad `Juez` en `registro/domain/`
- `JuezRepositoryPort` + implementación SQLite
- `GET /registro/jueces/me` · `POST /registro/jueces/me` · `PATCH /registro/jueces/me`

## Estado

✅ Completado · PR #187
