# Contexto de Implementación — US-4.4.3

**US:** US-4.4.3 — Sincronización automática al reconectar  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13

---

## Objetivo validado

Sincronizar automáticamente la cola local (`comando_queue`) al volver la red,
en orden FIFO y con feedback visible para el juez.

## Alcance técnico confirmado

- `frontend/src/hooks/useSyncQueue.ts`: sincronización + retry/backoff + errores.
- `frontend/src/stores/useConnectionStore.ts`: estado de sync (`isSyncing`, `syncError`, `syncOkVisible`, conteos).
- `frontend/src/components/juez/SyncStatusBadge.tsx`: indicador global.
- `frontend/src/components/juez/JuezLayout.tsx`: integración del badge.
- `frontend/src/sw.ts` + `vite.config.ts`: PWA `injectManifest` y trigger `sync`.
- `frontend/src/db/queries.ts`: operaciones de cola para sync.

