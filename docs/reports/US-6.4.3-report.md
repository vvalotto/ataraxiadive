# Reporte de Implementacion: US-6.4.3

## Resumen Ejecutivo

- **Historia de Usuario:** US-6.4.3 - Routers sin imports cross-BC de infraestructura
- **Incremento:** INC-6.4 - Deuda Tecnica Sistema
- **Producto:** arquitectura / resultados / competencia
- **Puntos estimados:** 5
- **Tiempo estimado:** 2h 15min
- **Estado:** Completado
- **Fecha completado:** 2026-05-09

## Componentes Implementados

- `src/resultados/api/router.py`
  - El router ya no importa infraestructura de `competencia` ni `torneo`.
  - Agrega `configure_resultados_cross_bc_dependencies()` para recibir factories desde el composition root.
  - Tipa dependencias cross-BC con `CompetenciasPorTorneoPort` y `TorneoRepositoryPort`.
- `src/competencia/api/router.py`
  - El router ya no importa infraestructura de `registro`.
  - Agrega `configure_competencia_cross_bc_dependencies()` para inyectar `InscripcionRepositoryPort`.
  - `get_generar_grilla_handler()` recibe la proyeccion y el repositorio por Depends tipados a ports.
- `src/app.py`
  - Configura `SQLiteCompetenciasPorTorneo`, `SQLiteTorneoRepository` y `SQLiteInscripcionRepository`
    como dependencias concretas en el composition root.
- `src/resultados/application/queries/exportar_resultados.py`
  - Reemplaza tipos concretos cross-BC por ports.
- `src/registro/domain/ports/adjunto_storage_port.py`
  - Nuevo port para persistencia de adjuntos de inscripcion.
- `src/registro/infrastructure/adjuntos/local_adjunto_storage.py`
  - Implementacion local de storage; concentra `Path`, directorios y escritura de bytes fuera
    del router.
- `src/registro/api/router.py`
  - Deja de conocer detalles de filesystem para adjuntos y usa `AdjuntoStoragePort`.
- `tests/unit/test_us_6_4_3_architecture.py`
  - Cubre imports prohibidos en routers y contencion de `UploadFile`/`Path` fuera de
    `registro/domain` y `registro/application`.

## Metricas de Calidad

| Gate | Resultado | Estado |
|------|-----------|--------|
| Tests acotados US/API | 10 passed | OK |
| Regresion BCs tocados | 102 passed | OK |
| Ruff archivos tocados | All checks passed | OK |
| CodeGuard componentes US | 0 errores, 1 advertencia, 26 informativos | OK con warning preexistente |
| Busquedas directas cross-BC | Sin coincidencias | OK |
| DesignReviewer `src/` | 0 CRITICAL, 256 warnings | OK con warnings preexistentes |
| ArchitectAnalyst `src/` | 3 CRITICAL, 62 WARNING, 408 INFO | OK con críticos preexistentes |
| D(registro) automatizado | D=0.57, tendencia improving | OK |

## Validacion Ejecutada

```bash
.venv/bin/python -m pytest tests/unit/test_us_6_4_3_architecture.py tests/unit/resultados/api/test_router_export.py tests/unit/competencia/api/test_generar_grilla_endpoint.py tests/integration/competencia/test_generar_grilla_api.py -q
# 10 passed

.venv/bin/python -m pytest tests/unit/resultados tests/unit/competencia/api tests/integration/competencia/test_generar_grilla_api.py tests/integration/resultados tests/integration/registro/test_adjuntos_inscripcion_endpoint.py tests/unit/test_us_6_4_3_architecture.py -q
# 102 passed

.venv/bin/ruff check src/resultados/api/router.py src/competencia/api/router.py src/resultados/application/queries/exportar_resultados.py src/app.py src/registro/api/router.py src/registro/domain/ports/adjunto_storage_port.py src/registro/infrastructure/adjuntos/local_adjunto_storage.py tests/unit/test_us_6_4_3_architecture.py
# All checks passed

.venv/bin/codeguard src/resultados/api/router.py src/competencia/api/router.py src/resultados/application/queries/exportar_resultados.py src/app.py src/registro/api/router.py src/registro/domain/ports/adjunto_storage_port.py src/registro/infrastructure/adjuntos/local_adjunto_storage.py tests/unit/test_us_6_4_3_architecture.py
# 0 errores; 1 advertencia; 26 informativos

grep -n "competencia.infrastructure\|torneo.infrastructure" src/resultados/api/router.py
# sin coincidencias

grep -n "registro.infrastructure" src/competencia/api/router.py
# sin coincidencias

.venv/bin/designreviewer src/ --config pyproject.toml
# 0 CRITICAL; 256 warnings

.venv/bin/architectanalyst src/ --format text
# 3 CRITICAL; 62 WARNING; 408 INFO
# Criticos D preexistentes: identidad D=0.67, registro D=0.57, shared D=0.63
# registro: A=0.10, I=0.33, Ca=4, Ce=2, tendencia improving
```

## Criterios de Aceptacion

- [x] `resultados/api/router.py` no importa `competencia.infrastructure`.
- [x] `resultados/api/router.py` no importa `torneo.infrastructure`.
- [x] `competencia/api/router.py` no importa `registro.infrastructure`.
- [x] Endpoint de exportacion conserva wiring de handler por Depends.
- [x] Generacion de grilla conserva wiring de `PerformancesAPAdapter`.
- [x] `UploadFile` y `Path` no se propagan a `registro/domain` ni `registro/application`.

## Riesgos y Observaciones

- El composition root incrementa fan-out en `app.py`, esperado para concentrar construccion de
  concretos y sacar infraestructura cross-BC de routers.
- `DesignReviewer` mantiene warnings preexistentes en varias capas, sin CRITICAL. No se abordaron
  warnings fuera del alcance de esta US.
- `CodeGuard` reporta una advertencia de complejidad en `src/app.py:575`
  (`_obtener_disciplinas_pendientes_ejecucion`, complejidad 11), no introducida por esta US.
  Los B101 de tests son informativos por uso normal de `assert` en pytest.
- `architectanalyst` falla si se usa `--config pyproject.toml` por una incompatibilidad de la
  configuracion actual (`unexpected keyword argument 'paths'`), pero la corrida sin `--config`
  ejecuta correctamente. En esa corrida, `registro` mejora de `D=0.59` a `D=0.57` con tendencia
  `improving`.

## Archivos Creados o Modificados

- `CHANGELOG.md`
- `docs/plans/sp6/US-6.4.3-plan.md`
- `docs/reports/US-6.4.3-report.md`
- `src/app.py`
- `src/competencia/api/router.py`
- `src/resultados/api/router.py`
- `src/resultados/application/queries/exportar_resultados.py`
- `src/registro/api/router.py`
- `src/registro/domain/ports/adjunto_storage_port.py`
- `src/registro/infrastructure/adjuntos/__init__.py`
- `src/registro/infrastructure/adjuntos/local_adjunto_storage.py`
- `tests/unit/test_us_6_4_3_architecture.py`

## Proximo Paso

- Continuar con US-6.4.4 del incremento INC-6.4.
