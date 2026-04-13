# US-4.4.1: Pre-carga de disciplina en IndexedDB — base de almacenamiento offline

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.4
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/db/`, `frontend/src/hooks/`, `frontend/src/pages/juez/GrillaPage.tsx`, `vite.config.ts`

---

## Descripción

Como **juez**,
quiero **que la grilla y los datos de mi disciplina se guarden automáticamente en el dispositivo al abrirla**
para **poder consultarlos aunque pierda la señal antes de completar todas las performances**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Read Model (caché) | `GrillaCache` | Snapshot de grilla + estado de competencia en IndexedDB |
| Store Zustand | `useConnectionStore` | Estado de conexión: `isOnline`, `pendingCount` |
| Hook | `usePrecarga` | Dispara pre-carga al montar GrillaPage; usa caché si offline |
| DB | `AtaraxiaDiveDB` (Dexie) | Instancia singleton del cliente IndexedDB |

### Lenguaje ubicuo relevante

- **Pre-carga:** operación que descarga y persiste en el dispositivo los datos de la disciplina activa. Se ejecuta al abrir la grilla, con o sin conexión (actualiza si hay red; usa lo guardado si no).
- **Caché de grilla:** snapshot de `GrillaAtletaDto[]` + `EstadoCompetenciaDto` almacenado en IndexedDB con timestamp de última actualización.
- **Expiración:** los datos cacheados se consideran válidos por 24 horas. Si el cache expiró y no hay red, se muestra aviso pero se siguen usando los datos.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.4.1-01:** Al montar `GrillaPage`, `usePrecarga` se ejecuta siempre, independientemente del estado de conexión. Si hay red, actualiza la caché; si no hay red, usa la caché existente.
- **INV-4.4.1-02:** Si no hay datos en caché y no hay conexión, `GrillaPage` muestra estado de error explícito ("Sin datos disponibles — nunca se abrió esta disciplina con conexión"). No pantalla vacía.
- **INV-4.4.1-03:** Los datos cacheados incluyen timestamp. Si el cache tiene más de 24 horas, se muestra un aviso de posible desactualización, pero se usan igual.
- **INV-4.4.1-04:** `AtaraxiaDiveDB` es un singleton — una sola instancia por sesión del navegador.

### Operación principal: pre-carga al abrir disciplina

| | Descripción |
|---|---|
| **Precondición** | Juez autenticado · `competenciaId` y `disciplina` disponibles en `useCompetenciaStore` |
| **Postcondición** | `GrillaPage` muestra la grilla (desde servidor o IndexedDB) · cache actualizado si había conexión |
| **Excepciones** | Sin red y sin cache → pantalla de error con instrucción de reconectar |

**Ejemplo concreto:**

```
Precondición:  Juez abre disciplina DNF, hay red
usePrecarga:   fetch /competencia/{id}/grilla?disciplina=DNF → ok
               fetch /competencia/{id}/estado?disciplina=DNF → ok
               → persiste en IndexedDB { competencia_id, disciplina, grilla, estado, cached_at: now }
GrillaPage:    muestra grilla normal con badge "online"

---

Precondición:  Juez abre misma disciplina, sin red
usePrecarga:   fetch falla (network error)
               → lee IndexedDB cache existente (2h de antigüedad < 24h)
GrillaPage:    muestra grilla con badge "offline" y label "Datos del HH:MM"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.4.1 — Pre-carga de disciplina en IndexedDB

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 de DNF está en EnEjecucion

  Scenario: abrir disciplina con conexión — pre-carga y actualiza cache
    Given el dispositivo está online
    When el juez toca la DisciplinaCard de DNF
    And GrillaPage termina de montar
    Then la grilla se muestra con los datos actuales del servidor
    And IndexedDB contiene un registro de grilla para (C1, DNF) con timestamp reciente
    And el badge de conexión muestra "online"

  Scenario: abrir disciplina sin conexión con cache válido
    Given el juez abrió la disciplina DNF previamente (hace 2h)
    And el dispositivo está offline
    When el juez toca la DisciplinaCard de DNF
    Then GrillaPage muestra la grilla desde IndexedDB
    And se muestra label "Datos actualizados hace 2h" junto al badge "offline"
    And no hay llamadas de red pendientes

  Scenario: abrir disciplina sin conexión y sin cache previo
    Given el juez nunca abrió la disciplina DNF en este dispositivo
    And el dispositivo está offline
    When el juez toca la DisciplinaCard de DNF
    Then GrillaPage muestra el estado de error "Sin datos disponibles"
    And se muestra el mensaje "Conectate a internet para cargar la disciplina por primera vez"

  Scenario: cache expirado (> 24h) con red disponible
    Given el cache de DNF tiene 25 horas de antigüedad
    And el dispositivo está online
    When el juez abre GrillaPage
    Then se actualiza el cache desde el servidor
    And se muestra la grilla actualizada sin aviso de expiración
```

---

## Impacto arquitectónico

- [x] Sí → introduce Dexie.js como dependencia de almacenamiento local · crear `ADR-015`

**ADR-015** (a crear): elección de Dexie.js sobre IndexedDB nativo para almacenamiento offline.
Justificación: API promise-based + TypeScript nativo + schema migrations integradas vs. verbosidad de la API nativa.

**Capa(s) afectadas:**
- [x] Infrastructure / Frontend — nueva capa `frontend/src/db/` (cliente Dexie + schema)
- [x] Infrastructure / Frontend — `frontend/src/hooks/usePrecarga.ts` (lógica de cache)
- [x] Infrastructure / Frontend — `GrillaPage.tsx` (usa `usePrecarga` en lugar de fetch directo)

---

## Referencias

- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.4`
- Wireframes: `docs/design/ux/wireframes-juez.md §S-02`
- US dependientes: US-4.4.2 (usa el cache de grilla y define la tabla `comando_queue`)
- `frontend/src/stores/useConnectionStore.ts` — estado `isOnline` ya implementado

---

## Notas de implementación

### Estructura `frontend/src/db/`

```
frontend/src/db/
├── index.ts           ← AtaraxiaDiveDB (instancia singleton Dexie)
├── schema.ts          ← definición de tablas y tipos
└── queries.ts         ← funciones de acceso: getGrillaCache, setGrillaCache
```

### Schema IndexedDB (Dexie)

```typescript
// schema.ts
export interface GrillaCacheRecord {
  id?: number          // autoincrement PK
  competencia_id: string
  disciplina: string
  grilla: GrillaAtletaDto[]
  estado: EstadoCompetenciaDto
  cached_at: number    // Date.now()
}

export interface ComandoQueueRecord {
  id?: number          // autoincrement PK — orden FIFO
  tipo: 'llamar' | 'resultado' | 'tarjeta' | 'dns' | 'resolver_revision'
  competencia_id: string
  payload: string      // JSON serializado
  estado: 'pendiente' | 'enviando' | 'error'
  creado_at: number
  intentos: number
  error_mensaje?: string
}

// index.ts
class AtaraxiaDiveDB extends Dexie {
  grilla_cache!: Dexie.Table<GrillaCacheRecord, number>
  comando_queue!: Dexie.Table<ComandoQueueRecord, number>

  constructor() {
    super('AtaraxiaDiveDB')
    this.version(1).stores({
      grilla_cache: '++id, [competencia_id+disciplina], cached_at',
      comando_queue: '++id, estado, creado_at',
    })
  }
}
export const db = new AtaraxiaDiveDB()
```

### `usePrecarga` — lógica

```
1. Al montar GrillaPage: llamar a usePrecarga(competenciaId, disciplina)
2. Si isOnline:
   a. fetch grilla + fetch estado (en paralelo)
   b. Persistir en IndexedDB (upsert por [competencia_id, disciplina])
   c. Setear datos en estado local (GrillaPage los renderiza)
3. Si !isOnline:
   a. Leer IndexedDB para [competencia_id, disciplina]
   b. Si existe: setear datos + mostrar label con antigüedad
   c. Si no existe: setear estado de error
```

### Instalación de Dexie.js

```bash
npm install dexie
```

Agregar `"dexie": "^4.x"` en `package.json` dependencies (no devDependencies).

---

*Redactado: 2026-04-13 — INC-4.4 Offline-first*
