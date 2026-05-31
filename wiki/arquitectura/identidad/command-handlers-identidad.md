---
title: "Identidad — Command Handlers"
type: arquitectura-componente
bc: identidad
capa: application
tipo_componente: handler
responsabilidad: "5 handlers: registro (con multi-rol), autenticación (con selección de rol), cambio y reset de password"
interfaces_out:
  - UsuarioRepositoryPort
  - PasswordHashingPort
  - TokenServicePort
  - PerfilRegistroPort
adr_refs: [ADR-019, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/identidad/application/commands/registrar_usuario.py
  - src/identidad/application/commands/autenticar_usuario.py
  - src/identidad/application/commands/cambiar_password.py
  - src/identidad/application/commands/solicitar_reset_password.py
  - src/identidad/application/commands/reset_password.py
us_origen:
  - US-3.2.1-bc-identidad-usuario-jwt-minimo-auth
  - US-5.3.2-atleta-dashboard-page-perfil-inscripcion-a-torneos
  - US-5.4.1-auto-registro-publico-de-usuarios
  - US-5.4.2-cambiar-contrasena-para-usuario-autenticado
  - US-5.4.3-recuperar-contrasena-via-token-jwt
  - US-ADJ-10.3-email-de-bienvenida-y-auto-login-post-registro
  - US-ADJ-11.2-post-delete-auth-usuarios-me-roles-guard-no-quitar
tests:
  - tests/features/US-3.2.1-bc-identidad-jwt.feature
  - tests/integration/identidad/test_sqlite_usuario_repository.py
  - tests/features/US-5.3.2-vista-atleta.feature
  - tests/features/US-5.4.1-auto-registro.feature
  - tests/integration/identidad/test_registro_email_handler.py
  - tests/features/US-5.4.2-cambiar-password.feature
  - tests/features/US-5.4.3-recuperar-password.feature
  - tests/features/US-ADJ-10.3-email-autologin-post-registro.feature
  - tests/features/US-ADJ-11.2-agregar-quitar-rol.feature
---

# Command Handlers — BC Identidad

---

## RegistrarUsuarioHandler

El handler más complejo del BC — orquesta registro, email de bienvenida y creación de perfiles cross-BC.

### Invariantes de registro

- Password: mínimo 10 chars + al menos 1 mayúscula + al menos 1 número (ADR-019)
- `Rol.ADMIN` no permitido via API (`RolNoPermitido`)

### Flujo — usuario nuevo

```
1. Validar password (min 10, mayúscula, número)
2. Verificar email libre en repo
3. hash(password) con BcryptPasswordHasher
4. Usuario(uuid4(), nombre, apellido, email, hash, roles)
5. repo.save(usuario)
6. email_sender.enviar("Bienvenido/a a AtaraxiaDive")  — silenciado si falla
7. perfil_registro.crear_perfiles(...)  → PerfilRegistroAdapter → BC Registro
```

### Flujo — email ya registrado (agregar rol)

```
1. find_by_email → usuario existente
2. verify(password) → si falla: CredencialesInvalidas
3. Para cada rol nuevo: si ya existe → RolYaAsignado
4. existente.roles.append(rol)
5. repo.save(existente)
6. perfil_registro.crear_perfiles(...)
```

### Retorno: RegistroResult

- Un solo rol → retorna `TokenResponse` directamente (acceso inmediato)
- Múltiples roles → retorna `requires_role_selection=True` con lista de roles (el cliente elige)

---

## AutenticarUsuarioHandler

```python
async def handle(cmd) -> TokenResponse | RoleSelectionRequired
```

1. `find_by_email` o `CredencialesInvalidas`
2. Verificar `activo` o `UsuarioInactivo`
3. `password_hasher.verify()` o `CredencialesInvalidas`
4. Si `rol_elegido` provisto: verificar que pertenece al usuario → generar token
5. Si un solo rol: generar token automáticamente
6. Si múltiples roles sin elección: retornar `RoleSelectionRequired`

El cliente puede hacer dos llamadas: primera sin `rol_elegido` (recibe lista) → segunda con `rol_elegido` (recibe token).

---

## CambiarPasswordHandler

Verifica password actual, aplica políticas ADR-019 al nuevo, hashea y persiste.

---

## SolicitarResetPasswordHandler

Genera JWT de reset (1h), envía email con URL `{FRONTEND_BASE_URL}/reset-password?token=...`. Respuesta siempre 200 aunque el email no exista (anti-enumeración).

---

## ResetPasswordHandler

Verifica el JWT de reset (claim `type=password_reset`), hashea la nueva contraseña, persiste. Lanza `TokenResetInvalido` si el token expiró o es inválido.

---

## Relaciones

**Contenedor:** [[arquitectura/identidad]]

- Instanciados en [[router-identidad]]
- Usan [[sqlite-usuario-repository]], [[jwt-service]], y [[perfil-registro-adapter]] (vía `PerfilRegistroPort`)
- `RegistrarUsuarioHandler` es el punto de entrada del modelo multi-rol (ADR-020)

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/identidad/application/commands/registrar_usuario.py` | Handler: RegistrarUsuarioHandler (multi-rol, bcrypt, política password) |
| `src/identidad/application/commands/autenticar_usuario.py` | Handler: AutenticarUsuarioHandler (credenciales, JWT, selector de rol) |
| `src/identidad/application/commands/cambiar_password.py` | Handler: CambiarPasswordHandler |
| `src/identidad/application/commands/solicitar_reset_password.py` | Handler: SolicitarResetPasswordHandler |
| `src/identidad/application/commands/reset_password.py` | Handler: ResetPasswordHandler |
