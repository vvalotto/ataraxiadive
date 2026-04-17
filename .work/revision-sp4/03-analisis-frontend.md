# Revisión de Calidad — Cierre SP4
## Análisis Frontend — INC-4.2 a INC-4.6

**Fecha:** 2026-04-16
**Herramientas ejecutadas:** ESLint · TypeScript `tsc --noEmit` · madge (circular deps)
**Análisis manual:** capas, LOC, complejidad de hooks, uso de stores

---

## Resultados de herramientas automáticas

| Herramienta | Resultado | Observación |
|-------------|:---------:|-------------|
| ESLint | ✅ **0 errores, 0 warnings** | `rules-of-hooks`, `exhaustive-deps`, TypeScript strict — todo limpio |
| TypeScript `tsc` | ✅ **0 errores** | Strict mode activo — contratos de tipos respetados en todo el codebase |
| madge (circular deps) | ✅ **0 ciclos** | 47 archivos, ningún ciclo de dependencia |

El frontend pasa todos los gates automáticos con cero hallazgos. Esto es notable para un codebase de ~4100 líneas con PWA, IndexedDB y estado offline.

---

## Distribución de LOC por archivo

| Archivo | LOC | Categoría |
|---------|:---:|-----------|
| `hooks/usePerformanceFlow.ts` | **447** | Hook — mayor archivo del codebase |
| `pages/juez/PerformanceFlowPage.tsx` | **307** | Página |
| `pages/juez/GrillaPage.tsx` | **291** | Página |
| `hooks/useSyncQueue.ts` | 289 | Hook |
| `api/competencia.ts` | 259 | API client |
| `pages/organizador/AuditoriaCompetenciaPage.tsx` | 200 | Página |
| `components/juez/RpSelector.tsx` | 160 | Componente |
| `hooks/usePrecarga.ts` | 147 | Hook |
| `db/queries.ts` | 122 | DB layer |
| `components/juez/StepTarjeta.tsx` | 109 | Componente |

Total del codebase frontend: **4138 LOC** en 47 archivos.

Archivos pequeños y cohesivos dominan: 35 de 47 tienen menos de 100 líneas. Los tres archivos grandes (`usePerformanceFlow`, `PerformanceFlowPage`, `GrillaPage`) corresponden al flujo más complejo del dominio — el registro de performance del juez.

---

## Análisis de capas — arquitectura esperada

La arquitectura definida implícitamente para este frontend es:

```
pages/      → orquesta hooks y componentes
hooks/      → lógica de negocio + acceso a api/ y db/
components/ → UI pura, recibe props
stores/     → estado global compartido
api/        → HTTP clients
db/         → IndexedDB (Dexie)
```

### Violaciones encontradas

#### FE-ARCH-01 — Páginas del organizador llaman a `api/` directamente (sin hooks)

Las páginas del juez usan hooks (`usePrecarga`, `useComandoQueue`, `useSyncQueue`).
Las páginas del organizador acceden a `api/` directamente:

| Página | Import directo de api/ |
|--------|----------------------|
| `TorneoCompetenciasPage.tsx` | `fetchCompetenciasPorTorneo`, `fetchTorneos` |
| `DashboardPage.tsx` | revisar |
| `LoginPage.tsx` | `loginApi` |
| `AuditoriaPerformancePage.tsx` | `type AuditLogEventoDto` (solo tipo) |
| `AuditoriaCompetenciaPage.tsx` | `type GrillaAtletaDto` (solo tipo) |

Las importaciones de **tipos** no crean acoplamiento de runtime — son aceptables.
Los **fetch directos** en páginas sí son una violación: la página mezcla
responsabilidades de presentación con orquestación de red.

Comparación:
- `GrillaPage` (juez) → usa `usePrecarga` → que internamente llama `fetchGrillaCompetencia`
- `TorneoCompetenciasPage` (organizador) → llama `fetchCompetenciasPorTorneo` directamente

El patrón es inconsistente. La interfaz del juez está bien abstraída porque fue implementada
con offline-first en mente (los hooks necesitan la capa de caché). Las páginas del
organizador fueron implementadas sin ese requisito y la abstracción no se aplicó.

**Severidad:** Media — no es incorrecto funcionalmente, pero es deuda de consistencia
que crece si se agregan más páginas del organizador en SP5.

---

#### FE-ARCH-02 — `GrillaPage` importa de `db/` directamente

```typescript
// GrillaPage.tsx
import { getCommandsByCompetencia } from '../../db/queries'
import type { ComandoQueueRecord } from '../../db/schema'
```

Una página no debería conocer IndexedDB. Esta lógica — saber cuántos comandos hay en
cola por competencia — debería vivir en `useComandoQueue` o en un hook dedicado
`useCommandStatus`.

El motivo probable: `GrillaPage` necesita mostrar el indicador de comandos pendientes
por atleta (qué atletas tienen comandos encolados). `useComandoQueue` ya expone
`pendingCount` global pero no el detalle por atleta. En lugar de extender el hook,
se accedió directamente a la DB.

**Severidad:** Media — es la única violación `page → db/`.

---

## Análisis de hooks

### `usePerformanceFlow.ts` — 447 líneas, 13 estados

El hook más grande del codebase gestiona el flujo de 6 pasos del registro de performance.

**Estado interno:**
```
step · inlineError · metros · centimetros · otWindowActive · chronoStarted
selectedCard · motivoDq · distanciaBlackout · penalizaciones · isBkoMode
completed · resultKind
```

13 `useState` en un solo hook es alto. En el backend, el equivalente sería un aggregate
con muchos campos — el DesignReviewer lo marcaría como GodObject candidate.

Sin embargo, hay contexto importante: **el flujo de 6 pasos ES complejo por diseño del
dominio**. El juez pasa por: llamar → resultado → tarjeta → penalizaciones → BKO →
confirmación. Cada paso tiene estado propio. Extraer hooks por paso crearía hooks de
1-2 estados que no reducirían la complejidad total — solo la redistribuirían.

**Lo que sí es mejorable:** el hook exporta funciones utilitarias puras:

```typescript
// usePerformanceFlow.ts
export function buildResultadoValue(metros, centimetros, unidad) { ... }
export function formatMarca(value, unidad) { ... }
```

`GrillaPage` importa `formatMarca` directamente del archivo del hook:
```typescript
import { formatMarca } from '../../hooks/usePerformanceFlow'
```

Una función de formateo no tiene nada que ver con un hook. Estas funciones
deberían estar en `utils/disciplina.ts` (ya existe) o en un `utils/marca.ts`.

**Severidad del hook en sí:** Baja (complejidad esencial del dominio).
**Severidad de las utils exportadas:** Baja — pero crea acoplamiento innecesario entre `GrillaPage` y el hook más grande del codebase.

---

### `useSyncQueue.ts` — 289 líneas

Analizado en detalle en US-4.6.6 (offline-first). El hook tiene 6 `useEffect` con
responsabilidades bien separadas (sync on reconnect, background sync, SW message listener,
cleanup). La longitud es justificada por la complejidad del protocolo de sincronización.

Sin señales de alarma.

---

### Uso de stores en components/

Zustand está diseñado para ser accedido desde cualquier capa. Los casos encontrados:

| Componente | Store | Dato accedido |
|-----------|-------|--------------|
| `JuezLayout` | `useAuthStore` | Nombre del usuario (display) |
| `SyncStatusBadge` | `useConnectionStore` | Estado de conexión y sync |

Ambos son casos legítimos de estado global UI — no hay lógica de negocio en los
componentes, solo lectura de estado para display.

---

## Resumen de issues

| ID | Área | Issue | Severidad | Candidato SP-ADJ-06 |
|----|------|-------|-----------|:-------------------:|
| FE-ARCH-01 | `pages/organizador/` | Páginas del organizador llaman `api/` directamente — inconsistente con el patrón de hooks del juez | Media | Sí |
| FE-ARCH-02 | `pages/juez/GrillaPage.tsx` | Importa de `db/queries` directamente — lógica que debería estar en un hook | Media | Sí |
| FE-DES-01 | `hooks/usePerformanceFlow.ts` | Exporta `formatMarca` y `buildResultadoValue` — utils puras en un archivo de hook | Baja | Sí (mover a `utils/`) |

---

## Lo que está bien

- **ESLint + TypeScript:** cero errores en modo estricto — calidad de tipos excelente
- **Sin dependencias circulares** — la separación de módulos es limpia
- **Hooks del juez bien abstraídos** — `usePrecarga`, `useComandoQueue`, `useSyncQueue` encapsulan correctamente la complejidad offline
- **Stores sin acoplamiento entre sí** — `useAuthStore`, `useCompetenciaStore`, `useConnectionStore` son independientes
- **Componentes de paso (`StepTarjeta`, `StepRevision`, `StepBKO`)** — pequeños y cohesivos, reciben props, no acceden a stores ni a API
- **47 archivos, 35 con menos de 100 líneas** — el codebase es mayoritariamente modular

---

## Observación experimental

El frontend muestra una asimetría de madurez arquitectónica entre las dos interfaces:

- **Interfaz del juez** — diseñada con offline-first como restricción, lo que forzó la abstracción en hooks. El resultado es una arquitectura más limpia.
- **Interfaz del organizador** — diseñada sin restricción offline, el acceso directo a `api/` fue el camino de menor resistencia. El resultado es páginas más acopladas.

Esta asimetría es un hallazgo experimental relevante para IEDD: **los requisitos no funcionales (offline-first) producen mejores abstracciones que las convenciones de estilo**. La restricción técnica actuó como driver de diseño de forma más efectiva que la convención arquitectónica.

---

*Creado: 2026-04-16 — Revisión pre-BL-004*
