# US-5.1.1 — Estrategia de Tests

## Tipo de US

Frontend React/Vite para crear torneos desde la UI del organizador.

## Unit Tests

No se agregan tests unitarios automatizados de componentes porque el frontend no tiene runner
unitario configurado en `package.json` (no hay Vitest/Jest/Testing Library). Introducirlo en
esta US ampliaria el alcance tecnico mas alla de `US-5.1.1`.

Validacion aplicada:

- `npm run build`: TypeScript + bundle Vite.
- `npx eslint src`: lint acotado a codigo fuente.

## Integracion

La integracion cubierta por la implementacion es cliente UI -> endpoints existentes:

- `POST /torneos`
- `PUT /torneos/{torneo_id}/disciplinas`
- `GET /torneos/{torneo_id}` para detalle minimo post-creacion.

## BDD

Escenarios generados en:

- `tests/features/US-5.1.1-crear-torneo-ui.feature`

No se agregan step definitions ejecutables porque el proyecto no tiene harness E2E/browser
frontend configurado.
