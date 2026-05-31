---
title: "US-5.1.2 — DetalleTorneoPage: tabs y panel de acciones de fase"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: torneo
estado: cerrada
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.2-plan.md
us_id: US-5.1.2
tests_count: null
rf: []
software_items:
  - src/torneo/application/queries/obtener_torneo.py
test_units:
  - tests/features/US-5.1.2-gestion-fases-torneo.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/torneo/query-handlers-torneo
---

# US-5.1.2 — DetalleTorneoPage: tabs y panel de acciones de fase

## Descripción

Página de detalle del torneo para el organizador. Muestra tabs (`Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion`) y un `AccionesPanel` que expone las transiciones de fase (`EstadoTorneo`) disponibles según el estado actual. La política de tabs por fase fue refinada en [[US-5.1.7-politica-de-tabs-por-fase-en-detalletorneopage]].

## Contenido implementado

- `DetalleTorneoPage` — layout con tabs y panel lateral de acciones
- `AccionesPanel` — botones de transición según `EstadoTorneo` vigente
- `FaseBadge` — indicador visual del estado actual del torneo

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

## Estado

✅ Completado — 2026-04-21 · PR #96
