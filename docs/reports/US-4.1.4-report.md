# Reporte de Implementación — US-4.1.4
## Orden de grilla reglamentario

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se consolidó la regla reglamentaria de generación de grilla:

- `STA` y disciplinas de distancia siguen ordenando en forma ascendente por AP
- variantes `SPE_*` ordenan en forma descendente por AP

La lógica central ya estaba delegada en `DisciplinaDescriptor` y `GrillaDeSalida`.
Esta US dejó cobertura explícita y trazabilidad formal del comportamiento.

## Cambios implementados

### Cobertura de dominio e integración

- Nuevos tests de orden SPE en:
  - `tests/unit/competencia/domain/test_generar_grilla.py`
  - `tests/integration/competencia/test_generar_grilla_integration.py`
- Nueva BDD específica:
  - `tests/features/US-4.1.4-orden-grilla-reglamentario.feature`
  - `tests/features/steps/test_US_4_1_4_steps.py`

### Documentación

- `docs/reports/US-4.1.4-context.md`
- `docs/plans/sp4/US-4.1.4-plan.md`
- `docs/design/domain-model.md` no requirió ajuste adicional específico para esta US

## Validación ejecutada

- `.venv/bin/pytest tests/unit/competencia/domain/test_generar_grilla.py tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py -q`
  - `68 passed`
- `.venv/bin/pytest tests/integration/competencia/test_generar_grilla_integration.py -q`
  - `8 passed`
- `.venv/bin/pytest tests/features/steps/test_US_4_1_4_steps.py -q`
  - `6 passed`

## Quality Gates

- `.venv/bin/designreviewer src/shared/domain/value_objects/disciplina_descriptor.py src/competencia/domain/entities/grilla_de_salida.py src/competencia/application/commands/generar_grilla.py --config pyproject.toml`
  - `0 blocking`
  - `6 warning`
- `.venv/bin/codeguard -c pyproject.toml -f json src/competencia/domain/entities/grilla_de_salida.py tests/unit/competencia/domain/test_generar_grilla.py tests/integration/competencia/test_generar_grilla_integration.py tests/features/steps/test_US_4_1_4_steps.py`
  - `0 errors`
  - `7 warnings`
  - los warnings se concentran en:
    - complejidad/deuda previa en `GrillaDeSalida`
    - lineas largas y imports no usados en tests
    - `assert` en tests/steps reportado como info de seguridad

## Riesgos residuales

- La regla depende de que `DisciplinaDescriptor` siga siendo la fuente única de orden por disciplina.
- `GrillaDeSalida` mantiene deuda de diseño previa en `ajustar()`, pero sin bloqueantes para esta US.
