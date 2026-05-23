---
title: "US-ADJ-2.7 — Refactoring: eliminar código muerto get_on_finalizada_callback"
type: trazabilidad-us
sp: SP-ADJ-02
inc: SP-ADJ-02-code
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §8
us_id: US-ADJ-2.7
tests_count: null
---

# US-ADJ-2.7 — Refactoring: eliminar código muerto get_on_finalizada_callback

## Descripción

Elimina la función `get_on_finalizada_callback` del router y consolida la política P-08 en el composition root (`src/app.py`).

## Capas afectadas

`competencia/api/router.py`, `src/app.py`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| B-03 | `get_on_finalizada_callback` eliminado del router (código muerto) |
| — | `build_on_finalizada_callback` (P-08) vive exclusivamente en `src/app.py` |

## Motivación

La función quedó en el router como vestigio de una iteración previa. Su presencia confundía la arquitectura: la política P-08 debe vivir en el composition root, no en la capa API.

## Tests

BDD waiver — eliminación de código muerto. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-03-28
