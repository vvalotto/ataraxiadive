---
title: "US-6.2.3 — ResultadosPage: quitar PTS FAAS + andarivel como número"
type: trazabilidad-us
sp: SP6
inc: INC-6.2
bc: frontend, resultados
estado: cerrada
fecha_cierre: "2026-05-07"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §30
us_id: US-6.2.3
tests_count: null
rf: []
componentes_wiki: []
---

# US-6.2.3 — ResultadosPage: quitar PTS FAAS + andarivel como número

## Descripción

Ajustes en la tabla de resultados del organizador: se quita la columna de puntos FAAS (no relevante para todos los torneos), el andarivel se muestra como número (no como OT-texto), y se renombra "AP" por "Anuncios".

## Contenido implementado

- `ResultadosPage.tsx` — columna PTS FAAS eliminada; andarivel como número; "AP" → "Anuncios"

## Estado

✅ Completado — 2026-05-07 · PR #150
