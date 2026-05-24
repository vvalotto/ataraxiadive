---
title: "US-ADJ-4.6 — Value Object TiempoAP: parsear MM:SS → segundos"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: competencia, shared
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.6
tests_count: null
rf: []
software_items:
  - src/competencia/domain/value_objects/ap.py
test_units: null
origen_tipo: plataforma
---

# US-ADJ-4.6 — Value Object TiempoAP: parsear MM:SS → segundos

## Descripción

Introduce el Value Object `TiempoAP` que parsea y valida el formato `MM:SS` de los APs de tiempo (STA, SPE), convirtiéndolo a segundos para el dominio.

## RFs corregidos

Sin RF directo — corrección de modelo de dominio.

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-06 | APs de tiempo en `MM:SS` sin conversión en dominio | MEDIO |

## Contenido implementado

- VO `TiempoAP` con parsing `MM:SS → int (segundos)`
- Validación de formato (minutos 0-59, segundos 0-59)
- Integración en `RegistrarAP` para disciplinas de tiempo

## Motivación

Los jueces ingresan el AP en formato `MM:SS` (ej: `3:45`). El dominio necesita trabajar en segundos para cálculos de grilla y comparaciones. Sin el VO, la conversión estaba dispersa o ausente.

## Tests

Tests de parseo y validación del VO `TiempoAP` agregados.

## Estado

✅ Completado — 2026-04-03
