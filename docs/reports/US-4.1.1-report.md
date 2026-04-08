# Reporte de Implementación — US-4.1.1
## Motivos de tarjeta roja con catálogo formal

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`
**Tiempo total registrado:** `17 min`

## Resumen

Se reemplazó el uso de string libre para tarjeta roja por un catálogo formal
`MotivoDQ`, manteniendo motivo libre solo para tarjeta amarilla y agregando
compatibilidad de lectura para eventos históricos `TarjetaAsignada` con
`motivo="black-out"`.

## Cambios implementados

### Dominio

- Nuevo VO `src/competencia/domain/value_objects/motivo_dq.py`
- Nuevas excepciones:
  - `MotivoDQObligatorio`
  - `DistanciaBlackoutNoAplica`
- Refactor de `TarjetaAsignacion`:
  - roja usa `motivo_dq`
  - amarilla usa `motivo_texto`
  - `distancia_blackout` solo aplica a motivos BKO
- Refactor de `Performance.asignar_tarjeta()` y reconstitución histórica
- Refactor de `TarjetaAsignada` para emitir:
  - `motivo_dq_codigo`
  - `motivo_texto`
  - `distancia_blackout`

### Aplicación

- `AsignarTarjetaCommand` y `AsignarTarjetaHandler` ajustados al nuevo contrato

### BDD y tests

- Nuevo feature:
  - `tests/features/US-4.1.1-motivos-tarjeta-roja.feature`
- Nuevos steps:
  - `tests/features/steps/test_US_4_1_1_steps.py`
- Actualización de regresiones existentes:
  - `tests/features/US-1.2.4-asignar-tarjeta.feature`
  - `tests/features/US-1.4.1-blackout-con-distancia.feature`
  - `tests/features/steps/asignar_tarjeta_steps.py`
  - `tests/features/steps/blackout_con_distancia_steps.py`
  - `tests/unit/competencia/domain/test_performance.py`
  - `tests/unit/competencia/application/test_asignar_tarjeta_handler.py`
  - `tests/integration/competencia/test_asignar_tarjeta_integration.py`

### Documentación

- `docs/reports/US-4.1.1-context.md`
- `docs/plans/sp4/US-4.1.1-plan.md`
- `docs/design/domain-model.md`

## Validación ejecutada

- `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py`
  - `65 passed`
- `.venv/bin/pytest tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/integration/competencia/test_asignar_tarjeta_integration.py`
  - `20 passed`
- `.venv/bin/pytest tests/features/steps/test_US_4_1_1_steps.py`
  - `7 passed`
- `.venv/bin/pytest tests/features/steps/asignar_tarjeta_steps.py tests/features/steps/blackout_con_distancia_steps.py`
  - `10 passed`
- Suite consolidada:
  - `102 passed`

## Quality Gates

- `designreviewer src/competencia --config pyproject.toml`
  - `0 CRITICAL`
  - `72 WARNING` preexistentes o de deuda estructural del BC
- `codeguard`
  - corrida no concluida con salida util en este entorno
  - se dejó constancia en `quality/reports/codeguard/US-4.1.1-quality.json`

## Compatibilidad histórica

- `TarjetaAsignada.from_payload()` y `Performance._apply_tarjeta_asignada()` aceptan payload viejo:
  - `motivo="black-out"` se mapea a `BKO_SUPERFICIE`
  - otros `motivo` legacy quedan en `motivo_texto`

## Riesgos residuales

- Quedan helpers y seeds no cubiertos en esta corrida que aún pueden requerir adaptación si se ejecuta una suite más amplia del proyecto.
- `codeguard` necesita una estrategia de ejecución más estable en este entorno para dejar evidencia automática completa.
