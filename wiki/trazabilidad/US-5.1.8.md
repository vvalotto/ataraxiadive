---
title: "US-5.1.8 — TorneoCompetenciasPage: composición disciplinas + competencias"
type: trazabilidad-us
sp: SP5
inc: INC-5.1-ADJ
bc: torneo, competencia
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §20
  - docs/plans/sp5/US-5.1.8-plan.md
---

# US-5.1.8 — TorneoCompetenciasPage: composición disciplinas + competencias

## Descripción

Ajuste post-UAT (hallazgo UAT-5.1-01): corrección de la composición entre disciplinas y competencias materializadas. Usa `GET /torneos/{id}/disciplinas` como fuente primaria y cruza con competencias; muestra card por disciplina aunque no exista `competencia_id`.

## Contenido implementado

- `TorneoCompetenciasPage` — vista maestro corregida: una card por disciplina declarada, no por competencia materializada
- Cruce dinámico entre disciplinas del torneo y competencias existentes

## Estado

✅ Completado — 2026-04-21 · PR #102
