---
title: "US-5.7.1 — Mis torneos: lista de torneos inscriptos del atleta"
type: trazabilidad-us
sp: SP5
inc: INC-5.7
bc: registro, torneo
estado: cerrada
fecha_cierre: "2026-05-01"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §28
  - docs/plans/sp5/US-5.7.1-plan.md
us_id: US-5.7.1
tests_count: null
rf: []
software_items:
  - src/registro/application/queries/listar_inscriptos.py
test_units:
  - tests/features/US-5.7.1-mis-torneos.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/registro/query-handlers
---

# US-5.7.1 — Mis torneos: lista de torneos inscriptos del atleta

## Descripción

Sección `Mis torneos` del portal del atleta. Lista los torneos en los que el atleta tiene inscripción activa, con el estado actual de cada torneo. Incluye fix de inscripción condicional detectado en UAT.

## Contenido implementado

- Sección `Mis torneos` — torneos inscriptos con estado actual
- Fix inscripción condicional — evita duplicados en la lista

DesignReviewer consolidado INC-5.7: **0 CRITICAL · 256 WARNING** (+4 vs INC-5.6; `_rankear_categoria` en `ObtenerRankingProvisionalHandler` — aceptado como conocido).

## Estado

✅ Completado — 2026-05-01 · PR #137
