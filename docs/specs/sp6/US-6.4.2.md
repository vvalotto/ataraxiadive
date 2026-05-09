# US-6.4.2: Materializar proyección `competencias_por_torneo` en CalcularOverallHandler

**Estado**: `Pending`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgo**: ARCH-01
**Bounded Context**: `resultados` (consumidor) + `competencia` (proyección)
**Capas afectadas**:
- `resultados/application/commands/calcular_overall.py`
- `src/app.py` (composition root)

---

## Descripción

Como **sistema calculando el ranking overall de un torneo**,
quiero **que `CalcularOverallHandler` use la proyección materializada `CompetenciasPorTorneoPort` en lugar de escanear todos los streams del event store**
para **que la operación sea O(1) por torneo en lugar de O(n) sobre todos los streams de competencia**.

---

## Contexto del Hallazgo

### ARCH-01 — O(n) scan en CalcularOverallHandler

`CalcularOverallHandler.handle()` llama a `_mapear_competencias_por_torneo()`, que hace:

```python
streams = await competencia_store.load_all_streams_with_prefix("competencia-")
for events in streams:  # itera TODOS los streams de competencia
    for event in events:
        if event["event_type"] == _EVENTO_INTERVALO_OT:
            ...
```

Esto carga y recorre **todos** los streams del event store de competencia para encontrar los que pertenecen al torneo pedido. Con un torneo real que tiene N competencias de múltiples torneos, el costo crece linealmente.

La proyección `SQLiteCompetenciasPorTorneo` ya existe y tiene un índice en `torneo_id`. El query `listar_por_torneo(torneo_id)` es O(1) por diseño. Solo falta inyectarla en el handler.

**Nota**: la proyección se actualiza en `app.py` vía el event handler `CompetenciaIniciadaHandler` que llama a `guardar()`. El dato ya está disponible.

---

## Especificación

### Tarea 1 — Inyectar `CompetenciasPorTorneoPort` en `CalcularOverallHandler`

| | |
|---|---|
| **Precondición** | `CalcularOverallHandler.__init__` recibe `ranking_store` y `competencia_store` |
| **Postcondición** | `CalcularOverallHandler.__init__` recibe `ranking_store` y `competencias_por_torneo: CompetenciasPorTorneoPort` |
| **Invariante** | La interfaz del handler (command → list) no cambia |

```python
# calcular_overall.py — antes:
class CalcularOverallHandler:
    def __init__(
        self,
        ranking_store: EventStorePort,
        competencia_store: EventStorePort,
    ) -> None:
        self._ranking_store = ranking_store
        self._competencia_store = competencia_store

# después:
from competencia.domain.ports.competencias_por_torneo_port import CompetenciasPorTorneoPort

class CalcularOverallHandler:
    def __init__(
        self,
        ranking_store: EventStorePort,
        competencias_por_torneo: CompetenciasPorTorneoPort,
    ) -> None:
        self._ranking_store = ranking_store
        self._competencias_por_torneo = competencias_por_torneo
```

### Tarea 2 — Reemplazar `_mapear_competencias_por_torneo` por query a la proyección

| | |
|---|---|
| **Precondición** | `_mapear_competencias_por_torneo` itera todos los streams; `handle()` la llama con `self._competencia_store` |
| **Postcondición** | `handle()` usa `self._competencias_por_torneo.listar_por_torneo(torneo_id)` directamente |
| **Invariante** | El resultado es el mismo: `dict[Disciplina, UUID]`; la función `_mapear_competencias_por_torneo` puede eliminarse |

```python
# En handle():
records = await self._competencias_por_torneo.listar_por_torneo(command.torneo_id)
competencias: dict[Disciplina, UUID] = {
    Disciplina(r.disciplina): r.competencia_id
    for r in records
    if Disciplina(r.disciplina) in set(command.disciplinas)
}
```

La función libre `_mapear_competencias_por_torneo` queda sin uso y se elimina del módulo.

### Tarea 3 — Actualizar composition root (`app.py`)

| | |
|---|---|
| **Precondición** | `CalcularOverallHandler` se instancia en `app.py` con `competencia_store` |
| **Postcondición** | Se inyecta `SQLiteCompetenciasPorTorneo` (ya instanciada en `app.py`) en lugar de `competencia_store` |
| **Invariante** | `competencia_store` (EventStore) sigue existiendo para otros usos; solo se elimina su inyección en `CalcularOverallHandler` |

```python
# app.py — buscar la instanciación de CalcularOverallHandler y actualizar:
calcular_overall_handler = CalcularOverallHandler(
    ranking_store=resultados_event_store,
    competencias_por_torneo=competencias_por_torneo_projection,  # ya existe en app.py
)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.2 — CalcularOverallHandler usa proyección materializada

  Scenario: CalcularOverall no accede al event store de competencia
    Given un torneo con 3 disciplinas registradas en la proyección
    When se ejecuta CalcularOverallCommand para ese torneo
    Then el handler NO llama a competencia_store.load_all_streams_with_prefix
    And llama a competencias_por_torneo.listar_por_torneo(torneo_id) exactamente una vez

  Scenario: Resultado del overall es idéntico al anterior
    Given un torneo con competencias finalizadas y rankings calculados
    When se ejecuta CalcularOverallCommand antes y después de este cambio
    Then los entries del overall son equivalentes en ambos casos

  Scenario: Handler funciona con torneo sin competencias registradas
    Given un torneo sin competencias en la proyección
    When se ejecuta CalcularOverallCommand
    Then retorna lista vacía sin error (o lanza DisciplinasNoFinalizadas según invariante existente)
```

---

## Notas de implementación

- `SQLiteCompetenciasPorTorneo` ya se instancia en `app.py` como `competencias_por_torneo_projection` — verificar el nombre de la variable antes de referenciarla
- Posible import cross-BC: `CalcularOverallHandler` (en BC `resultados`) importaría `CompetenciasPorTorneoPort` (en BC `competencia`). Esto es comunicación entre BCs a través de un port — aceptable según la nota de ARCH-03, pero documentar si el DesignReviewer lo reporta
- Eliminar el import de `EventStorePort` del módulo si queda sin uso
- Los tests de integración de `CalcularOverallHandler` deben pasar un mock de `CompetenciasPorTorneoPort` en lugar de un event store

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — ARCH-01
- HITO-15: `docs/contexto/` — proyección `competencias_por_torneo`
- Código fuente: `src/resultados/application/commands/calcular_overall.py`
- Proyección existente: `src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py`
- Port: `src/competencia/domain/ports/competencias_por_torneo_port.py`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
