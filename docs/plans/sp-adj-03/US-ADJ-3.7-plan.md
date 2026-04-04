# Plan de Implementacion — US-ADJ-3.7

## Resumen

Materializar la proyeccion `competencias_por_torneo` dentro del BC
`competencia` para que `ObtenerCompetenciasPorTorneoHandler` deje de escanear
todos los streams historicos del event store.

## Objetivo observable

- existe un puerto de lectura/escritura para la proyeccion
- existe una implementacion SQLite para `competencias_por_torneo`
- `ConfigurarIntervaloOTHandler` actualiza la proyeccion cuando recibe
  `torneo_id`
- `ObtenerCompetenciasPorTorneoHandler` deja de depender de
  `load_all_streams_with_prefix`
- el router inyecta la proyeccion en lugar del event store para esa query

## Alcance

- `src/competencia/domain/ports/competencias_por_torneo_port.py`
- `src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py`
- `src/competencia/application/commands/configurar_intervalo_ot.py`
- `src/competencia/application/queries/obtener_competencias_por_torneo.py`
- `src/competencia/api/router.py`
- tests unitarios e integracion del flujo torneo -> competencia
- artefactos de tracking, calidad y reporte de la US

No incluye:

- worker asincrono o projector desacoplado
- migracion/backfill de datos historicos
- activos BDD nuevos

## Decisiones de diseño

1. Usar la misma DB de `COMPETENCIA_DB_PATH` para alojar la proyeccion. SQLite
   ya esta disponible en ese archivo y evita sumar una nueva configuracion.
2. Implementar la proyeccion en `infrastructure/repositories/` para seguir el
   patron ya usado por adapters SQLite del BC.
3. Actualizar la proyeccion de forma sincronica dentro de
   `ConfigurarIntervaloOTHandler`, inmediatamente despues de persistir
   `IntervaloOTConfigurado`.
4. Mantener `CompetenciaSummaryDTO` como contrato de lectura y reusarlo tanto
   en el handler como en la proyeccion.

## Implementacion por area

### Dominio

- crear `CompetenciasPorTorneoPort` con:
  - `guardar(dto)`
  - `listar_por_torneo(torneo_id)`

### Infraestructura

- crear `SQLiteCompetenciasPorTorneo`
- asegurar creacion idempotente de tabla e indice
- implementar `upsert` por `competencia_id`
- listar por `torneo_id`

### Aplicacion

- refactorizar `ObtenerCompetenciasPorTorneoHandler` para depender del nuevo
  puerto
- extender `ConfigurarIntervaloOTHandler` para actualizar la proyeccion cuando
  `command.torneo_id` no es `None`

### API / wiring

- agregar provider de proyeccion en `competencia/api/router.py`
- inyectar esa dependencia en el query handler
- inyectar la misma proyeccion en `ConfigurarIntervaloOTHandler`

## Validacion prevista

- `tests/unit/competencia/application/test_obtener_competencias_por_torneo.py`
- `tests/integration/competencia/test_torneo_id_integration.py`
- `grep "load_all_streams_with_prefix" src/competencia/application/queries/obtener_competencias_por_torneo.py`
- `py_compile` de archivos impactados
- `CodeGuard` sobre `application`, `api`, `ports` e `infrastructure`
- `git diff --check`

## Riesgos a controlar

1. desalinear el resultado de la proyeccion respecto del comportamiento previo
2. olvidar crear la tabla antes de usarla en tests/integracion
3. introducir acoplamiento circular entre DTO de aplicacion y puerto

## Artefactos esperados al cierre

- proyeccion materializada `competencias_por_torneo`
- query handler O(1) respecto del total de streams historicos
- wiring actualizado en API
- `docs/reports/US-ADJ-3.7-report.md`
