# Reporte de Implementación — US-4.1.5
## Descomponer aggregate `Performance`

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se descompuso `Performance` sin alterar su interfaz pública ni los eventos emitidos.
El aggregate ahora delega:

- cálculo de RP final a `RPFinal`
- resolución de tarjeta y compatibilidad legacy a `ResolucionTarjeta`
- reconstitución y factories de eventos a helpers del aggregate

El resultado observable se preservó y `designreviewer` dejó de marcar bloqueos
críticos sobre `Performance`.

## Cambios implementados

### Dominio

- `src/competencia/domain/value_objects/rp_final.py`
  - encapsula RP medido, RP penalizado y clamp a cero
- `src/competencia/domain/value_objects/resolucion_tarjeta.py`
  - centraliza payload de tarjeta, penalizaciones y reconstrucción legacy
- `src/competencia/domain/aggregates/performance_state.py`
  - extrae reconstitución y aplicación de eventos
- `src/competencia/domain/aggregates/performance_events.py`
  - extrae factories de eventos para reducir acoplamiento del aggregate
- `src/competencia/domain/aggregates/performance.py`
  - queda como orquestador de invariantes y estado, sin lógica incidental de serialización

### Tests

- `tests/unit/competencia/domain/test_performance.py`
  - agrega cobertura de corrección de resultado con penalizaciones acumuladas
- `tests/integration/competencia/test_corregir_resultado_integration.py`
  - agrega flujo completo de corrección sobre `BlancaConPenalizaciones`

## Validación ejecutada

- `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py -q`
  - `69 passed`
- `.venv/bin/pytest tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_corregir_resultado_integration.py -q`
  - `13 passed`
- `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py tests/integration/competencia/test_asignar_tarjeta_integration.py tests/integration/competencia/test_corregir_resultado_integration.py -q`
  - `82 passed`

## Quality Gates

- `designreviewer`
  - comando: `.venv/bin/designreviewer src/competencia/domain/aggregates/performance.py src/competencia/domain/aggregates/performance_state.py src/competencia/domain/aggregates/performance_events.py src/competencia/domain/value_objects/resolucion_tarjeta.py src/competencia/domain/value_objects/rp_final.py --config pyproject.toml`
  - resultado: `0 blocking`, `22 warning`
- `codeguard`
  - reporte: `quality/reports/codeguard/US-4.1.5-quality.json`
  - resumen: `0 errors`, `5 warnings`, `132 infos`

## Riesgos residuales

- Persisten warnings de método largo y data clumps en `Performance` y helpers, pero ya no son bloqueantes.
- `ResolucionTarjeta` mantiene deuda de diseño por feature envy; quedó encapsulada, pero conviene revisarla junto con `US-4.1.6`.
- No se actualizaron documentos de modelo de dominio porque este refactor no introduce conceptos ubicuos nuevos.
