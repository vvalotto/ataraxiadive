# Reporte de Implementacion - US-5.1.7

## Resumen

Se implemento la politica de tabs por fase en `DetalleTorneoPage` y el tratamiento
especial para torneos `CANCELADO`.

## Componentes modificados

- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
  - `TABS_POR_ESTADO` tipado por `EstadoTorneo`.
  - Tabs visibles pero deshabilitadas para estados donde no corresponden.
  - `TorneoOperativoPanel` remonta con `key={estado}` para resetear la tab a `Detalle` cuando cambia la fase.
  - `activeTabActual` derivado para evitar renderizar paneles incompatibles.
  - Vista terminal de `CANCELADO` sin tabs, sin `Ver competencias`, sin paneles hijos y sin `AccionesPanel`.
- `frontend/eslint.config.js`
  - Exclusion de `.vite` para evitar lint sobre cache/deps generados.

## Artefactos

- Spec: `docs/specs/sp5/US-5.1.7.md`
- Plan: `docs/plans/sp5/US-5.1.7-plan.md`
- Feature: `tests/features/US-5.1.7-politica-tabs.feature`
- Test strategy: `docs/reports/US-5.1.7-test-strategy.md`
- Integracion: `docs/reports/US-5.1.7-integration.md`
- BDD validation: `docs/reports/US-5.1.7-bdd-validation.md`

## Validacion

- `npm run build` - OK
- `npm run lint` - OK

## Criterios de aceptacion

- `INSCRIPCION_ABIERTA` habilita solo `Detalle` e `Inscriptos`.
- `PREPARACION` habilita hasta `Jueces`; `Ejecucion` queda deshabilitada.
- Tabs deshabilitadas no cambian la vista activa.
- `CANCELADO` muestra resumen terminal y no renderiza informacion operativa.
- Si una tab activa queda fuera de la politica del estado actual, la vista efectiva vuelve a `Detalle`.

## Riesgo residual

No hay harness automatizado de UI/browser para ejecutar los escenarios BDD. La cobertura
automatizada disponible para esta US queda limitada a TypeScript y ESLint.
