# Contexto de Implementación — US-4.1.6
## Aliviar handlers de `competencia`

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- La US afecta al BC `competencia`, capa `application/commands/`.
- Los handlers con mayor densidad de orquestación inline son:
  - `src/competencia/application/commands/asignar_tarjeta.py`
  - `src/competencia/application/commands/generar_grilla.py`
  - `src/competencia/application/commands/registrar_ap.py`
  - `src/competencia/application/commands/llamar_atleta.py`
- `CalcularRankingHandler` no existe en el árbol actual; no entra en el scope real de esta US.

## Arquitectura y quality gates validados

- Documentación arquitectónica presente:
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
- Estructura del BC `competencia` presente en `src/competencia/{application,domain,infrastructure,api}`
- Testing configurado:
  - `tests/conftest.py`
  - suites unitarias e integración de handlers existentes
- Herramientas de calidad configuradas en `pyproject.toml`:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`

## Estado actual del código

- `AsignarTarjetaHandler.handle()` mezcla:
  - construcción de `stream_id`
  - carga y validación de stream
  - reconstitución del aggregate
  - validación específica de penalizaciones por disciplina
  - persistencia de eventos
  - disparo de política P-08
- `GenerarGrillaHandler.handle()` mezcla:
  - carga de competencia
  - consulta a `performances_ap`
  - obtención de descriptor
  - persistencia de eventos del aggregate
- `RegistrarAPHandler.handle()` mezcla:
  - validación de unidad
  - verificación de invariantes de competencia
  - chequeo de duplicado
  - creación del aggregate y persistencia
- `LlamarAtletaHandler.handle()` mezcla:
  - verificación de estado de competencia
  - verificación de conflicto de andarivel
  - carga de stream
  - reconstitución y persistencia

## Cobertura existente detectada

- Unit tests:
  - `tests/unit/competencia/application/test_asignar_tarjeta_handler.py`
  - `tests/unit/competencia/application/test_generar_grilla_handler.py`
  - `tests/unit/competencia/application/test_registrar_ap_handler.py`
  - `tests/unit/competencia/application/test_llamar_atleta_handler.py`
- Integration tests:
  - `tests/integration/competencia/test_asignar_tarjeta_integration.py`
  - `tests/integration/competencia/test_generar_grilla_integration.py`
  - `tests/integration/competencia/test_registrar_ap_integration.py`
  - `tests/integration/competencia/test_llamar_atleta_integration.py`

## Riesgos

1. Extraer helpers compartidos puede derivar en un pseudo-servicio de aplicación si se modela demasiado grande.
2. Cambiar el orden de validaciones en handlers puede alterar excepciones observables aunque los tests sigan verdes parcialmente.
3. El refactor debe respetar la regla hexagonal: helpers en `application/commands/`, sin imports cruzados nuevos hacia otros BCs.
