---
title: "US-6.6.4 — PublicTorneoDetallePage: torneo en ejecución para visitantes"
type: trazabilidad-us
sp: SP6
inc: INC-6.6
bc: frontend, competencia, resultados
estado: completado
fecha_cierre: "2026-05-10"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §SP6
  - docs/plans/sp6/US-6.6.4-plan.md
---

# US-6.6.4 — PublicTorneoDetallePage: torneo en ejecución para visitantes

## Descripción

Página pública de detalle de un torneo en ejecución. Muestra grilla con tabs por disciplina y podios por categoría sin requerir autenticación. Incluye ajustes UX del portal público y fix en `PublicTorneosPage` para la navegación de visitantes.

## Contenido implementado

- `PublicTorneoDetallePage` — grilla con tabs por disciplina + podios por categoría
- Fix `PublicTorneosPage` — link "Ver panel" de visitante apunta a `/portalapnea/{id}` (no al panel organizador)
- Ajustes UX: header con logo + `Mi portal` / `Iniciar sesión`

## Estado

✅ Completado · PR #167
