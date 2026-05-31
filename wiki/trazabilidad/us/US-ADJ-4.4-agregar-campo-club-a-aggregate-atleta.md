---
title: "US-ADJ-4.4 — Agregar campo club a aggregate Atleta"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: registro
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.4
tests_count: null
rf:
  - RF-IN-10-club-atleta-obligatorio
software_items:
  - src/registro/domain/aggregates/atleta.py
test_units: null
origen_tipo: rf
componentes_wiki:
  - arquitectura/registro/atleta
---

# US-ADJ-4.4 — Agregar campo club a aggregate Atleta

## Descripción

Agrega el campo `club` al aggregate `Atleta` del BC Registro. El club del atleta debe ser visible en grillas y reportes según el reglamento de competencia.

## RFs corregidos

| RF | Corrección |
|----|-----------|
| RF-IN-10 | Club obligatorio del atleta y visible en grillas/reportes |

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-05 | `Atleta` sin campo `club` | MEDIO |

## Contenido implementado

- Campo `club: str` en aggregate `Atleta`
- Migración SQLite de la tabla `atletas`
- Exposición en API y en grilla de competencia

## Tests

Tests de creación y consulta de `Atleta` actualizados para incluir el campo `club`.

## Estado

✅ Completado — 2026-04-03
