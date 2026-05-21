---
title: "US-ADJ-3.8 — Desacoplar ACL resultados de BC Competencia"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: resultados
estado: completado
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
---

# US-ADJ-3.8 — Desacoplar ACL resultados de BC Competencia

## Descripción

Introduce una capa ACL (Anti-Corruption Layer) en `resultados/infrastructure/` para aislar el BC Resultados de las estructuras internas del BC Competencia.

## Capas afectadas

`resultados/infrastructure/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| HITO-14 | ACL explícita en `resultados/infrastructure/` — traduce estructuras de Competencia al lenguaje de Resultados |
| D-06 | Problema de acoplamiento cross-BC documentado y resuelto mediante ACL |

## Motivación

El BC Resultados necesitaba datos del BC Competencia (performances, disciplinas). Sin ACL, importaba directamente de la infraestructura de Competencia — acoplamiento prohibido por el Context Map.

## Tests

BDD waiver — refactoring arquitectónico. Tests existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
