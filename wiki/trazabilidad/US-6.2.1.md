---
title: "US-6.2.1 — Torneos ordenados por fecha desc en lista organizador"
type: trazabilidad-us
sp: SP6
inc: INC-6.2
bc: frontend, torneo
estado: completado
fecha_cierre: "2026-05-07"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §30
---

# US-6.2.1 — Torneos ordenados por fecha desc en lista organizador

## Descripción

Mejora la lista de torneos del organizador: ordenados por fecha descendente y con la fecha visible en cada item de la lista.

## Contenido implementado

- `TorneoList.tsx` — ordenación por fecha desc + columna/campo fecha visible

DesignReviewer cierre INC-6.2: **0 CRITICAL · 256 WARNING** (sin cambios Python).

## Estado

✅ Completado — 2026-05-07 · PR #148
