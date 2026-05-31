---
title: "US-ADJ-3.5 — Limpiar imports cross-module en ports de Competencia"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
us_id: US-ADJ-3.5
tests_count: null
rf: []
software_items:
  - src/competencia/domain/aggregates/competencia.py
test_units: null
origen_tipo: calidad
componentes_wiki:
  - arquitectura/competencia/competencia-aggregate
---

# US-ADJ-3.5 — Limpiar imports cross-module en ports de Competencia

## Descripción

Elimina imports que cruzaban módulos incorrectamente en la capa de ports del BC Competencia, respetando las reglas de dependencias de la arquitectura hexagonal.

## Capas afectadas

`competencia/domain/ports/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-06 | Imports circulares o cross-module en `ports/` eliminados; cada port importa solo de su propia capa de dominio o de `shared/` |

## Motivación

Los ports de dominio no deben importar de capas de infraestructura ni de otros BCs directamente. La limpieza garantiza la inversión de dependencias.

## Tests

BDD waiver — limpieza de imports. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
