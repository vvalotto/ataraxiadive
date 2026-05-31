---
title: "US-1.4.2 — Flujo E2E + audit log GET /events"
type: trazabilidad-us
sp: SP1
inc: INC-1.4
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.4.2
tests_count: 207
rf:
  - RF-EJ-05-cronometraje-manual-por-juez
  - RF-EJ-10-efecto-sp-registrado-como-tarjeta
software_items:
  - src/competencia/domain/aggregates/performance.py
  - src/competencia/domain/aggregates/competencia.py
test_units:
  - tests/features/US-1.4.2-flujo-e2e.feature
  - tests/integration/competencia/test_flujo_e2e.py
origen_tipo: rf
---

# US-1.4.2 — Flujo E2E + audit log GET /events

## Descripción

Valida el flujo completo de una competencia de punta a punta e introduce el endpoint de audit log que expone la traza de eventos almacenados en el Event Store.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-05-cronometraje-manual-por-juez]] | Cronometraje manual — juez ingresa el tiempo |
| [[RF-EJ-10-efecto-sp-registrado-como-tarjeta]] | Solo se registra resultado de tarjeta |

## Contenido implementado

- Flujo E2E: `RegistrarAP → LlamarAtleta → RegistrarResultado → AsignarTarjeta`
- Endpoint `GET /events` — exposición del audit log del Event Store para trazabilidad

## Invariantes validadas

- INV-P-05 a INV-P-10 — flujo completo cubierto

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.4.2 | ✅ |
| **Total acumulado** | **207 tests (98%)** |

## Estado

✅ Completado — 2026-03-23
