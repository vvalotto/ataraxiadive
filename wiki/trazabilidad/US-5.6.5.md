---
title: "US-5.6.5 — UI ResultadosPage: tabla de resultados por disciplina"
type: trazabilidad-us
sp: SP5
inc: INC-5.6
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §26
us_id: US-5.6.5
tests_count: null
---

# US-5.6.5 — UI ResultadosPage: tabla de resultados por disciplina

## Descripción

Página de resultados para el organizador (`/organizador/resultados`). Permite seleccionar torneo y disciplina, y muestra una tabla por OT con los datos de cada atleta: género, categoría, AP, RP, tarjeta y puntos.

## Contenido implementado

- `ResultadosPage` (`/organizador/resultados`) — selector torneo/disciplina + tabla de resultados
- Columnas: OT, nombre, género, categoría, AP, RP, tarjeta, puntos

## Estado

✅ Completado — 2026-04-28 · PR #127
