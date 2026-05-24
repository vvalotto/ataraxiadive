---
title: "BC Identidad — Generic Domain"
type: arquitectura
last_updated: "2026-05-23"
sources:
  - docs/architecture/14-bc-identidad.md
tipo_ddd: generic
persistencia: CRUD
db: identidad.db
test_coverage: null
componentes:
  - usuario-aggregate
  - jwt-service
  - sqlite-usuario-repository
  - command-handlers-identidad
  - router-identidad
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

## Salud (BL-006 · v1.0.0 · 2026-05-16)

### ArchitectAnalyst

| Métrica | Valor | Severidad | Tendencia |
|---------|-------|-----------|-----------|
| Distancia (D) | 0.652 | **CRITICAL** | ↓ mejorando |
| should_block | false | — | — |

D=0.652, el valor más alto de los BCs. Es el Zone of Pain esperado para un BC de autenticación CRUD puro: alta abstracción (interfaces y puertos), baja inestabilidad (pocos cambios). La tendencia es positiva: 0.87 (BL-004) → 0.67 (BL-005) → 0.65 (BL-006). Diferido para evaluación post-v1.0 (decisión AA-02 en BL-006).

### DesignReviewer

| Total WARNING | Top smells |
|:---:|---|
| **21** | LongMethod (8) · FeatureEnvy (8) · DataClumps (2) |

Volumen bajo. LongMethod y FeatureEnvy en los handlers de autenticación (JWT + hashing + validaciones multi-campo). Sin CRITICAL.

### Cobertura

Tests desde SP3. Suite ampliada en SP-ADJ-11 (modelo multi-rol — 10 US nuevas).

**UAT SP6 — flows que ejercen este BC:**
- F-01 Setup inicial y configuración (login, JWT) ✅
- Todos los flows requieren autenticación válida (Identidad es cross-cutting) ✅

**Nota:** % de cobertura numérico no disponible en BL-006 — pendiente de `pytest --cov`. D mejora sostenidamente (0.87 BL-004 → 0.65 BL-006), lo que indica incremento de tests relativos a la complejidad del BC.
