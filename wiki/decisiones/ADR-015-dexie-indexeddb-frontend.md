---
title: "ADR-015: Dexie.js como capa de acceso a IndexedDB"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-015-dexie-indexeddb-frontend.md
estado: Aceptada (implementada en INC-4.4)
fecha: 2026-04-13
bcs_afectados: []
---

# ADR-015: Dexie.js como capa de acceso a IndexedDB

## Decisión

Dexie.js como wrapper de IndexedDB en el frontend, en lugar de la API nativa.

## Por qué

La API nativa de IndexedDB es verbosa. Dexie provee API promise-based tipada, índices compuestos declarativos y manejo simple de versionado de schema.

## Consecuencias vigentes

- DB singleton: `AtaraxiaDiveDB`.
- Tablas creadas en v1: `grilla_cache` y `comando_queue`.
- `usePrecarga` accede a `grilla_cache`; `useComandoQueue` accede a `comando_queue`.
- Nueva dependencia en el frontend — requiere mantenimiento en actualizaciones de seguridad.

## ADRs relacionados

- [[ADR-003-offline-first-pwa]] — el contexto offline-first que requirió IndexedDB
