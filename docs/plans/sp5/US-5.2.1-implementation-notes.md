# US-5.2.1 — Notas de Implementacion

**Fecha:** 2026-04-22
**Fase:** 3 — Implementacion

---

## Cambios realizados

- `frontend/src/api/competencia.ts`
  - Agregado `iniciarCompetencia()` para `POST /competencia/{competencia_id}/iniciar`.

- `frontend/src/components/organizador/EjecucionPanel.tsx`
  - Reemplazado el monitor de solo disciplinas activas por una vista maestro-detalle.
  - El maestro compone:
    - `listarDisciplinasTorneo(torneoId)`
    - `fetchCompetenciasPorTorneo(torneoId)`
    - `fetchEstadoCompetencia()`
    - `fetchProgresoCompetencia()`
  - El detalle muestra:
    - estado operativo derivado;
    - juez asignado;
    - hash SHA-256 si la competencia finalizo;
    - grilla OT para estados no activos;
    - `MonitorDisciplina` para competencias en ejecucion.
  - Agregada accion `Habilitar disciplina` solo para estado operativo `lista_para_iniciar`.

---

## Estados operativos derivados

- `sin_competencia`
- `sin_grilla`
- `sin_juez`
- `lista_para_iniciar`
- `en_ejecucion`
- `finalizada`
- `no_disponible`

La decision de habilitar inicio queda en frontend, pero el backend sigue siendo fuente de verdad:
si la competencia no esta en estado `Confirmada`, `POST /competencia/{id}/iniciar` responde error.

---

## Validaciones ejecutadas

- `npm run build` — OK
- `npm run lint` — OK tras eliminar `setState` sincronico dentro de `useEffect`

---

## Pendiente para US-5.2.2

No se implementa cierre manual. El detalle queda preparado visualmente para acciones por disciplina,
pero la accion `Finalizar prueba` corresponde a `US-5.2.2`.
