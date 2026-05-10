# Reporte Final: US-6.4.5 - Refactor registro DesignReviewer

**Fecha:** 2026-05-09  
**Incremento:** INC-6.4 - Deuda Tecnica Sistema  
**Producto / BC:** registro  
**Estado:** Completada

## Resumen

Se resolvio DR-07 en `SQLiteInscripcionRepository` moviendo la reconstitucion de
`Inscripcion` a `Inscripcion.from_row()` y extrayendo helpers de serializacion/esquema fuera de
metodos largos del repositorio.

DR-06 en `DeclararAPInscripcionHandler` se investigo y quedo documentado como falso positivo
estructural: el handler solo coordina carga, metodo de dominio y persistencia.

## Cambios Implementados

- `src/registro/domain/aggregates/inscripcion.py`
  - Agrega `Inscripcion.from_row(data)` para reconstituir desde datos planos.
  - Encapsula parsing de `disciplinas`, `ap_por_disciplina`, IDs, fecha, estado y adjuntos.
- `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
  - `_row_to_inscripcion()` delega en `Inscripcion.from_row(_row_to_dict(row))`.
  - `save()` usa `_UPSERT_INSCRIPCION` y `_inscripcion_to_values()`.
  - `_ensure_schema()` y `_ensure_table()` quedan como helpers de modulo.
  - El repositorio deja de importar `APDeclarado`, `Disciplina`, `UnidadMedida`, `Decimal` y
    `datetime`.
- `tests/unit/registro/test_inscripcion.py`
  - Cobertura de `from_row()` con AP, estado, fecha, disciplinas y adjuntos.
  - Cobertura de `from_row()` con AP vacio.
- `tests/integration/registro/test_sqlite_inscripcion_repository.py`
  - Round-trip SQLite de AP por disciplina.
- Documentacion actualizada en `CHANGELOG.md`, spec, trazabilidad y plan SP6.

## Evidencia de Validacion

| Gate | Resultado |
| --- | --- |
| `pytest tests/unit/registro/test_inscripcion.py tests/integration/registro/test_sqlite_inscripcion_repository.py -q` | `23 passed` |
| `pytest tests/unit/registro -q` | `42 passed` |
| `pytest tests/integration/registro -q` | `25 passed` |
| `pytest tests/unit/registro tests/integration/registro -q` | `67 passed` |
| `designreviewer declarar_ap_inscripcion.py sqlite_inscripcion_repository.py` | DR-07 eliminado; solo queda DR-06 documentado |
| `codeguard inscripcion.py sqlite_inscripcion_repository.py` | `0 errores`, `0 advertencias`, `6 informativos` |
| `ruff check <archivos Python tocados>` | OK |
| `black --check <archivos Python tocados>` | OK |
| `isort --check-only <archivos Python tocados>` | OK |

## Criterios de Aceptacion

- DR-06 investigado: no hay logica de negocio en el handler; se documenta como no aplicable.
- `SQLiteInscripcionRepository` usa `Inscripcion.from_row()` para reconstitucion.
- El repositorio no importa `APDeclarado`, `Disciplina` ni `UnidadMedida` directamente.
- La reconstitucion preserva adjuntos y AP por disciplina.
- La suite de `registro` pasa completa.

## Observaciones

- DesignReviewer conserva una advertencia en `DeclararAPInscripcionHandler` por FeatureEnvy `4/2`.
  La decision de esta US es no refactorizar ese handler porque responde al patron normal de
  coordination handler en application layer.
- El refactor no cambia esquema SQLite ni formato JSON persistido.
- Persisten warnings de tests por `datetime.utcnow()` preexistente, fuera del alcance de esta US.

## Siguiente Paso

Preparar commit y PR de `feature/US-6.4.5-refactor-registro` hacia `develop`.
