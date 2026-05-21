---
title: "US-ADJ-3.4 — Mover deps auth a shared/api/dependencies.py (DIP cross-BC)"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: shared, identidad, torneo, registro
estado: completado
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
---

# US-ADJ-3.4 — Mover deps auth a shared/api/dependencies.py (DIP cross-BC)

## Descripción

Centraliza las dependencias de autenticación (guards de rol JWT) en `shared/api/dependencies.py`, eliminando la duplicación en los routers de cada BC.

## Capas afectadas

`shared/api/`, `*/api/router.py` (todos los BCs)

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-05 | `require_role()`, `get_current_user()` y helpers JWT movidos a `shared/api/dependencies.py` |

## Principios aplicados

- **DIP**: los routers de cada BC dependen de la abstracción compartida, no de implementaciones propias
- **DRY**: una sola fuente de verdad para la lógica de autenticación cross-BC

## Tests

BDD waiver — refactoring transversal. Tests de auth existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
