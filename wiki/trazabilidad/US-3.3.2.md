---
title: "US-3.3.2 — ACL Torneo/Registro → Competencia: crear competencias por disciplina"
type: trazabilidad-us
sp: SP3
inc: INC-3.3
bc: competencia, torneo, registro
estado: completado
fecha_cierre: "2026-03-31"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
---

# US-3.3.2 — ACL Torneo/Registro → Competencia: crear competencias por disciplina

## Descripción

Implementa la ACL que permite crear automáticamente una `Competencia` por cada disciplina configurada en un `Torneo`, usando datos de los BCs Torneo y Registro como contexto.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-IN-01 | Categorías configurables por edad y género |
| RF-IN-02 | Brevet no obligatorio |
| RF-IN-03 | Sin límite de atletas |
| RF-IN-04 | Cancelar inscripción hasta el día anterior |
| RF-GT-02 | Disciplinas configurables |
| RF-GT-03 | Múltiples torneos activos simultáneamente |

## Contenido implementado

- ACL en `competencia/application/` que consulta Torneo y Registro
- Creación automática de una `Competencia` por disciplina al pasar a estado `PREPARACION`
- Integración cross-BC mediante puertos y adaptadores

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/application | ✅ |
| integration cross-BC | ✅ |
| features/US-3.3.2 | ✅ |

## Estado

✅ Completado — 2026-03-31
