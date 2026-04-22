# US-ADJ-8.2 — Notas de implementacion

**Fecha:** 2026-04-22
**Fase:** 8 — Documentacion

## Cambios realizados

- `GrillaPanel`
  - consulta `GET /torneos/{torneo_id}/disciplinas`;
  - elimina la lista global hardcodeada como fuente del selector;
  - muestra estados de carga, error y vacio para disciplinas del torneo.

- `DetalleTorneoPage` + `AccionesPanel`
  - calculan disciplinas pendientes cruzando disciplinas configuradas, competencias y estado;
  - renombran la accion `Iniciar premiacion` a `Pasar a premiacion`;
  - bloquean la accion con detalle de disciplinas no finalizadas.

- Backend `torneo`
  - agrega `PremiacionNoPermitida`;
  - expone callback configurable previo a `IniciarPremiacionHandler`;
  - `src/app.py` cablea la precondicion leyendo Torneo + Competencia.

## Decision de frontera BC

La validacion de premiacion necesita datos de `torneo` y `competencia`. Para no acoplar
`torneo/domain` con `competencia`, la regla cross-BC se implemento en el composition root:

1. `torneo.api.router` define un callback opcional.
2. `src/app.py` construye el callback con repositorios/adaptadores reales.
3. El dominio de Torneo conserva solo la maquina de estados local.

## Validaciones

- `./.venv/bin/pytest tests/unit/torneo/application/test_premiacion_precondition.py tests/unit/torneo/application/test_transiciones_handlers.py tests/integration/torneo/test_premiacion_precondicion.py` — OK, `13 passed`.
- `npm run lint` — OK.
- `npm run build` — OK.

## Fases acotadas

- BDD UI no ejecutado por falta de harness browser; feature creado como especificacion.
- Quality gates acotados a cambios de la US.
