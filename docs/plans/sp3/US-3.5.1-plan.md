# Plan de Implementación — US-3.5.1

## Resumen

Implementar `RankingOverall` en el BC `resultados` reutilizando el patrón de
`RankingCompetencia`, pero con agregación por torneo y fórmula posicional
multi-disciplina.

## Objetivo observable

Dejar disponible un aggregate y un command handler capaces de calcular y
persistir el ranking overall de un torneo a partir de rankings por disciplina.

## Alcance

- `resultados/domain/value_objects/entrada_overall.py`
- `resultados/domain/aggregates/ranking_overall.py`
- `resultados/domain/events/ranking_overall_calculado.py`
- `resultados/application/commands/calcular_overall.py`
- tests unitarios de dominio y aplicación
- test de integración del cálculo overall
- feature BDD + step definitions

No incluye todavía:

- política P-09 (`US-3.5.2`)
- endpoint REST overall (`US-3.5.3`)

## Decisiones de diseño

1. `RankingOverall` vive en `resultados/domain/aggregates/` y usa Event Sourcing.
2. El stream canónico será `ranking-overall-{torneo_id}`.
3. El handler leerá rankings ya calculados por disciplina desde el Event Store de
   `resultados`, no reconstruirá el overall desde performances crudas de
   `competencia`.
4. La ausencia en una disciplina ejecutada se penaliza con `peor_posicion + 1`.
5. Una disciplina sin ranking calculado aún se excluye completamente del cálculo.

## Implementación por capa

### Dominio

- Crear `EntradaOverall` con:
  - `posicion`
  - `atleta_id`
  - `puntaje`
  - `detalle`
  - `en_podio`
- Crear `RankingOverallCalculado` con payload serializable.
- Implementar `RankingOverall` con:
  - estado interno de entradas calculadas
  - `calcular(torneo_id, rankings_por_disciplina, penalizacion_ausente=None)`
  - reconstitución desde eventos

### Aplicación

- Crear `CalcularOverallCommand`.
- Crear `CalcularOverallHandler` con dependencia solo a `ranking_store`.
- El handler debe:
  - cargar eventos existentes del stream overall
  - leer los rankings por disciplina desde streams `ranking-{competencia_id}-{disciplina}`
    ya almacenados en `resultados`
  - agrupar por `torneo_id` y disciplina según input de la US
  - delegar el cálculo al aggregate
  - persistir `RankingOverallCalculado`

## Riesgos a resolver

1. La spec menciona `competencia_store`, pero para esta US el insumo correcto son
   rankings de disciplina ya calculados. Se implementará sobre `ranking_store`
   para mantener la frontera del BC limpia.
2. El overall necesita mapear `torneo_id + disciplina` a competencia/ranking
   existente. Si el stream actual no alcanza, el test de integración debe
   explicitar el contrato mínimo esperado para `US-3.5.2`.

## Artefactos esperados al cierre

- código en `src/resultados/`
- `tests/unit/resultados/domain/test_ranking_overall.py`
- `tests/unit/resultados/application/test_calcular_overall_handler.py`
- `tests/integration/resultados/test_calcular_overall_integration.py`
- `tests/features/steps/calcular_overall_steps.py`
- `docs/reports/US-3.5.1-report.md`
