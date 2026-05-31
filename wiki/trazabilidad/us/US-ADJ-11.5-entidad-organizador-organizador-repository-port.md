---
title: "US-ADJ-11.5 — Entidad Organizador + OrganizadorRepositoryPort + endpoints"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: registro
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.5
tests_count: null
rf: []
software_items:
  - src/registro/domain/aggregates/organizador.py
  - src/registro/application/commands/registrar_organizador.py
  - src/registro/infrastructure/repositories/sqlite_organizador_repository.py
test_units:
  - tests/features/US-ADJ-11.5-organizador.feature
  - tests/integration/registro/test_sqlite_organizador_repository.py
origen_tipo: adr
origen_refs:
  - ADR-020
---

# US-ADJ-11.5 — Entidad Organizador + OrganizadorRepositoryPort + endpoints

## Descripción

Introduce la entidad `Organizador` en BC Registro con su puerto de repositorio, simétrica a [[US-ADJ-11.4-entidad-juez-juezrepositoryport-endpoints-registro]]. Expone endpoints para que el usuario con rol Organizador gestione su propio perfil.

## Contenido implementado

- Entidad `Organizador` en `registro/domain/`
- `OrganizadorRepositoryPort` + implementación SQLite
- `GET /registro/organizadores/me` · `POST /registro/organizadores/me` · `PATCH /registro/organizadores/me`

## Estado

✅ Completado · PR #188
