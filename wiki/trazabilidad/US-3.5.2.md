---
title: "US-3.5.2 — Política P-09: overall automático al cerrar torneo"
type: trazabilidad-us
sp: SP3
inc: INC-3.5
bc: resultados, torneo
estado: completado
fecha_cierre: "2026-04-02"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
---

# US-3.5.2 — Política P-09: overall automático al cerrar torneo

## Descripción

Implementa la política P-09: cuando el torneo pasa a estado `CERRADO`, el sistema calcula automáticamente el ranking overall sin intervención del organizador.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-PM-05 | Rankings por categoría y género |

## Contenido implementado

- Política P-09 registrada en composition root (`src/app.py`)
- Listener del evento `TorneoCerrado` → dispara `CalcularOverallHandler`
- Overall calculado y persistido en `resultados.db`

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/app | ✅ |
| integration/p09 | ✅ |
| features/US-3.5.2-politica-p09 | ✅ |
| **Total** | **17 tests** |

## Estado

✅ Completado — 2026-04-02
