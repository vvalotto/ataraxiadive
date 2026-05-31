---
title: "US-5.4.1 — Auto-registro público de usuarios"
type: trazabilidad-us
sp: SP5
inc: INC-5.4
bc: identidad
estado: cerrada
fecha_cierre: "2026-04-24"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §24
  - docs/plans/sp5/US-5.4.1-plan.md
us_id: US-5.4.1
tests_count: null
rf: []
software_items:
  - src/identidad/application/commands/registrar_usuario.py
test_units:
  - tests/features/US-5.4.1-auto-registro.feature
  - tests/integration/identidad/test_registro_email_handler.py
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/identidad/command-handlers-identidad
---

# US-5.4.1 — Auto-registro público de usuarios

## Descripción

Habilita el auto-registro de nuevos usuarios sin intervención del administrador. Extiende el modelo `Usuario` con nombre y apellido. El endpoint restringe la creación a roles distintos de ADMIN.

## Contenido implementado

- Extensión modelo `Usuario` — campos `nombre` y `apellido`
- `POST /auth/registro` — registro público, rol ≠ ADMIN
- Página `/registro` en frontend

DesignReviewer consolidado INC-5.4: **0 CRITICAL · 222 WARNING** (+7 vs INC-5.3, atribuidos a nuevos endpoints en `identidad/api/router.py`).

## Estado

✅ Completado — 2026-04-24 · PR #112
