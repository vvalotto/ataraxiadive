---
title: "US-5.6.2 — TipoReglamento en Torneo + DI en CalcularRankingHandler"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: torneo, resultados
estado: cerrada
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
us_id: US-5.6.2
tests_count: null
rf: []
software_items:
  - src/torneo/domain/value_objects/tipo_reglamento.py
  - src/torneo/infrastructure/repositories/sqlite_torneo_repository.py
test_units:
  - tests/features/US-5.6.2-tipo-reglamento-di-ranking.feature
  - tests/integration/torneo/test_tipo_reglamento_repository.py
origen_tipo: plataforma
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
