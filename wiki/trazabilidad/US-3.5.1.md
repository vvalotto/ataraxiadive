---
title: "US-3.5.1 — Aggregate RankingOverall + CalcularOverallHandler"
type: trazabilidad-us
sp: SP3
inc: INC-3.5
bc: resultados
estado: completado
fecha_cierre: "2026-04-02"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
---

# US-3.5.1 — Aggregate RankingOverall + CalcularOverallHandler

## Descripción

Introduce el aggregate `RankingOverall` en el BC Resultados con su handler de cálculo: suma los puntos de todas las disciplinas por atleta para producir el ranking general del torneo.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-PM-01 | Fórmula de puntos configurable por torneo |
| RF-PM-02 | Overall = ranking general multi-disciplina por categoría |

## Contenido implementado

- Aggregate `RankingOverall` con `puntos_overall = Σ puntos_disciplina` por atleta
- `CalcularOverallHandler` — orquesta la suma cross-disciplina
- Segmentación por categoría y género (ver también [[US-ADJ-4.5]])

## Tests

Validado como parte de la suite de INC-3.5.

## Estado

✅ Completado — 2026-04-02
