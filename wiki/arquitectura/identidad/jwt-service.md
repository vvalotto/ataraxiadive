---
title: "Identidad — JWTService + BcryptPasswordHasher"
type: arquitectura-componente
bc: identidad
capa: infrastructure
tipo_componente: adapter
responsabilidad: "Generación/verificación de JWT HS256 y hash bcrypt de contraseñas — las dos implementaciones de seguridad del BC"
interfaces_out: []
adr_refs: [ADR-019]
last_updated: "2026-05-23"
sources:
  - src/identidad/infrastructure/jwt_service.py
  - src/identidad/infrastructure/bcrypt_password_hasher.py
---

# JWTService + BcryptPasswordHasher

---

## JWTService

Implementa `TokenServicePort`. Algoritmo: HS256. Configurado por variables de entorno.

### Configuración

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `IDENTIDAD_JWT_SECRET` | Clave secreta HMAC | ✅ Falla en init si ausente |
| `IDENTIDAD_JWT_EXPIRY_HOURS` | Expiración en horas | No — default 24h |

### Claims del token de acceso

```json
{
  "sub": "usuario_id (UUID string)",
  "email": "user@example.com",
  "nombre": "Víctor",
  "apellido": "Valotto",
  "rol": "ATLETA",
  "exp": 1234567890
}
```

El claim `rol` lleva el **rol activo elegido** (no la lista completa). Todos los guards del sistema (`get_current_user`, `require_rol`) verifican `payload["rol"]`.

### Token de reset de password

Tipo especial con claim `"type": "password_reset"`, expiración 1h. Firmado con la misma clave. Verificado por `ResetPasswordHandler`.

### Métodos

| Método | Descripción |
|--------|-------------|
| `generate(usuario, rol_activo)` | JWT de acceso (24h) |
| `generate_reset_token(email)` | JWT de reset (1h) |
| `verify(token)` | Retorna payload o lanza `TokenInvalido` |

---

## BcryptPasswordHasher

Implementa `PasswordHashingPort`.

```python
class BcryptPasswordHasher(PasswordHashingPort):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hash: str) -> bool: ...
```

Usa `bcrypt` con work factor por defecto (12 rondas). Nunca expone contraseñas en claro. El aggregate `Usuario` solo almacena el hash resultante.

---

## Relaciones

- `JWTService` implementa `TokenServicePort` (domain port)
- `BcryptPasswordHasher` implementa `PasswordHashingPort` (domain port)
- Ambos instanciados via `configure_identity_dependencies()` en [[dependencies-identidad]]
- `JWTService.verify()` es llamado por `get_current_user()` en cada request autenticado — cross-cutting para todos los BCs
