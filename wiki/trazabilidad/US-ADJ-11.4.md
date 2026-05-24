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
rf: []
software_items:
  - src/registro/domain/aggregates/juez.py
  - src/registro/application/commands/registrar_juez.py
  - src/registro/infrastructure/repositories/sqlite_juez_repository.py
test_units:
  - tests/features/US-ADJ-11.4-juez.feature
  - tests/integration/registro/test_sqlite_juez_repository.py
origen_tipo: adr
origen_refs:
  - ADR-020
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
