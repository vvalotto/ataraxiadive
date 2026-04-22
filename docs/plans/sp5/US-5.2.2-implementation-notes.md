# US-5.2.2 — Notas de Implementacion

**Fecha:** 2026-04-22
**Fase:** 3 — Implementacion

## Enfoque

La US agrega un camino manual para el mismo cierre de dominio que ya existia por
P-08. La regla central es no duplicar semantica: la accion del organizador debe
terminar en `Competencia.finalizar()`.

## Cambios esperados

- `CompetenciaFinalizada`
  - nuevo `origen`;
  - nuevo `finalizada_por` opcional;
  - compatibilidad con eventos previos sin esos campos.

- `Competencia.finalizar()`
  - valida estado `EnEjecucion`;
  - valida pendientes;
  - emite `CompetenciaFinalizada` con origen.

- `FinalizarCompetenciaManualHandler`
  - consulta estado de performances;
  - calcula hash;
  - reconstituye aggregate;
  - ejecuta cierre con origen `manual`.

- `EjecucionPanel`
  - boton `Finalizar prueba`;
  - bloqueo textual si quedan pendientes;
  - recarga de estado y detalle despues del cierre.

## Validaciones a registrar al cierre

- Tests unitarios de dominio/aplicacion — OK.
- Tests de integracion focalizados de CompetenciaFinalizada — OK.
- Build frontend — OK.
- Lint frontend — OK.

## Cambios realizados

- `CompetenciaFinalizada`
  - agrega `origen`;
  - agrega `finalizada_por`;
  - mantiene compatibilidad: eventos historicos sin `origen` se leen como
    `automatico`.

- `Competencia.finalizar()`
  - acepta origen y solicitante opcional;
  - conserva la validacion de performances pendientes.

- `FinalizarCompetenciaManualHandler`
  - valida competencia en `EnEjecucion`;
  - retorna no-op si ya esta `Finalizada`;
  - rechaza con `CompetenciaNoFinalizable` si quedan pendientes;
  - calcula hash SHA-256 igual que P-08;
  - persiste `CompetenciaFinalizada(origen="manual")`.

- `P-08`
  - explicita `origen="automatico"`.

- `EjecucionPanel`
  - muestra `Finalizar prueba` en disciplinas en ejecucion;
  - habilita solo con `total > 0` y `completadas == total`;
  - muestra bloqueo con pendientes;
  - invalida queries tras cerrar.
