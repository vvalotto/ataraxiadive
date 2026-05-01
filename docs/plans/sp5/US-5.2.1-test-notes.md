# US-5.2.1 — Notas de Tests

**Fecha:** 2026-04-22

---

## Fase 4 — Tests Unitarios

El frontend no tiene harness unitario configurado:

- no existe `vitest.config.*`;
- `frontend/package.json` no define script `test`;
- las dependencias no incluyen runner unitario de React.

Por el ajuste local de `implement-us` para producto `frontend`, la validacion unitaria se sustituye
por compilacion TypeScript y lint:

- `npm run build` — OK
- `npm run lint` — OK

No se agrega Vitest/Testing Library en esta US para evitar ampliar el alcance del incremento.

---

## Fase 5 — Integracion

La integracion cubierta por esta US es cliente HTTP + React Query:

- `listarDisciplinasTorneo()` como fuente primaria de disciplinas.
- `fetchCompetenciasPorTorneo()` como enrichment de competencias existentes.
- `fetchEstadoCompetencia()` y `fetchProgresoCompetencia()` para maestro.
- `fetchGrillaCompetencia()`, `fetchPerformanceActual()` y `fetchProximasPerformances()` para detalle.
- `iniciarCompetencia()` para la accion de habilitacion.

La validacion automatizada disponible es `npm run build`, que confirma tipos y wiring de imports.

---

## Fase 6 — BDD/UI

Los escenarios BDD estan en:

- `tests/features/US-5.2.1-ejecucion-disciplinas.feature`

No existe harness automatizado de browser para ejecutar estos escenarios contra la UI. La validacion
BDD queda como manual/UI, consistente con el ajuste local de `implement-us`.
