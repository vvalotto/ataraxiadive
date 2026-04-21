# Estrategia de Tests - US-5.1.8

## Alcance

US-5.1.8 modifica `TorneoCompetenciasPage` para componer disciplinas configuradas
del torneo con competencias materializadas.

## Unit tests

**Estado:** waiver.

El frontend no tiene harness de tests unitarios React configurado
(Vitest/Jest/Testing Library). La logica agregada queda validada por TypeScript,
ESLint y revision manual contra la feature BDD.

## Validacion aplicada

- TypeScript via `npm run build`.
- ESLint via `npm run lint`.
- Feature BDD materializado en `tests/features/US-5.1.8-componer-competencias.feature`.

## Riesgo residual

No hay prueba automatizada que monte la page con mocks de React Query/Router. El riesgo
es aceptado para INC-5.1-ADJ por ausencia de harness UI en el repo.
