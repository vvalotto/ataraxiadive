---
title: "US-3.1.2 — API REST Torneo: CRUD + transiciones + repositorio SQLite"
type: trazabilidad-us
sp: SP3
inc: INC-3.1
bc: torneo
estado: cerrada
fecha_cierre: "2026-03-30"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.1.2
tests_count: null
rf:
  - RF-GT-01-sede-unica-por-torneo
  - RF-GT-02-disciplinas-configurables
  - RF-GT-03-torneos-activos-simultaneos
  - RF-GT-04-cancelacion-conserva-datos
  - RF-GT-05-transiciones-ciclo-vida-torneo
  - RF-GT-07-entidad-organizadora-registrada
software_items:
  - src/torneo/application/commands/crear_torneo.py
  - src/torneo/application/commands/transicionar_torneo.py
  - src/torneo/api/router.py
test_units:
  - tests/features/US-3.1.2-api-rest-torneo.feature
  - tests/integration/torneo/test_sqlite_torneo_repository.py
origen_tipo: rf
---

# US-3.1.2 — API REST Torneo: CRUD + transiciones + repositorio SQLite

## Descripción

Expone el aggregate Torneo vía API REST con endpoints de CRUD y los 7 endpoints de transición de fase. Incluye la implementación concreta del repositorio SQLite.

## RFs cubiertos

| RF       | Descripción                                    |
| -------- | ---------------------------------------------- |
| [[RF-GT-01-sede-unica-por-torneo]] | Un torneo tiene una sola sede                  |
| [[RF-GT-02-disciplinas-configurables]] | Disciplinas configurables                      |
| [[RF-GT-03-torneos-activos-simultaneos]] | Múltiples torneos activos simultáneamente      |
| [[RF-GT-04-cancelacion-conserva-datos]] | Cancelar = estado Cancelado, datos preservados |
| [[RF-GT-05-transiciones-ciclo-vida-torneo]] | Restricciones de transición entre fases        |
| [[RF-GT-07-entidad-organizadora-registrada]] | Registrar EntidadOrganizadora                  |

## Contenido implementado

- `POST /torneos` — crear torneo
- `GET /torneos`, `GET /torneos/{id}` — listar y obtener
- `PATCH /torneos/{id}/abrir-inscripcion`, `/iniciar-preparacion`, `/iniciar-ejecucion`, `/iniciar-premiacion`, `/cerrar`, `/cancelar`, `/retroceder-ejecucion`
- `SQLiteTorneoRepository` — implementación concreta del puerto

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/torneo/application/test_crear_torneo | ✅ |
| unit/torneo/application/test_transiciones_handlers | ✅ |
| unit/torneo/application/test_obtener_torneo | ✅ |
| integration/torneo/test_sqlite_torneo_repository | ✅ |
| features/US-3.1.2-api-rest-torneo | ✅ |
| **Total** | **33 tests (100%)** |

## Estado

✅ Completado — 2026-03-30
