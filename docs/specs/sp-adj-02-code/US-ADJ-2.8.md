# US-ADJ-2.8: DIP fix — `EventStoreDep` tipado como `EventStorePort`

**Estado**: `Done`
**Sprint**: SP-ADJ-02-code — Ajuste Técnico Post-BL-002
**Issues**: B-05
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/api/router.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **que `EventStoreDep` esté tipado con `EventStorePort` en lugar de `SQLiteEventStore`**
para **que la capa API dependa de la abstracción y no de la implementación concreta**.

---

## Contexto de la deuda

### B-05 — `EventStoreDep` usa tipo concreto en lugar del puerto

```python
# competencia/api/router.py:
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

def get_event_store() -> SQLiteEventStore:           # ← tipo concreto
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)

EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]  # ← tipo concreto
```

El puerto `EventStorePort` existe en `competencia/domain/ports/`. El factory
`get_event_store()` puede seguir retornando `SQLiteEventStore` en runtime —
lo que cambia es el **tipo declarado** que el resto del router ve.

Esta deuda fue especificada en US-ADJ-1.4 (SP-ADJ-01) como ADJ-05 pero no fue
completada — gap D-04 de la revisión de hito.

---

## Especificación

### Precondición

```python
# competencia/api/router.py:
def get_event_store() -> SQLiteEventStore:
    ...

EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]
```

### Postcondición

```python
# competencia/api/router.py:
from competencia.domain.ports.event_store_port import EventStorePort

def get_event_store() -> EventStorePort:
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)

EventStoreDep = Annotated[EventStorePort, Depends(get_event_store)]
```

### Invariantes

- `INV-ADJ-2.8-1`: El runtime sigue retornando `SQLiteEventStore` — no hay cambio funcional
- `INV-ADJ-2.8-2`: `mypy` no reporta errores en `router.py` tras el cambio
- `INV-ADJ-2.8-3`: `pytest tests/` — 100% pass sin regresiones

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-2.8 — DIP fix EventStoreDep

  Scenario: get_event_store declara retorno EventStorePort
    Given el archivo competencia/api/router.py modificado
    Then get_event_store() tiene anotación de retorno EventStorePort
    And el runtime retorna una instancia de SQLiteEventStore

  Scenario: EventStoreDep usa el puerto como tipo
    Given el archivo competencia/api/router.py modificado
    Then EventStoreDep está anotado con EventStorePort
    And no contiene referencias directas a SQLiteEventStore fuera del factory

  Scenario: mypy no reporta errores en router.py
    Given el archivo competencia/api/router.py modificado
    When se ejecuta mypy en modo estricto sobre router.py
    Then no hay errores de tipo

  Scenario: todos los tests pasan
    Given el router.py modificado
    When se ejecuta pytest tests/
    Then 100% de los tests pasan
```

---

## Notas de implementación

- Es un cambio mínimo: 3 líneas modificadas, 1 import agregado.
- El import de `SQLiteEventStore` permanece en `router.py` — lo usa el factory.
- Verificar que `EventStorePort` es un ABC o Protocol con los métodos que el router usa.
- Si `mypy` detecta incompatibilidad (el tipo concreto no satisface el protocolo),
  revisar si `SQLiteEventStore` declara correctamente que implementa `EventStorePort`.

---

## Referencias

- Revisión: `.work/revision-consistencia.md` (gap B-05, D-04)
- Spec original (no implementada): `docs/specs/sp-adj-01/US-ADJ-1.4.md` (ADJ-05)
- Plan: `docs/plans/sp-adj-02-code/PLAN-SP-ADJ-02-code.md`
- `EventStorePort`: `src/competencia/domain/ports/event_store_port.py`

---

*Redactado: 2026-03-28 — SP-ADJ-02-code*
