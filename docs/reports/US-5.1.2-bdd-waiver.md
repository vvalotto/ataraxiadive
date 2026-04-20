# US-5.1.2 — BDD Validation Waiver

## Feature

- `tests/features/US-5.1.2-gestion-fases-torneo.feature`

## Estado

Escenarios BDD generados y persistidos en disco. No se ejecutan automaticamente en esta US
porque el proyecto no tiene steps ni harness E2E/browser para flujos React.

## Cobertura Funcional del Feature

- Estado `CREADO` muestra abrir inscripcion y cancelar.
- Transicion exitosa `CREADO` a inscripcion.
- Retroceso `EJECUCION` a preparacion.
- Cancelacion con confirmacion.
- Error backend `409` mostrado inline sin recargar estado local.
- Estados terminales sin acciones de fase.

## Evidencia Sustitutiva

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
