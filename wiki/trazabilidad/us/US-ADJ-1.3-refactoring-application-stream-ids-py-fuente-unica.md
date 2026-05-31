---
title: "US-ADJ-1.3 — Refactoring application: _stream_ids.py fuente única"
type: trazabilidad-us
sp: SP-ADJ-01
inc: SP-ADJ-01
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §7
us_id: US-ADJ-1.3
tests_count: null
rf: []
software_items:
  - src/competencia/application/commands/_stream_ids.py
test_units: null
origen_tipo: calidad
componentes_wiki:
  - arquitectura/competencia/handler-utils
---

# US-ADJ-1.3 — Refactoring application: _stream_ids.py fuente única

## Descripción

Elimina duplicación de IDs de stream del Event Store creando un módulo centralizado `_stream_ids.py`.

## Capas afectadas

`competencia/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-09 | `_stream_ids.py` — fuente única de verdad para IDs de stream; 11 duplicaciones DRY eliminadas |

## Motivación

Los IDs de stream estaban dispersos como strings literales en múltiples handlers. Cualquier cambio requería editar 11 lugares distintos — riesgo de inconsistencia.

## Tests

BDD waiver — refactoring DRY sin comportamiento nuevo.

## Estado

✅ Completado — 2026-03-28
