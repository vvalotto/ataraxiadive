# Plan US-ADJ-11.1 — BC Identidad multi-rol

**Branch:** `feature/US-ADJ-11.1-identidad-multi-rol`
**Estimado total:** 90 min

---

## Tareas

### T1 — Domain: Usuario.roles + excepciones nuevas (10 min)
- `src/identidad/domain/aggregates/usuario.py`: `rol: Rol` → `roles: list[Rol]`
- `src/identidad/domain/exceptions.py`: agregar `RolYaAsignado`, `RolNoEncontrado`

### T2 — Port + Infra JWT: generate con rol_activo (10 min)
- `src/identidad/domain/ports/token_service_port.py`: `generate(usuario, rol_activo: Rol) -> str`
- `src/identidad/infrastructure/jwt_service.py`: `generate(usuario, rol_activo)` usa `rol_activo.value`

### T3 — Infra Repo: migración DB + serialización JSON (15 min)
- `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py`:
  - ADD COLUMN `roles TEXT NOT NULL DEFAULT '["ATLETA"]'`
  - Migración: UPDATE existentes (`rol` → `roles` JSON)
  - `save()`: serializa `json.dumps([r.value for r in usuario.roles])`
  - `find_by_*()`: deserializa `[Rol(r) for r in json.loads(roles_str)]`
  - `list_by_rol()`: filtro `WHERE roles LIKE '%"ROL"%'`
  - `_row_to_usuario()`: 8 columnas (agrega `roles`)

### T4 — Application: RegistrarUsuarioHandler (20 min)
- `src/identidad/application/commands/registrar_usuario.py`:
  - `RegistrarUsuarioCommand.roles: list[Rol]` (reemplaza `rol: Rol`)
  - Nuevo `RegistroResult(usuario_id, token_response, roles_disponibles)`
  - Handler inyecta `token_service: TokenServicePort`
  - Lógica: si email existe → validar password → agregar roles (o lanzar `RolYaAsignado`)
  - Respuesta: token si 1 rol, `roles_disponibles` si varios

### T5 — Application: AutenticarUsuarioHandler (10 min)
- `src/identidad/application/commands/autenticar_usuario.py`:
  - `AutenticarUsuarioCommand.rol_elegido: Rol | None = None`
  - Nuevo `RoleSelectionRequired(roles: list[Rol])`
  - Lógica: 1 rol → token; N roles sin `rol_elegido` → `RoleSelectionRequired`; `rol_elegido` fuera de roles → `CredencialesInvalidas`

### T6 — API Router: schemas + endpoints (15 min)
- `src/identidad/api/router.py`:
  - `RegistroRequest.roles: list[Rol]` (reemplaza `rol: Rol`)
  - `LoginRequest.rol_elegido: Rol | None = None`
  - `UsuarioResponse.roles: list[Rol]`
  - `/registro`: inyecta `token_service`; discrimina `RegistroResult` (201 new / 200 add-roles)
  - `/login`: discrimina `TokenResponse | RoleSelectionRequired`
  - `listar_usuarios`: serializa `roles` como lista

### T7 — Actualizar tests existentes (10 min)
- Cambio sistemático `rol=Rol.X` → `roles=[Rol.X]` en constructores `Usuario()`
- Cambio `RegistrarUsuarioCommand(rol=)` → `roles=[]`
- `generate(usuario)` → `generate(usuario, rol_activo)` en tests
- `_make_usuario()` helper actualizado
- US-3.2.1 BDD steps: `"rol": x` → `"roles": [x]`

---

## Archivos afectados

| Archivo | Tipo de cambio |
|---------|---------------|
| `src/identidad/domain/aggregates/usuario.py` | Refactor |
| `src/identidad/domain/exceptions.py` | Agregar |
| `src/identidad/domain/ports/token_service_port.py` | Refactor |
| `src/identidad/infrastructure/jwt_service.py` | Refactor |
| `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py` | Refactor + migración |
| `src/identidad/application/commands/registrar_usuario.py` | Refactor |
| `src/identidad/application/commands/autenticar_usuario.py` | Refactor |
| `src/identidad/api/router.py` | Refactor |
| `tests/unit/identidad/domain/test_usuario.py` | Actualizar |
| `tests/unit/identidad/application/test_handlers.py` | Actualizar + nuevos tests |
| `tests/unit/identidad/api/test_*.py` (4 archivos) | Actualizar |
| `tests/integration/identidad/test_sqlite_usuario_repository.py` | Actualizar |
| `tests/integration/identidad/test_registro_email_handler.py` | Actualizar |
| `tests/features/steps/identidad_jwt_steps.py` | Actualizar |
| `tests/features/US-3.2.1-bc-identidad-jwt.feature` | Actualizar |
| `tests/features/steps/adj_11_1_multi_rol_steps.py` | Nuevo |

---

## Riesgos

- **R4 (confirmado):** Tests existentes de handlers usan `rol=Rol.X` — todos rompen con T1. Resolver en T7.
- **R1:** Migración DB — `_ensure_column` + UPDATE solo si columna `rol` existe.
- Columna `rol` se mantiene como legacy (no se elimina) para migración incremental.
