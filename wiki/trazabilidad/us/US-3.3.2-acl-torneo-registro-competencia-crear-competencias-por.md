---
title: "US-3.3.2 — ACL Torneo/Registro → Competencia: crear competencias por disciplina"
type: trazabilidad-us
sp: SP3
inc: INC-3.3
bc: competencia, torneo, registro
estado: cerrada
fecha_cierre: "2026-03-31"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.3.2
tests_count: null
rf:
  - RF-GT-02-disciplinas-configurables
  - RF-GT-03-torneos-activos-simultaneos
  - RF-IN-01-categorias-configurables
  - RF-IN-02-brevet-opcional
  - RF-IN-03-sin-limite-atletas
  - RF-IN-04-cancelacion-inscripcion-atleta
software_items:
  - src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py
test_units:
  - tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature
origen_tipo: rf
componentes_wiki: []
---

# US-3.3.2 — ACL Torneo/Registro → Competencia: crear competencias por disciplina

## Descripción

Implementa la ACL que permite crear automáticamente una `Competencia` por cada disciplina configurada en un `Torneo`, usando datos de los BCs Torneo y Registro como contexto.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-IN-01-categorias-configurables]] | Categorías configurables por edad y género |
| [[RF-IN-02-brevet-opcional]] | Brevet no obligatorio |
| [[RF-IN-03-sin-limite-atletas]] | Sin límite de atletas |
| [[RF-IN-04-cancelacion-inscripcion-atleta]] | Cancelar inscripción hasta el día anterior |
| [[RF-GT-02-disciplinas-configurables]] | Disciplinas configurables |
| [[RF-GT-03-torneos-activos-simultaneos]] | Múltiples torneos activos simultáneamente |

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
