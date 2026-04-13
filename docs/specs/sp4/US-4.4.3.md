# US-4.4.3: Sincronización Background Sync + indicador de pendientes

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.4
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/sw.ts` (nuevo), `vite.config.ts`, `frontend/src/hooks/useSyncQueue.ts`, `frontend/src/components/juez/JuezLayout.tsx`, `frontend/src/stores/useConnectionStore.ts`

---

## Descripción

Como **juez**,
quiero **que los comandos guardados en mi celular se envíen solos al servidor cuando vuelva la señal**
para **no tener que hacer nada manual y saber en todo momento cuántas acciones están pendientes de confirmación**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Service Worker | `sw.ts` | Captura evento `sync` con tag `ataraxia-sync-queue`; procesa cola en orden FIFO |
| Hook | `useSyncQueue` | Orquesta sincronización manual (fallback); expone `pendingCount`, `syncError` |
| Store Zustand | `useConnectionStore` | Extendido: `pendingCount`, `syncError`, `isSyncing` |
| Componente | `SyncStatusBadge` | Indicador visible en `JuezLayout`: ⏳ N pendientes / ⚠ error / ✓ sincronizado |

### Lenguaje ubicuo relevante

- **Background Sync:** mecanismo del navegador que entrega un evento `sync` al Service Worker cuando hay conexión, aunque la app esté en background. Tag: `ataraxia-sync-queue`.
- **Fallback de sincronización:** si Background Sync no está disponible (Safari < 16), se usa el evento `window.online` + retry automático con `useSyncQueue`.
- **Sincronización completa:** la cola tiene cero registros con estado `pendiente`. Todos los comandos fueron confirmados por el servidor.
- **Comando en error:** comando que el servidor rechazó con 4xx. No se reintenta automáticamente — requiere que el juez lo descarte o lo reporte.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.4.3-01:** Al detectar reconexión (`online`), la sincronización arranca en ≤ 2 segundos, sea por Background Sync o por el fallback del evento `online`.
- **INV-4.4.3-02:** Los comandos se procesan en orden FIFO estricto (orden por `id` de `ComandoQueueRecord`). Un comando no se envía hasta que el anterior fue confirmado exitosamente.
- **INV-4.4.3-03:** Si un comando falla con 4xx (error de dominio), se marca `estado: 'error'` con `error_mensaje`. No se reintenta. El `SyncStatusBadge` muestra ⚠.
- **INV-4.4.3-04:** Si un comando falla con 5xx o error de red, se reintenta hasta 3 veces con backoff exponencial (1s, 2s, 4s). Tras 3 intentos fallidos → `estado: 'error'`.
- **INV-4.4.3-05:** `SyncStatusBadge` es visible en `JuezLayout` siempre que `pendingCount > 0` o `syncError !== null`.
- **INV-4.4.3-06:** Una vez que toda la cola se vacía exitosamente, la grilla se re-sincroniza con el servidor para confirmar el estado real.

### Operación principal: sincronización al reconectar

| | Descripción |
|---|---|
| **Precondición** | `pendingCount > 0` · dispositivo reconecta a la red |
| **Postcondición** | Cola vaciada · comandos enviados en orden · grilla actualizada desde servidor · `pendingCount = 0` |
| **Excepciones** | 4xx en algún comando → cola pausada en ese comando → `syncError` con detalle |

**Ejemplo concreto:**

```
Precondición:  3 comandos en cola (García: llamar, resultado, tarjeta blanca).
               Dispositivo reconecta.

Background Sync dispara evento 'sync' (tag: 'ataraxia-sync-queue'):
  1. Leer primer comando: { tipo: 'llamar', payload: {...} }
     → POST /competencia/{id}/llamar → 200 OK
     → DELETE de la cola
  2. Leer siguiente: { tipo: 'resultado', payload: {...} }
     → POST /competencia/{id}/registrar-resultado → 200 OK
     → DELETE
  3. Leer siguiente: { tipo: 'tarjeta', payload: {...} }
     → POST /competencia/{id}/asignar-tarjeta → 200 OK
     → DELETE

Cola vacía:
  → useSyncQueue.refetchGrilla()
  → grilla actualizada desde servidor (estado real confirmado)
  → SyncStatusBadge muestra "✓ Sincronizado"
  → badge desaparece a los 3 segundos

---

Error en un comando:
  Comando { tipo: 'tarjeta', tarjeta: 'Blanca' } → 409 Conflict
  → estado: 'error', error_mensaje: 'Performance no en estado ResultadoRegistrado'
  → cola pausada
  → SyncStatusBadge muestra "⚠ Error — 1 comando no pudo enviarse"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.4.3 — Sincronización automática al reconectar

  Background:
    Given el juez tiene 5 comandos encolados de la sesión offline
    And el SyncStatusBadge muestra "⏳ 5 pendientes"

  Scenario: sincronización exitosa vía Background Sync
    Given el navegador soporta Background Sync
    When el dispositivo reconecta a la red
    Then en ≤ 2 segundos el SW procesa los 5 comandos en orden FIFO
    And cada comando recibe respuesta 200 del servidor
    And la cola queda vacía
    And la grilla se actualiza con los datos confirmados del servidor
    And el SyncStatusBadge muestra "✓ Sincronizado" por 3 segundos y luego desaparece

  Scenario: sincronización exitosa vía fallback (sin Background Sync)
    Given el navegador NO soporta Background Sync
    When el dispositivo detecta el evento "online"
    Then useSyncQueue procesa los comandos en orden FIFO
    And el comportamiento es idéntico al escenario anterior

  Scenario: error 4xx en un comando de la cola
    Given el primer comando de la cola ya fue procesado por el servidor (conflicto de estado)
    When la sincronización intenta enviar ese comando
    Then recibe 409 del servidor
    And el comando pasa a estado "error" con el mensaje del servidor
    And la cola se pausa — los comandos siguientes NO se envían
    And SyncStatusBadge muestra "⚠ Error — 1 comando fallido"
    And el juez ve el detalle del error tocando el badge

  Scenario: error de red transitorio — retry con backoff
    Given el dispositivo tiene señal intermitente
    When un comando falla por timeout de red (no 4xx)
    Then el sistema reintenta hasta 3 veces con backoff 1s, 2s, 4s
    And si el tercer intento falla, el comando pasa a estado "error"
    And si algún intento tiene éxito, el comando se elimina y se continúa con el siguiente

  Scenario: indicador de pendientes visible durante todo el flujo
    Given el juez tiene 3 comandos pendientes
    And está en cualquier pantalla de JuezLayout
    Then el SyncStatusBadge es visible en el header con "⏳ 3"
    When el dispositivo reconecta y sincroniza exitosamente
    Then el badge muestra "✓" brevemente y luego desaparece
```

---

## Impacto arquitectónico

- [x] Sí → migración de `generateSW` a `injectManifest` en `vite-plugin-pwa` para soportar SW personalizado

**Cambio en `vite.config.ts`:**

```typescript
// Antes (US-4.2.1):
VitePWA({ registerType: 'autoUpdate', workbox: { runtimeCaching: [...] } })

// Después (US-4.4.3):
VitePWA({
  registerType: 'autoUpdate',
  strategies: 'injectManifest',
  srcDir: 'src',
  filename: 'sw.ts',
  // El manifest permanece igual
})
```

El SW personalizado (`src/sw.ts`) incluye:
- `precacheAndRoute(self.__WB_MANIFEST)` — assets pre-cacheados (migrado de generateSW)
- `registerRoute(...)` — NetworkFirst para `/competencia/...` y `/torneos/...`
- `addEventListener('sync', ...)` — procesa cola Background Sync

**Capa(s) afectadas:**
- [x] Infrastructure / Frontend — `frontend/src/sw.ts` (nuevo — SW personalizado)
- [x] Infrastructure / Frontend — `vite.config.ts` (strategies: injectManifest)
- [x] Infrastructure / Frontend — `frontend/src/hooks/useSyncQueue.ts` (lógica de sync + fallback)
- [x] Infrastructure / Frontend — `useConnectionStore.ts` (agregar `isSyncing`, `syncError`)
- [x] Infrastructure / Frontend — `JuezLayout.tsx` (mostrar `SyncStatusBadge`)
- [x] Infrastructure / Frontend — nuevo componente `SyncStatusBadge.tsx`

---

## Referencias

- Prerequisitos: US-4.4.1 (schema DB) · US-4.4.2 (cola de comandos)
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §Offline — estrategia de sincronización`
- Wireframes: `docs/design/ux/wireframes-juez.md §S-01, S-02` (badge conexión)
- ADR-015 (US-4.4.1): Dexie.js como motor de IndexedDB

---

## Notas de implementación

### `src/sw.ts` — estructura

```typescript
import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'

declare const self: ServiceWorkerGlobalScope

// 1. Pre-cache de assets
precacheAndRoute(self.__WB_MANIFEST)

// 2. Runtime cache: API (NetworkFirst, timeout 3s)
registerRoute(
  ({ url }) => url.pathname.startsWith('/competencia') || url.pathname.startsWith('/torneos'),
  new NetworkFirst({ cacheName: 'api-cache', networkTimeoutSeconds: 3 }),
)

// 3. Background Sync
self.addEventListener('sync', (event: SyncEvent) => {
  if (event.tag === 'ataraxia-sync-queue') {
    event.waitUntil(procesarCola())
  }
})

async function procesarCola() {
  // Abrir IndexedDB (db singleton de Dexie no disponible en SW — usar idb-keyval o IDBWrapper)
  // Leer comandos en orden FIFO, enviar uno a uno, eliminar los exitosos
  // Manejar errores por tipo (4xx → error, 5xx → retry)
}
```

> **Nota:** Dexie no funciona directamente en el SW context. Usar la API IDB nativa o
> `idb-keyval` para acceder a `comando_queue` desde el SW. Alternativamente, registrar
> Background Sync desde la app (`navigator.serviceWorker.ready.then(sw => sw.sync.register(...))`)
> y manejar toda la lógica de sync en `useSyncQueue` (estrategia más simple y portable).

### Estrategia recomendada: sync en la app (no en el SW)

Para mantener la lógica en TypeScript y evitar la duplicación de acceso a IndexedDB:

```typescript
// useSyncQueue.ts
export function useSyncQueue() {
  const isOnline = useConnectionStore(s => s.isOnline)
  const setPendingCount = useConnectionStore(s => s.setPendingCount)

  useEffect(() => {
    if (!isOnline) return
    sincronizarCola()
  }, [isOnline])

  async function sincronizarCola() {
    // Leer comando_queue donde estado = 'pendiente', orden por id ASC
    // Procesar FIFO, manejar errores, actualizar pendingCount
  }
}
```

El Background Sync del SW actúa como trigger de respaldo cuando la app está en segundo plano.

### Backoff exponencial

```typescript
async function conRetry(fn: () => Promise<void>, maxIntentos = 3): Promise<void> {
  for (let i = 0; i < maxIntentos; i++) {
    try {
      await fn()
      return
    } catch (e) {
      if (isClientError(e)) throw e  // 4xx: no reintentar
      if (i < maxIntentos - 1) await sleep(1000 * Math.pow(2, i))
    }
  }
  throw new Error('Max reintentos alcanzados')
}
```

### `SyncStatusBadge` — estados visuales

| Estado | Icono | Color | Texto |
|--------|-------|-------|-------|
| `pendingCount > 0`, sin error | ⏳ | amarillo | "N pendientes" |
| `isSyncing = true` | ↻ | accent | "Sincronizando…" |
| `syncError !== null` | ⚠ | rojo | "Error — toca para ver" |
| recién sincronizado | ✓ | verde | "Sincronizado" (3s, luego oculto) |
| sin pendientes, sin error | — | — | oculto |

---

*Redactado: 2026-04-13 — INC-4.4 Offline-first*
