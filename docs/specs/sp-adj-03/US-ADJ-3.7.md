# US-ADJ-3.7: Proyección `competencias_por_torneo` — O(n) → O(1)

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: HITO-15 — acción pendiente
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/application/queries/` · `competencia/infrastructure/` · `competencia/domain/ports/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **materializar una proyección `competencias_por_torneo` actualizada por evento**
para **que `ObtenerCompetenciasPorTorneoHandler` no escale linealmente con el número total de competencias históricas**.

---

## Contexto de la deuda

### HITO-15 — Read model implícito no materializado

`competencia/application/queries/obtener_competencias_por_torneo.py`:

```python
async def handle(self, query) -> list[CompetenciaSummaryDTO]:
    streams = await self._event_store.load_all_streams_with_prefix("competencia-")
    result = []
    for stream in streams:
        for event in stream:
            if event["event_type"] != "IntervaloOTConfigurado":
                continue
            payload = event["payload"]
            if UUID(payload.get("torneo_id", "")) == query.torneo_id:
                result.append(CompetenciaSummaryDTO(...))
            break
    return result
```

Para responder "dame las competencias del torneo X", el handler carga **todos los streams**
del BC Competencia y filtra en memoria. Es O(n) donde n = total de competencias
históricas en el sistema — no del torneo, sino de todos los torneos.

HITO-15 lo identifica explícitamente como un read model implícito no materializado,
y marca la acción como pendiente para SP-ADJ-03 o SP4.

En SP4 el volumen lo va a justificar: cada torneo puede tener entre 3 y 10 disciplinas,
y el sistema puede acumular décadas de torneos históricos.

---

## Especificación

### Proyección a materializar

```sql
-- competencia/infrastructure/projections/sqlite_competencias_por_torneo.py
CREATE TABLE IF NOT EXISTS competencias_por_torneo (
    competencia_id TEXT PRIMARY KEY,
    torneo_id      TEXT NOT NULL,
    disciplina     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cpt_torneo ON competencias_por_torneo(torneo_id);
```

La tabla se actualiza al procesar cada `IntervaloOTConfigurado` que incluya `torneo_id`.

### Puerto nuevo

```python
# competencia/domain/ports/competencias_por_torneo_port.py
from abc import ABC, abstractmethod
from uuid import UUID
from competencia.application.queries.obtener_competencias_por_torneo import CompetenciaSummaryDTO

class CompetenciasPorTorneoPort(ABC):
    """Puerto de lectura para la proyección competencias_por_torneo."""

    @abstractmethod
    async def guardar(self, dto: CompetenciaSummaryDTO) -> None:
        """Persiste o actualiza una entrada en la proyección."""

    @abstractmethod
    async def listar_por_torneo(self, torneo_id: UUID) -> list[CompetenciaSummaryDTO]:
        """Retorna las competencias del torneo desde la proyección materializada."""
```

### Implementación SQLite

```python
# competencia/infrastructure/projections/sqlite_competencias_por_torneo.py
class SQLiteCompetenciasPorTorneo(CompetenciasPorTorneoPort):
    """Proyección materializada en SQLite para competencias_por_torneo."""
    def __init__(self, db_path: str) -> None: ...
    async def guardar(self, dto: CompetenciaSummaryDTO) -> None: ...
    async def listar_por_torneo(self, torneo_id: UUID) -> list[CompetenciaSummaryDTO]: ...
```

### Handler de query refactorizado

```python
class ObtenerCompetenciasPorTorneoHandler:
    def __init__(self, proyeccion: CompetenciasPorTorneoPort) -> None:
        self._proyeccion = proyeccion

    async def handle(self, query: ObtenerCompetenciasPorTorneoQuery) -> list[CompetenciaSummaryDTO]:
        return await self._proyeccion.listar_por_torneo(query.torneo_id)
```

### Actualización de la proyección (síncrono, en el command handler)

El `ConfigurarIntervaloOTHandler` (o el lugar donde se persiste `IntervaloOTConfigurado`)
actualiza la proyección si el evento incluye `torneo_id`:

```python
# En ConfigurarIntervaloOTHandler.handle(), después de persistir el evento:
if command.torneo_id is not None:
    await self._proyeccion.guardar(CompetenciaSummaryDTO(
        competencia_id=command.competencia_id,
        disciplina=command.disciplina.value,
        torneo_id=command.torneo_id,
    ))
```

### DB path

La proyección puede usar la misma DB de Competencia (`COMPETENCIA_DB_PATH`) o una
DB separada. Decisión a tomar en implementación — documentar en el commit.

### Invariantes

- `INV-ADJ-3.7-1`: `ObtenerCompetenciasPorTorneoHandler` — `grep "load_all_streams_with_prefix"` devuelve cero matches
- `INV-ADJ-3.7-2`: el resultado de `listar_por_torneo` es idéntico al resultado anterior del escaneo de streams
- `INV-ADJ-3.7-3`: `app.py` actualiza el wiring de `ObtenerCompetenciasPorTorneoHandler` para inyectar la proyección
- `INV-ADJ-3.7-4`: los tests de integración de US-3.3.1 y US-3.3.2 pasan sin modificación

---

## Criterios de aceptación

```gherkin
Scenario: ObtenerCompetenciasPorTorneoHandler no escanea todos los streams
  Given el handler refactorizado con la proyección inyectada
  Then no contiene load_all_streams_with_prefix en su implementación

Scenario: proyeccion se actualiza al configurar IntervaloOT con torneo_id
  Given una competencia nueva con torneo_id
  When se ejecuta ConfigurarIntervaloOT
  Then la proyeccion contiene la entrada para esa competencia

Scenario: listar_por_torneo retorna solo las competencias del torneo indicado
  Given 3 competencias: 2 del torneo A, 1 del torneo B
  When se llama listar_por_torneo(torneo_id=A)
  Then retorna exactamente 2 competencias
  And no incluye la competencia del torneo B

Scenario: flujo E2E Torneo → Competencia sigue funcionando
  Given un torneo con 2 disciplinas configuradas
  When se crean las competencias y se consulta GET /competencias?torneo_id=X
  Then retorna las 2 competencias del torneo
```

---

## Notas de implementación

- La proyección es **síncrona**: se actualiza en el mismo request que persiste el evento.
  No requiere worker separado ni procesamiento asíncrono.
- Si hay competencias existentes en el event store sin entrada en la proyección
  (datos de prueba previos), puede ser necesario un script de backfill de una sola vez.
  Evaluar si es necesario durante la implementación.
- La DB de la proyección puede ser la misma que la de Competencia — SQLite soporta
  múltiples tablas en el mismo archivo.
- `CompetenciaSummaryDTO` ya existe en `obtener_competencias_por_torneo.py`. Reusar.

---

## Referencias

- HITO-15: `docs/contexto/HITO-15-CQRS-PROYECCIONES-EMERGEN-DE-ES.md`
- US-3.3.1: implementación original del handler (O(n))
- US-3.3.2: tests E2E que validan el flujo Torneo → Competencia
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
