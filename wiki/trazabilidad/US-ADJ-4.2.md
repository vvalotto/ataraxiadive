---
title: "US-ADJ-4.2 — Corregir orden grilla STA: ascendente"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.2
tests_count: null
---

# US-ADJ-4.2 — Corregir orden grilla STA: ascendente

## Descripción

Corrige el orden de la grilla para la disciplina STA (Static Apnea): el sistema generaba orden descendente cuando el reglamento FAAS exige orden ascendente (menor AP primero).

## RFs corregidos

| RF | Corrección |
|----|-----------|
| RF-PR-05 | `orden_ascendente=True` para STA (menor AP al primero — más tiempo en agua al final) |

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-04 | Orden grilla STA invertido (`orden_ascendente=False`) | CRÍTICO |

## Contexto

En STA el atleta con menor AP declarado sale primero para que el récord potencial cierre la sesión. El sistema tenía invertida la lógica heredada de SPE (descendente).

## Tests

Tests de generación de grilla STA actualizados para validar el orden correcto.

## Estado

✅ Completado — 2026-04-03
