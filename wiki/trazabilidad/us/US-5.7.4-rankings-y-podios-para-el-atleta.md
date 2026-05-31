---
title: "US-5.7.4 — Rankings y podios para el atleta"
type: trazabilidad-us
sp: SP5
inc: INC-5.7
bc: resultados
estado: cerrada
fecha_cierre: "2026-05-01"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §28
  - docs/plans/sp5/US-5.7.4-plan.md
us_id: US-5.7.4
tests_count: null
rf: []
software_items:
  - src/resultados/application/queries/obtener_ranking.py
  - src/resultados/application/queries/obtener_overall.py
test_units:
  - tests/features/US-5.7.4-rankings-podios.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/resultados/query-handlers-resultados
---

# US-5.7.4 — Rankings y podios para el atleta

## Descripción

Sección `Rankings y podios` del portal del atleta. Muestra la tabla de ejecución con todos los competidores y el podio de la disciplina en la que participó el atleta. Usa el endpoint de ranking provisional que hace fallback a `competencia.db` cuando `resultados.db` está vacío.

## Contenido implementado

- Tabla de ejecución — ranking de la disciplina del atleta
- Podio de disciplina — top-3 de la disciplina del atleta
- Fix ranking provisional — fallback a lectura de `competencia.db` cuando no hay datos en `resultados.db` (deuda técnica documentada en [[resultados]])

## Estado

✅ Completado — 2026-05-01 · PR #140
