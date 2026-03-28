# US-ADJ-1.4: Router DIP — EventStorePort + mover cross-BC a app.py

**Estado**: `Backlog`
**Sprint**: SP-ADJ-01 — Ajuste Técnico Post-SP2
**Issues**: ADJ-04 · ADJ-05
**Bounded Context**: `competencia` · `app.py`
**Capas afectadas**: `competencia/api/router.py` · `src/app.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **corregir dos violaciones DIP en el router de competencia**
para **que la capa API dependa de abstracciones y que el cableado cross-BC viva en el composition root**.

---

## Contexto de la deuda

### ADJ-05 — `EventStoreDep` tipado como clase concreta

```python
# router.py línea 60:
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

# línea 115:
def get_event_store() -> SQLiteEventStore:  ← tipo concreto
    return SQLiteEventStore(db_path)

# línea 147:
EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]  ← tipo concreto
```

El puerto `EventStorePort` existe. La capa `api/` debería depender de la abstracción,
no de la implementación SQLite.

### ADJ-04 — Router importa directamente del BC resultados

```python
# router.py líneas 70–76:
from resultados.application.commands.calcular_ranking import CalcularRankingHandler
from resultados.infrastructure.repositories.resultados_competencia_adapter import ResultadosCompetenciaAdapter
```

`get_on_finalizada_callback` (líneas 157–176) construye el handler de `resultados` dentro
del router de `competencia`. Violaciones simultáneas:
- **DIP**: depende de implementaciones concretas de otro BC
- **ADR-006 (BC isolation)**: el router de un BC no debe importar del otro
- **SRP**: el router asume responsabilidad de composition root

El lugar correcto es `app.py` — el composition root del sistema.

---

## Especificación

### ADJ-05: corregir tipo de `EventStoreDep`

| | |
|---|---|
| **Precondición** | `get_event_store() -> SQLiteEventStore`, `EventStoreDep` tipado como concreto |
| **Postcondición** | `get_event_store() -> EventStorePort`, `EventStoreDep = Annotated[EventStorePort, ...]` |
| **Invariante** | El runtime sigue usando `SQLiteEventStore`; el tipo visible es el puerto |

```python
# Después:
from competencia.domain.ports.event_store_port import EventStorePort

def get_event_store() -> EventStorePort:
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)

EventStoreDep = Annotated[EventStorePort, Depends(get_event_store)]
```

### ADJ-04: mover cableado P-08 a `app.py`

| | |
|---|---|
| **Precondición** | `get_on_finalizada_callback` y los imports de `resultados` viven en `competencia/api/router.py` |
| **Postcondición** | `router.py` no importa nada de `resultados`; el callback se inyecta desde `app.py` |
| **Invariante** | El comportamiento de P-08 (CompetenciaFinalizada → CalcularRanking) es idéntico |

**Mecanismo:** el `AsignarTarjetaHandler` ya acepta `on_finalizada` como parámetro opcional.
La modificación es solo en el wiring, no en la lógica.

```python
# app.py — composition root:
from competencia.api.router import router as competencia_router
from resultados.application.commands.calcular_ranking import CalcularRankingHandler, CalcularRankingCommand
from resultados.infrastructure.repositories.resultados_competencia_adapter import ResultadosCompetenciaAdapter

def build_on_finalizada_callback(...) -> Callable:
    """Construye el callback P-08 → CalcularRanking. Vive en el composition root."""
    ...

# router.py — solo recibe el callback inyectado, no lo construye
def get_asignar_tarjeta_handler(
    event_store: EventStoreDep,
    performances_estado: PerformancesEstadoAdapterDep,
    on_finalizada: OnFinalizadaDep,  ← inyectado desde fuera
) -> AsignarTarjetaHandler:
    ...
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-1.4 — Router DIP fixes

  Scenario: router.py no importa de resultados
    Given el archivo competencia/api/router.py refactorizado
    Then no contiene ningún import con "resultados" en el path

  Scenario: EventStoreDep usa el puerto, no la implementación
    Given el archivo competencia/api/router.py refactorizado
    Then EventStoreDep está anotado con EventStorePort
    And get_event_store() retorna EventStorePort como tipo

  Scenario: P-08 funciona igual tras mover el cableado
    Given una competencia con 3 performances, 2 Ejecutadas
    When la última performance recibe tarjeta blanca (POST /asignar-tarjeta)
    Then CompetenciaFinalizada se emite
    And CalcularRanking se ejecuta automáticamente
    And GET /resultados/{id}/ranking retorna el ranking calculado

  Scenario: app.py contiene el cableado cross-BC
    Given el archivo src/app.py refactorizado
    Then contiene la construcción del callback on_finalizada con CalcularRankingHandler
```

---

## Notas de implementación

- `app.py` necesita revisar cómo pasa `on_finalizada` al router. FastAPI permite
  sobreescribir dependencias en el app level con `app.dependency_overrides`.
- Alternativa más simple: `app.py` construye el router con el callback pre-configurado
  en lugar de usar el DI de FastAPI para esto.
- Verificar que los tests de integración que testean P-08 no dependan de la ubicación
  del cableado — deberían testear el comportamiento HTTP end-to-end.
- El import de `SQLiteEventStore` puede permanecer en `router.py` dentro de
  `get_event_store()` (es el factory) — lo que cambia es el tipo declarado de retorno.

---

## Referencias

- Análisis: `.work/revision-sp2/05-revision-solid.md` (H-M, H-N)
- Plan: `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`
- ADR-006: `docs/adr/ADR-006-estructura-bc-first.md`

---

*Redactado: 2026-03-28 — SP-ADJ-01*
