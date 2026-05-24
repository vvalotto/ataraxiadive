---
title: "US-5.1.7 — Política de tabs por fase en DetalleTorneoPage"
type: trazabilidad-us
sp: SP5
inc: INC-5.1-ADJ
bc: torneo
estado: cerrada
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §20
  - docs/plans/sp5/US-5.1.7-plan.md
us_id: US-5.1.7
tests_count: null
rf: []
software_items:
  - src/torneo/application/queries/obtener_torneo.py
test_units:
  - tests/features/US-5.1.7-politica-tabs.feature
origen_tipo: plataforma
---

# US-5.1.7 — Política de tabs por fase en DetalleTorneoPage

## Descripción

Ajuste post-UAT (hallazgos UAT-5.1-03 y UAT-5.1-05): define la política de visibilidad de tabs en [[US-5.1.2]] según el estado del torneo.

## Política implementada

| Estado torneo | Tabs visibles |
|---------------|--------------|
| `CREADO` | Solo Detalle |
| `INSCRIPCION_ABIERTA` | Detalle + Inscriptos |
| `PREPARACION` | Detalle + Inscriptos + Grilla + Jueces |
| `EJECUCION / PREMIACION / CERRADO` | Todas las tabs |
| `CANCELADO` | Resumen + mensaje; sin tabs operativas |

## Estado

✅ Completado — 2026-04-21 · PR #101
