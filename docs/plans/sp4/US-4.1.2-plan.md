# Plan de Implementación — US-4.1.2
## Tarjeta Blanca con penalizaciones

**Branch sugerida:** `feature/US-4.1.2-tarjeta-penalizaciones`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `4h 10min`
**Estado:** `Completado`

## Decisión arquitectónica

- Crear `docs/adr/ADR-014-penalizaciones-acumulables.md`
- Objetivo del ADR:
  - formalizar `BlancaConPenalizaciones` como tarjeta válida
  - justificar separación entre `rp_medido` y `rp_penalizado`
  - documentar por qué el ranking sigue leyendo la propiedad `rp`

## Componentes a crear o modificar

### ADR

- `docs/adr/ADR-014-penalizaciones-acumulables.md`

### Competencia

- `src/competencia/domain/value_objects/tipo_penalizacion.py`
- `src/competencia/domain/value_objects/penalizacion_tecnica.py`
- `src/competencia/domain/value_objects/tipo_tarjeta.py`
- `src/competencia/domain/value_objects/tarjeta_asignacion.py`
- `src/competencia/domain/aggregates/performance.py`
- `src/competencia/domain/events/tarjeta_asignada.py`
- `src/competencia/domain/exceptions.py`
- `src/competencia/application/commands/asignar_tarjeta.py`

### Resultados

- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- `src/resultados/domain/aggregates/ranking_competencia.py`
- `src/resultados/domain/ports/resultados_competencia_port.py`

### Tests y BDD

- tests unitarios de `Performance`, `AsignarTarjetaHandler`, `RankingCompetencia`
- tests de integración de `AsignarTarjeta` y `CalcularRanking`
- feature + steps para `US-4.1.2`

## Tareas

1. **[T1]** Crear `ADR-014` y modelar tipos de penalización. `25 min`
2. **[T2]** Extender `TipoTarjeta`, `TarjetaAsignacion` y excepciones. `25 min`
3. **[T3]** Implementar `rp_medido`, `rp_penalizado` y penalizaciones en `Performance` + `TarjetaAsignada`. `55 min`
4. **[T4]** Ajustar `AsignarTarjetaCommand/Handler` y validación de disciplina dinámica. `25 min`
5. **[T5]** Adaptar ACL de resultados y ranking para considerar `BlancaConPenalizaciones` como válida. `35 min`
6. **[T6]** Escribir y ajustar tests unitarios e integración. `45 min`
7. **[T7]** Implementar steps BDD de `US-4.1.2`. `20 min`
8. **[T8]** Ejecutar validaciones y cerrar documentación/reporte. `20 min`

## Decisiones de implementación

- `rp` seguirá exponiendo el valor penalizado si existe, para preservar compatibilidad con `RankingCompetencia`.
- `rp_medido` se conserva explícitamente para trazabilidad y payload de `TarjetaAsignada`.
- Si el total de deducciones supera el RP medido, `rp_penalizado` se clampa a `0`, sin excepción.
- La validación "solo disciplinas dinámicas" se hará en el handler de aplicación.

## Riesgos

1. El nuevo tipo de tarjeta puede afectar reglas previas que asumían solo `Blanca`, `Amarilla`, `Roja`.
2. El read model de resultados debe distinguir tarjeta válida con penalización de tarjeta inválida.
3. Los tests heredados de ranking y flujo e2e pueden requerir adaptación por el nuevo tipo válido.

## Cierre de ejecución

- ADR generado: `docs/adr/ADR-014-penalizaciones-acumulables.md`
- Validación ejecutada:
  - `.venv/bin/pytest tests/features/steps/test_US_4_1_2_steps.py -q` → `5 passed`
  - `.venv/bin/pytest tests/unit/competencia/domain/test_performance.py tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/unit/resultados/domain/test_ranking_competencia.py tests/integration/resultados/test_calcular_ranking_integration.py -q` → `107 passed`
- Quality gates:
  - `.venv/bin/designreviewer src/competencia src/resultados --config pyproject.toml` → `1 blocking`, `94 warning`
  - `.venv/bin/codeguard -c pyproject.toml -f json src/competencia src/resultados` → ejecución inconclusa en este entorno
