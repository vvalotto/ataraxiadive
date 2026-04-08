# Plan de Implementación — US-4.1.8
## Limpiar `Torneo`, `SQLiteTorneoRepository` y objetos de soporte

**Branch actual:** `feature/inc-4.1-correcciones-dominio`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `3h 10min`
**Estado:** `Completado`

## Objetivo

Reducir complejidad accidental en `Torneo`, su repositorio SQLite y los objetos
de soporte `TarjetaAsignacion` y `DisciplinaDescriptor`, preservando contratos,
excepciones y formato persistido.

## Componentes a crear o modificar

### Torneo / Domain

- `src/torneo/domain/aggregates/torneo.py`

### Torneo / Infrastructure

- `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py`

### Competencia / Domain

- `src/competencia/domain/value_objects/tarjeta_asignacion.py`

### Shared / Domain

- `src/shared/domain/value_objects/disciplina_descriptor.py`

### Tests

- `tests/unit/torneo/domain/test_torneo.py`
- `tests/unit/torneo/domain/test_disciplinas_torneo.py`
- `tests/unit/competencia/domain/test_disciplina_descriptor.py`
- `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py`
- `tests/integration/torneo/test_sqlite_torneo_repository.py`
- `tests/integration/torneo/test_torneo_domain_integration.py`
- `tests/integration/torneo/test_disciplinas_torneo_api.py`
- `tests/integration/competencia/test_disciplina_descriptor_integration.py`

## Tareas

1. **[T1]** Relevar condicionales repetidos en `Torneo` y extraer validaciones privadas por responsabilidad. `30 min`
2. **[T2]** Separar serialización/mapeo en `SQLiteTorneoRepository` sin cambiar el formato persistido. `35 min`
3. **[T3]** Simplificar `TarjetaAsignacion` dividiendo validaciones en helpers privados descriptivos. `25 min`
4. **[T4]** Simplificar `DisciplinaDescriptor.para()` extrayendo resolución de unidad/orden por variante. `25 min`
5. **[T5]** Ejecutar y ajustar tests unitarios/integración focalizados en `torneo` y descriptor. `40 min`
6. **[T6]** Ejecutar quality gates y documentar resultados. `25 min`

## Decisiones de implementación

- No se trabajará sobre `TarjetaAsignada` como VO porque ese artefacto no existe en el árbol actual.
- En `Torneo` se prioriza extracción a métodos privados del aggregate, no clases nuevas.
- En `SQLiteTorneoRepository` se extraen mappers privados `_serialize_*` y `_row_to_*`.
- `TarjetaAsignacion` y `DisciplinaDescriptor` seguirán siendo VOs autocontenidos; solo se parte la validación interna.

## Riesgos

1. Cambiar el formato JSON persistido en `SQLiteTorneoRepository` rompería compatibilidad con datos existentes.
2. Reordenar validaciones en `Torneo` o `TarjetaAsignacion` puede cambiar el tipo de excepción observable.
3. `DisciplinaDescriptor` tiene impacto transversal en competencia y resultados; cualquier cambio debe preservarse en tests de integración.

## Criterio de salida

- Tests unitarios e integración relevantes en verde
- `designreviewer` sin bloqueos en los módulos refactorizados
- El código queda organizado por helpers privados/mappers con responsabilidades explícitas

## Cierre de ejecución

- Refactor completado:
  - `Torneo` separa validaciones de nombre, fechas, transición, cancelación y asignación
  - `SQLiteTorneoRepository` separa serialización y deserialización de VO complejos
  - `TarjetaAsignacion` separa validaciones de penalizaciones, motivos y blackout
  - `DisciplinaDescriptor` separa resolución de unidad y orden
- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/torneo/domain/test_torneo.py tests/unit/torneo/domain/test_disciplinas_torneo.py tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py -q` → `91 passed`
  - `.venv/bin/pytest tests/integration/torneo/test_sqlite_torneo_repository.py tests/integration/torneo/test_torneo_domain_integration.py tests/integration/torneo/test_disciplinas_torneo_api.py tests/integration/competencia/test_disciplina_descriptor_integration.py -q` → `25 passed`
- Quality gates:
  - `.venv/bin/designreviewer ... --config pyproject.toml` → `0 blocking`, `6 warning`
  - `.venv/bin/codeguard ... > quality/reports/codeguard/US-4.1.8-quality.json` → `0 errors`, `10 warnings`
