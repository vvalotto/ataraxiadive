# Validación de Contexto — US-4.1.1

## Contexto Validado

**Historia de Usuario:** `US-4.1.1` - Motivos de tarjeta roja — catálogo formal de causas de DQ
**Producto:** `ataraxiadive`
**Puntos:** `3` (estimación operativa para tracking)
**Prioridad:** Alta
**Incremento:** `INC-4.1`
**Bounded Context:** `competencia`

## Arquitectura

- Patrón: Hexagonal DDD BC-first
- Documentación base leída:
  - `CLAUDE.md`
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
- Estructura del BC verificada:
  - `src/competencia/domain/`
  - `src/competencia/application/`
  - `src/competencia/infrastructure/`
  - `src/competencia/api/`

## Superficie de impacto detectada

- Aggregate: `src/competencia/domain/aggregates/performance.py`
- Value Object: `src/competencia/domain/value_objects/tarjeta_asignacion.py`
- Evento: `src/competencia/domain/events/tarjeta_asignada.py`
- Excepciones: `src/competencia/domain/exceptions.py`
- Handler de aplicación: `src/competencia/application/commands/asignar_tarjeta.py`
- ACL consumidora del evento: `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`

## Compatibilidad a preservar

- Los streams históricos con `TarjetaAsignada.motivo="black-out"` deben seguir reconstituyendo correctamente.
- La tarjeta amarilla mantiene motivo en texto libre.
- La tarjeta roja deja de aceptar string libre y pasa a exigir `MotivoDQ`.
- La proyección/lectura de resultados no debe romperse por el cambio de payload.

## Quality Gates

- `CLAUDE.md` presente con quality gates y reglas de arquitectura
- `tests/`, `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/features/` presentes
- `pyproject.toml` contiene configuración para:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`

## Riesgos principales

1. `TarjetaAsignada` cambia contrato y afecta tests, steps BDD y cualquier consumidor del payload.
2. La compatibilidad histórica requiere aceptar payload viejo y nuevo en reconstitución.
3. El cambio debe mantener comportamiento vigente para tarjeta amarilla y corrección de resultado.

## Estado

Listo para proceder con Fase 1 (BDD) y Fase 2 (plan) sobre la base de código existente.
