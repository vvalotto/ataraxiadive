---
title: "Identidad — SQLiteUsuarioRepository"
type: arquitectura-componente
bc: identidad
capa: infrastructure
tipo_componente: repository
responsabilidad: "Persistencia CRUD de Usuario en identidad.db — roles como JSON array, migración rol→roles"
interfaces_out: []
adr_refs: [ADR-007, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/identidad/infrastructure/repositories/sqlite_usuario_repository.py
---

# SQLiteUsuarioRepository

Implementa `UsuarioRepositoryPort`. Tabla `usuarios` en `identidad.db`.

## Tabla: `usuarios`

| Columna | Tipo | Notas |
|---------|------|-------|
| `usuario_id` | TEXT PK | UUID |
| `nombre` | TEXT NOT NULL | Default `''` — añadido en ADR-020 |
| `apellido` | TEXT NOT NULL | Default `''` — añadido en ADR-020 |
| `email` | TEXT UNIQUE NOT NULL | |
| `password_hash` | TEXT NOT NULL | bcrypt |
| `rol` | TEXT NOT NULL | Legacy — columna original (single rol) |
| `activo` | INTEGER NOT NULL | 1/0 |
| `roles` | TEXT NOT NULL | JSON array `["ATLETA","JUEZ"]` — ADR-020 |

## Migración: rol → roles (ADR-020)

`_migrate_rol_to_roles()` convierte filas legacy que tienen `rol='X'` pero `roles='["ATLETA"]'` (default):

```sql
UPDATE usuarios
SET roles = json_array(rol)
WHERE roles = '["ATLETA"]' AND rol != 'ATLETA'
```

Y repara cualquier `roles` con JSON inválido. Se ejecuta en cada `_ensure_table()` — idempotente.

## Métodos

| Método | Descripción |
|--------|-------------|
| `save(usuario)` | `INSERT OR REPLACE` — upsert |
| `find_by_id(usuario_id)` | Retorna `Usuario \| None` |
| `find_by_email(email)` | Lookup por email |
| `list_by_rol(rol)` | `WHERE roles LIKE '%"ROL"%'` — búsqueda en JSON string |
| `list_all()` | Todos los usuarios, ordenados por email |

`list_by_rol` usa `LIKE` sobre el JSON text serializado — funcional pero no indexado. Para volúmenes pequeños (usuarios de un torneo) es suficiente.

## Relaciones

- Implementa `UsuarioRepositoryPort` de `domain/ports/`
- Instanciado via `get_usuario_repository()` en [[dependencies-identidad]]
- Sus datos son la fuente de verdad de autenticación — todos los BCs confían en el JWT generado a partir de aquí
