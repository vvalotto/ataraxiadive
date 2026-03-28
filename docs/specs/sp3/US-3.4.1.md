# US-3.4.1: Torneo — AsignarDisciplinas + AsignarJuez

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.4
**Bounded Context**: `torneo`
**Capas afectadas**: `torneo/domain/`, `torneo/application/`, `torneo/api/`

---

## Descripción

Como **organizador**,
quiero **configurar las disciplinas del torneo y asignar un juez a cada una**
para **que los jueces puedan operar solo en sus disciplinas asignadas**.

---

## Especificación

### Precondición

```python
# US-3.1.1/3.1.2: Torneo con máquina de estados funcional
# Torneo no tiene disciplinas ni jueces asignados todavía
```

### Postcondición

```python
# torneo/domain/value_objects/disciplina_torneo.py
@dataclass(frozen=True)
class DisciplinaTorneo:
    disciplina: Disciplina        # de shared.domain.value_objects
    juez_id: UUID | None = None   # None si aún no asignado

# torneo/domain/aggregates/torneo.py (extensión):
@dataclass
class Torneo:
    # ... campos de US-3.1.1 ...
    disciplinas_torneo: list[DisciplinaTorneo] = field(default_factory=list)

    def asignar_disciplinas(self, disciplinas: frozenset[Disciplina]) -> None:
        """Configura las disciplinas disponibles. Solo en estado CREADO o PREPARACION."""
        ...

    def asignar_juez(self, disciplina: Disciplina, juez_id: UUID) -> None:
        """Asigna juez a una disciplina del torneo."""
        ...

    def obtener_disciplinas_de_juez(self, juez_id: UUID) -> list[Disciplina]:
        """Retorna las disciplinas asignadas al juez dado."""
        ...

# torneo/domain/exceptions.py (agregar):
class DisciplinaNoEnTorneo(Exception): ...      # disciplina no está en el torneo
class JuezYaAsignado(Exception): ...            # disciplina ya tiene juez asignado
class AsignacionNoPermitida(Exception): ...     # estado incorrecto para asignar

# torneo/application/commands/asignar_disciplinas.py
@dataclass(frozen=True)
class AsignarDisciplinasCommand:
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]

class AsignarDisciplinasHandler:
    async def handle(self, cmd: AsignarDisciplinasCommand) -> None: ...

# torneo/application/commands/asignar_juez.py
@dataclass(frozen=True)
class AsignarJuezCommand:
    torneo_id: UUID
    disciplina: Disciplina
    juez_id: UUID

class AsignarJuezHandler:
    async def handle(self, cmd: AsignarJuezCommand) -> None: ...

# torneo/application/queries/obtener_disciplinas_juez.py
class ObtenerDisciplinasDeJuezHandler:
    async def handle(self, torneo_id: UUID, juez_id: UUID) -> list[Disciplina]: ...

# torneo/api/router.py (extensión):
PUT  /torneos/{torneo_id}/disciplinas                       → 200
PUT  /torneos/{torneo_id}/disciplinas/{disciplina}/juez     → 200 { juez_id }
GET  /torneos/{torneo_id}/jueces/{juez_id}/disciplinas      → 200 [disciplinas]
GET  /torneos/{torneo_id}/disciplinas                       → 200 [{ disciplina, juez_id }]
```

### Invariantes

- `INV-TD-01`: Solo se pueden asignar disciplinas del conjunto `{STA, DNF, DYNB, DYN, SPE2X50}` (SP3)
- `INV-TD-02`: No se pueden asignar disciplinas con el torneo en estado `EJECUCION`, `PREMIACION` o `CERRADO`
- `INV-TD-03`: No se puede asignar juez a disciplina que no está en el torneo
- `INV-TD-04`: Una disciplina puede tener como máximo un juez asignado (se puede reasignar)
- `INV-TD-05`: `disciplinas` de `Inscripcion` (Registro) debe ser subconjunto de `disciplinas` del torneo — validado en US-3.2.3

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.4.1 — AsignarDisciplinas + AsignarJuez

  Scenario: asignar disciplinas a torneo
    Given torneo en estado CREADO
    When PUT /torneos/{id}/disciplinas con [STA, DNF, DYNB]
    Then 200
    And GET /torneos/{id}/disciplinas retorna las 3 disciplinas sin juez

  Scenario: asignar juez a disciplina
    Given torneo con disciplinas [STA, DNF] y juez_id válido
    When PUT /torneos/{id}/disciplinas/STA/juez con juez_id
    Then 200
    And GET /torneos/{id}/disciplinas/STA retorna juez_id

  Scenario: disciplina no asignada al torneo
    Given torneo con disciplinas [STA]
    When PUT /torneos/{id}/disciplinas/DYN/juez
    Then 409 DisciplinaNoEnTorneo

  Scenario: listar disciplinas de un juez
    Given juez asignado a STA y DNF en un torneo
    When GET /torneos/{id}/jueces/{juez_id}/disciplinas
    Then 200 con [STA, DNF]

  Scenario: asignar disciplinas en estado EJECUCION
    Given torneo en estado EJECUCION
    When PUT /torneos/{id}/disciplinas
    Then 409 AsignacionNoPermitida
```

---

## Notas de implementación

- `DisciplinaTorneo` se serializa como JSON en la columna `disciplinas_torneo TEXT` de la tabla `torneos`.
- La reasignación de juez (sobreescribir) es permitida — no es una violación de INV-TD-04.
- `Disciplina` se importa desde `shared.domain.value_objects.disciplina`.
- RF-EJ-01: "puede haber más de un juez asignado a una disciplina" — para SP3 simplificamos a 1 juez por disciplina. Múltiples jueces queda para SP4.

---

## Referencias

- US-3.1.1/3.1.2: Torneo
- US-3.2.3: Inscripcion valida disciplinas contra torneo
- RFs: RF-EJ-01, RF-US-04
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
