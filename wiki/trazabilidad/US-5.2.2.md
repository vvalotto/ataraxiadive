---
title: "US-5.2.2 — Acción Finalizar prueba por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.2
bc: competencia
estado: completado
fecha_cierre: "2026-04-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §21
  - docs/plans/sp5/US-5.2.2-plan.md
---

# US-5.2.2 — Acción Finalizar prueba por disciplina

## Descripción

Acción `Finalizar prueba` en el panel de ejecución por disciplina. Solo se habilita si no hay performances pendientes de registro. Distingue cierre manual (acción del organizador) vs. cierre automático por P-08 (todas las performances registradas).

## Contenido implementado

- Acción `Finalizar prueba` — `PATCH /competencia/{id}/finalizar`
- Precondición: sin performances pendientes
- Distinción cierre manual vs. automático (P-08)

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.2 | ✅ |

## Estado

✅ Completado — 2026-04-22 · PR #106
