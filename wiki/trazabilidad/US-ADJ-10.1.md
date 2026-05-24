---
title: "US-ADJ-10.1 — Edición completa del torneo (PUT /torneos/{id})"
type: trazabilidad-us
sp: SP-ADJ-10
inc: SP-ADJ-10
bc: torneo, frontend
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-10/PLAN-SP-ADJ-10.md
  - docs/plans/sp-adj-10/US-ADJ-10.1-plan.md
us_id: US-ADJ-10.1
tests_count: null
rf: []
software_items:
  - src/torneo/application/commands/actualizar_torneo.py
test_units:
  - tests/features/US-ADJ-10.1-edicion-torneo.feature
origen_tipo: plataforma
---

# US-ADJ-10.1 — Edición completa del torneo (PUT /torneos/{id})

## Descripción

Resuelve hallazgo H-02-06 de la UAT E2E SP6: el organizador no podía corregir nombre, sede, fechas ni categorías de un torneo ya creado. Agrega `PUT /torneos/{id}` con precondición de estado y convierte `CrearTorneoPage` en modo dual (creación + edición).

## Contenido implementado

- `ActualizarTorneoCommand` + handler en `torneo/application/`
- `PUT /torneos/{id}` — precondición: estado `CREADO` o `INSCRIPCION_ABIERTA`
- `CrearTorneoPage` — modo dual: crea o edita según contexto
- Rename de "Editar disciplinas" → "Editar torneo"

## Estado

✅ Completado · PR #179
