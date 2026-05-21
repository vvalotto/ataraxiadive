---
title: "US-ADJ-10.2 — Página Mis Datos del atleta (PATCH /registro/atletas/me)"
type: trazabilidad-us
sp: SP-ADJ-10
inc: SP-ADJ-10
bc: registro, frontend
estado: completado
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-10/PLAN-SP-ADJ-10.md
  - docs/plans/sp-adj-10/US-ADJ-10.2-plan.md
---

# US-ADJ-10.2 — Página Mis Datos del atleta (PATCH /registro/atletas/me)

## Descripción

Resuelve hallazgo H-01-06 de la UAT E2E SP6: no existía página para que el atleta editara su propio perfil. Agrega `PATCH /registro/atletas/me` y la página `AtletaMisDatosPage` en el portal del atleta.

## Contenido implementado

- `PATCH /registro/atletas/me` — actualización del perfil del atleta autenticado
- `AtletaMisDatosPage` — formulario de datos personales del atleta

## Estado

✅ Completado · PR #180
