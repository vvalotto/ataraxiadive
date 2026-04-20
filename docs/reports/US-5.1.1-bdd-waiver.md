# US-5.1.1 — BDD Validation Waiver

## Feature

- `tests/features/US-5.1.1-crear-torneo-ui.feature`

## Estado

Escenarios BDD generados y persistidos en disco. No se ejecutan automaticamente en esta US
porque el proyecto no tiene steps ni harness E2E/browser para flujos React.

## Cobertura Funcional del Feature

- Creacion exitosa con disciplinas.
- Validacion frontend por fechas incoherentes.
- Validacion frontend por nombre vacio.
- Validacion frontend por ausencia de disciplinas.
- Error de backend al crear torneo.
- Error de backend al asignar disciplinas despues de crear torneo.

## Evidencia Sustitutiva

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
