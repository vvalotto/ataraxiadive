---
title: "US-5.6.2 — TipoReglamento en Torneo + DI en CalcularRankingHandler"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: torneo, resultados
estado: completado
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
---

# US-5.6.2 — TipoReglamento en Torneo + DI en CalcularRankingHandler

## Descripción

Introduce el Value Object `TipoReglamento` (FAAS/CMAS/AIDA) en el aggregate `Torneo`. Agrega la migración SQLite correspondiente e inyecta el algoritmo correcto en `CalcularRankingHandler` según el reglamento del torneo.

## Contenido implementado

- `TipoReglamento` VO (StrEnum: FAAS / CMAS / AIDA) en `Torneo`
- Migración SQLite — columna `tipo_reglamento` en tabla de torneos
- DI de `AlgoritmoPuntaje` en `CalcularRankingHandler`
- 15 tests unitarios

## Estado

✅ Completado — 2026-04-28 · PR #124
