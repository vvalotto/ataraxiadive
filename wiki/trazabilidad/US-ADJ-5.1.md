---
title: "US-ADJ-5.1 — Poda metodológica: clasificar artefactos ARTEFACTOS-WORKFLOW.md"
type: trazabilidad-us
sp: SP-ADJ-05
inc: SP-ADJ-05
bc: docs, metodología
estado: completado
fecha_cierre: "2026-04-04"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-05/PLAN-SP-ADJ-05.md
  - commit 5109eff
---

# US-ADJ-5.1 — Poda metodológica: clasificar artefactos

## Descripción

Crea `docs/contexto/ARTEFACTOS-WORKFLOW.md` — inventario clasificado de todos los artefactos del workflow por categoría de obligatoriedad. Prescrito por HITO-14 D-01 al cierre de SP3.

## Fuente

HITO-14 D-01 — "ejecutar poda metodológica al cierre de SP3"

## Contenido implementado

- `docs/contexto/ARTEFACTOS-WORKFLOW.md` (95 líneas) — tabla de tres columnas:
  - `obligatorio`: sin él el workflow no funciona
  - `opcional`: aporta valor pero omisible sin consecuencias sistémicas
  - `derivado`: se genera automáticamente, sin mantenimiento manual requerido
- Inventario por US, por Incremento y por SP

## Motivación

El overhead del ecosistema había convergido a ~18 min (HITO confirmada). La clasificación permite identificar qué artefactos pueden eliminarse o automatizarse para mantenerlo controlado.

## Estado

✅ Completado — 2026-04-04 (commit `5109eff`, PR #63)
