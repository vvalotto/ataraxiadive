# US-ADJ-9.2 - Implementation Notes

**Fecha:** 2026-04-28
**Sprint:** `SP-ADJ-09`
**US:** `US-ADJ-9.2`

---

## Resumen

La navegacion primaria del organizador dejo de depender de tabs deshabilitadas y de
links dominantes a `dashboard`. Se normalizo el routing del rol para que cada seccion
principal tenga una ruta real bajo el shell compartido.

---

## Cambios implementados

### Routing del organizador

- `frontend/src/App.tsx`
  - redirect inicial del organizador actualizado a `/organizador/torneo`
  - alias `/organizador` y `/organizador/dashboard` redirigen a la home del rol
  - nuevas rutas primarias:
    - `/organizador/panel`
    - `/organizador/grilla`
    - `/organizador/jueces`
    - `/organizador/torneo`
    - `/organizador/audit-log`

### Shell y estado activo

- `frontend/src/components/organizador/OrganizadorLayout.tsx`
  - tabs primarios ya no estan deshabilitados
  - cada tab apunta a un destino real
  - deteccion de seccion activa ajustada para rutas nuevas e historicas

### Paginas primarias nuevas o adaptadas

- `frontend/src/pages/organizador/OrganizadorGrillaPage.tsx`
- `frontend/src/pages/organizador/OrganizadorJuecesPage.tsx`
- `frontend/src/components/organizador/TorneoRouteSelector.tsx`

Estas pantallas montan secciones primarias con seleccion de torneo por `query param`
sin obligar a pasar por `DetalleTorneoPage`.

### Panel y audit log

- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
  - soporta `/organizador/panel?torneo_id=...`
  - cuando no hay torneo seleccionado muestra selector de torneo
  - `Grilla` y `Jueces` salen de las tabs internas y pasan a links hacia rutas primarias

- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
  - soporta `/organizador/audit-log?torneo_id=...`
  - mantiene compatibilidad con la ruta historica `/organizador/torneos/:torneoId/competencias`

### Links internos normalizados

- paginas del organizador ajustadas para volver a `Torneo` o `Audit Log` segun contexto:
  - `CrearTorneoPage.tsx`
  - `UsuariosPage.tsx`
  - `ResultadosPage.tsx`
  - `AuditoriaCompetenciaPage.tsx`
  - `AuditoriaPerformancePage.tsx`
  - `DashboardPage.tsx`

---

## Quality Gates

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: falla solo por error preexistente fuera de alcance en:
  - `frontend/src/pages/atleta/portalData.ts:120`

---

## Observaciones

- La home del organizador queda hoy en `/organizador/torneo`, preparada para la
  formalizacion funcional de `US-ADJ-9.3`.
- La branch de trabajo usa el nombre `feature-US-ADJ-9.2-routing-organizador`
  por una restriccion local al crear refs con `/` en `.git/refs`.
