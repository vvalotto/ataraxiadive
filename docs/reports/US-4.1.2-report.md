# Reporte de Implementación — US-4.1.2
## Tarjeta Blanca con penalizaciones

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se incorporó `BlancaConPenalizaciones` como resultado válido explícito para
disciplinas dinámicas, con penalizaciones técnicas acumulables, preservando
`rp_medido` para trazabilidad y usando `rp_penalizado` como valor efectivo de ranking.

## Cambios implementados

### Arquitectura y dominio

- Nuevo ADR: `docs/adr/ADR-014-penalizaciones-acumulables.md`
- Nuevos value objects:
  - `src/competencia/domain/value_objects/tipo_penalizacion.py`
  - `src/competencia/domain/value_objects/penalizacion_tecnica.py`
- `TipoTarjeta` agrega `BlancaConPenalizaciones`
- `TarjetaAsignacion` exige penalizaciones para la nueva tarjeta
- `Performance` conserva:
  - `rp_medido`
  - `rp_penalizado`
  - `penalizaciones`
- `TarjetaAsignada` amplía payload con:
  - `penalizaciones`
  - `rp_medido`
  - `rp_penalizado`

### Aplicación

- `AsignarTarjetaCommand` y `AsignarTarjetaHandler` aceptan penalizaciones
- Validación explícita: `BlancaConPenalizaciones` solo aplica a `DNF`, `DYN`, `DBF`

### Resultados

- `ResultadosCompetenciaAdapter` publica `rp_penalizado` como `rp` efectivo
- `RankingCompetencia` considera `BlancaConPenalizaciones` como tarjeta válida

### Tests y BDD

- Nueva feature:
  - `tests/features/US-4.1.2-tarjeta-blanca-penalizaciones.feature`
- Nuevos steps:
  - `tests/features/steps/test_US_4_1_2_steps.py`
- Regresiones actualizadas:
  - `tests/unit/competencia/domain/test_performance.py`
  - `tests/unit/competencia/application/test_asignar_tarjeta_handler.py`
  - `tests/unit/resultados/domain/test_ranking_competencia.py`
  - `tests/integration/resultados/test_calcular_ranking_integration.py`

### Documentación

- `docs/reports/US-4.1.2-context.md`
- `docs/plans/sp4/US-4.1.2-plan.md`
- `docs/design/domain-model.md`

## Validación ejecutada

- `.venv/bin/pytest tests/features/steps/test_US_4_1_2_steps.py -q`
  - `5 passed`
- `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/unit/resultados/domain/test_ranking_competencia.py tests/integration/resultados/test_calcular_ranking_integration.py -q`
  - `107 passed`

## Quality Gates

- `.venv/bin/designreviewer src/competencia src/resultados --config pyproject.toml`
  - `1 blocking`
  - `94 warning`
  - el blocking corresponde a deuda estructural de `Performance`, no a una regresión funcional puntual de esta US
- `.venv/bin/codeguard -c pyproject.toml -f json src/competencia src/resultados`
  - corrida sin salida final util en este entorno
  - se dejó constancia en `quality/reports/codeguard/US-4.1.2-quality.json`

## Riesgos residuales

- `Performance` sigue concentrando demasiada responsabilidad y mantiene deuda de diseño previa.
- `codeguard` necesita una estrategia de ejecución más estable para dejar evidencia automática completa.
