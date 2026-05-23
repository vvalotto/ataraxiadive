---
title: "US-ADJ-6.5 — Corregir violaciones de capa en GrillaPage (frontend)"
type: trazabilidad-us
sp: SP-ADJ-06
inc: SP-ADJ-06
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §18
us_id: US-ADJ-6.5
tests_count: null
---

# US-ADJ-6.5 — Corregir violaciones de capa en GrillaPage

## Descripción

Corrige las violaciones de arquitectura de capas en `GrillaPage`: reemplaza imports directos a módulos de API por el uso correcto de hooks de estado.

## Capas afectadas

`frontend/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| Arq. capas | `GrillaPage` importaba directamente de `api/competencia.ts` — reemplazado por `useCompetenciaStore` y hooks dedicados |

## Motivación

Los componentes de UI no deben conocer la capa de API. El acceso a datos debe ir siempre a través de hooks o stores (D-03).

## Estado

✅ Completado — 2026-04-18
