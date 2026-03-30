# US-3.2.1: BC Identidad — Usuario + JWT mínimo

**Estado**: `Done`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.2
**Bounded Context**: `identidad`
**Capas afectadas**: `identidad/domain/`, `identidad/application/`, `identidad/infrastructure/`, `identidad/api/`, `src/app.py`

---

## Descripción

Como **usuario del sistema**,
quiero **registrarme y autenticarme para obtener un JWT**
para **que los demás endpoints puedan verificar mi identidad y rol**.

---

## Especificación

### Precondición

```
identidad/ — scaffolding vacío (solo __init__.py en cada subcarpeta)
```

### Postcondición

```python
# identidad/domain/value_objects/rol.py
class Rol(StrEnum):
    ORGANIZADOR = "ORGANIZADOR"
    JUEZ = "JUEZ"
    ATLETA = "ATLETA"
    ADMIN = "ADMIN"

# identidad/domain/aggregates/usuario.py
@dataclass
class Usuario:
    usuario_id: UUID
    email: str
    password_hash: str  # bcrypt
    rol: Rol
    activo: bool = True

# identidad/domain/ports/usuario_repository_port.py
class UsuarioRepositoryPort(ABC):
    async def save(self, usuario: Usuario) -> None: ...
    async def find_by_id(self, usuario_id: UUID) -> Usuario | None: ...
    async def find_by_email(self, email: str) -> Usuario | None: ...

# identidad/domain/exceptions.py
class EmailYaRegistrado(Exception): ...
class CredencialesInvalidas(Exception): ...
class UsuarioNoEncontrado(Exception): ...
class UsuarioInactivo(Exception): ...

# identidad/application/commands/registrar_usuario.py
@dataclass(frozen=True)
class RegistrarUsuarioCommand:
    email: str
    password: str  # plain — el handler hashea con bcrypt
    rol: Rol

class RegistrarUsuarioHandler:
    async def handle(self, cmd: RegistrarUsuarioCommand) -> UUID: ...

# identidad/application/commands/autenticar_usuario.py
@dataclass(frozen=True)
class AutenticarUsuarioCommand:
    email: str
    password: str

@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str = "bearer"

class AutenticarUsuarioHandler:
    async def handle(self, cmd: AutenticarUsuarioCommand) -> TokenResponse: ...

# identidad/infrastructure/jwt_service.py
class JWTService:
    """Genera y verifica tokens JWT."""
    def generate(self, usuario: Usuario) -> str: ...
    def verify(self, token: str) -> dict: ...  # payload: {sub, email, rol, exp}

# identidad/infrastructure/repositories/sqlite_usuario_repository.py
class SQLiteUsuarioRepository(UsuarioRepositoryPort): ...

# identidad/api/router.py
router = APIRouter(prefix="/auth", tags=["auth"])

POST /auth/registro  → 201 { usuario_id }
POST /auth/login     → 200 { access_token, token_type }

# identidad/api/dependencies.py — dependencia reutilizable por otros BCs
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Verifica JWT y retorna payload {sub, email, rol}. Lanza 401 si inválido."""
    ...
```

### Invariantes

- `INV-ID-01`: email único — no se puede registrar dos usuarios con el mismo email
- `INV-ID-02`: password debe tener mínimo 8 caracteres
- `INV-ID-03`: password se almacena como hash bcrypt, nunca en plain text
- `INV-ID-04`: JWT expira en 24h (configurable via `IDENTIDAD_JWT_EXPIRY_HOURS`)
- `INV-ID-05`: JWT contiene `{ sub: usuario_id, email, rol, exp }`
- `INV-ID-06`: usuario inactivo no puede autenticarse

### Variables de entorno

```
IDENTIDAD_JWT_SECRET=<secret>   # requerido
IDENTIDAD_DB_PATH=data/identidad.db
IDENTIDAD_JWT_EXPIRY_HOURS=24
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.2.1 — BC Identidad JWT

  Scenario: registrar usuario nuevo
    Given email no existente y password válido
    When POST /auth/registro con rol ORGANIZADOR
    Then 201 con usuario_id

  Scenario: email duplicado
    Given un usuario con email "test@test.com" ya registrado
    When POST /auth/registro con el mismo email
    Then 409 Conflict

  Scenario: login exitoso retorna JWT
    Given usuario registrado con email y password
    When POST /auth/login con credenciales correctas
    Then 200 con access_token válido
    And el token contiene email y rol del usuario

  Scenario: credenciales incorrectas
    Given usuario registrado
    When POST /auth/login con password incorrecto
    Then 401 Unauthorized

  Scenario: JWT verificable por get_current_user
    Given un access_token válido
    When se llama get_current_user(token)
    Then retorna payload con sub, email y rol
```

---

## Notas de implementación

- Dependencias nuevas: `PyJWT`, `bcrypt` (o `passlib[bcrypt]`).
- `JWTService` vive en `identidad/infrastructure/` — no en domain.
- `get_current_user()` en `identidad/api/dependencies.py` es la dependencia FastAPI que los otros BCs importarán en SP3-INC-3.4 (US-3.4.2).
- `IDENTIDAD_JWT_SECRET` debe existir en el entorno — la app falla en startup si no está seteada.
- DB: `data/identidad.db`, tabla `usuarios (usuario_id TEXT, email TEXT UNIQUE, password_hash TEXT, rol TEXT, activo INTEGER)`.

---

## Referencias

- Context Map: `docs/design/context-map.md §3.1` (Identidad → otros BCs, Conformist)
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
