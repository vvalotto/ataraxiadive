---
title: "US-5.1.3 — InscriptosPanel: lista de atletas con estado AP"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: registro
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.3-plan.md
---

# US-5.1.3 — InscriptosPanel: lista de atletas con estado AP

## Descripción

Tab `Inscriptos` del panel organizador. Muestra la lista de atletas inscriptos con su estado de anuncio previo (`AnunciadaAP` / `NoCompite`) por disciplina.

## Contenido implementado

- `InscriptosPanel` — tabla de inscriptos con estado AP por disciplina
- Integración con `GET /registro/inscripciones?torneo_id={id}` y datos de AP desde BC Competencia

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

## Estado

✅ Completado — 2026-04-21 · PR #97
