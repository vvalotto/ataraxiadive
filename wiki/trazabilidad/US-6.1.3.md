---
title: "US-6.1.3 — Grilla ordenada por estado + keypad visible en móvil"
type: trazabilidad-us
sp: SP6
inc: INC-6.1
bc: frontend
estado: cerrada
fecha_cierre: "2026-05-04"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §29
us_id: US-6.1.3
tests_count: null
---

# US-6.1.3 — Grilla ordenada por estado + keypad visible en móvil

## Descripción

Correcciones de usabilidad en la vista del juez: grilla ordenada por estado (MUX-03 ya resuelto), keypad visible en móvil (MUX-01) y ajustes de espaciado en `RpSelector`.

## Contenido implementado

- `RpSelector.tsx` — `space-y-2` + `py-2` en keypad para visibilidad móvil (MUX-01)
- Grilla ordenada por estado de actuación

## Estado

✅ Completado — 2026-05-04 · PR #145
