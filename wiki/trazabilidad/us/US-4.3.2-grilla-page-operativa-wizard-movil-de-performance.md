---
title: "US-4.3.2 — GrillaPage operativa + wizard móvil de performance"
type: trazabilidad-us
sp: SP4
inc: INC-4.3
bc: frontend, competencia
estado: cerrada
fecha_cierre: "2026-04-11"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §14
us_id: US-4.3.2
tests_count: null
rf:
  - RF-EJ-05-cronometraje-manual-por-juez
  - RF-EJ-06-correccion-resultado-registrado
componentes_wiki: []
---

# US-4.3.2 — GrillaPage operativa + wizard móvil de performance

## Descripción

Implementa la grilla de salida interactiva y el wizard móvil paso a paso que guía al juez en el registro de cada performance.

## RFs / Wireframes cubiertos

RF-EJ-05, RF-EJ-06 · wireframes-juez S-02 a S-09

## Contenido implementado

- Router `competencia`: `POST /llamar`, `POST /registrar-resultado`, `POST /asignar-tarjeta`
- `GrillaPage` — grilla enriquecida con estado de cada atleta, AP declarado y resultado
- `PerformanceFlowPage` — wizard móvil multi-paso para registrar resultados
- Componentes: `StepIndicator`, `AtletaCard`, `RpSelector`

## Tests

`npm run build` + `npm run lint` + `compileall` + smoke test `TestClient` OK. UAT INC-4.3 — 2026-04-12.

## Estado

✅ Completado — 2026-04-11
