---
title: "US-3.2.3 — Aggregate Inscripcion: inscribir, cancelar y listar"
type: trazabilidad-us
sp: SP3
inc: INC-3.2
bc: registro
estado: cerrada
fecha_cierre: "2026-03-31"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.2.3
tests_count: null
rf:
  - RF-IN-03-sin-limite-atletas
  - RF-IN-04-cancelacion-inscripcion-atleta
software_items:
  - src/registro/application/commands/inscribir_atleta.py
  - src/registro/domain/aggregates/inscripcion.py
  - src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py
test_units:
  - tests/features/US-3.2.3-inscripcion-atleta.feature
  - tests/integration/registro/test_sqlite_inscripcion_repository.py
origen_tipo: rf
---

# US-3.2.3 — Aggregate Inscripcion: inscribir, cancelar y listar

## Descripción

Introduce el aggregate `Inscripcion` en el BC Registro: permite inscribir un atleta a un torneo/disciplina, cancelar la inscripción y listar los inscriptos.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-IN-03-sin-limite-atletas]] | Sin límite de atletas por torneo o disciplina |
| [[RF-IN-04-cancelacion-inscripcion-atleta]] | Cancelar inscripción hasta el día anterior |

## Contenido implementado

- Aggregate `Inscripcion` con estados: `ACTIVA / CANCELADA`
- `POST /registro/inscripciones` — inscribir atleta
- `DELETE /registro/inscripciones/{id}` — cancelar inscripción
- `GET /registro/torneos/{id}/inscriptos` — listar inscriptos
- Regla: cancelación permitida solo hasta el día anterior al torneo

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/registro | ✅ |
| integration/registro | ✅ |
| features/US-3.2.3 | ✅ |
| **Total** | **31 tests** |

## Estado

✅ Completado — 2026-03-31
