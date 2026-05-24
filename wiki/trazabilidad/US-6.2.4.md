---
title: "US-6.2.4 — Panel torneo: alertas sin botón Resolver + jueces sin nombre"
type: trazabilidad-us
sp: SP6
inc: INC-6.2
bc: frontend, torneo
estado: cerrada
fecha_cierre: "2026-05-07"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §30
us_id: US-6.2.4
tests_count: null
rf: []
---

# US-6.2.4 — Panel torneo: alertas sin botón Resolver + jueces sin nombre

## Descripción

Correcciones en el panel del torneo: las alertas ya no muestran un botón "Resolver" que no hacía nada; la lista de jueces asignados no muestra un campo de nombre vacío.

## Contenido implementado

- `TorneoPanel.tsx` — alertas sin botón "Resolver"; jueces sin texto nombre redundante

## Estado

✅ Completado — 2026-05-07 · PR #151
