---
title: "US-5.1.5 — JuecesPanel: asignación de juez por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: torneo, identidad
estado: cerrada
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.5-plan.md
us_id: US-5.1.5
tests_count: null
rf: []
software_items:
  - src/torneo/application/commands/asignar_juez.py
  - src/torneo/application/queries/obtener_disciplinas_juez.py
test_units:
  - tests/features/US-5.1.5-asignacion-jueces.feature
origen_tipo: plataforma
---

# US-5.1.5 — JuecesPanel: asignación de juez por disciplina

## Descripción

Tab `Jueces` del panel organizador. Permite asignar un juez a cada disciplina del torneo mediante un selector. La precondición de grilla para habilitar el selector fue refinada en [[US-5.1.9]].

## Contenido implementado

- `JuecesPanel` + `TablaJueces` — vista de jueces por disciplina
- `JuezSelector` — desplegable de usuarios con rol Juez
- `PUT /torneos/{id}/disciplinas/{disc}/juez` — endpoint de asignación

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

## Estado

✅ Completado — 2026-04-21 · PR #99
