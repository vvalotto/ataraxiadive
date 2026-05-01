# Estrategia de Tests - US-5.1.9

## Alcance

US-5.1.9 modifica `JuecesPanel` y `TablaJueces` para bloquear la asignacion de jueces
cuando la disciplina no tiene competencia con grilla generada.

## Unit tests

**Estado:** waiver.

El frontend no tiene harness de tests unitarios React configurado
(Vitest/Jest/Testing Library). La regla queda validada por TypeScript, ESLint y
revision manual contra la feature BDD.

## Validacion aplicada

- TypeScript via `npm run build`.
- ESLint via `npm run lint`.
- Feature BDD materializado en `tests/features/US-5.1.9-bloquear-jueces-sin-grilla.feature`.

## Riesgo residual

No hay prueba automatizada que monte `JuecesPanel` con mocks de React Query/Router.
