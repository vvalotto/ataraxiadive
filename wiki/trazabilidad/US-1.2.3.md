---
title: "US-1.2.3 — RegistrarResultado"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.2.3
tests_count: 65
---

# US-1.2.3 — RegistrarResultado

## Descripción

Permite al juez registrar el resultado real (RP — Resultado de Performance) de un atleta tras su actuación.

## RFs cubiertos

| RF       | Descripción                                  |
| -------- | -------------------------------------------- |
| RF-EJ-05 | Cronometraje manual — juez ingresa el tiempo |

## Comando principal

`RegistrarResultado`

## Invariantes aplicadas

- INV-P-06: resultado solo registrable si atleta fue llamado
- INV-P-09: resultado inmutable salvo `CorregirResultado` en ventana habilitada

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.3 | ✅ |
| **Total acumulado** | **65 tests (98%)** |

## Estado

✅ Completado — 2026-03-22
