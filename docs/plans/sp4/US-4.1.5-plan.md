# Plan de Implementación — US-4.1.5
## Descomponer aggregate `Performance`

**Branch actual:** `feature/inc-4.1-correcciones-dominio`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `3h 00min`
**Estado:** `Completado`

## Objetivo

Extraer del aggregate `Performance` la resolución de tarjeta y el cálculo de RP final
para reducir la métrica de GodObject sin modificar el contrato observable del dominio.

## Componentes a crear o modificar

### Competencia / Domain

- `src/competencia/domain/aggregates/performance.py`
- `src/competencia/domain/aggregates/performance_state.py`
- `src/competencia/domain/aggregates/performance_events.py`
- `src/competencia/domain/value_objects/resolucion_tarjeta.py`
- `src/competencia/domain/value_objects/rp_final.py`
- `src/competencia/domain/value_objects/__init__.py`

### Tests

- `tests/unit/competencia/domain/test_performance.py`
- `tests/integration/competencia/test_asignar_tarjeta_integration.py`
- `tests/integration/competencia/test_corregir_resultado_integration.py`

## Tareas

1. **[T1]** Relevar flujo actual de `asignar_tarjeta()`, `_apply_tarjeta_asignada()` y `corregir_resultado()` para fijar puntos exactos de extracción. `20 min`
2. **[T2]** Crear VO `RPFinal` para encapsular cálculo de RP medido/penalizado y clamp a cero. `35 min`
3. **[T3]** Crear VO `ResolucionTarjeta` para centralizar tipo, motivos, blackout, penalizaciones y payload del evento. `45 min`
4. **[T4]** Refactorizar `Performance` para delegar en los nuevos VOs, dejando `asignar_tarjeta()` y `corregir_resultado()` como orquestadores breves. `40 min`
5. **[T5]** Ajustar y ampliar tests unitarios e integración para cubrir preservación de payload, RP penalizado y reconstitución legacy. `35 min`
6. **[T6]** Ejecutar quality gates y documentar resultados de la US. `25 min`

## Decisiones de implementación

- Los nuevos componentes vivirán en `competencia/domain/value_objects/`; no se crean servicios de aplicación.
- `TarjetaAsignacion` sigue siendo el punto de validación de invariantes de entrada.
- `ResolucionTarjeta` encapsulará el resultado derivado de una `TarjetaAsignacion` más el RP medido.
- La compatibilidad legacy se mantiene, pero se moverá a helpers/VOs privados para sacar ruido del aggregate.
- No se modifica la firma pública de `Performance.asignar_tarjeta()` ni de `Performance.corregir_resultado()`.

## Riesgos

1. Cambiar el payload de `TarjetaAsignada` rompería reconstitución y tests de integración.
2. Mover compatibilidad legacy al lugar equivocado puede dispersar demasiado la lógica de rehidratación.
3. Si el refactor crea demasiados helpers dentro del aggregate, podría bajar longitud pero no cohesión real.

## Criterio de salida

- Tests unitarios e integración relevantes en verde
- `Performance` sin regresiones observables
- `designreviewer` sin bloqueo sobre el aggregate refactorizado

## Cierre de ejecución

- Refactor completado:
  - cálculo de RP final extraído a `RPFinal`
  - resolución de tarjeta y compatibilidad legacy extraídas a `ResolucionTarjeta`
  - reconstitución y factories de eventos movidas a helpers de aggregate
- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py -q` → `69 passed`
  - `.venv/bin/pytest tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_corregir_resultado_integration.py -q` → `13 passed`
  - `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_corregir_resultado_integration.py -q` → `82 passed`
- Quality gates:
  - `.venv/bin/designreviewer ... --config pyproject.toml` → `0 blocking`, `22 warning`
  - `.venv/bin/codeguard ... > quality/reports/codeguard/US-4.1.5-quality.json` → `0 errors`, `5 warnings`
