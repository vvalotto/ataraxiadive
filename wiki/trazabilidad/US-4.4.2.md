---
title: "US-4.4.2 — useComandoQueue: cola offline + estado optimista en grilla"
type: trazabilidad-us
sp: SP4
inc: INC-4.4
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §15
us_id: US-4.4.2
tests_count: null
---

# US-4.4.2 — useComandoQueue: cola offline + estado optimista en grilla

## Descripción

Implementa la cola de comandos offline: los comandos del juez (llamar, registrar resultado, asignar tarjeta) se envían directo si hay red o se encolan en IndexedDB si no hay conexión.

## Decisiones cubiertas

PLAN-SP4 §INC-4.4

## Contenido implementado

- Hook `useComandoQueue` — intercepta comandos y decide envío directo vs. encolado
- `PerformanceFlowPage` integra el hook: transparente para el juez
- Estado optimista en grilla: badge ⏳ para performances con comandos pendientes
- `useConnectionStore.pendingCount` — contador de comandos en cola visible en UI

## Tests

Frontend (build + lint) · UAT INC-4.4 iPhone. UAT SP4 — 2026-04-18.

## Estado

✅ Completado — 2026-04-18 (PR #77)
