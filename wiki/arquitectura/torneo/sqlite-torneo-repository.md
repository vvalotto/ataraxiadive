---
title: "Torneo — SQLiteTorneoRepository"
type: arquitectura-componente
bc: torneo
capa: infrastructure
tipo_componente: repository
responsabilidad: "Persistencia CRUD del aggregate Torneo en torneo.db con serialización JSON para value objects compuestos"
interfaces_out: []
adr_refs: [ADR-007]
last_updated: "2026-05-23"
sources:
  - src/torneo/infrastructure/repositories/sqlite_torneo_repository.py
us_origen:
  - US-3.1.1-aggregate-torneo-maquina-de-estados
  - US-4.1.8-limpieza-torneo-sq-lite-torneo-repository-disciplina
  - US-5.6.2-tipo-reglamento-en-torneo-di-en-calcular-ranking
tests:
  - tests/features/US-3.1.1-aggregate-torneo.feature
  - tests/integration/torneo/test_torneo_domain_integration.py
---

# SQLiteTorneoRepository

Implementa `TorneoRepositoryPort`. Persiste el aggregate `Torneo` completo en una sola tabla `torneos` de `torneo.db`.

## Tabla: `torneos`

| Columna | Tipo | Notas |
|---------|------|-------|
| `torneo_id` | TEXT PK | UUID string |
| `nombre` | TEXT NOT NULL | |
| `descripcion` | TEXT NOT NULL | |
| `fecha_inicio` | TEXT NOT NULL | ISO-8601 |
| `fecha_fin` | TEXT NOT NULL | ISO-8601 |
| `sede` | TEXT NOT NULL | JSON `{nombre, ciudad, pais}` |
| `entidad` | TEXT NOT NULL | JSON `{nombre, tipo}` |
| `estado` | TEXT NOT NULL | StrEnum value |
| `disciplinas_torneo` | TEXT NOT NULL | JSON array de `{disciplina, juez_id}` — default `[]` |
| `tipo_reglamento` | TEXT NOT NULL | default `'FAAS'` |
| `grupos_etarios` | TEXT NOT NULL | JSON array de strings — default `["SENIOR"]` |

## Estrategia de serialización

Los Value Objects compuestos (Sede, EntidadOrganizadora, DisciplinaTorneo) se serializan como JSON en columnas TEXT — no hay tablas de detalle. `DisciplinaTorneo.to_dict()` / `from_dict()` gestionan la serialización.

`grupos_etarios` se serializa usando `ordenar_grupos_etarios()` para garantizar orden consistente en el JSON.

## Auto-migration

```python
async def _ensure_table(self, conn) -> None:
    await conn.execute(_CREATE_TABLE)
    for migration in (
        _ADD_DISCIPLINAS_COLUMN,
        _ADD_TIPO_REGLAMENTO_COLUMN,
        _ADD_GRUPOS_ETARIOS_COLUMN,
    ):
        try:
            await conn.execute(migration)
        except Exception:
            pass  # columna ya existe
```

Misma estrategia que BC Registro: migraciones inline, silenciosas. Tres columnas fueron añadidas evolutivamente (disciplinas en INC-3.4, tipo_reglamento y grupos_etarios en SP5).

## Métodos

| Método | Descripción |
|--------|-------------|
| `save(torneo)` | `INSERT OR REPLACE` — upsert completo |
| `find_by_id(torneo_id)` | Retorna `Torneo \| None` |
| `find_all()` | Lista todos los torneos |

## Relaciones

**Contenedor:** [[arquitectura/torneo]]

- Implementa `TorneoRepositoryPort` definido en `torneo/domain/ports/`
- Instanciado en [[router-torneo]] via `_repo()`
- Su DB (`torneo.db`) es leída también por BC Registro via [[torneo-consulta-port]] — acceso cross-BC directo (misma estrategia que `registro.db` / `AtletaNombreAdapter`)

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py` | Repositorio CRUD del aggregate Torneo en torneo.db |
