# US-5.1.1 — Reporte Final

**US:** Crear/editar torneo — formulario del organizador  
**Sprint:** SP5  
**Incremento:** INC-5.1  
**Branch:** `feature/US-5.1.1-crear-torneo`  
**Producto:** frontend  
**Estado:** Implementada

## Resultado

Se implemento el flujo de alta de torneo desde el panel del organizador:

- Nueva ruta protegida `/organizador/torneos/nuevo`.
- Formulario de torneo con nombre, descripcion, fechas, sede, entidad organizadora y disciplinas.
- Selector de disciplinas FAAS.
- Validaciones frontend para nombre, fechas y disciplinas.
- Flujo HTTP en dos pasos:
  - `POST /torneos`
  - `PUT /torneos/{torneo_id}/disciplinas`
- Manejo inline de errores backend sin perder datos del formulario.
- Ruta minima `/organizador/torneo/:torneoId` para destino post-creacion.
- Accion "Nuevo torneo" desde el dashboard.

## Archivos Principales

- `frontend/src/api/torneo.ts`
- `frontend/src/components/organizador/DisciplinaSelector.tsx`
- `frontend/src/pages/organizador/CrearTorneoPage.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `frontend/src/pages/organizador/DashboardPage.tsx`
- `frontend/src/App.tsx`

## Artefactos del Pipeline

- `docs/reports/US-5.1.1-context.md`
- `tests/features/US-5.1.1-crear-torneo-ui.feature`
- `docs/plans/sp5/US-5.1.1-plan.md`
- `docs/reports/US-5.1.1-test-strategy.md`
- `docs/reports/US-5.1.1-integration.md`
- `docs/reports/US-5.1.1-bdd-waiver.md`
- `quality/reports/codeguard/US-5.1.1-quality.json`
- `docs/traceability/matrix.md`
- `.claude/tracking/US-5.1.1-tracking.json`

## Validacion

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
- `npm run lint`: no aprobado por archivos generados preexistentes en `frontend/.vite/deps/react-router-dom.js`, fuera del codigo fuente modificado.

## Decisiones

- Se implemento una pantalla de detalle minima aunque el detalle completo pertenece a `US-5.1.2`, porque `US-5.1.1` navega alli despues de crear el torneo.
- No se introdujo runner unitario frontend nuevo. La evidencia de calidad para esta US queda en TypeScript build, ESLint sobre `src` y escenarios BDD persistidos.

## Pendientes Para US Posteriores

- `US-5.1.2`: acciones reales de transicion de fase en el detalle del torneo.
- `US-5.1.3`: inscriptos en preparacion.
- `US-5.1.4`: generacion y ajuste de grilla.
- `US-5.1.5`: asignacion de jueces.
- `US-5.1.6`: monitor de ejecucion.
