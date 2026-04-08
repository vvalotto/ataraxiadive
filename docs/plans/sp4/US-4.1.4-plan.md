# Plan de Implementación — US-4.1.4
## Orden de grilla reglamentario

**Branch sugerida:** `feature/US-4.1.4-orden-grilla`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `2h 30min`
**Estado:** `Completado`

## Objetivo

Validar y dejar formalizado que la grilla reglamentaria usa orden ascendente
para STA y disciplinas de distancia, y orden descendente para variantes SPE.

## Componentes a crear o modificar

### Competencia

- tests unitarios/integración de `GenerarGrilla`
- feature BDD específica de la US

### Shared

- validación explícita de `DisciplinaDescriptor` para SPE vs no SPE

## Tareas

1. **[T1]** Relevar la implementación actual y confirmar dependencia con `US-4.1.3`. `15 min`
2. **[T2]** Agregar cobertura de integración de grilla para `SPE_4X50` y `SPE_2X50`. `35 min`
3. **[T3]** Agregar BDD específica de `US-4.1.4` para orden reglamentario. `30 min`
4. **[T4]** Ejecutar validaciones y cerrar documentación/reporte. `25 min`

## Decisiones de implementación

- No se modifica la lógica central de `GrillaDeSalida.generar()`.
- La regla del negocio sigue centralizada en `DisciplinaDescriptor`.
- `US-4.1.4` actúa como consolidación funcional y documental del comportamiento reglamentario ya habilitado por `US-4.1.3`.

## Riesgos

1. Si se cambia `DisciplinaDescriptor` más adelante, la grilla puede degradarse sin tocar `GrillaDeSalida`.
2. Hay solapamiento funcional con `US-4.1.3`, por lo que la trazabilidad debe explicar que esta US consolida y valida la regla, más que introducir un cambio estructural nuevo.

## Cierre de ejecución

- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/competencia/domain/test_generar_grilla.py tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py -q` → `68 passed`
  - `.venv/bin/pytest tests/integration/competencia/test_generar_grilla_integration.py -q` → `8 passed`
  - `.venv/bin/pytest tests/features/steps/test_US_4_1_4_steps.py -q` → `6 passed`
- Quality gates:
  - `.venv/bin/designreviewer ...` → `0 blocking`, `6 warning`
  - `.venv/bin/codeguard ...` → `0 errors`, `7 warnings`
