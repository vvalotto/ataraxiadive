---
title: "US-ADJ-11.1 — Usuario.roles: list[Rol] + JWT rol_activo + login condicional"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: identidad
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.1
tests_count: null
rf: []
software_items:
  - src/identidad/domain/aggregates/usuario.py
  - src/identidad/infrastructure/jwt_service.py
test_units:
  - tests/features/US-ADJ-11.1-identidad-multi-rol.feature
origen_tipo: adr
origen_refs:
  - ADR-020
---

# US-ADJ-11.1 — Usuario.roles: list[Rol] + JWT rol_activo + login condicional

## Descripción

Núcleo del modelo multi-rol (BT-001 — bloqueaba producción). Extiende `Usuario` a `roles: list[Rol]`, agrega `rol_activo` al JWT, e implementa login condicional: selector de rol cuando el usuario tiene más de uno, token directo cuando tiene uno solo. Migración `rol → roles`.

## Decisión asociada

[[ADR-020-modelo-usuarios-roles]] — `Usuario.roles: list[Rol]` · JWT `rol_activo`.

## Contenido implementado

- `Usuario.roles: list[Rol]` — extensión del aggregate Identidad
- JWT con campo `rol_activo`
- Login condicional: selector vs token directo
- Migración SQLite `rol → roles`

DesignReviewer cierre SP-ADJ-11: **0 CRITICAL · 287 WARNING**.

## Estado

✅ Completado · PR #184
