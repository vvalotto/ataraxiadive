---
title: "US-5.6.3 — RankingCompetencia con puntos por categoría"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: resultados
estado: completado
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
  - docs/plans/sp5/US-5.6.3-plan.md
---

# US-5.6.3 — RankingCompetencia con puntos por categoría

## Descripción

Extiende `RankingCompetencia` para calcular y almacenar `puntos: Decimal` por atleta usando el `AlgoritmoPuntaje` inyectado. Los resultados se agrupan por `Categoria` para soportar rankings por categoría/género.

## Contenido implementado

- `RankingCompetencia` — campo `puntos: Decimal` calculado con `AlgoritmoPuntaje`
- Agrupación de resultados por `Categoria`
- 84 tests unitarios

## Estado

✅ Completado — 2026-04-28 · PR #125
