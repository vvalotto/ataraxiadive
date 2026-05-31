---
title: "US-2.2.2 — API disciplina-aware + validación de unidades"
type: trazabilidad-us
sp: SP2
inc: INC-2.2
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.2.2
tests_count: null
rf:
  - RF-EJ-08-distancias-con-decimales
software_items:
  - src/competencia/api/router.py
test_units:
  - tests/features/US-2.2.2-api-disciplina-aware.feature
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/router-competencia
---

# US-2.2.2 — API disciplina-aware + validación de unidades

## Descripción

Hace que la API de competencia comprenda la disciplina activa: valida que las unidades de medida sean correctas (metros vs. segundos) y aplica el ordenamiento correspondiente en la grilla.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-08-distancias-con-decimales]] | Distancia con decimales (metros) / tiempo según disciplina |

## Contenido implementado

- API endpoints validando unidades según `DisciplinaDescriptor`
- Ordenamiento de grilla disciplina-aware (usa `orden_ascendente` del VO)
- Política P-06: validación de formato de marca según disciplina

## Invariantes aplicadas

- P-06: el RP debe estar en la unidad correcta para la disciplina

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.2.

## Estado

✅ Completado — 2026-03-28
