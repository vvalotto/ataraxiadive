---
title: "Registro — SQLite Repositories (×4)"
type: arquitectura-componente
bc: registro
capa: infrastructure
tipo_componente: repository
responsabilidad: "Persistencia CRUD de los 4 aggregates de BC Registro en registro.db via aiosqlite"
interfaces_out: []
adr_refs: [ADR-005, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/registro/infrastructure/repositories/sqlite_atleta_repository.py
  - src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py
  - src/registro/infrastructure/repositories/sqlite_juez_repository.py
  - src/registro/infrastructure/repositories/sqlite_organizador_repository.py
us_origen:
  - US-3.2.2-aggregate-atleta-registro-consulta-y-repositorio-sq
  - US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar
  - US-6.4.5-refactoring-declarar-ap-inscripcion-handler-sq-lite
  - US-ADJ-11.4-entidad-juez-juez-repository-port-endpoints-registro
  - US-ADJ-11.5-entidad-organizador-organizador-repository-port
---

# SQLite Repositories — BC Registro

Cuatro repositorios que implementan los puertos definidos en `domain/ports/`. Todos usan `aiosqlite` contra `registro.db` y siguen el mismo patrón de self-migration de tabla.

## Patrón común

```python
class SQLite<X>Repository(<X>RepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn) -> None:
        await conn.execute(CREATE_TABLE)
        await conn.commit()
```

- `_ensure_table` crea la tabla si no existe (DDL inline) — no hay Alembic ni migrations externas
- `INSERT OR REPLACE` para `save()` — upsert implícito
- `find_by_id` / `find_by_email` para lookup — retornan `None` si no existe

---

## SQLiteAtletaRepository

Tabla: `atletas`

| Columna | Tipo | Notas |
|---------|------|-------|
| `atleta_id` | TEXT PK | UUID string |
| `nombre` | TEXT NOT NULL | |
| `apellido` | TEXT NOT NULL | |
| `email` | TEXT NOT NULL UNIQUE | |
| `fecha_nacimiento` | TEXT | ISO-8601; nullable (migración dinámica elimina NOT NULL legacy) |
| `categoria` | TEXT | StrEnum Categoria |
| `club` | TEXT | |
| `brevet` | TEXT | |
| `dni` | TEXT | columna añadida por `_ensure_columns` |
| `telefono` | TEXT | columna añadida por `_ensure_columns` |

**Migración dinámica**: `_migrate_fecha_nacimiento_nullable` recrea la tabla si la columna tenía `NOT NULL` en versiones previas. Ejemplo de migración evolutiva sin Alembic.

**Métodos**: `save`, `find_by_id`, `find_by_email`

---

## SQLiteInscripcionRepository

Tabla: `inscripciones`

| Columna | Tipo | Notas |
|---------|------|-------|
| `inscripcion_id` | TEXT PK | UUID |
| `atleta_id` | TEXT | FK lógica a `atletas` |
| `torneo_id` | TEXT | FK lógica a BC Torneo |
| `disciplinas` | TEXT | JSON array de strings (ej. `["STA","DNF"]`) |
| `estado` | TEXT | `ACTIVA` / `CANCELADA` |
| `fecha_inscripcion` | TEXT | ISO-8601 datetime |
| `ap_por_disciplina` | TEXT | JSON dict `{disciplina: {valor, unidad}}` |
| `apto_medico_path` | TEXT | nullable |
| `constancia_pago_path` | TEXT | nullable |

**Métodos**: `save`, `find_by_id`, `find_by_atleta_y_torneo`, `find_by_atleta`, `find_active_by_torneo`

El campo `ap_por_disciplina` serializa `APDeclarado` a JSON — reconstitución via `from_row()` en el aggregate.

---

## SQLiteJuezRepository

Tabla: `jueces`

| Columna | Tipo |
|---------|------|
| `juez_id` | TEXT PK |
| `email` | TEXT NOT NULL UNIQUE |
| `numero_licencia` | TEXT |
| `federacion` | TEXT |

**Métodos**: `save`, `find_by_id`, `find_by_email`

---

## SQLiteOrganizadorRepository

Tabla: `organizadores`

| Columna | Tipo |
|---------|------|
| `organizador_id` | TEXT PK |
| `email` | TEXT NOT NULL UNIQUE |
| `nombre_organizacion` | TEXT |

**Métodos**: `save`, `find_by_id`, `find_by_email`

---

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Implementan [[atleta-repository-port]], [[inscripcion-repository-port]], [[juez-repository-port]], [[organizador-repository-port]]
- Instanciados directamente en [[router-registro]] via funciones `_repo()`, `_juez_repo()`, etc. (sin DI container)
- `SQLiteAtletaRepository` es leído también por BC Competencia via [[atleta-nombre-port]] (acceso directo a `registro.db`)

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Repositorio CRUD de Atleta en registro.db |
| `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` | Repositorio CRUD de Inscripcion en registro.db |
| `src/registro/infrastructure/repositories/sqlite_juez_repository.py` | Repositorio CRUD de Juez en registro.db |
| `src/registro/infrastructure/repositories/sqlite_organizador_repository.py` | Repositorio CRUD de Organizador en registro.db |
