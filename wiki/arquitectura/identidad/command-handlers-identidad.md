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

- Instanciados en [[router-identidad]]
- Usan [[sqlite-usuario-repository]], [[jwt-service]], y [[perfil-registro-adapter]] (vía `PerfilRegistroPort`)
- `RegistrarUsuarioHandler` es el punto de entrada del modelo multi-rol (ADR-020)
