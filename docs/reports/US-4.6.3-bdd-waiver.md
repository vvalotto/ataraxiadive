# Waiver BDD — US-4.6.3
## UI de auditoria del organizador

**Fecha:** `2026-04-16`
**Decisión:** `BDD no automatizado`

## Justificación

`US-4.6.3` agrega comportamiento observable en frontend y por eso se generó el
feature `tests/features/US-4.6.3-ui-auditoria-organizador.feature`, pero el
repositorio no cuenta hoy con harness automatizado para UI React
(`vitest`, `playwright` o equivalente) ni con step definitions reutilizables
para navegación del organizador.

Implementar esa infraestructura en esta US hubiera desviado el alcance hacia una
base de testing frontend transversal en lugar de cerrar la funcionalidad de
auditoría del incremento.

## Validación sustitutiva

- Tests unitarios backend de `ObtenerEstadoCompetenciaHandler`
- Tests backend existentes de `CompetenciaFinalizada` y persistencia de hash
- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- Quality gate focalizado con `codeguard` sobre backend tocado

## Alcance del waiver

- Se mantiene Fase 1 con generación del `.feature`
- Se reemplaza la automatización de Fase 6 por validación backend + build/lint frontend
- No exime Fases 7, 8 y 9
