# Contexto de Implementación — US-4.4.2

**US:** US-4.4.2 — Operación offline del flujo de 6 pasos  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13

---

## Objetivo validado

Permitir que el juez continúe el flujo de performance cuando no hay red:

- encolando comandos de escritura en IndexedDB;
- manteniendo la UI del wizard operativa;
- reflejando estado optimista en grilla con pendientes de sincronización.

## Alcance técnico confirmado

- `frontend/src/hooks/useComandoQueue.ts` (nuevo).
- `frontend/src/hooks/usePerformanceFlow.ts` (mutaciones online/offline).
- `frontend/src/pages/juez/GrillaPage.tsx` (proyección optimista + badge pendientes).
- `frontend/src/stores/useConnectionStore.ts` (`pendingCount`).
- `frontend/src/db/queries.ts` (cola y utilidades optimistas).

