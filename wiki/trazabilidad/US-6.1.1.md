---
title: "US-6.1.1 — Fix canSubmitBko + reorden flujo juez (tarjeta → marca)"
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

# US-6.1.1 — Fix canSubmitBko + reorden flujo juez (tarjeta → marca)

## Descripción

Corrige el remanente de `canSubmitBko` y reordena el flujo del juez: el paso 5 pasa a ser la tarjeta y el paso 6 la marca (antes era al revés). Cambios en `usePerformanceFlow.ts` y `PerformanceFlowPage.tsx`.

## Contenido implementado

- `usePerformanceFlow.ts` — reorden de pasos: tarjeta (5) → marca (6)
- `PerformanceFlowPage.tsx` — refleja el nuevo orden de pasos
- Limpieza del remanente `canSubmitBko`

DesignReviewer cierre conjunto INC-6.1/6.2: **0 CRITICAL · 256 WARNING**.

## Estado

✅ Completado — 2026-05-04 · PR #143
