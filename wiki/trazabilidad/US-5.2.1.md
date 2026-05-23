---
title: "US-5.2.1 — TorneoCompetenciasPage: maestro-detalle por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.2
bc: competencia, torneo
estado: cerrada
fecha_cierre: "2026-04-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §21
  - docs/plans/sp5/US-5.2.1-plan.md
us_id: US-5.2.1
tests_count: null
---

# US-5.2.1 — TorneoCompetenciasPage: maestro-detalle por disciplina

## Descripción

Vista maestro-detalle que lista todas las disciplinas del torneo con su estado, juez asignado y progreso. Al seleccionar una disciplina, abre el detalle con la acción `Habilitar disciplina` que inicia la competencia vía `POST /competencia/{id}/iniciar`.

## Contenido implementado

- `TorneoCompetenciasPage` — lista de disciplinas con estado, juez y progreso
- Acción `Habilitar disciplina` — `POST /competencia/{id}/iniciar`
- Panel de detalle por disciplina seleccionada

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.2 | ✅ |

DesignReviewer consolidado INC-5.2: **0 CRITICAL · 215 WARNING**.

## Estado

✅ Completado — 2026-04-22 · PR #105
