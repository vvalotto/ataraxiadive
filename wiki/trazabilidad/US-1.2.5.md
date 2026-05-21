---
title: "US-1.2.5 — RegistrarDNS"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: completado
fecha_cierre: "2026-03-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
---

# US-1.2.5 — RegistrarDNS

## Descripción

Registra la ausencia de un atleta en su turno (Did Not Start). El DNS es una descalificación inmediata sin esperar el OT completo.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-EJ-02 | DNS = descalificación inmediata, sin espera (P-07, INV-P-08) |

## Comando principal

`RegistrarDNS`

## Invariantes aplicadas

- INV-P-08: DNS solo aplicable si el atleta fue llamado y no inició
- INV-P-09: resultado inmutable post-registro

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.5 | ✅ |
| **Total acumulado** | **108 tests (98.51%)** |

## Estado

✅ Completado — 2026-03-23
