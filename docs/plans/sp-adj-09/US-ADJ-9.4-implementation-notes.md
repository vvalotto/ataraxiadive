# US-ADJ-9.4 - Implementation Notes

**Fecha:** 2026-04-28
**Sprint:** `SP-ADJ-09`
**US:** `US-ADJ-9.4`

---

## Resumen

Se separo la ruta primaria `Panel` del detalle de torneo y se implemento un
dashboard operativo dedicado para el organizador, alineado al wireframe `S-01`
con KPIs, disciplina activa, alertas y proximos atletas.

---

## Cambios implementados

### Ruta primaria `Panel`

- `frontend/src/App.tsx`
  - `/organizador/panel` ahora monta `DashboardOperativoPage`
  - `DetalleTorneoPage` deja de ser el contenido principal del panel operativo

### Dashboard operativo

- `frontend/src/pages/organizador/DashboardOperativoPage.tsx`
  - selector de torneo operativo cuando no existe `torneo_id`
  - carga del torneo y sus competencias activas
  - seleccion de disciplina principal priorizando estado `EnEjecucion`
  - KPI strip con:
    - atletas totales
    - completados
    - en revision
    - tiempo estimado

### Composicion de datos

- se reutilizaron queries existentes del frontend:
  - `fetchTorneo`
  - `fetchCompetenciasPorTorneo`
  - `fetchEstadoCompetencia`
  - `fetchProgresoCompetencia`
  - `fetchPerformanceActual`
  - `fetchGrillaCompetencia`
  - `fetchProximasPerformances`

- el dashboard deriva:
  - alertas activas desde filas en `EnRevision`
  - empty state explicito `Sin alertas`
  - proximos atletas desde grilla/proximas performances
  - otras disciplinas como cards informativas

### Separacion conceptual confirmada

- `/organizador/torneo` sigue siendo la home de torneos de `US-ADJ-9.3`
- `/organizador/panel` pasa a ser la vista ejecutiva del torneo activo
- no se reutilizo el listado general de torneos como contenido principal del panel

---

## Quality Gates

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: falla solo por error preexistente fuera de alcance en:
  - `frontend/src/pages/atleta/portalData.ts:120`

---

## Observaciones

- las alertas del panel se modelan con la informacion observable hoy en frontend,
  principalmente performances en `EnRevision`
- el ETA es una estimacion basada en intervalo configurado y atletas pendientes;
  no intenta simular precision mayor a la expuesta por los datos actuales
- `DetalleTorneoPage` sigue disponible para flujos de detalle/contexto, pero ya no
  ocupa la ruta primaria del `Panel`
