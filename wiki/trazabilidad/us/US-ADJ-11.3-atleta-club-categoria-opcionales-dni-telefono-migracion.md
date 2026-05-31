---
title: "US-ADJ-11.3 — Atleta: club/categoría opcionales + dni/telefono + migración"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: registro
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.3
tests_count: null
rf: []
software_items:
  - src/registro/domain/aggregates/atleta.py
test_units:
  - tests/features/US-ADJ-11.3-atleta-refactor.feature
origen_tipo: adr
origen_refs:
  - ADR-020
---

# US-ADJ-11.3 — Atleta: club/categoría opcionales + dni/telefono + migración

## Descripción

Refactoring del aggregate `Atleta` en BC Registro: `club` y `categoría` pasan a ser opcionales (no son requeridos en el auto-registro), y se agregan los campos `dni` y `telefono`. Incluye migración SQLite con `_ensure_columns`.

## Contenido implementado

- `Atleta` — `club`/`categoria` opcionales; `dni`/`telefono` nuevos campos
- Migración `_ensure_columns` en SQLite

## Estado

✅ Completado · PR #186
