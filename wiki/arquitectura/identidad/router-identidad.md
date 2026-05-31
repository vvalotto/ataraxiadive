---
title: "Identidad — Router FastAPI + Dependencies"
type: arquitectura-componente
bc: identidad
capa: api
tipo_componente: router
responsabilidad: "API HTTP /auth: registro, login, cambio y reset de password, gestión de usuarios — con guards de rol cross-cutting"
interfaces_out: []
adr_refs: [ADR-019, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/identidad/api/router.py
  - src/identidad/api/dependencies.py
---

# Router — BC Identidad

`APIRouter(prefix="/auth", tags=["auth"])`

---

## Endpoints

| Método | Path | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/auth/registro` | público | Registrar usuario (201 nuevo / 200 agrega rol) |
| `POST` | `/auth/login` | público | Autenticar — retorna token o pide selección de rol |
| `POST` | `/auth/cambiar-password` | autenticado | Cambia password con verificación actual (204) |
| `POST` | `/auth/solicitar-reset` | público | Envía email de reset (200 siempre, anti-enumeración) |
| `POST` | `/auth/reset-password` | público | Aplica reset con token (204) |
| `GET` | `/auth/usuarios` | `OrganizadorDep` | Lista usuarios, filtrables por `?rol=X` |

---

## Lógica multi-rol en login y registro

**Registro** — si el usuario tiene múltiples roles después del registro:
```json
{"usuario_id": "...", "requires_role_selection": true, "roles": ["ATLETA", "JUEZ"]}
```
Si tiene un solo rol, retorna token directamente.

**Login** — si se envía `rol_elegido` en el body, genera token con ese rol. Si no y el usuario tiene un solo rol, lo auto-selecciona. Si tiene múltiples, retorna:
```json
{"requires_role_selection": true, "roles": ["ATLETA", "JUEZ"]}
```
El cliente debe repetir el login con `rol_elegido` para obtener el token.

---

## Dependencies (cross-cutting)

El archivo `dependencies.py` es el **corazón del sistema de autenticación** — sus funciones son importadas por todos los BCs.

### `get_current_user(token)`

Verifica el JWT via `token_service.verify(token)`. Retorna el payload completo `{sub, email, nombre, apellido, rol}`. Lanza HTTP 401 si inválido.

### `require_rol(*roles)`

Factory de guard — crea una dependencia FastAPI que verifica `payload["rol"]`. Lanza HTTP 403 si el rol activo del token no está en la lista.

### Guards exportados

```python
OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep        = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep      = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
```

Estos tipos se usan como `Annotated` dependencies en **todos los routers** del sistema. Son el mecanismo de autorización cross-cutting de AtaraxiaDive.

### `configure_identity_dependencies()`

```python
configure_identity_dependencies(
    token_service=JWTService(),
    password_hasher=BcryptPasswordHasher(),
    email_sender=ResendEmailAdapter(),  # o LoggingEmailAdapter en tests
    perfil_registro=PerfilRegistroAdapter(...),
)
```

Llamado desde `app.py` (composition root). Permite inyectar implementaciones alternativas para tests.

---

## Relaciones

**Contenedor:** [[arquitectura/identidad]]

- Usa [[command-handlers-identidad]]
- Instancia [[jwt-service]] y [[sqlite-usuario-repository]] via dependency providers
- Los guards `OrganizadorDep`, `JuezDep`, `AtletaDep` son importados por [[router-torneo]], [[router-registro]], [[router-resultados]] y BC Competencia
- `configure_identity_dependencies()` inyecta [[perfil-registro-adapter]] como `PerfilRegistroPort`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/identidad/api/router.py` | Router FastAPI — endpoints HTTP del BC |
| `src/identidad/api/dependencies.py` | Guards de rol: get_current_user, OrganizadorDep, JuezDep, AtletaDep |
