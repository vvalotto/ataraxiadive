---
title: "US-5.1.6 — EjecucionPanel: monitor de competencias activas"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: competencia, torneo
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.6-plan.md
---

# US-5.1.6 — EjecucionPanel: monitor de competencias activas

## Descripción

Tab `Ejecucion` del panel organizador. Monitor de competencias activas que muestra el estado de cada disciplina en tiempo real. Consume `GET /competencia?torneo_id={id}` para listar competencias materializadas.

## Contenido implementado

- `EjecucionPanel` — lista de disciplinas con estado de competencia activa
- `GET /competencia?torneo_id={id}` — listado de competencias por torneo

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

## Estado

✅ Completado — 2026-04-21 · PR #100
