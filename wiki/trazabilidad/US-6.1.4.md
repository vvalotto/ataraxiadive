---
title: "US-6.1.4 — Rediseño inicio juez + STA mm:ss + tarjeta amarilla"
type: trazabilidad-us
sp: SP6
inc: INC-6.1
bc: frontend
estado: completado
fecha_cierre: "2026-05-04"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §29
---

# US-6.1.4 — Rediseño inicio juez + STA mm:ss + tarjeta amarilla

## Descripción

Mejoras en la experiencia del juez: rediseño de la pantalla de inicio (UI-JUE-01), formato mm:ss para STA (MUX-08), indicador de tarjeta amarilla en revisión (MUX-07) y cleanup de la pantalla de disciplinas.

## Contenido implementado

- `DisciplinasPage.tsx` — renombrado a "Mis asignaciones"; eliminado campo Password innecesario
- `utils/marca.ts` — sufijo " min" para marcas STA
- `StepRevision.tsx` — labels BLANCA/ROJA explícitos

## Estado

✅ Completado — 2026-05-04 · PR #146
