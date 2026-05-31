---
title: "US-2.1.3 — AjustarGrilla"
type: trazabilidad-us
sp: SP2
inc: INC-2.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.1.3
tests_count: null
rf:
  - RF-PR-07-ajuste-manual-grilla
software_items:
  - src/competencia/application/commands/ajustar_grilla.py
test_units:
  - tests/features/US-2.1.3-ajustar-grilla.feature
  - tests/integration/competencia/test_ajustar_grilla_integration.py
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/command-handlers
---

# US-2.1.3 — AjustarGrilla

## Descripción

Permite al organizador modificar manualmente el orden de la grilla generada antes de confirmarla, intercambiando posiciones de atletas.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PR-07-ajuste-manual-grilla]] | Organizador puede ajustar manualmente el orden de la grilla |

## Comando principal

`AjustarGrilla`

## Invariantes aplicadas

- INV-C-02 (parcial): el ajuste solo es válido mientras la grilla no esté confirmada

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.1.

## Estado

✅ Completado — 2026-03-28
