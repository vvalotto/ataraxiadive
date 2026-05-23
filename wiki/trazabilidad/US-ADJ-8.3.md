---
title: "US-ADJ-8.3 — SP-ADJ-08: cancelar torneo con confirmación fuerte"
type: trazabilidad-us
sp: SP-ADJ-08
inc: SP-ADJ-08
bc: torneo
estado: cerrada
fecha_cierre: "2026-04-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §22
  - docs/plans/sp-adj-08/PLAN-SP-ADJ-08.md
us_id: US-ADJ-8.3
tests_count: null
---

# US-ADJ-8.3 — SP-ADJ-08: cancelar torneo con confirmación fuerte

## Descripción

Resolución de hallazgo UAT-5.2-08: la acción `Cancelar torneo` se mueve a una zona de peligro con un modal de confirmación fuerte. El botón de confirmación solo se habilita cuando el usuario escribe el nombre exacto del torneo.

## Contenido implementado

- `AccionesPanel` — zona de peligro para cancelación
- Modal de confirmación — campo de texto con nombre exacto del torneo como guard

## Estado

✅ Completado — 2026-04-22 · PR #109
