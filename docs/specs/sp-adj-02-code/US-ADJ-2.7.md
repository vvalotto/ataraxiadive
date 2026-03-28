# US-ADJ-2.7: Mover composition root P-08 a `app.py`

**Estado**: `Done`
**Sprint**: SP-ADJ-02-code — Ajuste Técnico Post-BL-002
**Issues**: B-03 · B-04
**Bounded Context**: `competencia` · `resultados` · `app.py`
**Capas afectadas**: `competencia/api/router.py` · `resultados/api/router.py` · `src/app.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **mover el cableado de la política P-08 (CompetenciaFinalizada → CalcularRanking) a `src/app.py`**
para **que el router de `competencia` no importe nada del BC `resultados` y el composition root
viva en el único lugar correcto**.

---

## Contexto de la deuda

### B-03 — `competencia/api/router.py` importa de `resultados/`

```python
# competencia/api/router.py líneas 70–76:
from resultados.application.commands.calcular_ranking import CalcularRankingHandler
from resultados.infrastructure.repositories.resultados_competencia_adapter import ResultadosCompetenciaAdapter
```

`get_on_finalizada_callback()` (función de dependencia FastAPI) construye el
`CalcularRankingHandler` directamente en el router de `competencia`. Esto viola:
- **ADR-006 (BC isolation)**: el router de un BC no importa del dominio de otro BC
- **SRP**: el router asume responsabilidad del composition root
- **Regla de Oro**: `api/` de un BC no puede importar de otro BC

### B-04 — `resultados/api/router.py` importa `SQLiteEventStore` de `competencia.infrastructure`

```python
# resultados/api/router.py línea 12:
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
```

El router de `resultados` accede directamente a la infraestructura de `competencia`
para construir su propio store. Doble violación: cross-BC + DIP.

---

## Especificación

### Precondición

```python
# competencia/api/router.py contiene:
from resultados.application.commands.calcular_ranking import CalcularRankingHandler
from resultados.infrastructure.repositories.resultados_competencia_adapter import ResultadosCompetenciaAdapter

def get_on_finalizada_callback(event_store: EventStoreDep) -> Callable:
    adapter = ResultadosCompetenciaAdapter(event_store)
    handler = CalcularRankingHandler(ranking_repo=..., adapter=adapter)
    return lambda competencia_id: handler.handle(...)
```

```python
# resultados/api/router.py contiene:
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
```

### Postcondición

```python
# competencia/api/router.py — sin imports de resultados/
# El callback on_finalizada se recibe como dependencia inyectada

# resultados/api/router.py — sin imports de competencia.infrastructure
# Recibe su repositorio/store via inyección, no lo construye desde la infra de competencia

# src/app.py — composition root wires P-08:
from competencia.api import router as competencia_router
from resultados.application.commands.calcular_ranking import CalcularRankingHandler
from resultados.infrastructure.repositories.resultados_competencia_adapter import ResultadosCompetenciaAdapter

def build_on_finalizada_callback(db_path: str) -> Callable:
    """Construye el callback P-08 → CalcularRanking. Vive en el composition root."""
    event_store = SQLiteEventStore(db_path)
    adapter = ResultadosCompetenciaAdapter(event_store)
    handler = CalcularRankingHandler(...)
    return lambda competencia_id: handler.handle(CalcularRankingCommand(competencia_id))
```

### Invariantes

- `INV-ADJ-2.7-1`: El comportamiento de P-08 (CompetenciaFinalizada → CalcularRanking) es idéntico al actual
- `INV-ADJ-2.7-2`: `competencia/api/router.py` — `grep "from resultados"` devuelve cero matches
- `INV-ADJ-2.7-3`: `resultados/api/router.py` — `grep "from competencia.infrastructure"` devuelve cero matches
- `INV-ADJ-2.7-4`: Los tests de integración que prueban P-08 end-to-end siguen pasando

---

## Plan de implementación

### Paso 1 — Refactorizar `competencia/api/router.py`

Eliminar los imports de `resultados`. El callback `on_finalizada` debe llegar
como dependencia inyectada desde el exterior, no construirse en el router.

Mecanismo recomendado: `app.dependency_overrides` o un módulo de dependencias
compartidas que `app.py` configure antes de montar el router.

Alternativa más simple: parametrizar el router con el callback antes de `include_router()`:

```python
# En router.py — solo declara que necesita el callback:
_on_finalizada_callback: Callable[[str], None] | None = None

def set_on_finalizada_callback(callback: Callable[[str], None]) -> None:
    global _on_finalizada_callback
    _on_finalizada_callback = callback
```

```python
# En app.py — configura antes de incluir el router:
from competencia.api.router import set_on_finalizada_callback, router as competencia_router
set_on_finalizada_callback(build_on_finalizada_callback(db_path))
app.include_router(competencia_router)
```

### Paso 2 — Refactorizar `resultados/api/router.py`

Eliminar el import de `competencia.infrastructure.event_store`. El store de eventos
de competencia que necesita el BC Resultados debe llegar via parámetro de configuración
o dependencia, no construirse con un import directo.

Si `resultados/api/router.py` necesita un event store para leer eventos de competencia,
`app.py` debe construirlo y pasarlo (o usar `dependency_overrides`).

### Paso 3 — Actualizar `src/app.py`

`app.py` pasa a ser el composition root real: importa de ambos BCs y cablea P-08.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-2.7 — Composition root en app.py

  Scenario: router de competencia no importa de resultados
    Given el archivo competencia/api/router.py refactorizado
    Then no contiene ningún import con "resultados" en el path

  Scenario: router de resultados no importa de competencia.infrastructure
    Given el archivo resultados/api/router.py refactorizado
    Then no contiene ningún import con "competencia.infrastructure" en el path

  Scenario: app.py contiene el cableado de P-08
    Given el archivo src/app.py refactorizado
    Then contiene la construcción del callback on_finalizada con CalcularRankingHandler
    And importa desde resultados.application.commands.calcular_ranking

  Scenario: P-08 funciona igual tras mover el cableado
    Given una competencia con 3 performances, 2 Ejecutadas
    When la última performance recibe tarjeta blanca (POST /asignar-tarjeta)
    Then CompetenciaFinalizada se emite
    And CalcularRanking se ejecuta automáticamente
    And GET /resultados/{id}/ranking retorna el ranking calculado
```

---

## Notas de implementación

- Revisar si ya existe un mecanismo de DI en el router (`dependency_overrides` de FastAPI
  permite que `app.py` sobreescriba dependencias a nivel de aplicación).
- La forma más directa y compatible con el diseño actual es el patrón
  `set_callback()` + `app.py` configura antes de `include_router()`.
- Los tests de integración que mockean P-08 pueden quedar intactos si el mecanismo
  de inyección lo permite.
- `app.py` es el único archivo que tiene "permiso" de importar de múltiples BCs —
  su rol es exactamente ese.

---

## Referencias

- Regla de Oro: `CLAUDE.md §6`
- ADR-006: `docs/adr/ADR-006-estructura-bc-first.md`
- Revisión: `.work/revision-consistencia.md` (gaps B-03, B-04)
- Plan: `docs/plans/sp-adj-02-code/PLAN-SP-ADJ-02-code.md`
- US relacionada: `docs/specs/sp-adj-01/US-ADJ-1.4.md` (spec original de ADJ-04 — no implementada)

---

*Redactado: 2026-03-28 — SP-ADJ-02-code*
