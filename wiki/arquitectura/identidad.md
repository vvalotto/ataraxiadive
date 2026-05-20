---
title: "BC Identidad — Generic Domain"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/14-bc-identidad.md
tipo_ddd: Generic Domain
persistencia: CRUD
db: identidad.db
---

# BC Identidad — Generic Domain

## Rol

**Generic Domain** cross-cutting. No modela reglas deportivas ni organizativas. Provee un contrato común de autenticación y rol consumido por todos los demás BCs.

**Responsabilidades:** registrar usuarios, hashear contraseñas (bcrypt), autenticar email+contraseña, emitir JWT, verificar tokens.

## Persistencia

CRUD sobre `identidad.db`. Tabla `usuarios`: `usuario_id`, `email` (UNIQUE), `password_hash`, `roles` (JSON array desde ADR-020), `activo`.

## Aggregate principal: Usuario

Conserva: `usuario_id`, email, hash de contraseña, lista de roles, estado activo/inactivo.

**Roles (`list[Rol]` desde ADR-020):** `ORGANIZADOR`, `JUEZ`, `ATLETA`, `ADMIN`.

`ADMIN` es superrol interno — no asignable desde la UI. `ATLETA` no se puede quitar. Los demás roles se pueden agregar o quitar desde "Mis Datos".

## JWT — contrato de salida

```json
{ "sub": "uuid", "email": "...", "nombre": "...", "apellido": "...", "rol": "ATLETA", "exp": ... }
```

El token lleva el **rol elegido al login** (uno solo — ver [[ADR-020-modelo-usuarios-roles]]). Los BCs downstream (Torneo, Registro, Competencia) adoptan relación Conformist: aceptan este contrato sin negociar el modelo de identidad.

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | `POST /auth/registro`, `POST /auth/login`; dependencia `get_current_user` reutilizable para verificar JWT |
| `application/` | `RegistrarUsuarioHandler` (unicidad email, política contraseña, bcrypt), `AutenticarUsuarioHandler` (valida credenciales, impide login de inactivos, emite token) |
| `domain/` | `Usuario`, `Rol`, excepciones (`EmailDuplicado`, `CredencialesInvalidas`, `PasswordDemasiadoCorto`), `UsuarioRepositoryPort` |
| `infrastructure/` | `SQLiteUsuarioRepository`, `JWTService` (HS256, secreto y expiración desde vars de entorno) |

## Política de contraseñas (ADR-019)

Mínimo 10 caracteres + 1 mayúscula + 1 número. Aplicada en `RegistrarUsuarioHandler`, `CambiarPasswordHandler`, `ResetPasswordHandler`. Excepción: `PasswordDemasiadoCorto`.

## Flujo de login multi-rol (ADR-020)

- 1 rol → acceso directo al portal.
- N roles → selector de rol. El JWT lleva el rol elegido.
- Para cambiar de portal hay que volver a loguearse.

## Restricciones arquitectónicas

- Nunca persistir contraseña en texto plano.
- Los BCs downstream no consultan a Identidad en runtime — trabajan con claims locales.
- El contrato público debe mantenerse pequeño y estable (candidato a reemplazo externo en el futuro).

## ADRs relacionados

- [[ADR-019-politica-contrasenas]] — reglas de contraseña; `PasswordStrengthBar.tsx`
- [[ADR-020-modelo-usuarios-roles]] — `roles: list[Rol]`; perfiles por rol en BC Registro
- [[ADR-007-sqlite-persistencia-bc]] — persistencia CRUD en SQLite
- [[ADR-012-rfc7807-errores-http]] — mapeo de excepciones a HTTP
