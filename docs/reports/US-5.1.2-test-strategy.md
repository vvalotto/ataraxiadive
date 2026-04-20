# US-5.1.2 — Estrategia de Tests

## Tipo de US

Frontend React/Vite para gestionar fases del torneo desde el panel del organizador.

## Unit Tests

No se agregan tests unitarios automatizados de componentes porque el frontend no tiene runner
unitario configurado en `package.json` (no hay Vitest/Jest/Testing Library). Introducirlo en
esta US ampliaria el alcance tecnico.

Validacion aplicada:

- `npm run build`: TypeScript + bundle Vite.
- `npx eslint src`: lint acotado a codigo fuente.

## Integracion

La integracion cubierta por la implementacion es UI -> endpoints existentes:

- `PUT /torneos/{id}/abrir-inscripcion`
- `PUT /torneos/{id}/cerrar-inscripcion`
- `PUT /torneos/{id}/iniciar-ejecucion`
- `PUT /torneos/{id}/volver-preparacion`
- `PUT /torneos/{id}/iniciar-premiacion`
- `PUT /torneos/{id}/cerrar`
- `PUT /torneos/{id}/cancelar`
- `GET /torneos/{id}` para refresco post-transicion.

## BDD

Escenarios generados en:

- `tests/features/US-5.1.2-gestion-fases-torneo.feature`

No se agregan step definitions ejecutables porque el proyecto no tiene harness E2E/browser
frontend configurado.
