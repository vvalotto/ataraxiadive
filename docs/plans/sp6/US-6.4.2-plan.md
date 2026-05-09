# Plan de Implementacion: US-6.4.2 - Materializar proyeccion competencias_por_torneo en CalcularOverallHandler

**Patron:** Hexagonal DDD BC-first
**Producto:** resultados + competencia
**Incremento:** INC-6.4 - Deuda Tecnica Sistema
**Estimacion total:** 2h 00min
**Estado:** Completado
**Fecha completado:** 2026-05-09

## Contexto Validado

- La US existe en `docs/specs/sp6/US-6.4.2.md`.
- `CalcularOverallHandler` en `src/resultados/application/commands/calcular_overall.py`
  todavia usa `_mapear_competencias_por_torneo()` con
  `competencia_store.load_all_streams_with_prefix("competencia-")`.
- `CompetenciasPorTorneoPort` ya existe en
  `src/competencia/domain/ports/competencias_por_torneo_port.py`.
- `SQLiteCompetenciasPorTorneo` ya existe, crea indice por `torneo_id` y expone
  `listar_por_torneo(torneo_id)`.
- `src/app.py` ya importa `SQLiteCompetenciasPorTorneo`, pero
  `_calcular_overall_si_corresponde()` sigue instanciando
  `CalcularOverallHandler(ranking_store, competencia_event_store)`.

## Decisiones de Diseno

- `CalcularOverallHandler` recibira `CompetenciasPorTorneoPort` en lugar de
  `EventStorePort` de competencia.
- Se eliminara `_mapear_competencias_por_torneo()` y la constante
  `_EVENTO_INTERVALO_OT`.
- El handler filtrara los records de la proyeccion por las disciplinas pedidas.
- Si la proyeccion no devuelve competencias, el handler retornara `[]` sin persistir
  `RankingOverallCalculado`; esto evita crear eventos vacios para torneos sin datos
  materializados y cubre el tercer criterio BDD.
- La importacion cross-BC de `competencia.domain.ports.CompetenciasPorTorneoPort`
  se acepta como comunicacion por port. Si DesignReviewer la marca, se documentara en
  el reporte final.

## Componentes a Modificar

### 1. Handler de resultados

- [x] `src/resultados/application/commands/calcular_overall.py` (35 min)
  - Importar `CompetenciasPorTorneoPort`.
  - Cambiar constructor a `ranking_store, competencias_por_torneo`.
  - Usar `await self._competencias_por_torneo.listar_por_torneo(command.torneo_id)`.
  - Construir `dict[Disciplina, UUID]` desde records filtrados.
  - Retornar `[]` si no hay competencias para las disciplinas solicitadas.
  - Eliminar `_mapear_competencias_por_torneo()` y `_EVENTO_INTERVALO_OT`.

### 2. Composition root

- [x] `src/app.py` (15 min)
  - Instanciar `SQLiteCompetenciasPorTorneo()` dentro de
    `_calcular_overall_si_corresponde()`.
  - Pasar la proyeccion a `CalcularOverallHandler`.
  - Mantener `competencia_event_store` para las precondiciones P-09 existentes.

### 3. Tests unitarios

- [x] `tests/unit/resultados/application/test_calcular_overall_handler.py` (30 min)
  - Reemplazar mocks de `competencia_store` por mock de `competencias_por_torneo`.
  - Agregar test que asegura que no se llama `load_all_streams_with_prefix`.
  - Cubrir caso sin competencias materializadas: retorna `[]` y no persiste evento.

### 4. Tests de integracion

- [x] `tests/integration/resultados/test_calcular_overall_integration.py` (25 min)
  - Usar `SQLiteCompetenciasPorTorneo` con DB temporal.
  - Materializar competencias con `guardar()` en lugar de depender del scan de eventos.
  - Mantener rankings en `ranking_store`.

### 5. BDD y steps existentes

- [x] `tests/features/US-6.4.2-proyeccion-overall.feature` (10 min)
  - Escenarios BDD creados.
- [x] `tests/features/steps/calcular_overall_steps.py` (20 min)
  - Agregar `SQLiteCompetenciasPorTorneo` al contexto.
  - Hacer que `_append_competencia()` guarde en la proyeccion.
  - Instanciar `CalcularOverallHandler(ctx["ranking_store"], ctx["competencias_por_torneo"])`.
  - Si se automatiza el feature nuevo, registrar `scenarios("../US-6.4.2-proyeccion-overall.feature")`.

### 6. Seeds/UAT que instancian el handler

- [x] `tests/uat/sp3/seed_sp3.py` (10 min)
  - Actualizar `CalcularOverallHandler(resultados_store, store)` a la nueva firma.
  - Reutilizar la proyeccion `SQLiteCompetenciasPorTorneo` ya importada en el seed.

### 7. Quality Gates

- [x] Tests unitarios de resultados (10 min)
  - `.venv/bin/python -m pytest tests/unit/resultados/application/test_calcular_overall_handler.py -q`
- [x] Tests de integracion de resultados (10 min)
  - `.venv/bin/python -m pytest tests/integration/resultados/test_calcular_overall_integration.py -q`
- [x] BDD overall (10 min)
  - `.venv/bin/python -m pytest tests/features/steps/calcular_overall_steps.py -q`
- [x] Suite acotada P-09/app si aplica (10 min)
  - `.venv/bin/python -m pytest tests/unit/test_app_p09.py tests/integration/test_p09_callback_integration.py -q`
- [x] CodeGuard/DesignReviewer acotados (10 min)
  - `.venv/bin/codeguard src/resultados/application/commands/calcular_overall.py`
  - `.venv/bin/designreviewer src/resultados/ --config pyproject.toml`

### 8. Documentacion y Reporte

- [x] Actualizar `CHANGELOG.md` (5 min).
- [x] Actualizar este plan con resultados de validacion en Fase 8 (5 min).
- [ ] Generar `docs/reports/US-6.4.2-report.md` en Fase 9 (10 min).

## Resultado de Implementacion

- `CalcularOverallHandler` ahora depende de `CompetenciasPorTorneoPort`.
- Se elimino el scan de `competencia_store.load_all_streams_with_prefix("competencia-")`.
- `src/app.py` inyecta `SQLiteCompetenciasPorTorneo` en el handler de P-09.
- Tests unitarios, integracion, BDD steps y seed UAT SP3 quedaron alineados con la nueva firma.
- El caso sin competencias materializadas retorna `[]` sin persistir `RankingOverallCalculado`.

## Validacion Ejecutada

- `.venv/bin/python -m pytest tests/unit/resultados/application/test_calcular_overall_handler.py -q`
  - Resultado: 3 passed.
- `.venv/bin/python -m pytest tests/unit/resultados/ tests/unit/test_app_p09.py -q`
  - Resultado: 77 passed.
- `.venv/bin/python -m pytest tests/integration/resultados/test_calcular_overall_integration.py tests/integration/test_p09_callback_integration.py -q`
  - Resultado: 3 passed.
- `.venv/bin/python -m pytest tests/features/steps/calcular_overall_steps.py -q`
  - Resultado: 8 passed.
- `.venv/bin/python -m pytest tests/unit/resultados/ tests/integration/resultados/test_calcular_overall_integration.py tests/integration/test_p09_callback_integration.py tests/features/steps/calcular_overall_steps.py -q`
  - Resultado: 85 passed.
- `.venv/bin/codeguard src/resultados/application/commands/calcular_overall.py`
  - Resultado: 0 errores, 0 advertencias.
- `.venv/bin/designreviewer src/resultados/ --config pyproject.toml`
  - Resultado: 0 CRITICAL, 40 warnings preexistentes/acotados al BC.

## Lecciones Aprendidas

- La proyeccion ya estaba presente en `app.py`; la deuda estaba en la ultima milla de inyeccion.
- Los BDD de US-3.5.1 eran buenos tests de regresion para preservar el comportamiento del overall.

## Riesgos

- La capa application de `resultados` importara un port del domain de `competencia`.
  Es mejor que importar infraestructura o escanear el event store, pero DesignReviewer
  puede marcarlo como cross-BC. Se validara y documentara.
- Los tests/steps BDD previos de US-3.5.1 dependen de la firma vieja del handler y
  deben actualizarse junto con el codigo.
- La proyeccion debe estar poblada antes de calcular overall; `app.py` ya lo hace en el
  flujo de `CompetenciaIniciadaHandler`/`guardar()`.

## STOP de Fase 2

No se modifica codigo de `src/` ni tests existentes hasta recibir aprobacion explicita
de este plan.
