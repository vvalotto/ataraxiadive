# Estrategia de Tests - US-5.1.7

## Alcance

US-5.1.7 modifica exclusivamente comportamiento de presentacion en
`DetalleTorneoPage`: politica de tabs por estado, reset de `activeTab` y vista terminal
para `CANCELADO`.

## Unit tests

**Estado:** waiver.

El frontend no tiene harness de tests unitarios configurado para React
(Vitest/Jest/Testing Library). Agregarlo para este fix puntual ampliaria el alcance del
ajuste post-UAT.

## Validacion aplicada

- TypeScript via `npm run build`.
- ESLint via `npm run lint`.
- Feature BDD materializado en `tests/features/US-5.1.7-politica-tabs.feature`.
- Validacion manual UI contra escenarios de la spec.

## Riesgo residual

La regla queda validada por compilacion y revision manual, no por una prueba browser
automatizada. Este riesgo es aceptado para INC-5.1-ADJ porque el repo aun no dispone de
harness UI.
