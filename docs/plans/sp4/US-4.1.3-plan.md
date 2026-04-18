# Plan de Implementación — US-4.1.3
## Subdisciplinas SPE

**Branch sugerida:** `feature/US-4.1.3-subdisciplinas-spe`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `4h`
**Estado:** `Completado`

## Objetivo

Incorporar las variantes `SPE_2X50`, `SPE_4X50`, `SPE_8X50` y `SPE_16X50`
como disciplinas explícitas del dominio, manteniendo `SPE` genérica solo para
compatibilidad histórica y rechazándola en torneos nuevos.

## Componentes a crear o modificar

### Shared

- `src/shared/domain/value_objects/disciplina.py`
- `src/shared/domain/value_objects/disciplina_descriptor.py`

### Torneo

- `src/torneo/domain/exceptions.py`
- `src/torneo/domain/aggregates/torneo.py`
- `src/torneo/api/router.py`
- `src/torneo/api/exception_handlers.py`

### Tests y BDD

- `tests/features/US-4.1.3-subdisciplinas-spe.feature`
- steps BDD específicos de la US
- tests unitarios de descriptor y torneo
- tests de integración de API/handler de torneo
- tests de integración de ranking con variantes SPE

## Tareas

1. **[T1]** Extender `Disciplina` con variantes SPE y helpers `es_spe()`/`es_tiempo()`. `25 min`
2. **[T2]** Ajustar `DisciplinaDescriptor` para variantes SPE. `20 min`
3. **[T3]** Introducir `DisciplinaObsoleta` y rechazar `Disciplina.SPE` en `Torneo.asignar_disciplinas()`. `25 min`
4. **[T4]** Adaptar API de torneo para exponer el nuevo error. `20 min`
5. **[T5]** Adecuar tests unitarios e integración existentes. `55 min`
6. **[T6]** Implementar BDD de `US-4.1.3`. `25 min`
7. **[T7]** Ejecutar validaciones, documentación y reporte. `30 min`

## Decisiones de implementación

- `Disciplina.SPE` se mantiene en el enum para reconstitución legacy.
- `Disciplina.es_spe()` debe considerar tanto `SPE` legacy como las cuatro variantes nuevas.
- `Disciplina.es_tiempo()` pasa a devolver `True` para `STA` y para variantes SPE nuevas, pero no para `SPE` legacy.
- `DisciplinaDescriptor.para()` devolverá:
  - `Segundos` y `orden_ascendente=False` para variantes SPE nuevas
  - comportamiento previo para `SPE` legacy
- El rechazo de `Disciplina.SPE` se hará en el aggregate `Torneo`, no en el enum.
- La separación de rankings por variante ocurre de forma natural por la clave `disciplina`; no requiere rediseño del aggregate de resultados.

## Riesgos

1. Cambiar `es_tiempo()` afecta validaciones de AP/RP, seeds y tests auxiliares.
2. Variantes SPE nuevas impactan serialización y endpoints que aceptan disciplina por string.
3. `US-4.1.4` volverá a tocar parte de la semántica de `orden_ascendente`; evitar sobrerrefactor ahora.

## Cierre de ejecución

- Validación ejecutada:
  - `.venv/bin/pytest tests/unit/competencia/domain/test_disciplina_descriptor.py tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py tests/unit/torneo/domain/test_disciplinas_torneo.py -q` → `73 passed`
  - `.venv/bin/pytest tests/integration/competencia/test_registrar_ap_integration.py tests/integration/torneo/test_disciplinas_torneo_api.py tests/integration/resultados/test_calcular_ranking_integration.py -q` → `28 passed`
  - `.venv/bin/pytest tests/features/steps/test_US_4_1_3_steps.py -q` → `6 passed`
- Quality gates:
  - `.venv/bin/designreviewer src/shared src/torneo src/resultados --config pyproject.toml` → `0 blocking`, `37 warning`
  - `.venv/bin/codeguard -c pyproject.toml -f json src/shared src/torneo src/resultados` → ejecución inconclusa en este entorno
