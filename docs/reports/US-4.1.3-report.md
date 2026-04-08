# Reporte de Implementación — US-4.1.3
## Subdisciplinas SPE

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se formalizaron las variantes `SPE_2X50`, `SPE_4X50`, `SPE_8X50` y `SPE_16X50`
como disciplinas explícitas del dominio. Estas variantes usan segundos como
unidad, se reconocen como familia SPE y quedan separadas para torneo, AP/RP y ranking.
`Disciplina.SPE` se mantiene solo como valor legacy y pasa a rechazarse en torneos nuevos.

## Cambios implementados

### Shared

- `Disciplina` agrega:
  - `SPE_2X50`
  - `SPE_4X50`
  - `SPE_8X50`
  - `SPE_16X50`
- Nuevo helper `Disciplina.es_spe()`
- `Disciplina.es_tiempo()` ahora incluye variantes SPE nuevas, pero no `SPE` legacy
- `DisciplinaDescriptor` devuelve para variantes SPE:
  - `unidad_esperada = Segundos`
  - `orden_ascendente = False`

### Torneo

- Nueva excepción `DisciplinaObsoleta`
- `Torneo.asignar_disciplinas()` rechaza `Disciplina.SPE` en torneos nuevos
- API de torneo devuelve `409` al intentar configurar `SPE` genérica

### Resultados y Competencia

- `RegistrarAP` y `RegistrarResultado` toman la unidad correcta por descriptor para variantes SPE
- `RankingCompetencia` mantiene separación natural por disciplina, por lo que cada variante SPE genera ranking independiente

### Tests y BDD

- Nueva feature:
  - `tests/features/US-4.1.3-subdisciplinas-spe.feature`
- Nuevos steps:
  - `tests/features/steps/test_US_4_1_3_steps.py`
- Regresiones actualizadas:
  - `tests/unit/competencia/domain/test_disciplina_descriptor.py`
  - `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py`
  - `tests/unit/torneo/domain/test_disciplinas_torneo.py`
  - `tests/integration/competencia/test_registrar_ap_integration.py`
  - `tests/integration/torneo/test_disciplinas_torneo_api.py`
  - `tests/integration/resultados/test_calcular_ranking_integration.py`

### Documentación

- `docs/reports/US-4.1.3-context.md`
- `docs/plans/sp4/US-4.1.3-plan.md`
- `docs/design/domain-model.md`

## Validación ejecutada

- `.venv/bin/pytest tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py tests/unit/torneo/domain/test_disciplinas_torneo.py -q`
  - `73 passed`
- `.venv/bin/pytest tests/integration/competencia/test_registrar_ap_integration.py tests/integration/torneo/test_disciplinas_torneo_api.py tests/integration/resultados/test_calcular_ranking_integration.py -q`
  - `28 passed`
- `.venv/bin/pytest tests/features/steps/test_US_4_1_3_steps.py -q`
  - `6 passed`

## Quality Gates

- `.venv/bin/designreviewer src/shared src/torneo src/resultados --config pyproject.toml`
  - `0 blocking`
  - `37 warning`
- `.venv/bin/codeguard -c pyproject.toml -f json` sobre archivos modificados de la US
  - `0 errors`
  - `2 warnings`
  - warnings detectados:
    - `src/torneo/domain/aggregates/torneo.py:39` — `E302 expected 2 blank lines, found 1`
    - `src/torneo/domain/aggregates/torneo.py:90` — `E501 line too long (111 > 100 characters)`
  - evidencia registrada en `quality/reports/codeguard/US-4.1.3-quality.json`

## Riesgos residuales

- `US-4.1.4` todavía debe consolidar la semántica reglamentaria completa del orden de grilla para SPE.
- Persisten warnings de diseño en `torneo`, `resultados` y `shared`, pero sin bloqueantes para esta US.
