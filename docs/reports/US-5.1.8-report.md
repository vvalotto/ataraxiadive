# Reporte de Implementacion - US-5.1.8

## Resumen

Se corrigio `TorneoCompetenciasPage` para mostrar una card por disciplina configurada
del torneo, aunque la competencia aun no exista en `competencia.db`.

## Componentes modificados

- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
  - Agrega query a `listarDisciplinasTorneo(torneoId)`.
  - Mantiene `fetchCompetenciasPorTorneo(torneoId)` como fuente secundaria.
  - Compone disciplinas y competencias por codigo `disciplina`.
  - Renderiza `Competencia pendiente` cuando no existe `competencia_id`.
  - Deshabilita `Ver auditoria` para disciplinas sin competencia.

## Artefactos

- Spec: `docs/specs/sp5/US-5.1.8.md`
- Plan: `docs/plans/sp5/US-5.1.8-plan.md`
- Feature: `tests/features/US-5.1.8-componer-competencias.feature`
- Test strategy: `docs/reports/US-5.1.8-test-strategy.md`
- Integracion: `docs/reports/US-5.1.8-integration.md`
- BDD validation: `docs/reports/US-5.1.8-bdd-validation.md`

## Validacion

- `npm run build` - OK
- `npm run lint` - OK

## Criterios de aceptacion

- En estados tempranos, `Ver competencias` muestra disciplinas aunque no existan competencias.
- `Ver auditoria` queda habilitado solo cuando existe `competencia_id`.
- La pantalla vacia queda reservada para torneos sin disciplinas configuradas.
- Errores de carga de disciplinas o competencias muestran mensaje de error.

## Riesgo residual

No hay harness automatizado de UI/browser para ejecutar los escenarios BDD. La cobertura
automatizada disponible para esta US queda limitada a TypeScript y ESLint.
