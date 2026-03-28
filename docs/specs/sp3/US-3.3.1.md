# US-3.3.1: Competencia — agregar `torneo_id` a ConfigurarIntervaloOT

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.3
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/`, `competencia/application/`, `competencia/api/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **que `Competencia` registre el `torneo_id` al que pertenece**
para **que la política P-09 pueda calcular el Overall cuando todas las disciplinas de un torneo finalicen**.

---

## Especificación

### Precondición

```python
# competencia/domain/aggregates/competencia.py (actual):
class Competencia(AggregateRoot):
    def __init__(self, competencia_id: UUID, disciplina: Disciplina):
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        # NO hay torneo_id

# competencia/application/commands/configurar_intervalo_ot.py:
@dataclass(frozen=True)
class ConfigurarIntervaloOTCommand:
    competencia_id: UUID
    disciplina: Disciplina
    intervalo_segundos: int
    # NO hay torneo_id
```

### Postcondición

```python
# competencia/domain/aggregates/competencia.py:
class Competencia(AggregateRoot):
    def __init__(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        torneo_id: UUID | None = None,   # ← nuevo campo, backward compat
    ):
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        self._torneo_id = torneo_id      # ← None para competencias standalone (SP1/SP2)

    @property
    def torneo_id(self) -> UUID | None:
        return self._torneo_id

# competencia/domain/events/competencia_events.py:
# El evento CompetenciaInicializada (o CompetenciaConfigurada) incluye torneo_id en payload

# competencia/application/commands/configurar_intervalo_ot.py:
@dataclass(frozen=True)
class ConfigurarIntervaloOTCommand:
    competencia_id: UUID
    disciplina: Disciplina
    intervalo_segundos: int
    torneo_id: UUID | None = None        # ← nuevo campo, backward compat

# competencia/api/router.py:
# POST /competencias body incluye torneo_id como campo opcional
# Respuesta de GET /competencias/{id} incluye torneo_id (null si no aplica)

# competencia/application/queries/ — query que busca competencias por torneo_id:
class ObtenerCompetenciasPorTorneoHandler:
    async def handle(self, torneo_id: UUID) -> list[dict]: ...

# competencia/api/router.py:
GET /competencias?torneo_id={uuid}  → 200 [lista de competencias del torneo]
```

### Invariantes

- `INV-CT-01`: `torneo_id` es opcional — si `None`, la competencia es standalone (compatible con SP1/SP2)
- `INV-CT-02`: Si `torneo_id` se provee, se persiste en el stream del evento `CompetenciaConfigurada`
- `INV-CT-03`: Todos los tests existentes de SP1/SP2 pasan sin modificación (backward compat total)

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.3.1 — torneo_id en Competencia

  Scenario: configurar competencia con torneo_id
    Given un torneo_id válido
    When POST /competencias con torneo_id
    Then la competencia se crea con torneo_id almacenado
    And GET /competencias/{id} retorna torneo_id

  Scenario: configurar competencia sin torneo_id (backward compat)
    Given payload sin campo torneo_id
    When POST /competencias
    Then la competencia se crea con torneo_id = null
    And todos los tests SP1/SP2 siguen pasando

  Scenario: listar competencias de un torneo
    Given 3 competencias con mismo torneo_id
    When GET /competencias?torneo_id={uuid}
    Then 200 con lista de 3 competencias

  Scenario: tests existentes no se rompen
    Given la suite completa de tests SP1/SP2 (481 tests)
    When pytest tests/
    Then 100% pass sin modificaciones en los tests
```

---

## Notas de implementación

- Cambio mínimo: `torneo_id: UUID | None = None` en `Competencia.__init__` y en `ConfigurarIntervaloOTCommand`.
- El payload del evento `CompetenciaConfigurada` o `CompetenciaIniciada` agrega `"torneo_id": str(torneo_id) if torneo_id else None`.
- Al reconstituir desde eventos, si el payload no tiene `torneo_id`, se usa `None` (backward compat con streams existentes en SP1/SP2).
- La query `ObtenerCompetenciasPorTorneo` scannea el event store buscando streams con `torneo_id` en su primer evento.
- Esta US NO modifica ningún test existente — solo agrega capacidades nuevas.

---

## Referencias

- US-3.5.2: P-09 usa `torneo_id` para detectar cuándo todas las disciplinas de un torneo finalizaron
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
