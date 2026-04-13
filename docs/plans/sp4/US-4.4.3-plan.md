# Plan de Implementación — US-4.4.3

**US:** US-4.4.3 — Sincronización automática al reconectar  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13  
**Branch:** `feature/US-4.4.3-sync-reconexion`

---

## Objetivo

Enviar automáticamente la cola local al recuperar conexión y mostrar estado de sincronización en UI.

## Decisiones

1. Sincronización principal en la app (`useSyncQueue`) para centralizar lógica y acceso a IndexedDB.
2. Service Worker como trigger de respaldo (`SYNC_QUEUE_REQUEST`) usando `injectManifest`.
3. Procesamiento FIFO estricto por `id`.
4. Manejo de errores:
   - 4xx -> marcar `error` y pausar.
   - red/5xx -> retry 3 intentos con backoff 1s/2s/4s.
5. Badge global en `JuezLayout` para pendientes, sincronizando, error y éxito.

## Validación prevista

- `npm run lint`
- `npm run build`
- Smoke manual reconexión:
  - cola pendiente -> sync automática.
  - error 4xx -> badge error.
  - sync completa -> badge ✓ 3s.

