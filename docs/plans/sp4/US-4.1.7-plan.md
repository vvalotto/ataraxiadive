# Plan de Implementación — US-4.1.7
## Simplificar `GrillaDeSalida` y `RankingCompetencia`

**Branch actual:** `feature/inc-4.1-correcciones-dominio`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `3h 20min`
**Estado:** `Completado`

## Objetivo

Partir métodos largos de ajuste de grilla y cálculo/traducción de ranking para que
cada módulo delegue en colaboradores o submétodos cohesivos, preservando exactamente
el orden de grilla y el ranking observable.

## Componentes a crear o modificar

### Competencia / Domain

- `src/competencia/domain/entities/grilla_de_salida.py`

### Resultados / Domain

- `src/resultados/domain/aggregates/ranking_competencia.py`

### Resultados / Infrastructure

- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`

### Tests

- `tests/unit/competencia/domain/test_generar_grilla.py`
- `tests/unit/resultados/domain/test_ranking_competencia.py`
- `tests/integration/competencia/test_generar_grilla_integration.py`
- `tests/integration/resultados/test_calcular_ranking_integration.py`

## Tareas

1. **[T1]** Relevar duplicación y puntos de extracción en `GrillaDeSalida.ajustar()` y `aplicar_cambios_persistidos()`. `25 min`
2. **[T2]** Extraer submétodos privados en `GrillaDeSalida` para actualización de entradas, intercambio de posiciones y recalculo de OTs. `40 min`
3. **[T3]** Simplificar `RankingCompetencia` separando cálculo por categoría, serialización y replay de eventos. `40 min`
4. **[T4]** Reorganizar `ResultadosCompetenciaAdapter` para desacoplar traducción de eventos y construcción de `ResultadoFinal`. `30 min`
5. **[T5]** Ajustar/agregar tests unitarios e integración focalizados en preservación de orden y empates. `40 min`
6. **[T6]** Ejecutar quality gates y documentar resultados. `25 min`

## Decisiones de implementación

- En `GrillaDeSalida` se prioriza extracción a métodos privados del mismo objeto; no se crean servicios nuevos.
- En `RankingCompetencia` se mantiene el cálculo como lógica de dominio pura, pero se separan etapas del algoritmo con nombres explícitos.
- En `ResultadosCompetenciaAdapter` la reorganización será estructural; no se cambia la estrategia de leer streams crudos.
- La comparación de comportamiento se validará con los tests existentes y, si hace falta, con nuevos casos mínimos de empate/AP.

## Riesgos

1. `GrillaDeSalida` depende de mantener consistente el payload de cambios y el replay persistido.
2. `RankingCompetencia` usa reglas de empate y podio sensibles a off-by-one; un refactor superficial puede introducir regressions sutiles.
3. `ResultadosCompetenciaAdapter` consume payloads heterogéneos; abstraer demasiado puede volver menos clara la compatibilidad backward.

## Criterio de salida

- Tests unitarios e integración relevantes en verde
- `designreviewer` sin bloqueos en los módulos refactorizados
- Los métodos principales quedan como orquestación breve y los helpers privados expresan reglas de negocio concretas

## Cierre de ejecución

- Refactor completado:
  - `GrillaDeSalida` separa intercambio de posiciones, actualización de andarivel y recalculo de OTs
  - `RankingCompetencia` separa replay/deserialización y ordenamiento de válidas
  - `ResultadosCompetenciaAdapter` separa construcción de resultado y handlers por tipo de evento
- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/competencia/domain/test_generar_grilla.py tests/unit/resultados/domain/test_ranking_competencia.py -q` → `32 passed`
  - `.venv/bin/pytest tests/integration/competencia/test_generar_grilla_integration.py tests/integration/resultados/test_calcular_ranking_integration.py -q` → `17 passed`
- Quality gates:
  - `.venv/bin/designreviewer ... --config pyproject.toml` → `0 blocking`, `12 warning`
  - `.venv/bin/codeguard ... > quality/reports/codeguard/US-4.1.7-quality.json` → `0 errors`, `6 warnings`
