---
title: "US-5.1.9 — Precondición de grilla para asignación de juez"
type: trazabilidad-us
sp: SP5
inc: INC-5.1-ADJ
bc: torneo, competencia
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §20
  - docs/plans/sp5/US-5.1.9-plan.md
---

# US-5.1.9 — Precondición de grilla para asignación de juez

## Descripción

Ajuste post-UAT (hallazgo UAT-5.1-02): el selector de juez en [[US-5.1.5]] solo se habilita si la disciplina tiene una `Competencia` en estado `GrillaGenerada`, `GrillaConfirmada`, `EnEjecucion` o `Finalizada`. Evita asignación de juez antes de que exista la competencia.

## Contenido implementado

- `JuecesPanel` / `TablaJueces` — lógica de habilitación del selector según estado de competencia por disciplina

## Estado

✅ Completado — 2026-04-21 · PR #103
