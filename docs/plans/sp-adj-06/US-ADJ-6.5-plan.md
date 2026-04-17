# Plan Técnico — US-ADJ-6.5
## Frontend — corregir violaciones de capa en GrillaPage

*Generado: 2026-04-17 — Fase 2 /implement-us US-ADJ-6.5*

---

## Situación actual

**FE-ARCH-02:** `GrillaPage` importa `getCommandsByCompetencia` de `db/queries` y
`ComandoQueueRecord` de `db/schema`. El queue se usa para 3 cosas: proyectar estado
optimista, calcular `firstPendingPerformanceId` y computar `pendingByAtleta`.

**FE-DES-01:** `formatMarca` y `buildResultadoValue` están exportadas desde
`usePerformanceFlow.ts`. Dos consumidores: `GrillaPage` y `AtletaCard`.

---

## Solución

### T1 — Crear `hooks/useGrillaQueue.ts`

Encapsula todo acceso a db/queries del queue de grilla:
- Importa `getCommandsByCompetencia` y `ComandoQueueRecord` de `db/`
- Exporta `useGrillaQueue(competenciaId)` → `{ queueData, pendingByAtleta, projectedEstado }`
- Mueve `projectedEstado` al hook (era función privada de GrillaPage)
- `pendingByAtleta` calculado con `useMemo` interno

### T2 — Crear `utils/marca.ts`

Mueve `formatMarca` y `buildResultadoValue` a `frontend/src/utils/marca.ts`.

### T3 — Actualizar `GrillaPage.tsx`

- Reemplazar `useQuery(getCommandsByCompetencia)` con `useGrillaQueue(competenciaId)`
- Eliminar imports de `db/queries` y `db/schema`
- Importar `formatMarca` desde `../../utils/marca`
- Eliminar `function projectedEstado` (viene del hook)

### T4 — Actualizar `usePerformanceFlow.ts`

- Importar `formatMarca` y `buildResultadoValue` desde `../utils/marca`
- Eliminar las definiciones locales y sus exports

### T5 — Actualizar `AtletaCard.tsx`

- Cambiar import de `formatMarca` de `hooks/usePerformanceFlow` a `../../utils/marca`

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `frontend/src/hooks/useGrillaQueue.ts` | Nuevo |
| `frontend/src/utils/marca.ts` | Nuevo |
| `frontend/src/pages/juez/GrillaPage.tsx` | T3 |
| `frontend/src/hooks/usePerformanceFlow.ts` | T4 |
| `frontend/src/components/juez/AtletaCard.tsx` | T5 |

## Validación

- `npx tsc --noEmit` sin errores
- `npm run build` exitoso

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1 + T2 | 20 min |
| T3 + T4 + T5 | 15 min |
| tsc + build | 5 min |
| **Total** | **40 min** |
