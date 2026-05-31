---
title: "US-5.6.6 — UI podios por división (6 divisiones fijas)"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
  - docs/plans/sp5/US-5.6.6-plan.md
us_id: US-5.6.6
tests_count: null
rf: []
software_items:
  - src/resultados/application/queries/obtener_overall.py
test_units:
  - tests/features/US-5.6.6-ui-podios.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/resultados/query-handlers-resultados
---

# US-5.6.6 — UI podios por división (6 divisiones fijas)

## Descripción

Vista de podios del torneo segmentada en 6 divisiones fijas: SENIOR M/F, MASTER M/F, JUNIOR M/F. El ranking overall permanece bloqueado hasta que todas las disciplinas del torneo estén cerradas.

## Contenido implementado

- Vista de podios — 6 cards de división con top-3 por división
- Lock de overall — bloqueado si alguna disciplina no está `Finalizada`

## Estado

✅ Completado — 2026-04-28 · PR #128
