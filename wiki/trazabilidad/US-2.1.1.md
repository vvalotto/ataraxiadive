---
title: "US-2.1.1 — ConfigurarIntervaloOT + scaffold aggregate Competencia"
type: trazabilidad-us
sp: SP2
inc: INC-2.1
bc: competencia
estado: completado
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
---

# US-2.1.1 — ConfigurarIntervaloOT + scaffold aggregate Competencia

## Descripción

Permite configurar el intervalo entre Official Tops (OT) de una competencia. Introduce además el scaffold del aggregate `Competencia` resolviendo deuda SOLID acumulada en SP1.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-PR-08 | Intervalo entre OTs configurable por competencia (P-02) |

## Comando principal

`ConfigurarIntervaloOT`

## Invariantes aplicadas

- INV-C-01: el intervalo debe ser positivo y dentro de rangos válidos de reglamento

## Contenido implementado

- Comando `ConfigurarIntervaloOT` + handler
- Refactor scaffold aggregate `Competencia` (deuda SOLID SP1 resuelta)

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.1.

## Estado

✅ Completado — 2026-03-28
