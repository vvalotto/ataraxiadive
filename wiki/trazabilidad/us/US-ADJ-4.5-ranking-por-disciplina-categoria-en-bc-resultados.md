---
title: "US-ADJ-4.5 — Ranking por (disciplina, categoría) en BC Resultados"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.5
tests_count: null
rf:
  - RF-PM-05-rankings-por-categoria-y-genero
software_items:
  - src/resultados/domain/aggregates/ranking_competencia.py
test_units: null
origen_tipo: rf
componentes_wiki:
  - arquitectura/resultados/ranking-competencia
---

# US-ADJ-4.5 — Ranking por (disciplina, categoría) en BC Resultados

## Descripción

Corrige el modelo de ranking: en lugar de un ranking plano por disciplina, el sistema calcula rankings segmentados por la combinación (disciplina, categoría), que es la unidad real de competencia reglamentaria.

## RFs corregidos

| RF | Corrección |
|----|-----------|
| RF-PM-05 | Rankings por categoría y género — agrupación real del reglamento |

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-01 | Ranking flat vs. por (disciplina, categoría, sexo) | CRÍTICO |

## Contexto

En la apnea competitiva, los atletas compiten dentro de su categoría (SENIOR, MASTER, JUNIOR) y los rankings y podios se calculan separadamente. Un ranking global mezclaría categorías incompatibles.

## Tests

Tests de ranking actualizados para validar la segmentación correcta.

## Estado

✅ Completado — 2026-04-03
