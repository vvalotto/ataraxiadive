---
title: "US-4.1.5 — Descomponer aggregate Performance en módulos especializados"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.5
tests_count: 82
rf: []
software_items:
  - src/competencia/domain/aggregates/performance.py
  - src/competencia/domain/aggregates/performance_state.py
test_units: null
origen_tipo: calidad
origen_refs:
  - BL-004
---

# US-4.1.5 — Descomponer aggregate Performance en módulos especializados

## Descripción

Refactoring técnico derivado del DesignReviewer al cierre de INC-4.1: el aggregate `Performance` monolítico se descompone en módulos con responsabilidades claras.

## Capas afectadas

`competencia/domain/`

## Contenido implementado

| Módulo | Responsabilidad |
|--------|----------------|
| `performance.py` | Aggregate principal — interfaz pública y coordinación |
| `performance_state.py` | Máquina de estados de la performance |
| `performance_events.py` | Definición de eventos de dominio de Performance |
| VO `ResolucionTarjeta` | Encapsula el resultado final de la tarjeta asignada |
| VO `RPFinal` | Encapsula el RP definitivo tras penalizaciones |

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| integration/competencia | ✅ |
| **Total acumulado** | **82 passed** |

BDD waiver — refactoring interno sin comportamiento nuevo.

## Estado

✅ Completado — 2026-04-08
