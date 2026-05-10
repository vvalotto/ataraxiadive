# Plan de Implementacion: US-6.4.5 - Refactor registro DesignReviewer

**Patron:** Hexagonal DDD BC-first  
**Producto:** registro  
**Incremento:** INC-6.4 - Deuda Tecnica Sistema  
**Estimacion total:** 2h 30min  
**Estado:** Completado

## Contexto Validado

- La US existe en `docs/specs/sp6/US-6.4.5.md`.
- El BC afectado es `registro`.
- El handler existe en `src/registro/application/commands/declarar_ap_inscripcion.py`.
- El repositorio existe en
  `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`.
- El aggregate existe en `src/registro/domain/aggregates/inscripcion.py`.
- Tests existentes relevantes:
  - `tests/unit/registro/test_inscripcion.py`
  - `tests/integration/registro/test_sqlite_inscripcion_repository.py`
- DesignReviewer reproduce los hallazgos iniciales:
  - `DeclararAPInscripcionHandler`: FeatureEnvy `4/2`.
  - `SQLiteInscripcionRepository`: FanOut `9/7`, FeatureEnvy `7/0` y `9/2`,
    LongMethod `40/20`.

## Diagnostico DR-06

`DeclararAPInscripcionHandler` implementa el patron esperado de application layer:

1. carga el aggregate desde el puerto de repositorio;
2. valida ausencia con excepcion de dominio;
3. delega la regla de negocio en `inscripcion.declarar_ap()`;
4. persiste el aggregate.

No hay condiciones, calculos ni validaciones de negocio propias del handler. Por lo tanto, DR-06 se
trata como falso positivo estructural del analyzer para coordination handlers. El codigo del handler
no se modificara salvo que durante tests aparezca evidencia contraria.

## Decisiones de Diseno

- Mantener el handler sin cambios funcionales.
- Agregar `Inscripcion.from_row(data: Mapping[str, Any]) -> Inscripcion` como factory de
  reconstitucion desde datos planos.
- Mover el parsing de `disciplinas`, `ap_por_disciplina`, fechas e IDs al aggregate.
- Reducir `SQLiteInscripcionRepository._row_to_inscripcion()` a conversion de `aiosqlite.Row` a
  `dict` + llamada a `Inscripcion.from_row()`.
- El repositorio debe dejar de importar `APDeclarado`, `Disciplina`, `UnidadMedida`, `Decimal`,
  `datetime` y `UUID` si ya no los usa directamente.
- Mantener `EstadoInscripcion` en el repositorio si se sigue usando para query de activas.
- Extraer serializacion de `save()` a helpers de modulo para eliminar LongMethod y FeatureEnvy
  remanentes en el repositorio.
- No cambiar esquema SQLite ni formato JSON persistido.

## Componentes a Modificar

### 1. Aggregate `Inscripcion`

- [x] `src/registro/domain/aggregates/inscripcion.py` (35 min)
  - Importar dependencias necesarias para reconstitucion (`json`, `Any`, `Mapping`,
    `Decimal`, `UnidadMedida`).
  - Agregar `from_row()` tipado.
  - Encapsular reconstruccion de `ap_por_disciplina`.
  - Preservar adjuntos opcionales.

### 2. Repositorio SQLite

- [x] `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` (25 min)
  - Simplificar `_row_to_inscripcion(row)` a `Inscripcion.from_row(_row_to_dict(row))`.
  - Agregar helper privado `_row_to_dict()` si `dict(row)` no es robusto con `aiosqlite.Row`.
  - Eliminar imports huerfanos.

### 3. Tests Unitarios

- [x] `tests/unit/registro/test_inscripcion.py` (25 min)
  - Agregar test de `Inscripcion.from_row()` con disciplinas, AP, estado, fecha y adjuntos.
  - Agregar test de `from_row()` con `ap_por_disciplina` vacio.

### 4. Tests de Integracion

- [x] `tests/integration/registro/test_sqlite_inscripcion_repository.py` (20 min)
  - Agregar/ajustar test para round-trip con AP declarado.
  - Mantener test de adjuntos.
  - Mantener test legacy sin adjuntos.

### 5. BDD

- [x] `tests/features/US-6.4.5-refactor-registro-designreviewer.feature` (10 min)
  - Escenarios creados en Fase 1.
- [x] Validar escenarios por correspondencia con tests/gates (10 min)
  - No crear steps nuevos salvo que exista patron BDD automatizado aplicable.

### 6. Quality Gates

- [x] Unitarios de registro (10 min)
  - `.venv/bin/python -m pytest tests/unit/registro -q`
- [x] Integracion de registro (10 min)
  - `.venv/bin/python -m pytest tests/integration/registro -q`
- [x] Regresion registro (10 min)
  - `.venv/bin/python -m pytest tests/unit/registro tests/integration/registro -q`
- [x] DesignReviewer acotado (10 min)
  - `.venv/bin/designreviewer src/registro/application/commands/declarar_ap_inscripcion.py src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py --config pyproject.toml`
  - Criterio: DR-07 no aparece en `SQLiteInscripcionRepository`; DR-06 puede quedar documentado
    como falso positivo si el analyzer lo sigue reportando.
- [x] CodeGuard acotado (10 min)
  - `.venv/bin/codeguard src/registro/domain/aggregates/inscripcion.py src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- [x] Formato/lint acotado (10 min)
  - `.venv/bin/ruff check <archivos Python tocados>`
  - `.venv/bin/black --check <archivos Python tocados>`
  - `.venv/bin/isort --check-only <archivos Python tocados>`

### 7. Documentacion y Cierre

- [x] Documentar DR-06 como falso positivo/no aplicable de coordination handler (10 min).
- [x] Actualizar `CHANGELOG.md` (5 min).
- [x] Actualizar `docs/specs/sp6/US-6.4.5.md` a `Done` si los gates pasan (5 min).
- [x] Actualizar `docs/traceability/matrix.md` (5 min).
- [x] Generar `docs/reports/US-6.4.5-report.md` (15 min).
- [x] Actualizar este plan con resultados de validacion (5 min).

## Resultados de Validacion

- `.venv/bin/python -m pytest tests/unit/registro/test_inscripcion.py tests/integration/registro/test_sqlite_inscripcion_repository.py -q`
  - `23 passed`
- `.venv/bin/python -m pytest tests/unit/registro -q`
  - `42 passed`
- `.venv/bin/python -m pytest tests/integration/registro -q`
  - `25 passed`
- `.venv/bin/python -m pytest tests/unit/registro tests/integration/registro -q`
  - `67 passed`
- `.venv/bin/designreviewer src/registro/application/commands/declarar_ap_inscripcion.py src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py --config pyproject.toml`
  - `SQLiteInscripcionRepository`: sin DR-07, sin FanOut, sin LongMethod.
  - `DeclararAPInscripcionHandler`: conserva FeatureEnvy `4/2`, documentado como falso
    positivo estructural de coordination handler.
- `.venv/bin/codeguard src/registro/domain/aggregates/inscripcion.py src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
  - `0 errores`, `0 advertencias`, `6 informativos`
- `.venv/bin/ruff check <archivos Python tocados>`
  - `All checks passed`
- `.venv/bin/black --check <archivos Python tocados>`
  - `4 files would be left unchanged`
- `.venv/bin/isort --check-only <archivos Python tocados>`
  - OK

## Riesgos

- Mover parsing al aggregate puede aumentar fan-out del aggregate. Es aceptable si reduce el
  repositorio y no introduce imports fuera de `registro/domain` o `shared/domain`.
- DesignReviewer puede seguir reportando DR-06 por el patron normal de handler. Se documentara como
  falso positivo si no hay logica de negocio movible.
- La corrida amplia de `registro` puede exponer warnings preexistentes fuera del alcance. Se
  registraran sin reformateos masivos.

## STOP de Fase 2

No se modifica codigo de `src/` ni tests existentes hasta recibir aprobacion explicita de este plan.
