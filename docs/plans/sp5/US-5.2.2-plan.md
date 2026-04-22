# US-5.2.2 — Plan de Implementacion

**Fecha:** 2026-04-22
**US:** Finalizacion manual de prueba por disciplina

## Tareas

1. Dominio
   - Extender `CompetenciaFinalizada` con `origen` y `finalizada_por`.
   - Ajustar `Competencia.finalizar()` para recibir origen de cierre.
   - Mantener `from_payload()` compatible con eventos historicos.

2. Aplicacion
   - Agregar `FinalizarCompetenciaManualCommand`.
   - Reutilizar `PerformancesEstadoPort`, `CalculadorHashCompetencia` y
     `Competencia.finalizar()`.
   - Rechazar cierre si quedan pendientes o si no hay performances.
   - Manejar competencia ya finalizada como no-op controlado.
   - Marcar P-08 con `origen="automatico"`.

3. API
   - Agregar body `FinalizarCompetenciaBody`.
   - Agregar endpoint `POST /competencia/{competencia_id}/finalizar`.
   - Usar `OrganizadorDep` y `user["email"]` como `solicitado_por`.

4. Frontend
   - Agregar cliente `finalizarCompetencia()`.
   - Mostrar accion `Finalizar prueba` en detalle de disciplina en ejecucion.
   - Habilitar solo si `progreso.total > 0` y `completadas == total`.
   - Mostrar bloqueo con cantidad de pendientes.
   - Invalidar queries tras cierre.

5. Tests y documentacion
   - Agregar feature BDD de `US-5.2.2`.
   - Agregar tests unitarios de dominio/handler/P-08.
   - Agregar notas y reporte de cierre.
   - Ejecutar tests backend focalizados y build frontend.

## Criterio de listo

- El cierre manual persiste `CompetenciaFinalizada` con `origen="manual"`.
- El cierre automatico persiste `origen="automatico"`.
- El endpoint responde 204 al cerrar o ante no-op controlado de competencia ya
  finalizada.
- Con pendientes, backend responde 409 y frontend no dispara la accion.
- `npm run build` y tests focalizados pasan.
