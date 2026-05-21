---
title: "US-ADJ-3.7 — Proyección competencias_por_torneo O(n)→O(1)"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: competencia
estado: completado
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
---

# US-ADJ-3.7 — Proyección competencias_por_torneo O(n)→O(1)

## Descripción

Materializa la proyección `competencias_por_torneo` en infraestructura, eliminando el scan lineal sobre todos los eventos del Event Store para encontrar competencias de un torneo.

## Capas afectadas

`competencia/infrastructure/`, `competencia/application/queries/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| HITO-15 | Proyección `competencias_por_torneo` materializada en tabla SQL dedicada — acceso O(1) en lugar de O(n) scan del Event Store |

## Motivación

El HITO-15 identificó que con muchas competencias el rendimiento degradaba. La proyección materializada resuelve el problema sin cambiar la interfaz de la query.

## Tests

BDD waiver — optimización de infraestructura. Tests de queries existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
