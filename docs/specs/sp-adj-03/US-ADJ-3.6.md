# US-ADJ-3.6: `TokenServicePort` + `PasswordHashingPort` en Identidad (DIP)

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: SOLID-02 · SOLID-03
**Bounded Context**: `identidad`
**Capas afectadas**: `identidad/domain/ports/` · `identidad/application/commands/` · `identidad/api/dependencies.py` · `identidad/infrastructure/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **crear `TokenServicePort` y `PasswordHashingPort` en `identidad/domain/ports/` y desacoplar la application layer de `JWTService` y `bcrypt` concretos**
para **que las decisiones de implementación de autenticación (algoritmo JWT, hashing) sean reemplazables sin tocar lógica de aplicación**.

---

## Contexto de la deuda

### SOLID-02 — `application/` depende de infraestructura concreta

`identidad/application/commands/autenticar_usuario.py`:

```python
import bcrypt
from identidad.infrastructure.jwt_service import JWTService

class AutenticarUsuarioHandler:
    def __init__(self, repo: UsuarioRepositoryPort, jwt_service: JWTService) -> None:
        self._jwt = jwt_service

    async def handle(self, cmd: AutenticarUsuarioCommand) -> TokenResponse:
        if not bcrypt.checkpw(cmd.password.encode(), usuario.password_hash.encode()):
            raise CredencialesInvalidas()
        token = self._jwt.generate(usuario)
```

`autenticar_usuario.py` importa `bcrypt` directamente (infraestructura) y recibe
`JWTService` (clase concreta de `infrastructure/`) en su constructor. Viola DIP:
la application layer debe depender de abstracciones, no de implementaciones concretas.

`identidad/application/commands/registrar_usuario.py`:

```python
import bcrypt

async def handle(self, cmd: RegistrarUsuarioCommand) -> UUID:
    hashed = bcrypt.hashpw(cmd.password.encode(), bcrypt.gensalt()).decode()
```

Mismo problema: `bcrypt` importado directamente en la application layer.

### SOLID-03 — `JWTService` instanciado inline en `api/dependencies.py`

`identidad/api/dependencies.py:20-21`:

```python
async def get_current_user(token: ...) -> dict:
    jwt_svc = JWTService()    # ← instanciado por request, sin inyección
    return jwt_svc.verify(token)
```

`JWTService()` se crea en cada request. No es inyectado desde el composition root —
el router construye su propia instancia de infraestructura directamente.

---

## Especificación

### Puertos nuevos

```python
# identidad/domain/ports/token_service_port.py
from abc import ABC, abstractmethod
from identidad.domain.aggregates.usuario import Usuario

class TokenServicePort(ABC):
    """Puerto de generación y verificación de tokens de autenticación."""

    @abstractmethod
    def generate(self, usuario: Usuario) -> str:
        """Genera un token para el usuario autenticado."""

    @abstractmethod
    def verify(self, token: str) -> dict:
        """Verifica el token y retorna el payload. Lanza TokenInvalido si inválido."""
```

```python
# identidad/domain/ports/password_hashing_port.py
from abc import ABC, abstractmethod

class PasswordHashingPort(ABC):
    """Puerto de hashing y verificación de contraseñas."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Retorna el hash de la contraseña."""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verifica si la contraseña coincide con el hash."""
```

### `AutenticarUsuarioHandler` post-refactor

```python
class AutenticarUsuarioHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        token_service: TokenServicePort,
        password_hasher: PasswordHashingPort,
    ) -> None:
        ...

    async def handle(self, cmd) -> TokenResponse:
        if not self._password_hasher.verify(cmd.password, usuario.password_hash):
            raise CredencialesInvalidas()
        token = self._token_service.generate(usuario)
```

### `RegistrarUsuarioHandler` post-refactor

```python
class RegistrarUsuarioHandler:
    def __init__(self, repo: UsuarioRepositoryPort, password_hasher: PasswordHashingPort) -> None:
        ...

    async def handle(self, cmd) -> UUID:
        hashed = self._password_hasher.hash(cmd.password)
```

### Implementaciones concretas en `identidad/infrastructure/`

`JWTService` implementa `TokenServicePort`. No requiere cambio de código — solo
agregar la declaración `class JWTService(TokenServicePort)`.

Nueva clase `BcryptPasswordHasher(PasswordHashingPort)` en `identidad/infrastructure/`:

```python
import bcrypt
from identidad.domain.ports.password_hashing_port import PasswordHashingPort

class BcryptPasswordHasher(PasswordHashingPort):
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
```

### `identidad/api/dependencies.py` post-refactor (SOLID-03)

`JWTService` deja de instanciarse inline. Se inyecta desde el composition root
(`app.py`) via `dependency_overrides` o parametrización similar a US-ADJ-2.7.

### `app.py` — wiring del BC Identidad

```python
# src/app.py
from identidad.infrastructure.jwt_service import JWTService
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher

jwt_service = JWTService()
password_hasher = BcryptPasswordHasher()
# inyectar en los routers vía FastAPI dependency_overrides o parámetro de módulo
```

### Invariantes

- `INV-ADJ-3.6-1`: `autenticar_usuario.py` — `grep "import bcrypt"` devuelve cero matches
- `INV-ADJ-3.6-2`: `registrar_usuario.py` — `grep "import bcrypt"` devuelve cero matches
- `INV-ADJ-3.6-3`: `application/commands/` — `grep "from identidad.infrastructure"` devuelve cero matches
- `INV-ADJ-3.6-4`: login y registro funcionan igual que antes
- `INV-ADJ-3.6-5`: todos los tests existentes de Identidad pasan sin modificación

---

## Criterios de aceptación

```gherkin
Scenario: application layer no importa bcrypt ni JWTService
  Given los archivos autenticar_usuario.py y registrar_usuario.py refactorizados
  Then ninguno contiene "import bcrypt"
  And ninguno contiene "from identidad.infrastructure"

Scenario: TokenServicePort y PasswordHashingPort existen en domain/ports/
  Given el directorio identidad/domain/ports/
  Then contiene token_service_port.py con clase abstracta TokenServicePort
  And contiene password_hashing_port.py con clase abstracta PasswordHashingPort

Scenario: JWTService implementa TokenServicePort
  Given la clase JWTService en identidad/infrastructure/jwt_service.py
  Then hereda de TokenServicePort

Scenario: BcryptPasswordHasher existe en infrastructure
  Given el archivo identidad/infrastructure/bcrypt_password_hasher.py
  Then hereda de PasswordHashingPort
  And implementa hash() y verify()

Scenario: login sigue funcionando tras el refactor
  Given un usuario registrado con email y password válidos
  When se llama POST /auth/login con las credenciales correctas
  Then retorna 200 con access_token
  When se llama con password incorrecto
  Then retorna 401 Unauthorized
```

---

## Notas de implementación

- `JWTService` solo necesita agregar `(TokenServicePort)` como base — su implementación
  ya cumple el contrato. No requiere reescritura.
- El mecanismo de inyección de `JWTService` en `dependencies.py` puede ser el mismo
  patrón que US-ADJ-2.7 (variable de módulo inicializada desde `app.py`).
- Los tests unitarios de `AutenticarUsuarioHandler` que mockean `JWTService` directamente
  pueden mockearlo vía el puerto — el mock se simplifica.

---

## Referencias

- Revisión SOLID SP3: `.work/revision-sp3/05b-revision-solid-sp3.md` (SOLID-02, SOLID-03)
- Issues consolidados: `.work/revision-sp3/07-issues-consolidados.md`
- US-ADJ-2.7: patrón de inyección de callback desde `app.py`
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`
- CLAUDE.md §6 — Regla de Oro: `application/` no importa `infrastructure/`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
