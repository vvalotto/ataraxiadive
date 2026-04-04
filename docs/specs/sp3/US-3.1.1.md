# US-3.1.1: Aggregate Torneo — máquina de estados

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.1
**Bounded Context**: `torneo`
**Capas afectadas**: `torneo/domain/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **implementar el aggregate `Torneo` con su máquina de estados completa**
para **modelar el ciclo de vida de un torneo de apnea desde su creación hasta su cierre**.

---

## Especificación

### Precondición

```
torneo/domain/aggregates/ — vacío (solo __init__.py)
torneo/domain/value_objects/ — vacío
torneo/domain/ports/ — vacío
```

### Postcondición

```python
# torneo/domain/value_objects/estado_torneo.py
class EstadoTorneo(StrEnum):
    CREADO = "CREADO"
    INSCRIPCION_ABIERTA = "INSCRIPCION_ABIERTA"
    PREPARACION = "PREPARACION"
    EJECUCION = "EJECUCION"
    PREMIACION = "PREMIACION"
    CERRADO = "CERRADO"
    CANCELADO = "CANCELADO"

# torneo/domain/value_objects/sede.py
@dataclass(frozen=True)
class Sede:
    nombre: str
    ciudad: str
    pais: str

# torneo/domain/value_objects/entidad_organizadora.py
@dataclass(frozen=True)
class EntidadOrganizadora:
    nombre: str
    tipo: str  # "FEDERACION" | "CLUB" | "ORGANIZACION"

# torneo/domain/aggregates/torneo.py
@dataclass
class Torneo:
    torneo_id: UUID
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede: Sede
    entidad_organizadora: EntidadOrganizadora
    estado: EstadoTorneo = EstadoTorneo.CREADO

    # Transiciones
    def abrir_inscripcion(self) -> None: ...       # CREADO → INSCRIPCION_ABIERTA
    def cerrar_inscripcion(self) -> None: ...      # INSCRIPCION_ABIERTA → PREPARACION
    def iniciar_ejecucion(self) -> None: ...       # PREPARACION → EJECUCION
    def volver_a_preparacion(self) -> None: ...    # EJECUCION → PREPARACION (retroceso)
    def iniciar_premiacion(self) -> None: ...      # EJECUCION → PREMIACION
    def cerrar(self) -> None: ...                  # PREMIACION → CERRADO
    def cancelar(self) -> None: ...                # cualquier estado (exc. CERRADO) → CANCELADO

# torneo/domain/ports/torneo_repository_port.py
class TorneoRepositoryPort(ABC):
    async def save(self, torneo: Torneo) -> None: ...
    async def find_by_id(self, torneo_id: UUID) -> Torneo | None: ...
    async def find_all(self) -> list[Torneo]: ...

# torneo/domain/exceptions.py
class TorneoNoEncontrado(Exception): ...
class TransicionEstadoInvalida(Exception): ...
class TorneoYaCancelado(Exception): ...
class TorneoCerrado(Exception): ...
```

### Invariantes

- `INV-T-01`: `nombre` no puede ser vacío ni solo espacios
- `INV-T-02`: `fecha_fin >= fecha_inicio`
- `INV-T-03`: Un torneo en estado `CERRADO` no puede transicionar (ni cancelarse)
- `INV-T-04`: El único retroceso permitido es `EJECUCION → PREPARACION`
- `INV-T-05`: `Cancelado` es estado terminal (no transiciona hacia ningún otro)
- `INV-T-06`: Las transiciones deben seguir estrictamente el grafo de estados definido

### Grafo de transiciones

```
CREADO
  └─ abrir_inscripcion() → INSCRIPCION_ABIERTA
       └─ cerrar_inscripcion() → PREPARACION
            └─ iniciar_ejecucion() → EJECUCION
                 ├─ volver_a_preparacion() → PREPARACION  ← único retroceso
                 └─ iniciar_premiacion() → PREMIACION
                       └─ cerrar() → CERRADO (terminal)

Desde cualquier estado (excepto CERRADO):
  └─ cancelar() → CANCELADO (terminal)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.1.1 — Aggregate Torneo

  Scenario: crear torneo con datos válidos
    Given datos válidos (nombre, fechas, sede, entidad_organizadora)
    When se instancia un Torneo
    Then el estado es CREADO
    And fecha_fin >= fecha_inicio

  Scenario: nombre vacío lanza excepción
    Given un nombre vacío o solo espacios
    When se instancia un Torneo
    Then se lanza ValueError

  Scenario: fecha_fin anterior a fecha_inicio lanza excepción
    Given fecha_fin < fecha_inicio
    When se instancia un Torneo
    Then se lanza ValueError

  Scenario: ciclo completo de transiciones
    Given un Torneo en estado CREADO
    When se ejecutan abrir_inscripcion, cerrar_inscripcion, iniciar_ejecucion, iniciar_premiacion, cerrar
    Then el estado final es CERRADO

  Scenario: retroceso EJECUCION a PREPARACION
    Given un Torneo en estado EJECUCION
    When se llama volver_a_preparacion()
    Then el estado es PREPARACION

  Scenario: cancelar desde cualquier estado activo
    Given un Torneo en estado INSCRIPCION_ABIERTA
    When se llama cancelar()
    Then el estado es CANCELADO

  Scenario: no se puede cancelar un torneo CERRADO
    Given un Torneo en estado CERRADO
    When se llama cancelar()
    Then se lanza TorneoCerrado

  Scenario: transición inválida lanza excepción
    Given un Torneo en estado CREADO
    When se llama iniciar_ejecucion() directamente (saltando INSCRIPCION_ABIERTA)
    Then se lanza TransicionEstadoInvalida
```

---

## Notas de implementación

- `Torneo` es un dataclass simple (no Event Sourcing — BC Supporting/CRUD).
- Las excepciones de dominio viven en `torneo/domain/exceptions.py`.
- `EstadoTorneo`, `Sede`, `EntidadOrganizadora` son value objects en `torneo/domain/value_objects/`.
- `TorneoRepositoryPort` es la única salida del dominio — no hay imports de infraestructura.
- Los eventos de dominio (`TorneoCreado`, `TorneoCancelado`, etc.) son opcionales en SP3; si se emiten, es para la integración con Notificaciones en SP4.

---

## Referencias

- Plan: `docs/plans/sp3/PLAN-SP3.md`
- RFs: RF-GT-01..07
- Context Map: `docs/design/context-map.md §3.1`

---

*Redactado: 2026-03-28 — SP3*
