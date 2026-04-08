# Validación de Contexto — US-4.1.2

## Contexto Validado

**Historia de Usuario:** `US-4.1.2` - Tarjeta Blanca con penalizaciones
**Producto:** `ataraxiadive`
**Puntos:** `5` (estimación operativa para tracking)
**Prioridad:** Alta
**Incremento:** `INC-4.1`
**Bounded Contexts:** `competencia`, `resultados`

## Arquitectura

- Patrón: Hexagonal DDD BC-first
- Documentación base verificada:
  - `CLAUDE.md`
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
- Estructura de BCs verificada:
  - `src/competencia/domain|application|infrastructure|api`
  - `src/resultados/domain|application|infrastructure|api`

## Superficie de impacto detectada

### Competencia

- `src/competencia/domain/value_objects/tipo_tarjeta.py`
- `src/competencia/domain/value_objects/tarjeta_asignacion.py`
- `src/competencia/domain/aggregates/performance.py`
- `src/competencia/domain/events/tarjeta_asignada.py`
- `src/competencia/application/commands/asignar_tarjeta.py`

### Resultados

- `src/resultados/domain/aggregates/ranking_competencia.py`
- `src/resultados/domain/ports/resultados_competencia_port.py`
- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`

## Decisión arquitectónica para esta US

- Se crea `ADR-014` para formalizar el modelo de penalizaciones acumulables.
- Alcance esperado del ADR:
  - nueva tarjeta válida `BlancaConPenalizaciones`
  - `rp_medido` y `rp_penalizado` como conceptos distintos
  - penalizaciones acumulables modeladas como value objects
  - compatibilidad de ranking mediante la propiedad `rp`

## Riesgos principales

1. `TarjetaAsignada` vuelve a cambiar contrato, ahora agregando penalizaciones y RP penalizado.
2. `RankingCompetencia` hoy considera válidas solo `Blanca` y `Amarilla`; debe admitir la nueva tarjeta válida.
3. El aggregate `Performance` necesita conservar RP medido y penalizado sin romper compatibilidad con consultas existentes.

## Quality Gates

- `tests/`, `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/features/` presentes
- `pyproject.toml` contiene `[tool.coverage.run]`, `[tool.codeguard]`, `[tool.designreviewer]`
- El proyecto cuenta con `codeguard` y `designreviewer` en `.venv/bin/`

## Estado

Listo para proceder con BDD, plan, ADR-014 e implementación de `US-4.1.2`.
