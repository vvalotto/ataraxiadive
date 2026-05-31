---
title: "US-ADJ-3.1 — Extraer GrillaDeSalida VO + eliminar _DISCIPLINAS_SP3"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: competencia, torneo
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
us_id: US-ADJ-3.1
tests_count: null
rf: []
software_items:
  - src/competencia/domain/aggregates/competencia.py
test_units: null
origen_tipo: calidad
componentes_wiki: []
---

# US-ADJ-3.1 — Extraer GrillaDeSalida VO + eliminar _DISCIPLINAS_SP3

## Descripción

Extrae el concepto de grilla de salida a un Value Object propio y elimina la constante hardcodeada `_DISCIPLINAS_SP3`, aplicando OCP para que el sistema soporte nuevas disciplinas sin modificar código existente.

## Capas afectadas

`competencia/domain/`, `torneo/domain/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| ADJ-01 | `GrillaDeSalida` extraído como VO con lógica de generación y ajuste encapsulada |
| SOLID-01 | Eliminación de `_DISCIPLINAS_SP3` — lista hardcodeada que violaba OCP |

## Principios aplicados

- **OCP**: agregar una disciplina nueva no requiere modificar el aggregate `Competencia`

## Tests

BDD waiver — refactoring estructural. Tests existentes de SP2/SP3 pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
