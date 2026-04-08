# Reporte de Implementación — US-4.1.8
## Limpiar `Torneo`, `SQLiteTorneoRepository` y objetos de soporte

**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Fecha:** `2026-04-08`
**Estado:** `COMPLETADO`

## Resumen

Se redujo complejidad accidental en `Torneo`, su repositorio SQLite y los VOs
de soporte existentes, preservando contratos, excepciones y formato persistido.

La spec mencionaba `TarjetaAsignada` como VO, pero en el árbol actual no existe
ese artefacto; por eso el refactor se limitó a `TarjetaAsignacion` y al resto de
componentes efectivamente presentes.

## Cambios implementados

### Torneo / Domain

- `src/torneo/domain/aggregates/torneo.py`
  - separa validación de nombre y fechas
  - separa validación de transición y cancelación
  - separa validación de estado de asignación y disciplinas legacy

### Torneo / Infrastructure

- `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py`
  - extrae `_torneo_to_row`
  - extrae serialización de `Sede`, `EntidadOrganizadora` y `DisciplinaTorneo`
  - extrae deserialización inversa desde SQLite

### Competencia / Domain

- `src/competencia/domain/value_objects/tarjeta_asignacion.py`
  - separa validaciones internas por tipo de regla

### Shared / Domain

- `src/shared/domain/value_objects/disciplina_descriptor.py`
  - separa resolución de unidad y orden de grilla

## Validación ejecutada

- `.venv/bin/pytest tests/unit/torneo/domain/test_torneo.py tests/unit/torneo/domain/test_disciplinas_torneo.py tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py -q`
  - `91 passed`
- `.venv/bin/pytest tests/integration/torneo/test_sqlite_torneo_repository.py tests/integration/torneo/test_torneo_domain_integration.py tests/integration/torneo/test_disciplinas_torneo_api.py tests/integration/competencia/test_disciplina_descriptor_integration.py -q`
  - `25 passed`

## Quality Gates

- `designreviewer`
  - comando: `.venv/bin/designreviewer src/torneo/domain/aggregates/torneo.py src/torneo/infrastructure/repositories/sqlite_torneo_repository.py src/competencia/domain/value_objects/tarjeta_asignacion.py src/shared/domain/value_objects/disciplina_descriptor.py --config pyproject.toml`
  - resultado: `0 blocking`, `6 warning`
- `codeguard`
  - reporte: `quality/reports/codeguard/US-4.1.8-quality.json`
  - resumen: `0 errors`, `10 warnings`, `129 infos`

## Riesgos residuales

- Persisten warnings de cohesión (`LCOM`) en `Torneo`, `SQLiteTorneoRepository` y `TarjetaAsignacion`.
- `SQLiteTorneoRepository` sigue concentrando lógica de persistencia en un único repositorio, aunque con mappers más explícitos.
- No se tocó `TarjetaAsignada` porque ese VO no existe actualmente; si aparece más adelante, debería entrar como refactor separado.
