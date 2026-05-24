---
title: "US-5.6.4 — RankingOverall: puntos acumulados por categoría y género"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
  - docs/plans/sp5/US-5.6.4-plan.md
us_id: US-5.6.4
tests_count: null
rf: []
software_items:
  - src/resultados/application/commands/calcular_overall.py
  - src/resultados/domain/aggregates/ranking_overall.py
test_units:
  - tests/features/US-5.6.4-ranking-overall-puntos.feature
origen_tipo: plataforma
---

# US-5.6.4 — RankingOverall: puntos acumulados por categoría y género

## Descripción

Implementa el ranking global del torneo (`RankingOverall`). Los puntos overall se calculan como la suma de puntos por disciplina. Para FAAS, la penalización por ausente es 0. El ranking se segmenta por categoría y género.

## Contenido implementado

- `RankingOverall` — `puntos_overall = Σ puntos_disciplina`
- `penalizacion_ausente = 0` (política FAAS)
- Segmentación por categoría y género
- 91 tests unitarios

## Estado

✅ Completado — 2026-04-28 · PR #126
