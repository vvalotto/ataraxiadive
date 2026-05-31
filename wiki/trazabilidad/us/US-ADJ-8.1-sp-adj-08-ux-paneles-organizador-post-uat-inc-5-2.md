---
title: "US-ADJ-8.1 — SP-ADJ-08: UX paneles organizador post-UAT INC-5.2"
type: trazabilidad-us
sp: SP-ADJ-08
inc: SP-ADJ-08
bc: torneo, competencia
estado: cerrada
fecha_cierre: "2026-04-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §22
  - docs/plans/sp-adj-08/PLAN-SP-ADJ-08.md
us_id: US-ADJ-8.1
tests_count: null
rf: []
software_items:
  - src/torneo/api/router.py
test_units:
  - tests/features/US-ADJ-8.1-claridad-operativa-panel-organizador.feature
origen_tipo: calidad
componentes_wiki:
  - arquitectura/torneo/router-torneo
---

# US-ADJ-8.1 — SP-ADJ-08: UX paneles organizador post-UAT INC-5.2

## Descripción

Resolución de 5 hallazgos UAT (UAT-5.2-01, 03, 04, 06, 07): estados vacío/loading/error claros en paneles; mensajes de ejecución accionables; disciplina seleccionada visualmente destacada; lenguaje de fase preciso (`Pasar a premiacion` / `Cerrar torneo`).

## Hallazgos resueltos

- UAT-5.2-01: estados vacío/loading/error sin feedback claro
- UAT-5.2-03: mensajes de ejecución no accionables
- UAT-5.2-04: disciplina seleccionada no destacada visualmente
- UAT-5.2-06: lenguaje de fase impreciso
- UAT-5.2-07: lenguaje de transición inconsistente

## Estado

✅ Completado — 2026-04-22 · PR #108
