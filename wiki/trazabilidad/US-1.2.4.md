---
title: "US-1.2.4 — AsignarTarjeta (blanca/roja)"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: completado
fecha_cierre: "2026-03-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
---

# US-1.2.4 — AsignarTarjeta (blanca/roja)

## Descripción

Permite al juez asignar tarjeta blanca (actuación válida) o roja (descalificación) a un atleta tras su performance.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-EJ-10 | Solo se registra resultado de tarjeta (no el SP en sí) |

## Comando principal

`AsignarTarjeta`

## Invariantes aplicadas

- INV-P-07: tarjeta asignable solo tras resultado registrado
- INV-P-10: tarjeta roja implica DQ — no se pueden registrar más resultados
- INV-P-11: una sola tarjeta por performance

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.4 | ✅ |
| **Total acumulado** | **92 tests (98%)** |

## Estado

✅ Completado — 2026-03-22
