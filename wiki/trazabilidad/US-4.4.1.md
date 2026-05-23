---
title: "US-4.4.1 — Dexie.js: cache local de grilla + expiración 24h"
type: trazabilidad-us
sp: SP4
inc: INC-4.4
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §15
us_id: US-4.4.1
tests_count: null
---

# US-4.4.1 — Dexie.js: cache local de grilla + expiración 24h

## Descripción

Introduce la base de datos local IndexedDB (via Dexie.js) para cachear la grilla de salida y permitir operación sin red al juez en el campo.

## Decisiones cubiertas

PLAN-SP4 §INC-4.4 · ADR-015 (Dexie.js)

## Contenido implementado

- Instalar Dexie.js — wrapper IndexedDB tipado
- `AtaraxiaDiveDB` schema: tablas `grilla_cache` y `comando_queue`
- Hook `usePrecarga` — descarga y almacena la grilla al conectarse
- `GrillaPage` con lectura offline desde IndexedDB
- Expiración automática de cache a las 24h
- Label de antigüedad visible al juez ("Actualizado hace X min")

## Tests

Frontend (build + lint) · UAT INC-4.4 iPhone (BDD waiver — frontend offline-first). UAT SP4 — 2026-04-18.

## Estado

✅ Completado — 2026-04-18 (PR #77)
