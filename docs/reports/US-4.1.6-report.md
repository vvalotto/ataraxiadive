# Reporte de Implementación — US-4.1.6
## Aliviar handlers de `competencia`

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se redujo la orquestación repetida en los handlers principales de `competencia`
sin cambiar la firma pública de `handle()` ni las excepciones observables.

La extracción quedó acotada a un helper interno de módulo, evitando crear una
clase de servicio artificial. Los handlers siguen siendo dueños del caso de uso,
pero delegan carga de streams, reconstitución y persistencia de eventos.

## Cambios implementados

### Application

- `src/competencia/application/commands/_handler_utils.py`
  - centraliza `build_*_stream_id`
  - centraliza carga obligatoria de streams
  - centraliza reconstitución de `Performance` y `Competencia`
  - centraliza persistencia de eventos pendientes
- `src/competencia/application/commands/asignar_tarjeta.py`
  - extrae validación de penalizaciones
  - delega carga/persistencia al helper
- `src/competencia/application/commands/generar_grilla.py`
  - delega reconstitución y persistencia al helper
- `src/competencia/application/commands/registrar_ap.py`
  - separa validación de unidad, estado de competencia y duplicado
- `src/competencia/application/commands/llamar_atleta.py`
  - separa validación de competencia en ejecución y conflicto de andarivel

## Validación ejecutada

- `.venv/bin/pytest tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/unit/competencia/application/test_generar_grilla_handler.py tests/unit/competencia/application/test_registrar_ap_handler.py tests/unit/competencia/application/test_llamar_atleta_handler.py -q`
  - `36 passed`
- `.venv/bin/pytest tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_generar_grilla_integration.py tests/integration/competencia/test_registrar_ap_integration.py tests/integration/competencia/test_llamar_atleta_integration.py -q`
  - `27 passed`

## Quality Gates

- `designreviewer`
  - comando: `.venv/bin/designreviewer src/competencia/application/commands/asignar_tarjeta.py src/competencia/application/commands/generar_grilla.py src/competencia/application/commands/registrar_ap.py src/competencia/application/commands/llamar_atleta.py src/competencia/application/commands/_handler_utils.py --config pyproject.toml`
  - resultado: `0 blocking`, `13 warning`
- `codeguard`
  - reporte: `quality/reports/codeguard/US-4.1.6-quality.json`
  - resumen: `0 errors`, `8 warnings`, `95 infos`

## Riesgos residuales

- Persisten warnings de `FeatureEnvy` y `LongMethod` en handlers, aunque ya no son bloqueantes.
- El helper interno reduce repetición mecánica, pero no elimina toda la deuda de diseño; parte de esa deuda puede requerir rediseño más profundo de comandos/puertos.
- No fue necesario tocar contratos HTTP ni documentación del modelo de dominio porque el refactor es puramente de application layer.
