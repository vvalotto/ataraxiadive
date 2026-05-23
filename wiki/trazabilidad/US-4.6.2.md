---
title: "US-4.6.2 — CalculadorHashCompetencia: hash SHA-256 de integridad"
type: trazabilidad-us
sp: SP4
inc: INC-4.6
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §17
us_id: US-4.6.2
tests_count: null
---

# US-4.6.2 — CalculadorHashCompetencia: hash SHA-256 de integridad

## Descripción

Calcula y persiste un hash SHA-256 del estado final de una competencia al momento de su cierre, garantizando la integridad de los resultados y permitiendo detección de alteraciones.

## Decisiones cubiertas

PLAN-SP4 §INC-4.6 · ADR-001 · ADR-008

## Contenido implementado

- Servicio `CalculadorHashCompetencia` — cálculo canónico deterministico de hash
- `CompetenciaFinalizada.hash_sha256` — campo persistido en el event store al cierre
- Integración en política P-08 (antes del evento de finalización)
- Valor conocido para disciplina sin performances (hash de string vacío)

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain (CalculadorHashCompetencia) | ✅ |
| integration/competencia | ✅ |

## Estado

✅ Completado — 2026-04-18
