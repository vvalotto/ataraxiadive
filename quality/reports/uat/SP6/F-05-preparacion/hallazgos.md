# Hallazgos — Fase F-05: Preparación (Grilla y Asignación de Jueces)

## Defectos

| ID | Escenario | Descripción | Severidad | Estado | Fix |
|----|-----------|-------------|-----------|--------|-----|
| H-05-01 | F05-S02 | Al regenerar grilla, falta el campo "Intervalo OT" — no se puede modificar | 🟡 | Resuelto | `GrillaPanel.tsx`: nueva mutation `regenerarConIntervaloMutation` · `requiresIntervalo` en form de regenerar · llama `POST /competencia` con ID existente antes de regenerar |
| H-05-02 | F05-S02 | Columna ESTADO en tabla de grilla no tiene sentido en PREPARACION | 🟡 | Resuelto | `TablaGrilla.tsx`: eliminada columna ESTADO (header + celda + funciones huérfanas) |
| H-05-03 | F05-S10 | Panel operativo sin selector de disciplina — muestra solo la disciplina auto-elegida | 🟡 | Resuelto | `DashboardOperativoPage.tsx`: selector `<select>` de disciplina visible cuando hay más de una competencia |
| H-05-04 | F05-S10 | "Tiempo estimado" muestra en minutos crudos (ej. `95'`) — debe ser hh:mm | 🟡 | Resuelto | `DashboardOperativoPage.tsx`: `formatDurationMinutes` reformateado a `hh:mm` · label actualizado a "Tiempo estimado (hh:mm)" |
| H-05-05 | F05-S12 | Juez no ve asignaciones en estado PREPARACION — hook filtraba solo EJECUCION | 🔴 | Resuelto | `useDisciplinasJuez.ts`: `esEnEjecucion` → `esTorneoOperativo` · incluye PREPARACION y PREMIACION |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| — | — | Sin mejoras registradas | — |
