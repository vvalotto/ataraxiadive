# US-4.4.2: Operación offline — el flujo de los 6 pasos funciona sin conexión

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.4
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/db/`, `frontend/src/hooks/useComandoQueue.ts`, `frontend/src/pages/juez/PerformanceFlowPage.tsx`, `frontend/src/pages/juez/GrillaPage.tsx`

---

## Descripción

Como **juez**,
quiero **registrar performances normalmente aunque no tenga señal**
para **que el resultado de cada atleta quede guardado en mi celular y se envíe solo cuando vuelva la conexión, sin interrumpir el torneo**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Cola local | `ComandoQueueRecord` (Dexie) | Fila de comandos pendientes — FIFO, persistidos en IndexedDB |
| Hook | `useComandoQueue` | Intercepta comandos de escritura: envía directo si online, encola si offline |
| Estado optimista | `GrillaLocal` | Proyección local de la grilla derivada de los comandos encolados |
| Store Zustand | `useConnectionStore` | Extiende con `pendingCount: number` |

### Lenguaje ubicuo relevante

- **Comando encolado:** acción del juez (llamar, resultado, tarjeta, DNS) registrada localmente cuando no hay red. Se identifica por tipo + competencia_id + payload + timestamp.
- **Estado optimista:** la grilla refleja el resultado esperado de los comandos encolados sin esperar confirmación del servidor. Si la sincronización falla, el estado se reconcilia.
- **Pendiente de sync:** performance cuyo comando fue encolado pero aún no confirmado por el servidor. La fila en la grilla muestra un badge de reloj.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.4.2-01:** Cuando `isOnline = false`, todos los comandos de escritura (`llamar`, `registrarResultado`, `asignarTarjeta`, `registrarDns`, `resolverRevision`) se encolan en IndexedDB en lugar de enviarse al servidor.
- **INV-4.4.2-02:** La cola es estrictamente FIFO — los comandos se sincronizan en el mismo orden en que fueron registrados (orden por `id` autoincremental).
- **INV-4.4.2-03:** La grilla local refleja el estado derivado de los comandos encolados (estado optimista): una performance con `llamar` encolado aparece como `Llamada`; con `asignarTarjeta` encolado aparece como `TarjetaAsignada (pendiente sync)`.
- **INV-4.4.2-04:** Un comando en la cola no puede editarse ni eliminarse manualmente por el juez. Solo el sistema lo elimina al sincronizar exitosamente (US-4.4.3).
- **INV-4.4.2-05:** Si hay comandos encolados al reconectar, la sincronización en US-4.4.3 tiene prioridad antes de permitir nuevos comandos online.

### Operación principal: ejecutar paso del flujo offline

| | Descripción |
|---|---|
| **Precondición** | `isOnline = false` · juez en cualquier paso del wizard `PerformanceFlowPage` |
| **Postcondición** | Comando persistido en `comando_queue` · UI avanza al siguiente paso · grilla local actualizada (estado optimista) |
| **Excepciones** | Fallo de escritura en IndexedDB → mostrar error "No se pudo guardar localmente — memoria del dispositivo llena" |

**Ejemplo concreto:**

```
Precondición:  Dispositivo offline. García, Ana — estado: Pendiente en grilla local.
Paso 1:        Juez toca "LLAMAR ATLETA"
               → useComandoQueue.encolar({ tipo: 'llamar', competencia_id, payload: {...} })
               → IndexedDB: INSERT comando_queue { tipo: 'llamar', estado: 'pendiente', creado_at: now }
               → grilla local: García → estado 'Llamada (pendiente sync)'
               → UI avanza a Paso 2
Paso 5:        Juez ingresa RP=72m, toca "SIGUIENTE"
               → encolar { tipo: 'resultado', valor_rp: '72', unidad: 'm' }
               → grilla local: García → 'ResultadoRegistrado (pendiente sync)'
Paso 6:        Juez asigna Tarjeta Blanca
               → encolar { tipo: 'tarjeta', tarjeta: 'Blanca' }
               → grilla local: García → 'TarjetaAsignada BLANCA (pendiente sync)' con badge ⏳
Postcondición: 3 comandos en cola. García visible en grilla con badge ⏳ x3.
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.4.2 — Flujo de 6 pasos funcionando offline

  Background:
    Given el juez está autenticado
    And la disciplina DNF está pre-cargada en IndexedDB (US-4.4.1)
    And el dispositivo está offline

  Scenario: flujo completo de performance en modo offline
    Given García, Ana está en estado Pendiente en la grilla
    When el juez ejecuta los 6 pasos del flujo y asigna tarjeta blanca
    Then hay 3 comandos en IndexedDB con estado "pendiente" (llamar, resultado, tarjeta)
    And García aparece en la grilla con estado "BLANCA" y badge "⏳ pendiente sync"
    And la UI no muestra ningún error de conexión durante el flujo

  Scenario: DNS offline
    Given Rodríguez, Juan está en estado Pendiente
    And el dispositivo está offline
    When el juez toca "DNS — No se presenta" en Paso 1
    Then hay 1 comando encolado { tipo: 'dns' }
    And Rodríguez aparece como DNS en la grilla con badge "⏳ pendiente sync"

  Scenario: múltiples performances offline
    Given el dispositivo está offline
    When el juez procesa 5 performances completas (registro + tarjeta)
    Then hay 15 comandos en la cola (3 por performance: llamar, resultado, tarjeta)
    And los 5 atletas aparecen en la grilla con sus estados optimistas y badge ⏳

  Scenario: grilla usa datos en cache cuando no hay red
    Given el dispositivo está offline
    And GrillaPage ya tiene datos en IndexedDB de la última pre-carga
    When el juez navega a GrillaPage
    Then se muestra la grilla desde IndexedDB
    And las performances con comandos encolados muestran sus estados optimistas

  Scenario: fallo de escritura en IndexedDB
    Given el almacenamiento del dispositivo está lleno
    And el dispositivo está offline
    When el juez intenta ejecutar el Paso 1
    Then aparece el mensaje "No se pudo guardar localmente — dispositivo sin espacio"
    And el juez permanece en el mismo paso sin avanzar
```

---

## Impacto arquitectónico

- [x] No requiere ADR nuevo — usa schema definido en US-4.4.1 (`ComandoQueueRecord`)

**Capa(s) afectadas:**
- [x] Infrastructure / Frontend — `frontend/src/hooks/useComandoQueue.ts` (nuevo hook)
- [x] Infrastructure / Frontend — `PerformanceFlowPage.tsx` (sustituye llamadas directas por `useComandoQueue`)
- [x] Infrastructure / Frontend — `GrillaPage.tsx` (proyección optimista + badge ⏳)
- [x] Infrastructure / Frontend — `useConnectionStore.ts` (agregar `pendingCount: number`)

---

## Referencias

- Prerequisito: US-4.4.1 (schema IndexedDB + `db` singleton)
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.4`
- Wireframes: `docs/design/ux/wireframes-juez.md §S-02` (estados de grilla-row)
- Sincronización: US-4.4.3 (procesa la cola una vez que vuelve la red)

---

## Notas de implementación

### `useComandoQueue` — interfaz

```typescript
// hooks/useComandoQueue.ts
export function useComandoQueue() {
  const isOnline = useConnectionStore(s => s.isOnline)

  async function ejecutar<T>(
    tipo: ComandoQueueRecord['tipo'],
    competenciaId: string,
    payload: object,
    apiFn: () => Promise<T>,
  ): Promise<{ encolado: boolean }> {
    if (isOnline) {
      await apiFn()
      return { encolado: false }
    }
    await db.comando_queue.add({
      tipo, competencia_id: competenciaId,
      payload: JSON.stringify(payload),
      estado: 'pendiente', creado_at: Date.now(), intentos: 0,
    })
    return { encolado: true }
  }

  return { ejecutar }
}
```

### Integración en `PerformanceFlowPage`

Reemplazar cada llamada directa a `llamarAtleta()`, `registrarResultado()`, etc. por:

```typescript
const { ejecutar } = useComandoQueue()

// Antes (US-4.3.2):
await llamarAtleta({ competenciaId, ... })

// Después (US-4.4.2):
const { encolado } = await ejecutar('llamar', competenciaId, payload, () =>
  llamarAtleta({ competenciaId, ... })
)
if (encolado) {
  actualizarGrillaLocal(participanteId, 'Llamada')
}
```

### Estado optimista en `GrillaPage`

La grilla combina:
1. Datos del servidor (o caché IndexedDB)
2. Comandos en cola: proyectar estado esperado por `participante_id`

Función `proyectarEstado(grillaCache, cola)`:
- Recorre `cola` en orden FIFO
- Para cada `participante_id`, aplica la transición de estado correspondiente al último comando encolado

### Badge ⏳ — estados derivados de la cola

| Último comando encolado | Estado optimista en grilla |
|------------------------|---------------------------|
| `llamar` | `Llamada ⏳` |
| `resultado` | `ResultadoRegistrado ⏳` |
| `tarjeta` | `TarjetaAsignada ⏳` |
| `dns` | `DNS ⏳` |

---

*Redactado: 2026-04-13 — INC-4.4 Offline-first*
