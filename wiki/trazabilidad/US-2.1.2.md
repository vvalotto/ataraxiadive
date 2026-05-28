---
title: "US-2.1.2 — GenerarGrilla / RegenerarGrilla"
type: trazabilidad-us
sp: SP2
inc: INC-2.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.1.2
tests_count: null
rf:
  - RF-PR-04
  - RF-PR-05
software_items:
  - src/competencia/application/commands/generar_grilla.py
test_units:
  - tests/features/US-2.1.2-generar-grilla.feature
  - tests/integration/competencia/test_generar_grilla_integration.py
origen_tipo: rf
---

# US-2.1.2 — GenerarGrilla / RegenerarGrilla

## Descripción

Genera el orden de salida de los atletas según el AP declarado. La grilla puede ser regenerada si se agregan o modifican atletas antes de confirmarla.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PR-04]] | Atleta sin AP no compite — no aparece en grilla (P-05) |
| [[RF-PR-05]] | Orden de grilla: AP ascendente (DNF/DYN/DBF/STA) o descendente (SPE) |

## Comandos principales

`GenerarGrilla`, `RegenerarGrilla`

## Invariantes aplicadas

- INV-C-01: solo atletas con AP aparecen en la grilla
- P-01: ordenamiento según disciplina (ascendente/descendente)
- P-02: respeto del intervalo OT configurado

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.1.

## Estado

✅ Completado — 2026-03-28
