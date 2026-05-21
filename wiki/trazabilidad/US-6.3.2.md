---
title: "US-6.3.2 — Inscripción atleta: AP inline + apto médico + constancia pago"
type: trazabilidad-us
sp: SP6
inc: INC-6.3
bc: registro, frontend
estado: completado
fecha_cierre: "2026-05-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §31
---

# US-6.3.2 — Inscripción atleta: AP inline + apto médico + constancia pago

## Descripción

Extiende el wizard de inscripción del atleta con AP inline (sin salir del wizard) y persiste dos nuevos campos requeridos: apto médico y constancia de pago. Incluye cambios en backend (aggregate, repo, API de registro).

## Contenido implementado

- `AtletaInscripcionPage.tsx` — AP inline en wizard; campos apto médico + constancia de pago
- BC `registro` — aggregate + repo + API con nuevos campos de inscripción

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/registro | 32 tests ✅ |
| BDD features/registro | 8 escenarios ✅ |

## Estado

✅ Completado — 2026-05-08 · PR #155
