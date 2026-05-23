---
title: "US-4.1.7 — Descomponer GrillaDeSalida.ajustar() y RankingCompetencia"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.7
tests_count: 32
---

# US-4.1.7 — Descomponer GrillaDeSalida.ajustar() y RankingCompetencia

## Descripción

Refactoring técnico: descompone métodos complejos en `GrillaDeSalida` y `RankingCompetencia` en submétodos con responsabilidades únicas.

## Capas afectadas

`competencia/domain/`

## Contenido implementado

- `GrillaDeSalida.ajustar()` partido en submétodos privados (validación, intercambio, recálculo de OTs)
- `RankingCompetencia` descompuesto — separación entre ordenamiento, cálculo de puntos y generación de podio

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/resultados/domain | ✅ |
| **Total acumulado** | **32 passed** |

BDD waiver — refactoring estructural.

## Estado

✅ Completado — 2026-04-08
