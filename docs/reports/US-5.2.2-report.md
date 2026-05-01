# US-5.2.2 — Reporte de Implementacion

**Fecha:** 2026-04-22
**Incremento:** INC-5.2 — Ejecucion por Disciplina
**Estado:** Implementada

## Resumen

Se implemento la finalizacion manual de una prueba por disciplina desde el panel
del organizador, manteniendo la convivencia con el cierre automatico P-08.

## Cambios principales

- Nuevo comando `FinalizarCompetenciaManualCommand`.
- Nuevo handler `FinalizarCompetenciaManualHandler`.
- Nuevo endpoint `POST /competencia/{competencia_id}/finalizar`.
- `CompetenciaFinalizada` distingue `origen="manual"` y `origen="automatico"`.
- `EjecucionPanel` agrega la accion `Finalizar prueba` con bloqueo por
  performances pendientes.

## Validaciones

- `./.venv/bin/pytest tests/unit/competencia/domain/test_competencia_finalizar.py tests/unit/competencia/application/test_p08_finalizacion.py tests/unit/competencia/application/test_finalizar_competencia_manual.py tests/integration/competencia/test_competencia_finalizada_integration.py` — OK, `25 passed`.
- `npm run build` — OK.
- `npm run lint` — OK.

## Notas

- El backend es la fuente de verdad: aunque la UI bloquee el boton con pendientes,
  el endpoint vuelve a validar con `PerformancesEstadoPort`.
- La competencia ya finalizada se trata como no-op controlado para evitar doble
  emision de `CompetenciaFinalizada`.
