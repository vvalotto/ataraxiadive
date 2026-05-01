# US-5.1.3 — Estrategia de Tests

## Tipo de US

Frontend React/Vite para visualizar inscriptos y estado AP por disciplina.

## Unit Tests

No se agregan tests unitarios automatizados de componentes porque el frontend no tiene runner
unitario configurado en `package.json` (no hay Vitest/Jest/Testing Library). Introducirlo en
esta US ampliaria el alcance tecnico.

Validacion aplicada:

- `npm run build`: TypeScript + bundle Vite.
- `npx eslint src`: lint acotado a codigo fuente.

## Integracion

La integracion cubierta por la implementacion cruza datos de:

- `GET /registro/torneos/{torneo_id}/inscriptos`
- `GET /registro/atletas/{atleta_id}`
- `GET /competencia?torneo_id={id}`
- `GET /competencia/{competencia_id}/grilla?disciplina={disciplina}`

## BDD

Escenarios generados en:

- `tests/features/US-5.1.3-vista-inscriptos-ap.feature`

No se agregan step definitions ejecutables porque el proyecto no tiene harness E2E/browser
frontend configurado.
