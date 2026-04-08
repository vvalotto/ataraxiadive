# Contexto de Implementación — US-4.1.5
## Descomponer aggregate `Performance`

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- La US afecta exclusivamente al BC `competencia`, capa `domain/`.
- El foco principal está en `src/competencia/domain/aggregates/performance.py`.
- El refactor debe preservar interfaz pública, eventos emitidos y semántica observable.
- La deuda señalada por HITO-19 se concentra en:
  - cálculo inline de `rp_penalizado` en `asignar_tarjeta()`
  - recalculo de RP en `corregir_resultado()`
  - compatibilidad legacy incrustada en `_apply_tarjeta_asignada()`

## Arquitectura y quality gates validados

- Documentación arquitectónica presente:
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
- Estructura del BC `competencia` presente en `src/competencia/{domain,application,infrastructure,api}`
- Testing configurado:
  - `tests/conftest.py`
  - suites unitarias e integración existentes para `Performance`
- Herramientas de calidad configuradas en `pyproject.toml`:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`

## Estado actual del código

- `Performance.asignar_tarjeta()` hoy:
  - valida estado
  - construye `TarjetaAsignacion`
  - calcula `rp_penalizado` inline
  - serializa payload del evento
  - muta todo el estado interno
- `Performance._apply_tarjeta_asignada()` hoy:
  - reconstituye compatibilidad con payload legacy
  - reconstruye penalizaciones
  - recompone RP medido/final y motivo de DQ
- `Performance._calcular_rp_penalizado_desde_estado()` ya sugiere una responsabilidad separable

## Cobertura existente detectada

- Unit tests:
  - `tests/unit/competencia/domain/test_performance.py`
- Integration tests:
  - `tests/integration/competencia/test_asignar_tarjeta_integration.py`
  - `tests/integration/competencia/test_corregir_resultado_integration.py`

## Riesgos

1. El payload de `TarjetaAsignada` debe quedar byte-a-byte compatible en sus campos observables.
2. La reconstitución desde eventos legacy no puede degradarse al mover la compatibilidad fuera de la lógica principal.
3. Un refactor que introduzca nuevos helpers mal ubicados puede romper la regla hexagonal del BC.
