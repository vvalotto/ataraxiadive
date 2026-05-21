---
title: "US-5.6.1 — Puerto AlgoritmoPuntaje + implementación FAAS"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: resultados
estado: completado
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
---

# US-5.6.1 — Puerto AlgoritmoPuntaje + implementación FAAS

## Descripción

Define el puerto `AlgoritmoPuntaje` (clase abstracta base) e implementa `AlgoritmoPuntajeFAAS` con las fórmulas oficiales FAAS para cada modalidad: disciplinas de distancia (DNF, DYN, DBF) y de tiempo (STA, SPE).

## Contenido implementado

- Puerto `AlgoritmoPuntaje` — ABC que desacopla el algoritmo del cálculo de ranking
- `AlgoritmoPuntajeFAAS` — fórmulas FAAS por tipo de disciplina
- 23 tests unitarios

DesignReviewer INC-5.6 + SP-ADJ-09 consolidado: **0 CRITICAL · 252 WARNING** (+25 vs INC-5.5; LCOM/FanOut en RankingCompetencia/RankingOverall/AlgoritmoPuntajeFAAS).

## Estado

✅ Completado — 2026-04-28 · PR #123
