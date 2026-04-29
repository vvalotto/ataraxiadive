# Notas de Implementacion - US-ADJ-9.6

## Resumen

`US-ADJ-9.6` cierra la migracion UX de las secciones primarias del organizador para que `Grilla`, `Jueces`, `Torneo` y `Audit Log` queden integradas al shell persistente correcto, sin depender de tabs locales ni de un flujo basado en "volver al dashboard".

## Cambios implementados

### 1. Navbar del shell con contexto de torneo persistente

- `frontend/src/components/organizador/OrganizadorLayout.tsx`
- La navbar superior ahora conserva el `torneo_id` cuando existe un torneo activo.
- La seccion `Torneo` ya no apunta a la home general cuando hay contexto activo; navega a `/organizador/torneo/:torneoId`.
- Se corrigio la seccion activa para que `/organizador/torneo/:torneoId` marque `Torneo` y las rutas de auditoria marquen `Audit Log`.

### 2. `DetalleTorneoPage` redefinida como vista contextual

- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- Se eliminaron los tabs locales `Detalle / Inscriptos / Ejecucion`.
- Se eliminaron los accesos primarios redundantes a `Grilla`, `Jueces`, `Audit Log` y `Resultados`.
- La pagina ahora conserva:
  - resumen del torneo
  - acciones propias del contexto (`Cambiar torneo`, `Ver panel`)
  - bloque contextual de inscriptos
  - bloque contextual de ejecucion
- Se reencuadro visualmente al lenguaje dark del shell.

### 3. `Audit Log` como seccion primaria real

- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
- La pagina se reencuadro como `Audit Log`, con copy y jerarquia de shell primario.
- Se mantuvo la trazabilidad por disciplina y competencia, pero dentro de una seccion dark consistente con el organizador.

### 4. Auditorias contextuales con shell persistente

- `frontend/src/pages/organizador/AuditoriaCompetenciaPage.tsx`
- `frontend/src/pages/organizador/AuditoriaPerformancePage.tsx`
- Ambas vistas siguen siendo contextuales, pero ahora:
  - mantienen navbar principal visible
  - reciben `activeTournamentId` para conservar navegacion coherente
  - reducen acciones redundantes
  - adoptan lenguaje visual dark alineado al shell

### 5. Secciones primarias integradas al torneo activo

- `frontend/src/pages/organizador/DashboardOperativoPage.tsx`
- `frontend/src/pages/organizador/OrganizadorGrillaPage.tsx`
- `frontend/src/pages/organizador/OrganizadorJuecesPage.tsx`
- `frontend/src/pages/organizador/ResultadosPage.tsx`
- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
- Todas estas vistas pasan el `activeTournamentId` al layout para que el cambio de seccion desde la navbar no pierda el contexto del torneo activo.

## Invariantes cubiertas

- `INV-ADJ-9.6-01`: las secciones primarias se acceden desde la navbar superior.
- `INV-ADJ-9.6-02`: las vistas detalle/contextuales no reemplazan el shell principal.
- `INV-ADJ-9.6-03`: `DetalleTorneoPage` deja de concentrar navegacion primaria.
- `INV-ADJ-9.6-04`: `Grilla`, `Jueces`, `Torneo` y `Audit Log` comparten lenguaje visual dark del shell.

## Quality Gates

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: falla solo por el error preexistente en `frontend/src/pages/atleta/portalData.ts:120`

## Observaciones

- No hubo cambios de backend ni de dominio.
- El ajuste es estructural de frontend y navegacion del rol organizador.
- La mejora principal no es cosmetica: la navbar ahora conserva el torneo activo al moverse entre secciones primarias.
