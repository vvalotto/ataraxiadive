# US-3.2.2: BC Registro — Aggregate Atleta

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.2
**Bounded Context**: `registro`
**Capas afectadas**: `registro/domain/`, `registro/application/`, `registro/infrastructure/`, `registro/api/`

---

## Descripción

Como **atleta**,
quiero **registrar mis datos personales en el sistema**
para **poder inscribirme en torneos y competir**.

---

## Especificación

### Precondición

```
registro/ — scaffolding vacío
US-3.2.1 implementada: Identidad con usuarios y JWT
```

### Postcondición

```python
# registro/domain/value_objects/categoria.py
class Categoria(StrEnum):
    SENIOR_MASCULINO = "SENIOR_MASCULINO"
    SENIOR_FEMENINO = "SENIOR_FEMENINO"
    MASTER_MASCULINO = "MASTER_MASCULINO"   # 50+ años
    MASTER_FEMENINO = "MASTER_FEMENINO"
    JUVENIL_MASCULINO = "JUVENIL_MASCULINO"  # -18 años
    JUVENIL_FEMENINO = "JUVENIL_FEMENINO"

# registro/domain/aggregates/atleta.py
@dataclass
class Atleta:
    atleta_id: UUID           # coincide con usuario_id de Identidad
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    brevet: str | None = None  # RF-IN-02: no obligatorio

# registro/domain/ports/atleta_repository_port.py
class AtletaRepositoryPort(ABC):
    async def save(self, atleta: Atleta) -> None: ...
    async def find_by_id(self, atleta_id: UUID) -> Atleta | None: ...
    async def find_by_email(self, email: str) -> Atleta | None: ...

# registro/domain/exceptions.py
class AtletaNoEncontrado(Exception): ...
class AtletaYaRegistrado(Exception): ...  # email duplicado

# registro/application/commands/registrar_atleta.py
@dataclass(frozen=True)
class RegistrarAtletaCommand:
    atleta_id: UUID   # provisto por el caller (= usuario_id de Identidad)
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    brevet: str | None = None

class RegistrarAtletaHandler:
    async def handle(self, cmd: RegistrarAtletaCommand) -> UUID: ...

# registro/application/queries/obtener_atleta.py
class ObtenerAtletaHandler:
    async def handle(self, atleta_id: UUID) -> Atleta: ...

# registro/infrastructure/repositories/sqlite_atleta_repository.py
class SQLiteAtletaRepository(AtletaRepositoryPort): ...

# registro/api/router.py (parcial — se completa en US-3.2.3)
POST /registro/atletas      → 201 { atleta_id }
GET  /registro/atletas/{id} → 200 { atleta }
```

### Invariantes

- `INV-A-01`: `nombre` y `apellido` no pueden ser vacíos
- `INV-A-02`: `email` debe tener formato válido
- `INV-A-03`: `atleta_id` es único — no se puede registrar dos atletas con el mismo ID
- `INV-A-04`: `fecha_nacimiento` en el pasado (no puede ser futuro)
- `INV-A-05`: `brevet` puede ser `None` (RF-IN-02)

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.2.2 — Aggregate Atleta

  Scenario: registrar atleta con datos válidos
    Given datos personales completos (nombre, apellido, email, fecha_nacimiento, categoria)
    When POST /registro/atletas con atleta_id = usuario_id existente
    Then 201 con atleta_id
    And GET /registro/atletas/{id} retorna los datos del atleta

  Scenario: registrar atleta sin brevet
    Given datos válidos sin campo brevet
    When POST /registro/atletas
    Then 201 — brevet es null en la respuesta

  Scenario: atleta duplicado (mismo ID)
    Given un atleta ya registrado con atleta_id X
    When POST /registro/atletas con atleta_id X
    Then 409 Conflict

  Scenario: nombre vacío
    Given nombre = ""
    When POST /registro/atletas
    Then 422 Unprocessable Entity

  Scenario: atleta no encontrado
    Given un UUID no registrado
    When GET /registro/atletas/{uuid}
    Then 404 Not Found
```

---

## Notas de implementación

- `Categoria` es un StrEnum en `registro/domain/value_objects/categoria.py`.
- El `atleta_id` lo provee el caller y coincide con el `usuario_id` de Identidad (soft reference — sin FK real entre BCs).
- DB: `data/registro.db`, tabla `atletas`.
- La `Categoria` puede derivarse de `fecha_nacimiento` + género (opcional para SP3) o ser explícita en el registro. Para SP3: explícita.

---

## Referencias

- US-3.2.1: Identidad — `atleta_id = usuario_id`
- RFs: RF-IN-01..04, RF-IN-08, RF-IN-09
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
