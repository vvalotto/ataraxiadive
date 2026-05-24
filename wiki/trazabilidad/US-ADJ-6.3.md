---
title: "US-ADJ-6.3 — Eliminar inspect.signature: callback on_finalizada unificado"
type: trazabilidad-us
sp: SP-ADJ-06
inc: SP-ADJ-06
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §18
us_id: US-ADJ-6.3
tests_count: null
rf: []
software_items:
  - src/competencia/application/_p08_finalizacion.py
test_units: null
origen_tipo: calidad
---

# US-ADJ-6.3 — Eliminar inspect.signature: callback on_finalizada unificado

## Descripción

Elimina el uso de `inspect.signature` para detección dinámica de la firma del callback `on_finalizada`, unificando el mecanismo en el composition root.

## Capas afectadas

`competencia/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| SOLID | `inspect.signature` eliminado — la firma del callback es ahora fija y conocida |
| — | `on_finalizada` unificado: un único callback registrado en `src/app.py` |

## Motivación

El uso de `inspect.signature` era frágil ante refactorings y difícil de razonar. La unificación en el composition root hace explícito el contrato del callback.

## Estado

✅ Completado — 2026-04-18
