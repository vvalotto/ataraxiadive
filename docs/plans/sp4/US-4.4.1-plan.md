# Plan de Implementación — US-4.4.1

**US:** US-4.4.1 — Pre-carga de disciplina en IndexedDB  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13  
**Branch:** `feature/US-4.4.1-precarga-offline`

---

## Objetivo

Implementar precarga offline para la pantalla de grilla del juez:

- al abrir grilla online, refrescar datos desde API y persistir cache local;
- al abrir grilla offline, usar cache existente;
- si no existe cache y no hay red, mostrar error explícito.

## Decisiones de implementación

1. **IndexedDB con Dexie**
- Crear DB singleton `AtaraxiaDiveDB`.
- Definir tablas `grilla_cache` y `comando_queue` (esta última ya preparada para US-4.4.2).

2. **Hook dedicado `usePrecarga`**
- Encapsular fetch online + fallback a cache.
- Evitar que `GrillaPage` mezcle lógica de IO remota/local.

3. **`GrillaPage` como consumidor**
- Reemplazar fetch directo de grilla por `usePrecarga`.
- Mantener `performance actual` solo cuando hay red.
- Agregar mensajes de estado para:
  - offline con cache;
  - offline sin cache;
  - cache expirado (>24h).

## Cambios previstos

- Crear `frontend/src/db/schema.ts`
- Crear `frontend/src/db/index.ts`
- Crear `frontend/src/db/queries.ts`
- Crear `frontend/src/hooks/usePrecarga.ts`
- Modificar `frontend/src/pages/juez/GrillaPage.tsx`
- Modificar `frontend/package.json`

## Validación prevista

- `npm run lint`
- `npm run build`
- Smoke manual:
  - online carga y persiste cache;
  - offline con cache muestra grilla;
  - offline sin cache muestra error.

