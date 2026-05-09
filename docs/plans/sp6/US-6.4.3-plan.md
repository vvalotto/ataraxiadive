# Plan de Implementacion: US-6.4.3 - Routers sin imports cross-BC de infraestructura

**Patron:** Hexagonal DDD BC-first
**Producto:** arquitectura / resultados / competencia
**Incremento:** INC-6.4 - Deuda Tecnica Sistema
**Estimacion total:** 2h 15min
**Estado:** Completado

## Contexto Validado

- La US existe en `docs/specs/sp6/US-6.4.3.md`.
- `src/resultados/api/router.py` importa infraestructura de otros BCs:
  - `competencia.infrastructure.repositories.sqlite_competencias_por_torneo`
  - `torneo.infrastructure.repositories.sqlite_torneo_repository`
- `src/competencia/api/router.py` importa infraestructura de otro BC:
  - `registro.infrastructure.repositories.sqlite_inscripcion_repository`
- Los ports existen:
  - `torneo.domain.ports.torneo_repository_port.TorneoRepositoryPort`
  - `registro.domain.ports.inscripcion_repository_port.InscripcionRepositoryPort`
  - `competencia.domain.ports.competencias_por_torneo_port.CompetenciasPorTorneoPort`
- `src/app.py` ya importa los concretos necesarios y es el composition root correcto para
  construirlos.
- En `registro`, `UploadFile` y `Path` estan limitados a `registro/api/router.py`; no aparecen
  en `registro/domain` ni `registro/application`.

## Decisiones de Diseno

- Los routers mantendran funciones dependency provider, pero sin importar concretos cross-BC.
- Se agregaran funciones `configure_*` para que `app.py` inyecte factories concretas al importar
  la aplicacion.
- Los routers tiparan dependencias cross-BC con ports, no con implementaciones SQLite.
- `ExportarResultadosHandler` tambien se ajustara para tipar sus dependencias con ports cuando
  hoy expone concretos cross-BC. Esto evita que el problema se desplace del router al handler.
- No se moveran adapters de infraestructura propios del mismo BC en esta US; el alcance formal
  es cross-BC de infraestructura.

## Componentes a Modificar

### 1. Resultados API router

- [x] `src/resultados/api/router.py` (35 min)
  - Eliminar imports de:
    - `competencia.infrastructure.repositories.sqlite_competencias_por_torneo`
    - `torneo.infrastructure.repositories.sqlite_torneo_repository`
  - Importar ports:
    - `CompetenciasPorTorneoPort`
    - `TorneoRepositoryPort`
  - Agregar factories configurables para:
    - proyeccion `competencias_por_torneo`
    - repositorio de torneo
  - Actualizar `get_competencias_por_torneo_projection()` y `get_torneo_repository()`
    para devolver ports.
  - Mantener behavior de `get_exportar_resultados_handler()`.

### 2. Competencia API router

- [x] `src/competencia/api/router.py` (35 min)
  - Eliminar import de `registro.infrastructure.repositories.sqlite_inscripcion_repository`.
  - Importar `InscripcionRepositoryPort`.
  - Agregar factory configurable de repositorio de inscripciones.
  - Actualizar `get_generar_grilla_handler()` para recibir:
    - `CompetenciasPorTorneoProjectionDep`
    - `InscripcionRepositoryDep`
  - Pasar esos ports a `PerformancesAPAdapter`.

### 3. Composition root

- [x] `src/app.py` (20 min)
  - Importar las nuevas funciones `configure_*` de ambos routers.
  - Configurar factories concretas:
    - `SQLiteCompetenciasPorTorneo`
    - `SQLiteTorneoRepository`
    - `SQLiteInscripcionRepository`
  - Hacerlo antes de que los endpoints sean usados. Como `Depends` resuelve en runtime,
    puede configurarse antes o despues de `include_router`; se preferira antes del include
    si el orden de imports lo permite.

### 4. Handler de exportacion

- [x] `src/resultados/application/queries/exportar_resultados.py` (25 min)
  - Reemplazar tipos concretos cross-BC por ports:
    - `SQLiteCompetenciasPorTorneo` -> `CompetenciasPorTorneoPort`
    - `SQLiteTorneoRepository` -> `TorneoRepositoryPort`
  - Eliminar imports de infraestructura de `competencia` y `torneo`.
  - Mantener `EventStorePort` y adapters propios de resultados.

### 5. Tests y BDD

- [x] `tests/features/US-6.4.3-routers-sin-infra-crossbc.feature` (10 min)
  - Escenarios BDD creados.
- [x] Tests de routers existentes (20 min)
  - `tests/unit/resultados/api/test_router_export.py`
  - `tests/unit/competencia/api/test_generar_grilla_endpoint.py`
  - `tests/integration/competencia/test_generar_grilla_api.py`
- [x] Agregar test de imports cross-BC (20 min)
  - Verificar que `resultados/api/router.py` no contiene imports de `competencia.infrastructure`
    ni `torneo.infrastructure`.
  - Verificar que `competencia/api/router.py` no contiene imports de `registro.infrastructure`.
  - Verificar que `registro/domain` y `registro/application` no contienen `UploadFile` ni `Path`.

### 6. Quality Gates

- [x] Tests de API acotados (10 min)
  - `.venv/bin/python -m pytest tests/unit/resultados/api/test_router_export.py tests/unit/competencia/api/test_generar_grilla_endpoint.py -q`
- [x] Integracion grilla API (10 min)
  - `.venv/bin/python -m pytest tests/integration/competencia/test_generar_grilla_api.py -q`
- [x] Tests de import/arquitectura de esta US (10 min)
- [x] DesignReviewer (15 min)
  - `.venv/bin/designreviewer src/ --config pyproject.toml`
  - Criterio: 0 CRITICAL nuevos; documentar D(registro).
- [x] Busquedas directas (5 min)
  - `grep -R "from competencia.infrastructure\\|from torneo.infrastructure" src/resultados/api/router.py`
  - `grep -R "from registro.infrastructure" src/competencia/api/router.py`

### 7. Documentacion y Reporte

- [x] Actualizar `CHANGELOG.md` (5 min).
- [x] Actualizar este plan con resultados de validacion en Fase 8 (5 min).
- [x] Generar `docs/reports/US-6.4.3-report.md` en Fase 9 (10 min).

## Resultados de Validacion

- `.venv/bin/python -m pytest tests/unit/test_us_6_4_3_architecture.py tests/unit/resultados/api/test_router_export.py tests/unit/competencia/api/test_generar_grilla_endpoint.py tests/integration/competencia/test_generar_grilla_api.py -q`
  - `10 passed`
- `.venv/bin/python -m pytest tests/unit/resultados tests/unit/competencia/api tests/integration/competencia/test_generar_grilla_api.py tests/integration/resultados -q`
  - `95 passed`
- `.venv/bin/python -m pytest tests/unit/resultados tests/unit/competencia/api tests/integration/competencia/test_generar_grilla_api.py tests/integration/resultados tests/integration/registro/test_adjuntos_inscripcion_endpoint.py tests/unit/test_us_6_4_3_architecture.py -q`
  - `102 passed`, `4 warnings` (`datetime.utcnow()` preexistente en fixture)
- `.venv/bin/ruff check src/resultados/api/router.py src/competencia/api/router.py src/resultados/application/queries/exportar_resultados.py src/app.py tests/unit/test_us_6_4_3_architecture.py`
  - `All checks passed`
- `.venv/bin/codeguard src/resultados/api/router.py src/competencia/api/router.py src/resultados/application/queries/exportar_resultados.py src/app.py src/registro/api/router.py src/registro/domain/ports/adjunto_storage_port.py src/registro/infrastructure/adjuntos/local_adjunto_storage.py tests/unit/test_us_6_4_3_architecture.py`
  - `0 errores`, `1 advertencia` (`src/app.py:575`, complejidad preexistente), `26 informativos`
- `.venv/bin/designreviewer src/ --config pyproject.toml`
  - `0 blocking issues (CRITICAL)`, `256 advertencias (WARNING)`
- `.venv/bin/architectanalyst src/ --format text`
  - `3 CRITICAL`, `62 WARNING`, `408 INFO`
  - Criticos por D preexistente: `identidad D=0.67`, `registro D=0.57`, `shared D=0.63`
  - `registro` mejora de `D=0.59` a `D=0.57` (`A=0.10`, `I=0.33`, tendencia `improving`).
- Busquedas directas:
  - `grep -n "competencia.infrastructure\|torneo.infrastructure" src/resultados/api/router.py` sin coincidencias
  - `grep -n "registro.infrastructure" src/competencia/api/router.py` sin coincidencias

## Riesgos

- Los routers ya importan infraestructura propia del mismo BC. Esta US no corrige todo el
  acoplamiento router-infra, solo imports de infraestructura de otros BCs.
- `ExportarResultadosHandler` usa varios colaboradores; cambiar tipos a ports debe conservar
  runtime porque los concretos implementan esos contratos.
- `DesignReviewer` puede reportar warnings preexistentes en `registro` y `resultados`; se
  documentaran si no son causados por esta US.

## STOP de Fase 2

No se modifica codigo de `src/` ni tests existentes hasta recibir aprobacion explicita
de este plan.
