---
title: "US-5.1.4 — GrillaPanel: generar y confirmar grilla por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.4-plan.md
us_id: US-5.1.4
tests_count: null
rf: []
software_items:
  - src/competencia/application/commands/generar_grilla.py
  - src/competencia/application/commands/confirmar_grilla.py
test_units:
  - tests/features/US-5.1.4-generacion-ajuste-grilla.feature
origen_tipo: plataforma
---

# US-5.1.4 — GrillaPanel: generar y confirmar grilla por disciplina

## Descripción

Tab `Grilla` del panel organizador. Lista las disciplinas del torneo con botón para generar/confirmar grilla por disciplina. Muestra los estados `GrillaGenerada` y `GrillaConfirmada` por cada una.

## Contenido implementado

- `GrillaPanel` — lista de disciplinas con acciones de grilla
- Estados `GrillaGenerada` / `GrillaConfirmada` visualizados por disciplina
- Integración con endpoints de generación de grilla por disciplina

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

## Estado

✅ Completado — 2026-04-21 · PR #98
