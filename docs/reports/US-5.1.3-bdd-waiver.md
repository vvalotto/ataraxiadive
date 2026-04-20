# US-5.1.3 — BDD Validation Waiver

## Feature

- `tests/features/US-5.1.3-vista-inscriptos-ap.feature`

## Estado

Escenarios BDD generados y persistidos en disco. No se ejecutan automaticamente en esta US
porque el proyecto no tiene steps ni harness E2E/browser para flujos React.

## Cobertura Funcional del Feature

- Lista de inscriptos con AP mixto.
- Filtro por disciplina.
- Estado vacio sin inscriptos.
- Atleta multidisciplina con AP parcial.

## Evidencia Sustitutiva

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
