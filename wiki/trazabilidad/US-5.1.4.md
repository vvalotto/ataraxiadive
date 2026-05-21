---
title: "US-5.1.4 — GrillaPanel: generar y confirmar grilla por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: competencia
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.4-plan.md
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
