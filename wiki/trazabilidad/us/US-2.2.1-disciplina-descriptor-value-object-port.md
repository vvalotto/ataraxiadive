---
title: "US-2.2.1 — DisciplinaDescriptor value object + port"
type: trazabilidad-us
sp: SP2
inc: INC-2.2
bc: competencia, shared
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.2.1
tests_count: null
rf:
  - RF-EJ-08-distancias-con-decimales
software_items:
  - src/competencia/domain/value_objects/disciplina_descriptor.py
test_units:
  - tests/features/US-2.2.1-disciplina-descriptor.feature
  - tests/integration/competencia/test_disciplina_descriptor_integration.py
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/competencia-aggregate
---

# US-2.2.1 — DisciplinaDescriptor value object + port

## Descripción

Introduce el value object `DisciplinaDescriptor` que encapsula las reglas de cada disciplina (unidad de medida, orden de grilla, etc.) y su puerto abstracto correspondiente.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-08-distancias-con-decimales]] | Distancia con decimales (metros) / tiempo en segundos según disciplina |

## Contenido implementado

- VO `DisciplinaDescriptor` con propiedades: `unidad_medida`, `orden_ascendente`, `es_disciplina_tiempo`
- Port abstracto para inyectar el descriptor en handlers
- Variantes: STA/tiempo, DNF/distancia

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.2.

## Estado

✅ Completado — 2026-03-28
