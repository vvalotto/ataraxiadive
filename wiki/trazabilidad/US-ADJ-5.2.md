---
title: "US-ADJ-5.2 — Consistencia documental residual: README, docker-compose, estrategia"
type: trazabilidad-us
sp: SP-ADJ-05
inc: SP-ADJ-05
bc: docs
estado: cerrada
fecha_cierre: "2026-04-04"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-05/PLAN-SP-ADJ-05.md
  - commit 415fa10
us_id: US-ADJ-5.2
tests_count: null
rf: []
---

# US-ADJ-5.2 — Consistencia documental residual

## Descripción

Corrige documentos operativos que aún tenían referencias pre-ADR (PostgreSQL, stack anterior) y marca como históricos los documentos fundacionales que no pueden actualizarse sin perder trazabilidad del experimento.

## Fuente

HITO-14 D-02 + D-03

## Contenido implementado

| Documento | Acción |
|-----------|--------|
| `README.md` | Actualizado — SP3 marcado como cerrado |
| `docker-compose.yml` | Marcado histórico (PostgreSQL → SQLite no aplica para dev local) |
| `docs/dominio/04-estrategia_desarrollo.md` | Marcado histórico con nota de vigencia |

## Estado

✅ Completado — 2026-04-04 (commit `415fa10`, PR #63)
