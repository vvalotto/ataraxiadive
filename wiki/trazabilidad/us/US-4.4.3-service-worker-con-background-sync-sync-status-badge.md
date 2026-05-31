---
title: "US-4.4.3 — Service Worker con Background Sync + SyncStatusBadge"
type: trazabilidad-us
sp: SP4
inc: INC-4.4
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §15
us_id: US-4.4.3
tests_count: null
rf: []
---

# US-4.4.3 — Service Worker con Background Sync + SyncStatusBadge

## Descripción

Migra el Service Worker a `injectManifest` para control total y agrega Background Sync: cuando el dispositivo recupera conexión, la cola de comandos se procesa automáticamente en background.

## Decisiones cubiertas

PLAN-SP4 §INC-4.4

## Contenido implementado

- Migración SW a `injectManifest` (Workbox) — control explícito del SW
- `sw.ts`: precache + NetworkFirst + Background Sync API
- Hook `useSyncQueue`: FIFO, backoff exponencial, fallback a evento `online`
- `SyncStatusBadge` en `JuezLayout` — indica estado de sincronización al juez

DesignReviewer post-INC-4.4: **0 CRITICAL · 158 WARNING**.
Fix robustez offline: `fetchWithTimeout` con `AbortController` (timeout 5s) mergeado en `dfb6ec3`.

## Tests

Frontend (build + lint) · UAT INC-4.4 iPhone (Background Sync). UAT SP4 — 2026-04-18.

## Estado

✅ Completado — 2026-04-18 (PR #77)
