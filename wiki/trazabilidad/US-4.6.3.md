---
title: "US-4.6.3 — UI auditoría para organizador: timeline + hash"
type: trazabilidad-us
sp: SP4
inc: INC-4.6
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §17
us_id: US-4.6.3
tests_count: null
---

# US-4.6.3 — UI auditoría para organizador: timeline + hash

## Descripción

Implementa las pantallas de auditoría en el portal del organizador: lista de atletas de una competencia, timeline de eventos por performance y visualización del hash SHA-256 de integridad.

## Decisiones cubiertas

PLAN-SP4 §INC-4.6 · [[US-4.6.1]] · [[US-4.6.2]]

## Contenido implementado

- Rutas de auditoría en el portal organizador
- Lista de atletas por competencia con estado de cada performance
- Timeline puntual por performance (usa `ObtenerAuditLog`)
- Visualización y copia del `hash_sha256` cuando la disciplina está finalizada

## Tests

Frontend (build + lint) · UAT INC-4.6 iPad organizador. UAT SP4 — 2026-04-18.

## Estado

✅ Completado — 2026-04-18
