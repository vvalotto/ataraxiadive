# US-3.2.3: BC Registro — Inscripcion (inscribir + cancelar)

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.2
**Bounded Context**: `registro`
**Capas afectadas**: `registro/domain/`, `registro/application/`, `registro/api/`

---

## Descripción

Como **atleta inscripto**,
quiero **inscribirme en un torneo eligiendo disciplinas y cancelar si es necesario**
para **participar formalmente en la competencia**.

---

## Especificación

### Precondición

```
US-3.2.2 implementada: Atleta en Registro
US-3.1.1/3.1.2 implementadas: Torneo con estados
```

### Postcondición

```python
# registro/domain/value_objects/estado_inscripcion.py
class EstadoInscripcion(StrEnum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"

# registro/domain/aggregates/inscripcion.py
@dataclass
class Inscripcion:
    inscripcion_id: UUID
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]   # de shared.domain.value_objects
    estado: EstadoInscripcion = EstadoInscripcion.ACTIVA
    fecha_inscripcion: datetime = field(default_factory=datetime.utcnow)

    def cancelar(self, fecha_actual: date, fecha_inicio_torneo: date) -> None:
        """INV-I-03: solo cancela si fecha_actual < fecha_inicio_torneo."""
        ...

# registro/domain/ports/inscripcion_repository_port.py
class InscripcionRepositoryPort(ABC):
    async def save(self, inscripcion: Inscripcion) -> None: ...
    async def find_by_id(self, inscripcion_id: UUID) -> Inscripcion | None: ...
    async def find_by_atleta_y_torneo(
        self, atleta_id: UUID, torneo_id: UUID
    ) -> Inscripcion | None: ...
    async def find_by_torneo(self, torneo_id: UUID) -> list[Inscripcion]: ...

# registro/domain/ports/torneo_consulta_port.py  ← ACL read-only sobre Torneo
class TorneoConsultaPort(ABC):
    """Lee estado y fechas de Torneo para validar inscripciones."""
    async def esta_abierto_para_inscripcion(self, torneo_id: UUID) -> bool: ...
    async def obtener_fecha_inicio(self, torneo_id: UUID) -> date: ...
    async def obtener_disciplinas(self, torneo_id: UUID) -> frozenset[Disciplina]: ...

# registro/domain/exceptions.py (agregar a las de US-3.2.2)
class InscripcionNoEncontrada(Exception): ...
class AtletaYaInscripto(Exception): ...          # INV-I-04
class TorneoNoDisponible(Exception): ...          # torneo no en INSCRIPCION_ABIERTA
class DisciplinaNoDisponible(Exception): ...      # disciplina no en el torneo
class PlazoCancelacionVencido(Exception): ...     # INV-I-03: ya es el día del torneo

# registro/application/commands/inscribir_atleta.py
@dataclass(frozen=True)
class InscribirAtletaCommand:
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]

class InscribirAtletaHandler:
    async def handle(self, cmd: InscribirAtletaCommand) -> UUID: ...  # inscripcion_id

# registro/application/commands/cancelar_inscripcion.py
@dataclass(frozen=True)
class CancelarInscripcionCommand:
    inscripcion_id: UUID
    fecha_actual: date  # para validar INV-I-03

class CancelarInscripcionHandler:
    async def handle(self, cmd: CancelarInscripcionCommand) -> None: ...

# registro/application/queries/listar_inscriptos.py
class ListarInscriptosHandler:
    async def handle(self, torneo_id: UUID) -> list[Inscripcion]: ...

# registro/api/router.py (extensión del router de US-3.2.2)
POST   /registro/inscripciones                   → 201 { inscripcion_id }
DELETE /registro/inscripciones/{inscripcion_id}  → 200
GET    /registro/torneos/{torneo_id}/inscriptos  → 200 [{ atleta_id, disciplinas, estado }]
```

### Invariantes

- `INV-I-01`: `disciplinas` ⊆ disciplinas del torneo — no se puede inscribir en disciplina no disponible
- `INV-I-02`: El torneo debe estar en estado `INSCRIPCION_ABIERTA` para aceptar inscripciones
- `INV-I-03`: Cancelación solo permitida si `fecha_actual < fecha_inicio_torneo` (hasta el día anterior)
- `INV-I-04`: Un atleta no puede inscribirse dos veces en el mismo torneo
- `INV-I-05`: `disciplinas` no puede ser vacío al inscribirse

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.2.3 — Inscripcion

  Scenario: inscribir atleta exitosamente
    Given atleta registrado, torneo en estado INSCRIPCION_ABIERTA con STA y DNF
    When POST /registro/inscripciones con atleta_id, torneo_id, disciplinas=[STA]
    Then 201 con inscripcion_id
    And GET /registro/torneos/{id}/inscriptos incluye al atleta

  Scenario: torneo no disponible para inscripción
    Given torneo en estado CREADO (no INSCRIPCION_ABIERTA)
    When POST /registro/inscripciones
    Then 409 Conflict con TorneoNoDisponible

  Scenario: disciplina no disponible en el torneo
    Given torneo con disciplinas [STA, DNF]
    When POST /registro/inscripciones con disciplinas=[DYN]
    Then 409 Conflict con DisciplinaNoDisponible

  Scenario: atleta duplicado en el mismo torneo
    Given atleta ya inscripto en torneo
    When POST /registro/inscripciones con mismo atleta_id y torneo_id
    Then 409 Conflict con AtletaYaInscripto

  Scenario: cancelar inscripción antes del torneo
    Given inscripcion ACTIVA y fecha_inicio del torneo es mañana
    When DELETE /registro/inscripciones/{id}
    Then 200 y estado = CANCELADA

  Scenario: cancelar el día del torneo
    Given inscripcion ACTIVA y fecha_inicio es hoy
    When DELETE /registro/inscripciones/{id}
    Then 409 Conflict con PlazoCancelacionVencido

  Scenario: listar inscriptos de un torneo
    Given 3 atletas inscriptos en un torneo
    When GET /registro/torneos/{id}/inscriptos
    Then 200 con lista de 3 inscripciones ACTIVAS
```

---

## Notas de implementación

- `TorneoConsultaPort` en `registro/domain/ports/` — implementado en `registro/infrastructure/` consultando la DB de Torneo (cross-BC read-only, permitido por el context map §3.2).
- Alternativa para SP3: en `app.py`, el handler recibe el torneo como parámetro (inyección desde la capa de aplicación, sin que el dominio importe Torneo directamente).
- `Disciplina` se importa desde `shared.domain.value_objects.disciplina`.
- Tabla `inscripciones` en `data/registro.db`: columnas `inscripcion_id, atleta_id, torneo_id, disciplinas (JSON), estado, fecha_inscripcion`.

---

## Referencias

- US-3.2.2: Atleta
- US-3.1.1/3.1.2: Torneo
- RFs: RF-IN-01..04, RF-IN-08, RF-IN-09
- Context Map §3.2: Torneo → Registro (Customer-Supplier)
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
