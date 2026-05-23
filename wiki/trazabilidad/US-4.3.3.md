---
title: "US-4.3.3 — Wizard extendido: DNS, BKO, tarjeta roja con MotivoDQ y BlancaConPenalizaciones"
type: trazabilidad-us
sp: SP4
inc: INC-4.3
bc: frontend, competencia
estado: cerrada
fecha_cierre: "2026-04-12"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §14
us_id: US-4.3.3
tests_count: null
---

# US-4.3.3 — Wizard extendido: DNS, BKO, tarjeta roja con MotivoDQ

## Descripción

Extiende el wizard del juez para cubrir todos los casos especiales: DNS, black-out, descalificación con motivo específico y tarjeta blanca con penalizaciones.

## RFs / Wireframes cubiertos

RF-EJ-07, RF-EJ-08 · wireframes-juez S-12 a S-14

## Contenido implementado

- `POST /competencia/{id}/registrar-dns` en router backend
- Wizard extendido con pasos: DNS, BKO (con distancia), tarjeta roja + `MotivoDqSelector`
- `MotivoDqSelector` — selector de motivo de DQ (BKO_SUPERFICIE, NO_PROTOCOLO, etc.)
- `PenalizacionesSelector` — selector de penalizaciones técnicas acumulables
- Fixture STA + DNF para tests de integración

## Tests

`npm run build` + `npm run lint` + `compileall` + smoke test `TestClient` OK. UAT INC-4.3 — 2026-04-12.

## Estado

✅ Completado — 2026-04-12
