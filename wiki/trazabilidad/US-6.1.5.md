---
title: "US-6.1.5 — AtletaCard compacta en paso de RpSelector"
type: trazabilidad-us
sp: SP6
inc: INC-6.1
bc: frontend
estado: cerrada
fecha_cierre: "2026-05-04"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §29
us_id: US-6.1.5
tests_count: null
---

# US-6.1.5 — AtletaCard compacta en paso de RpSelector

## Descripción

Introduce variante compacta de `AtletaCard` para el paso de registro de marca (MUX-06). El paso 6 (RpSelector) usa la variante `compact` para no ocupar espacio excesivo en pantalla durante la ejecución.

## Contenido implementado

- `AtletaCard.tsx` — prop `variant='full'|'compact'`
- `PerformanceFlowPage.tsx` — paso 6 (RpSelector) usa `variant='compact'`

## Estado

✅ Completado — 2026-05-04 · PR #147
