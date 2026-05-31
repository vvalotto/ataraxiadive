---
title: "US-ADJ-5.3 — Marcar madurez de BCs en context-map"
type: trazabilidad-us
sp: SP-ADJ-05
inc: SP-ADJ-05
bc: docs
estado: cerrada
fecha_cierre: "2026-04-04"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-05/PLAN-SP-ADJ-05.md
  - commit 4cf8ca0
us_id: US-ADJ-5.3
tests_count: null
rf: []
---

# US-ADJ-5.3 — Marcar madurez de BCs en context-map

## Descripción

Agrega la columna `Madurez` al context-map para reflejar honestamente el estado de implementación de cada BC al cierre de SP3.

## Fuente

HITO-14 D-07

## Contenido implementado

- `docs/design/context-map.md` — columna `Madurez` con valores:
  - `operativo`: BC con dominio completo y API funcional
  - `parcial`: BC con scaffold y funcionalidad básica
  - `modelado`: BC definido en el modelo pero sin implementación significativa

## Motivación

`Notificaciones` aparecía con la misma madurez implícita que `Competencia` en el context-map, cuando en realidad era casi solo scaffolding en SP3. La columna hace visible el estado real.

## Estado

✅ Completado — 2026-04-04 (commit `4cf8ca0`, PR #63)
