---
title: "US-4.6.4 — ExportarResultados: descarga CSV/JSON del torneo"
type: trazabilidad-us
sp: SP4
inc: INC-4.6
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §17
us_id: US-4.6.4
tests_count: null
---

# US-4.6.4 — ExportarResultados: descarga CSV/JSON del torneo

## Descripción

Expone un endpoint consolidado de exportación que permite descargar los resultados completos de un torneo en formato CSV o JSON, incluyendo datos de integridad (hash).

## Decisiones cubiertas

PLAN-SP4 §INC-4.6 · [[US-4.6.2]] · [[US-4.6.3]]

## Contenido implementado

- Query `ExportarResultados` — consolida datos de Torneo, Registro, Competencia y Resultados
- `GET /resultados/{torneo_id}/export` — parámetro `format=csv|json`
- `Content-Disposition: attachment` — descarga directa desde el browser
- ACLs cross-BC: torneo, atletas, estado e integridad (hash)

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/resultados/application (ExportarResultados) | ✅ |
| integration/resultados | ✅ |
| UAT INC-4.6 | ✅ |

DesignReviewer post-INC-4.6: **0 CRITICAL · ~158 WARNING**.

## Estado

✅ Completado — 2026-04-18
