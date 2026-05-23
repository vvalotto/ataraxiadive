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
---

# US-ADJ-11.5 — Entidad Organizador + OrganizadorRepositoryPort + endpoints

## Descripción

Introduce la entidad `Organizador` en BC Registro con su puerto de repositorio, simétrica a [[US-ADJ-11.4]]. Expone endpoints para que el usuario con rol Organizador gestione su propio perfil.

## Contenido implementado

- Entidad `Organizador` en `registro/domain/`
- `OrganizadorRepositoryPort` + implementación SQLite
- `GET /registro/organizadores/me` · `POST /registro/organizadores/me` · `PATCH /registro/organizadores/me`

## Estado

✅ Completado · PR #188
