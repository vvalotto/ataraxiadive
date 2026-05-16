# Plan US-ADJ-11.2 — Agregar/Quitar Rol a Usuario

**Branch:** feature/US-ADJ-11.2-agregar-quitar-rol
**Estimación total:** 60 min

---

## Tareas

### T1 — Domain: excepciones nuevas (5 min)
- `RolNoRemovible(rol)` — quitar ATLETA → 409
- `UltimoRolNoRemovible()` — quitar último rol → 409
- Archivo: `src/identidad/domain/exceptions.py`

### T2 — Domain: métodos en Usuario aggregate (10 min)
- `agregar_rol(rol: Rol) -> None` — INV-11.2-01/02
- `quitar_rol(rol: Rol) -> None` — INV-11.2-03/04/05
- Archivo: `src/identidad/domain/aggregates/usuario.py`

### T3 — Application: AgregarRolUsuarioCommand + Handler (10 min)
- `AgregarRolUsuarioCommand(usuario_id: UUID, nuevo_rol: Rol)`
- `AgregarRolUsuarioHandler(repo).handle(cmd) -> list[Rol]`
- Archivo nuevo: `src/identidad/application/commands/agregar_rol_usuario.py`

### T4 — Application: QuitarRolUsuarioCommand + Handler (10 min)
- `QuitarRolUsuarioCommand(usuario_id: UUID, rol: Rol)`
- `QuitarRolUsuarioHandler(repo).handle(cmd) -> list[Rol]`
- Archivo nuevo: `src/identidad/application/commands/quitar_rol_usuario.py`

### T5 — API: endpoints POST y DELETE (15 min)
- `POST /auth/usuarios/me/roles` — body `{"rol": "JUEZ"}`
- `DELETE /auth/usuarios/me/roles/{rol}` — path param
- Ambos usan `get_current_user`, retornan `{"roles": [...]}`
- Manejo: 409 RolYaAsignado/RolNoRemovible/UltimoRolNoRemovible, 404 RolNoEncontrado, 403 RolNoPermitido
- Archivo: `src/identidad/api/router.py`

### T6 — Tests unitarios domain + handlers (5 min est, real en Fase 4)
### T7 — Tests integración + BDD (5 min est, real en Fases 5-6)

---

## Archivos impactados

| Archivo | Tipo de cambio |
|---------|---------------|
| `src/identidad/domain/exceptions.py` | Agregar 2 excepciones |
| `src/identidad/domain/aggregates/usuario.py` | Agregar 2 métodos |
| `src/identidad/application/commands/agregar_rol_usuario.py` | Nuevo |
| `src/identidad/application/commands/quitar_rol_usuario.py` | Nuevo |
| `src/identidad/api/router.py` | 2 endpoints nuevos |
