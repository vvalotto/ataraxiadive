---
title: "US-3.3.1 — torneo_id opcional en Competencia para overall"
type: trazabilidad-us
sp: SP3
inc: INC-3.3
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-31"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.3.1
tests_count: null
rf:
  - RF-PM-01-resultados-por-puntos-faas
  - RF-PM-02-ranking-general-overall
  - RF-PM-05-rankings-por-categoria-y-genero
software_items:
  - src/competencia/domain/aggregates/competencia.py
  - src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py
test_units:
  - tests/features/US-3.3.1-torneo-id-competencia.feature
  - tests/integration/competencia/test_torneo_id_integration.py
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/competencia-aggregate
  - arquitectura/competencia/sqlite-event-store
---

# US-3.3.1 — torneo_id opcional en Competencia para overall

## Descripción

Agrega el campo `torneo_id` opcional al aggregate `Competencia`, habilitando la asociación de una competencia a un torneo y el posterior cálculo de overall multi-disciplina.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PM-01-resultados-por-puntos-faas]] | Fórmula de puntos configurable por torneo |
| [[RF-PM-02-ranking-general-overall]] | Overall = ranking general multi-disciplina por categoría |
| [[RF-PM-05-rankings-por-categoria-y-genero]] | Rankings por categoría y género |

## Contenido implementado

- Campo `torneo_id: Optional[str]` en `Competencia`
- Migración SQLite
- Query `GET /competencia?torneo_id={id}` para listar competencias de un torneo

## Tests

Validado como parte de la suite acumulada de INC-3.3.

## Estado

✅ Completado — 2026-03-31
