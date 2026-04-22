# US-5.2.2 — Fase 0

**Fecha:** 2026-04-22
**Incremento:** INC-5.2 — Ejecucion por Disciplina
**US:** Finalizacion manual de prueba por disciplina

## Objetivo

Implementar el cierre manual de una disciplina desde el panel del organizador,
permitiendo la accion solo cuando la competencia esta en ejecucion y todas sus
performances estan cerradas.

El cierre manual debe convivir con P-08, que sigue cerrando automaticamente al
registrar DNS o tarjeta final.

## Fuentes revisadas

- `docs/specs/sp5/US-5.2.2.md`
- `docs/plans/sp5/PLAN-SP5.md`
- `docs/plans/WORKFLOW-DESARROLLO.md`
- `src/competencia/application/_p08_finalizacion.py`
- `src/competencia/domain/aggregates/competencia.py`
- `src/competencia/domain/events/competencia_finalizada.py`
- `frontend/src/components/organizador/EjecucionPanel.tsx`
- `frontend/src/api/competencia.ts`

## Estado inicial observado

- El aggregate `Competencia` ya tiene `finalizar()`.
- P-08 usa `trigger_finalizacion_si_corresponde()` y calcula el hash SHA-256.
- `CompetenciaFinalizada` persiste `hash_sha256`, pero no distingue origen.
- No existe endpoint `POST /competencia/{competencia_id}/finalizar`.
- El frontend muestra detalle maestro-detalle, pero no accion `Finalizar prueba`.

## Decisiones de alcance

- Reutilizar `Competencia.finalizar()` para cierre manual y automatico.
- Extender `CompetenciaFinalizada` con `origen` y `finalizada_por`, manteniendo
  compatibilidad con eventos previos sin esos campos.
- Agregar `FinalizarCompetenciaManualCommand` y handler.
- El frontend habilita la accion solo con `completadas == total`, pero el backend
  conserva la validacion final.

## Riesgos

- Cambiar el payload de `CompetenciaFinalizada` puede impactar consumidores de
  resultados/notificaciones si no se mantiene backward compatibility.
- Si la competencia ya fue cerrada automaticamente antes de que el organizador
  pulse la accion, el backend debe responder sin duplicar eventos.
