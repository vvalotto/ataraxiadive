---
title: "US-2.1.4 — ConfirmarGrilla + IniciarCompetencia"
type: trazabilidad-us
sp: SP2
inc: INC-2.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.1.4
tests_count: null
---

# US-2.1.4 — ConfirmarGrilla + IniciarCompetencia

## Descripción

Cierra la fase de preparación confirmando la grilla e inicia formalmente la competencia. Reemplaza el stub `CompetenciaEstadoPort` por la implementación real.

## RFs cubiertos

Sin RF directo — US de flujo de estado / máquina de estados.

## Comandos principales

`ConfirmarGrilla`, `IniciarCompetencia`

## Invariantes aplicadas

- INV-C-02: grilla confirmada es inmutable — no se pueden agregar atletas ni cambiar el orden
- INV-C-03: la competencia solo puede iniciarse con grilla confirmada

## Contenido adicional

- Reemplazo del stub `CompetenciaEstadoPort` por implementación concreta (elimina deuda técnica de SP1)

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.1.

## Estado

✅ Completado — 2026-03-28
