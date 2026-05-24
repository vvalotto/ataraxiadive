---
title: "US-4.1.4 — Orden SPE descendente en GrillaDeSalida"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.4
tests_count: 68
rf:
  - RF-PR-05
software_items:
  - src/competencia/domain/aggregates/competencia.py
test_units:
  - tests/features/US-4.1.4-orden-grilla-reglamentario.feature
origen_tipo: rf
---

# US-4.1.4 — Orden SPE descendente en GrillaDeSalida

## Descripción

Corrige el ordenamiento de la grilla para SPE: según el reglamento CMAS/FAAS, los atletas con mayor AP salen primero (orden descendente), al contrario que DNF/DYN/DBF/STA.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-PR-05 | Orden de grilla: AP ascendente (DNF/DYN/DBF/STA) o **descendente (SPE)** |

## Contenido implementado

- `GrillaDeSalida.generar()` usa `orden_ascendente=False` para todas las variantes SPE
- `DisciplinaDescriptor.orden_ascendente` correctamente configurado por disciplina

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| integration/competencia | ✅ |
| features/US-4.1.4 | ✅ |
| **Total acumulado** | **68 passed** |

## Estado

✅ Completado — 2026-04-08
