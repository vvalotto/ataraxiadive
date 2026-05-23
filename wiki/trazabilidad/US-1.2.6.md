---
title: "US-1.2.6 — CorregirResultado"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.2.6
tests_count: 128
---

# US-1.2.6 — CorregirResultado

## Descripción

Permite corregir el RP de un atleta dentro de la ventana de impugnación habilitada por el organizador.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-EJ-06 | Corrección con ventana de impugnación (INV-P-15, HS-P2 ✅) |

## Comando principal

`CorregirResultado`

## Invariantes aplicadas

- INV-P-12: corrección solo posible dentro de la ventana de impugnación activa
- INV-P-13: la corrección reemplaza el RP previo, no lo acumula

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.6 | ✅ |
| **Total acumulado** | **128 tests (98.51%)** |

## Estado

✅ Completado — 2026-03-23
