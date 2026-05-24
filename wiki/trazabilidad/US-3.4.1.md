---
title: "US-3.4.1 — AsignarDisciplinas + AsignarJuez en Torneo"
type: trazabilidad-us
sp: SP3
inc: INC-3.4
bc: torneo
estado: cerrada
fecha_cierre: "2026-04-01"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.4.1
tests_count: null
rf:
  - RF-EJ-01
software_items:
  - src/torneo/application/commands/asignar_disciplinas.py
  - src/torneo/application/commands/asignar_juez.py
test_units:
  - tests/features/US-3.4.1-asignar-disciplinas-juez.feature
  - tests/integration/torneo/test_disciplinas_torneo_api.py
origen_tipo: rf
---

# US-3.4.1 — AsignarDisciplinas + AsignarJuez en Torneo

## Descripción

Permite al organizador asignar las disciplinas que tendrá el torneo y asignar un juez responsable a cada disciplina.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-EJ-01 | Más de un juez asignado a una disciplina |

## Comandos principales

`AsignarDisciplinas`, `AsignarJuez`

## Contenido implementado

- `PUT /torneos/{id}/disciplinas` — configurar lista de disciplinas del torneo
- `PUT /torneos/{id}/disciplinas/{disciplina}/juez` — asignar juez a disciplina
- Validación: el juez debe existir en el BC Identidad con rol JUEZ

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/torneo/domain | ✅ |
| integration/torneo | ✅ |
| features/US-3.4.1-asignar-disciplinas-juez | ✅ |
| **Total** | **35 tests** |

## Estado

✅ Completado — 2026-04-01
