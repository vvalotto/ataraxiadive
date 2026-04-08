# Plan de Implementación — US-4.1.6
## Aliviar handlers de `competencia`

**Branch actual:** `feature/inc-4.1-correcciones-dominio`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `3h 15min`
**Estado:** `Completado`

## Objetivo

Reducir `FeatureEnvy` y `LongMethod` en los handlers de `competencia`, separando
carga de aggregates, validaciones repetidas y persistencia de eventos sin cambiar
la firma pública de `handle()` ni las excepciones observables.

## Componentes a crear o modificar

### Competencia / Application

- `src/competencia/application/commands/asignar_tarjeta.py`
- `src/competencia/application/commands/generar_grilla.py`
- `src/competencia/application/commands/registrar_ap.py`
- `src/competencia/application/commands/llamar_atleta.py`
- `src/competencia/application/commands/_handler_utils.py`

### Tests

- `tests/unit/competencia/application/test_asignar_tarjeta_handler.py`
- `tests/unit/competencia/application/test_generar_grilla_handler.py`
- `tests/unit/competencia/application/test_registrar_ap_handler.py`
- `tests/unit/competencia/application/test_llamar_atleta_handler.py`
- `tests/integration/competencia/test_asignar_tarjeta_integration.py`
- `tests/integration/competencia/test_generar_grilla_integration.py`
- `tests/integration/competencia/test_registrar_ap_integration.py`
- `tests/integration/competencia/test_llamar_atleta_integration.py`

## Tareas

1. **[T1]** Relevar secuencias repetidas en handlers y fijar qué helpers pueden compartirse sin crear un servicio artificial. `20 min`
2. **[T2]** Crear helpers de carga/reconstitución/persistencia para streams de `Performance` y `Competencia`. `40 min`
3. **[T3]** Refactorizar `AsignarTarjetaHandler` y `LlamarAtletaHandler` para dejar `handle()` como orquestación breve. `35 min`
4. **[T4]** Refactorizar `RegistrarAPHandler` y `GenerarGrillaHandler` separando validaciones y persistencia. `40 min`
5. **[T5]** Ajustar y ampliar tests unitarios/integración donde haga falta para cubrir helpers y preservar excepciones/orden de llamadas. `35 min`
6. **[T6]** Ejecutar quality gates y documentar resultados. `25 min`

## Decisiones de implementación

- El helper compartido será un módulo interno de `application/commands/`; no una clase nueva.
- Los handlers seguirán siendo los dueños del caso de uso; los helpers solo concentran mecánica repetida.
- La construcción de `stream_id`, la carga de eventos y la persistencia de eventos pendientes deben salir de los `handle()` más cargados.
- Las validaciones específicas del caso de uso se mantendrán en cada handler, no en el helper genérico.

## Riesgos

1. Un helper demasiado genérico puede introducir una abstracción peor que el problema original.
2. Si cambia el orden de validaciones, pueden variar excepciones o llamadas esperadas por los tests.
3. `GenerarGrillaHandler` usa aggregate distinto (`Competencia`), así que no conviene forzar el mismo helper exacto que los handlers de `Performance`.

## Criterio de salida

- Tests unitarios e integración relevantes en verde
- `designreviewer` sin bloqueos en los handlers refactorizados
- `handle()` de los handlers prioritarios reducido a una orquestación legible

## Cierre de ejecución

- Refactor completado:
  - helper interno compartido en `application/commands/_handler_utils.py`
  - extracción de carga/reconstitución/persistencia fuera de `handle()`
  - separación de validaciones específicas en métodos privados por handler
- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/unit/competencia/application/test_generar_grilla_handler.py tests/unit/competencia/application/test_registrar_ap_handler.py tests/unit/competencia/application/test_llamar_atleta_handler.py -q` → `36 passed`
  - `.venv/bin/pytest tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_generar_grilla_integration.py tests/integration/competencia/test_registrar_ap_integration.py tests/integration/competencia/test_llamar_atleta_integration.py -q` → `27 passed`
- Quality gates:
  - `.venv/bin/designreviewer ... --config pyproject.toml` → `0 blocking`, `13 warning`
  - `.venv/bin/codeguard ... > quality/reports/codeguard/US-4.1.6-quality.json` → `0 errors`, `8 warnings`
