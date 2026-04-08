# Contexto de Implementación — US-4.1.8
## Limpiar `Torneo`, `SQLiteTorneoRepository` y objetos de soporte

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- La US afecta principalmente:
  - `src/torneo/domain/aggregates/torneo.py`
  - `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py`
  - `src/competencia/domain/value_objects/tarjeta_asignacion.py`
  - `src/shared/domain/value_objects/disciplina_descriptor.py`
- La spec menciona `TarjetaAsignada` como VO, pero en el árbol actual no existe ese VO.
  Solo existe el evento `src/competencia/domain/events/tarjeta_asignada.py`.
  Por lo tanto, el scope real se limita a los artefactos existentes.

## Arquitectura y quality gates validados

- Documentación arquitectónica presente:
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
- Testing configurado:
  - `tests/conftest.py`
  - suites unitarias e integración existentes para `torneo` y `disciplina_descriptor`
- Herramientas de calidad configuradas en `pyproject.toml`:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`

## Estado actual del código

- `Torneo` concentra:
  - validación de transiciones
  - validación de estados terminales
  - validación de asignación de disciplinas/jueces
  - mutación del aggregate en métodos compactos pero con lógica condicional repetida
- `SQLiteTorneoRepository` concentra:
  - aseguramiento de tabla
  - serialización JSON de VO complejos
  - mapeo de fila SQLite a aggregate
- `TarjetaAsignacion` concentra toda la validación en `__post_init__`
- `DisciplinaDescriptor.para()` concentra resolución de variantes SPE, tiempo y distancia inline

## Cobertura existente detectada

- Unit tests:
  - `tests/unit/torneo/domain/test_torneo.py`
  - `tests/unit/torneo/domain/test_disciplinas_torneo.py`
  - `tests/unit/competencia/domain/test_disciplina_descriptor.py`
  - `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py`
- Integration tests:
  - `tests/integration/torneo/test_sqlite_torneo_repository.py`
  - `tests/integration/torneo/test_torneo_domain_integration.py`
  - `tests/integration/torneo/test_disciplinas_torneo_api.py`
  - `tests/integration/competencia/test_disciplina_descriptor_integration.py`

## Riesgos

1. `Torneo` no usa eventos; el riesgo principal es alterar excepciones/validaciones observables.
2. El repositorio persiste estructuras JSON anidadas; reorganizar serialización/mapeo no puede cambiar el formato persistido.
3. `TarjetaAsignacion` y `DisciplinaDescriptor` ya son puntos compartidos; cualquier extracción debe evitar ciclos entre BCs.
