---
title: "US-4.1.3 — Subdisciplinas SPE: SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: shared, torneo
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.3
tests_count: 73
rf:
  - RF-GT-02-disciplinas-configurables
---

# US-4.1.3 — Subdisciplinas SPE: variantes de piscina

## Descripción

Agrega las cuatro variantes de la disciplina SPE (Static Pool Equipment) según las distancias reglamentarias CMAS/FAAS: 2×50m, 4×50m, 8×50m y 16×50m.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-GT-02-disciplinas-configurables]] | Disciplinas configurables — variantes SPE |

## Contenido implementado

- `Disciplina.SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50` en `shared/domain/value_objects/`
- `DisciplinaDescriptor` extendido para cada variante (orden descendente, unidad distancia)
- Propagación a fixtures y seeds de tests

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/shared | ✅ |
| unit/torneo | ✅ |
| integration/torneo | ✅ |
| features/US-4.1.3 | ✅ |
| **Total acumulado** | **73 passed** |

## Estado

✅ Completado — 2026-04-08
