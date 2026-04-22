# US-ADJ-8.2 — Reporte de Implementacion

**Fecha:** 2026-04-22
**Sprint:** SP-ADJ-08
**Estado:** Implementada

## Resumen

Se implementaron restricciones operativas para el flujo organizador:

- el selector de grilla ahora usa solo disciplinas configuradas en el torneo actual;
- la accion `Pasar a premiacion` se bloquea si quedan disciplinas sin competencia finalizada;
- el backend tambien rechaza `EJECUCION -> PREMIACION` cuando la app esta cableada con
  la precondicion cross-BC desde `src/app.py`.

## Cambios principales

- `GrillaPanel` consume `listarDisciplinasTorneo(torneoId)` y elimina el selector global.
- `DetalleTorneoPage` calcula disciplinas pendientes cruzando Torneo + Competencia.
- `AccionesPanel` cambia `Iniciar premiacion` por `Pasar a premiacion`, bloquea la accion
  y muestra el detalle de pendientes.
- `torneo.api.router` permite configurar una precondicion async antes de iniciar premiacion.
- `src/app.py` cablea la precondicion con Torneo y Competencia.
- Nueva excepcion `PremiacionNoPermitida` con respuesta HTTP 409.

## Validaciones

- `./.venv/bin/pytest tests/unit/torneo/application/test_premiacion_precondition.py tests/unit/torneo/application/test_transiciones_handlers.py tests/integration/torneo/test_premiacion_precondicion.py` — OK, `13 passed`.
- `npm run lint` — OK.
- `npm run build` — OK.

## Fases acotadas

- BDD automatizado UI omitido: no existe harness browser/DOM en el repo.
- Se dejo feature BDD en `tests/features/US-ADJ-8.2-restringir-operaciones-torneo-fase.feature`.
- Quality gates acotados al alcance modificado.

## Notas

- La regla cross-BC no se puso en `torneo/domain`; queda cableada en composition root
  para conservar la frontera de bounded contexts.
- Disciplinas configuradas sin competencia cuentan como pendientes de cierre.
