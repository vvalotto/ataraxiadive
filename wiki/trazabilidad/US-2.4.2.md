---
title: "US-2.4.2 — CalcularRanking — BC Resultados núcleo"
type: trazabilidad-us
sp: SP2
inc: INC-2.4
bc: resultados
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.4.2
tests_count: null
rf:
  - RF-PM-03
software_items:
  - src/resultados/application/commands/calcular_ranking.py
  - src/resultados/domain/aggregates/ranking_competencia.py
test_units:
  - tests/features/US-2.4.2-calcular-ranking.feature
  - tests/integration/resultados/test_calcular_ranking_integration.py
origen_tipo: rf
---

# US-2.4.2 — CalcularRanking — BC Resultados núcleo

## Descripción

Introduce el BC Resultados con su funcionalidad núcleo: calcular el ranking de una competencia, resolver empates y determinar el podio.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PM-03]] | Empates = mismo puesto y mismos puntos |

## Comando principal

`CalcularRanking`

## Contenido implementado

- BC Resultados scaffold inicial
- Aggregate `RankingCompetencia`
- Lógica de ordenamiento por RP descendente
- Resolución de empates: mismo puesto compartido, mismo puntaje
- Cálculo del podio (top 3 por categoría)

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.4.

## Estado

✅ Completado — 2026-03-28
