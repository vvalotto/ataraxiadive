# Contexto de Implementación — US-4.1.7
## Simplificar `GrillaDeSalida` y `RankingCompetencia`

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- La US afecta tres puntos concretos:
  - `src/competencia/domain/entities/grilla_de_salida.py`
  - `src/resultados/domain/aggregates/ranking_competencia.py`
  - `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- En el árbol real, `GrillaDeSalida` vive en `entities/`, no en `aggregates/`.
- El refactor es puramente técnico: no debe cambiar orden de grilla, ranking ni payloads observables.

## Arquitectura y quality gates validados

- Documentación arquitectónica presente:
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
- Testing configurado:
  - `tests/conftest.py`
  - cobertura unitaria e integración existente para grilla y ranking
- Herramientas de calidad configuradas en `pyproject.toml`:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`

## Estado actual del código

- `GrillaDeSalida.ajustar()` mezcla:
  - intercambio de posiciones
  - actualización de andarivel
  - armado de `cambios_payload`
  - detección de recalculo de OTs
- `GrillaDeSalida.aplicar_cambios_persistidos()` repite parte de la misma lógica de mutación.
- `RankingCompetencia` ya usa varios helpers, pero todavía concentra:
  - parsing de payload
  - aplicación de evento
  - cálculo de ranking válido/inválido
  - serialización/deserialización de `EntradaRanking`
- `ResultadosCompetenciaAdapter` tiene una estructura razonable, pero `_aplicar_evento_en_estado()` sigue acumulando reglas de traducción de eventos heterogéneos.

## Cobertura existente detectada

- Unit tests:
  - `tests/unit/competencia/domain/test_generar_grilla.py`
  - `tests/unit/resultados/domain/test_ranking_competencia.py`
  - `tests/unit/resultados/application/test_calcular_ranking_handler.py`
  - `tests/unit/resultados/api/test_router_ranking.py`
- Integration tests:
  - `tests/integration/competencia/test_generar_grilla_integration.py`
  - `tests/integration/resultados/test_calcular_ranking_integration.py`

## Riesgos

1. `GrillaDeSalida` duplica mutaciones entre ajuste en memoria y replay persistido; separar mal esa lógica puede romper replay.
2. `RankingCompetencia` maneja empates y podio; cualquier refactor debe preservar exactamente la política actual.
3. `ResultadosCompetenciaAdapter` traduce streams sin reconstituir aggregates; si se abstrae de más, puede perder compatibilidad con payloads existentes.
