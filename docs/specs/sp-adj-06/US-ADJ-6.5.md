# US-ADJ-6.5: Frontend — corregir violaciones de capa en `GrillaPage` y `usePerformanceFlow`

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: N/A (frontend)
**Bounded Context**: `frontend`

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero corregir dos violaciones de capa en el frontend del juez
para alinear `GrillaPage` con la arquitectura esperada (páginas → hooks → db/api)
y mover funciones utilitarias puras a su ubicación correcta.

---

## Contexto del dominio

### Arquitectura frontend esperada

```
pages/      → orquesta hooks y componentes
hooks/      → lógica de negocio + acceso a api/ y db/
components/ → UI pura, recibe props
utils/      → funciones puras sin estado
```

### Hallazgos que originan esta US

De `03-analisis-frontend.md`:

**FE-ARCH-02 — `GrillaPage` importa de `db/queries` directamente:**

```typescript
// GrillaPage.tsx
import { getCommandsByCompetencia } from '../../db/queries'
import type { ComandoQueueRecord } from '../../db/schema'
```

Una página no debería conocer IndexedDB. La lógica de "cuántos comandos pendientes
hay por atleta" debería vivir en `useComandoQueue`, que ya gestiona la cola de comandos.
Se accedió directamente a la DB porque `useComandoQueue` exponía `pendingCount` global
pero no el detalle por atleta.

**FE-DES-01 — `formatMarca` y `buildResultadoValue` exportadas desde un archivo de hook:**

```typescript
// usePerformanceFlow.ts — funciones puras exportadas desde un hook
export function buildResultadoValue(metros, centimetros, unidad) { ... }
export function formatMarca(value, unidad) { ... }

// GrillaPage.tsx — importa utilidades de un archivo de hook
import { formatMarca } from '../../hooks/usePerformanceFlow'
```

Estas funciones no tienen estado, no usan React ni hooks, y no dependen del contexto
del hook. Son utilidades puras de formato de marca que pertenecen a `utils/`.

---

## Especificación del comportamiento

### Precondición

- `GrillaPage.tsx` importa `getCommandsByCompetencia` de `db/queries`
- `GrillaPage.tsx` importa `formatMarca` de `hooks/usePerformanceFlow`
- `usePerformanceFlow.ts` exporta `formatMarca` y `buildResultadoValue` como funciones de módulo

### Cambio propuesto

**Fix FE-ARCH-02:** extender `useComandoQueue` para exponer comandos pendientes por atleta:

```typescript
// useComandoQueue.ts — nueva propiedad expuesta
pendingByAtleta: Record<string, number>  // atleta_id → cantidad de comandos pendientes
```

`GrillaPage` usa `useComandoQueue().pendingByAtleta[atleta.id]` en lugar de importar de `db/`.

**Fix FE-DES-01:** crear `frontend/src/utils/marca.ts` con las dos funciones:

```typescript
// frontend/src/utils/marca.ts
export function formatMarca(value: Decimal | null, unidad: UnidadMedida): string { ... }
export function buildResultadoValue(metros: string, centimetros: string, unidad: UnidadMedida): Decimal { ... }
```

Actualizar `GrillaPage` para importar desde `utils/marca.ts`.
Mantener la exportación de `usePerformanceFlow.ts` si hay otros consumidores, o eliminarla
si `GrillaPage` era el único.

### Postcondición

- `GrillaPage.tsx` no importa nada de `db/` ni de `schema`
- `GrillaPage.tsx` importa `formatMarca` de `utils/marca.ts`
- `useComandoQueue` expone `pendingByAtleta`
- `utils/marca.ts` existe con las dos funciones puras
- ESLint 0 errores · `tsc --noEmit` 0 errores · `npm run build` exitoso

---

## Criterios de aceptación

```gherkin
Feature: GrillaPage sin imports directos de db/ ni de archivos de hooks

  Scenario: GrillaPage no importa de db/queries ni de db/schema
    Given el archivo GrillaPage.tsx
    Then no contiene imports de '../../db/queries'
    And no contiene imports de '../../db/schema'

  Scenario: El indicador de comandos pendientes por atleta funciona
    Given un atleta con 2 comandos pendientes en la cola offline
    When se renderiza la GrillaPage
    Then el indicador del atleta muestra "2 pendientes"
    And la información proviene de useComandoQueue, no de db/queries directamente

  Scenario: formatMarca vive en utils/marca.ts
    Given el archivo frontend/src/utils/marca.ts
    Then exporta formatMarca y buildResultadoValue
    And GrillaPage importa formatMarca desde utils/marca.ts

  Scenario: El build de TypeScript es exitoso
    Given el código refactorizado
    When se ejecuta tsc --noEmit y npm run build
    Then no hay errores de TypeScript ni de compilación
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — es un refactor de capa dentro del frontend existente

**Capa(s) afectadas:**
- [x] `frontend/src/pages/juez/GrillaPage.tsx`
- [x] `frontend/src/hooks/useComandoQueue.ts`
- [x] `frontend/src/hooks/usePerformanceFlow.ts` (eliminar exports de utilidades)
- [x] `frontend/src/utils/marca.ts` (nuevo archivo)

---

## Notas de implementación

1. Verificar si hay otros consumidores de `formatMarca` o `buildResultadoValue` fuera de `GrillaPage`
   antes de modificar `usePerformanceFlow.ts`.
2. `pendingByAtleta` en `useComandoQueue` puede calcularse como un `useMemo` sobre
   `db.comandoQueue.where('estado').anyOf(['pendiente', 'error']).toArray()`.
3. Ejecutar ESLint (`npm run lint`) y `tsc --noEmit` antes y después del cambio.
4. Validar visualmente que el indicador de comandos pendientes por atleta sigue
   funcionando en la grilla — este es el único cambio de comportamiento observable.

---

*Spec creada: 2026-04-16 — FE-ARCH-02 y FE-DES-01 de revisión frontend pre-BL-004*
