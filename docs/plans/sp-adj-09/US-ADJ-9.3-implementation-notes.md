# US-ADJ-9.3 - Implementation Notes

**Fecha:** 2026-04-28
**Sprint:** `SP-ADJ-09`
**US:** `US-ADJ-9.3`

---

## Resumen

La home del organizador quedó formalizada como listado inicial de torneos bajo su
responsabilidad, con foco en torneos vigentes y acceso explícito al histórico.

---

## Cambios implementados

### Home del organizador

- `frontend/src/pages/organizador/DashboardPage.tsx`
  - la vista quedó expresada como `Home de torneos`
  - se reemplazaron los filtros heredados:
    - `Todos`
    - `Abiertos`
    - `Cerrados`
    - `Cancelados`
  - por la semántica formal:
    - `Vigentes`
    - `Histórico`

### Clasificación de estados

- se definieron helpers explícitos:
  - `esTorneoVigente`
  - `esTorneoHistorico`
  - `esTorneoPendienteActivacion`

- la vista por defecto muestra solo:
  - `INSCRIPCION_ABIERTA`
  - `PREPARACION`
  - `EJECUCION`
  - `PREMIACION`

- el filtro histórico muestra solo:
  - `CERRADO`
  - `CANCELADO`

### Tratamiento de torneos en estado `CREADO`

- los torneos `CREADO` no se consideran vigentes por defecto
- si existen, la home muestra una advertencia separada indicando que permanecen
  pendientes de activación y no integran el listado vigente hasta abrir inscripción

### Claridad de rol de la pantalla

- se agregó copy explícito aclarando que esta pantalla es la home del organizador
  y no el dashboard operativo del torneo
- se mantuvo la acción principal `Gestionar` por torneo hacia `/organizador/panel`

---

## Quality Gates

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: falla solo por error preexistente fuera de alcance en:
  - `frontend/src/pages/atleta/portalData.ts:120`

---

## Observaciones

- `US-ADJ-9.3` deja explícita la separación conceptual entre:
  - home de torneos del organizador
  - dashboard operativo del torneo activo
- el dashboard operativo sigue diferido a `US-ADJ-9.4`
