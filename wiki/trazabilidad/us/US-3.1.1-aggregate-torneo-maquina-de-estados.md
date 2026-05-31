---
title: "US-3.1.1 — Aggregate Torneo: máquina de estados"
type: trazabilidad-us
sp: SP3
inc: INC-3.1
bc: torneo
estado: cerrada
fecha_cierre: "2026-03-29"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.1.1
tests_count: null
rf:
  - RF-GT-01-sede-unica-por-torneo
  - RF-GT-03-torneos-activos-simultaneos
  - RF-GT-04-cancelacion-conserva-datos
  - RF-GT-05-transiciones-ciclo-vida-torneo
  - RF-GT-07-entidad-organizadora-registrada
software_items:
  - src/torneo/domain/aggregates/torneo.py
  - src/torneo/infrastructure/repositories/sqlite_torneo_repository.py
test_units:
  - tests/features/US-3.1.1-aggregate-torneo.feature
  - tests/integration/torneo/test_torneo_domain_integration.py
origen_tipo: rf
---

# US-3.1.1 — Aggregate Torneo: máquina de estados

## Descripción

Introduce el BC Torneo con su aggregate principal: `Torneo` con máquina de estados, value objects y puerto abstracto de repositorio.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-GT-01-sede-unica-por-torneo]] | Un torneo tiene una sola sede |
| [[RF-GT-03-torneos-activos-simultaneos]] | Múltiples torneos activos simultáneamente |
| [[RF-GT-04-cancelacion-conserva-datos]] | Cancelar = estado Cancelado, datos preservados |
| [[RF-GT-05-transiciones-ciclo-vida-torneo]] | Restricciones de transición entre fases (con retroceso Ejecución → Preparación) |
| [[RF-GT-07-entidad-organizadora-registrada]] | Registrar EntidadOrganizadora (federación/club) |

## Contenido implementado

- Aggregate `Torneo` con estados: `CREADO → INSCRIPCION_ABIERTA → PREPARACION → EJECUCION → PREMIACION → CERRADO / CANCELADO`
- Value objects: `Sede`, `EntidadOrganizadora`, `FechasTorneo`
- Puerto abstracto `TorneoRepositoryPort`
- Transiciones válidas e inválidas con excepciones de dominio

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/torneo/domain/test_torneo | ✅ |
| integration/torneo/test_torneo_domain_integration | ✅ |
| features/US-3.1.1-aggregate-torneo | ✅ |
| **Total** | **36 tests (100%)** |

## Estado

✅ Completado — 2026-03-29
