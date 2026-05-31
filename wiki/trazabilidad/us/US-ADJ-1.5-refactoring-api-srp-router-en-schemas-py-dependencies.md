---
title: "US-ADJ-1.5 — Refactoring api: SRP router en schemas.py + dependencies.py"
type: trazabilidad-us
sp: SP-ADJ-01
inc: SP-ADJ-01
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §7
us_id: US-ADJ-1.5
tests_count: null
rf: []
software_items:
  - src/competencia/api/schemas.py
  - src/competencia/api/dependencies.py
test_units: null
origen_tipo: calidad
componentes_wiki:
  - arquitectura/competencia/router-competencia
---

# US-ADJ-1.5 — Refactoring api: SRP router en schemas.py + dependencies.py

## Descripción

Descompone el módulo `router.py` monolítico en tres archivos con responsabilidades separadas.

## Capas afectadas

`competencia/api/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-07 | `schemas.py` — modelos Pydantic de request/response · `dependencies.py` — inyección de dependencias · `router.py` — solo definición de endpoints |

## Motivación

El router acumulaba schemas, dependencias y endpoints. SRP exige que cada módulo tenga una sola razón para cambiar.

## Tests

BDD waiver — refactoring estructural. Tests existentes de SP1 pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
