---
title: "US-3.4.1 — AsignarDisciplinas + AsignarJuez en Torneo"
type: trazabilidad-us
sp: SP3
inc: INC-3.4
bc: torneo
estado: completado
fecha_cierre: "2026-04-01"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
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
