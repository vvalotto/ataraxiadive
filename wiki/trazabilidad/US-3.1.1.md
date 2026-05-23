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
---

# US-3.1.1 — Aggregate Torneo: máquina de estados

## Descripción

Introduce el BC Torneo con su aggregate principal: `Torneo` con máquina de estados, value objects y puerto abstracto de repositorio.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-GT-01 | Un torneo tiene una sola sede |
| RF-GT-03 | Múltiples torneos activos simultáneamente |
| RF-GT-04 | Cancelar = estado Cancelado, datos preservados |
| RF-GT-05 | Restricciones de transición entre fases (con retroceso Ejecución → Preparación) |
| RF-GT-07 | Registrar EntidadOrganizadora (federación/club) |

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
