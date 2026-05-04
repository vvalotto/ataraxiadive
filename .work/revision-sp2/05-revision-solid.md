# Revisión SOLID — Cierre SP2

**Fecha:** 2026-03-28
**Archivos inspeccionados:**
- `src/competencia/api/router.py`
- `src/competencia/domain/aggregates/performance.py` (ya leído)
- `src/competencia/domain/aggregates/competencia.py` (ya leído)

---

## DIP — Dependency Inversion Principle

### Violación 1: EventStoreDep tipado como clase concreta (media)

```python
# router.py línea 60 — importa infraestructura directamente en la capa api/
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

# línea 115 — función retorna tipo concreto
def get_event_store() -> SQLiteEventStore:
    return SQLiteEventStore(db_path)

# línea 147 — el tipo de dependencia es la implementación, no el puerto
EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]
```

El puerto `EventStorePort` existe y es el contrato correcto. La cadena entera de providers
(`EventStoreDep`, y todos los `get_*` que lo reciben) usa el tipo concreto.

**Fix:** cambiar el tipo de retorno a `EventStorePort` y el `Annotated`. 2 líneas de código.

### Violación 2: Cross-BC directo en el router (alta)

```python
# router.py líneas 70–76 — el router de competencia importa del BC resultados:
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
```

`get_on_finalizada_callback` (líneas 157–176) instancia `CalcularRankingHandler` dentro
del router de `competencia`. Esto viola simultáneamente:
- **DIP**: `competencia` depende de una implementación concreta de `resultados`
- **ADR-006 (BC isolation)**: un router de BC no debería importar de otro BC

El lugar correcto para este cableado es `app.py` — el composition root del sistema.
El callback debería ser inyectado desde afuera, no construido dentro del router.

---

## OCP — Open/Closed Principle

### Inconsistencia en `_apply_stored` entre Performance y Competencia (baja)

`Performance` ya resuelve OCP correctamente:
```python
# performance.py __init__ — dict inicializado una vez:
self._event_handlers: dict[str, Any] = {
    "APRegistrado": self._apply_ap_registrado,
    ...
}
# _apply_stored usa self._event_handlers (no lo recrea)
# Comentario explícito: "OCP: agregar un tipo nuevo no requiere modificar este método"
```

`Competencia` recrea el dict en cada llamada a `_apply_stored`:
```python
# competencia.py _apply_stored — dict local, recreado en cada invocación:
def _apply_stored(self, event):
    _handlers: dict[str, Any] = {
        "IntervaloOTConfigurado": self._apply_intervalo_ot_configurado,
        ...
    }
    handler = _handlers.get(event_type)
```

Ambos son OCP-compliant funcionalmente. Pero `Competencia` recrea el dict en cada
reconstitución (N events = N dicts creados). En ES con streams largos, esto es ineficiente.
Además es inconsistente con el patrón ya establecido en `Performance`.

**Fix:** mover `_handlers` a `__init__` en `Competencia`, igual que `Performance`.

---

## SRP — Single Responsibility Principle

### router.py mezcla 4 responsabilidades (media)

1. **Schemas de request/response** — `CambioGrillaSchema`, `AjustarGrillaBody`, etc.
2. **Wiring de dependencias** — 20+ funciones `get_*` y tipos `Annotated`
3. **Endpoints HTTP** — los handlers de FastAPI
4. **Composición cross-BC** — `get_on_finalizada_callback` con lógica de wiring entre BCs

El punto 4 es el que rompe SRP más claramente: la composición entre `competencia` y
`resultados` no debería vivir en el router del BC. Los puntos 1 y 2 son separables
en `schemas.py` y `dependencies.py` sin urgencia.

**Propuesta de separación (baja urgencia, para SP3):**
```
competencia/api/
  router.py       ← solo endpoints
  schemas.py      ← Pydantic models de request/response
  dependencies.py ← providers de DI
```
El cableado cross-BC se mueve a `app.py`.

---

## LSP e ISP — Sin violaciones identificadas

Los puertos están bien segmentados (`EventStorePort`, `CompetenciaEstadoPort`,
`AndarivelesActivosPort`, etc.) — ningún cliente usa más de lo que necesita.
No hay jerarquías de herencia que violen LSP.

---

## Resumen de Violaciones SOLID

| Principio | Violación | Severidad | Fix |
|---|---|---|---|
| DIP | `EventStoreDep` tipado como `SQLiteEventStore` | Media | 2 líneas en router.py |
| DIP + BC boundary | Router importa `CalcularRankingHandler` de `resultados` | Alta | Mover a `app.py` |
| OCP | `Competencia._apply_stored` recrea dict local | Baja | Mover a `__init__` |
| SRP | `router.py` mezcla schemas + DI + endpoints + cross-BC | Media | Separar en SP3 |

---

## Hallazgos para el Experimento

### H-M — La violación DIP de mayor riesgo emerge en la integración entre BCs
La violación de tipo `EventStoreDep` es mecánica y de bajo riesgo.
La violación del cross-BC en el router es la que tiene impacto real:
si `resultados` cambia su API de aplicación, `competencia` se rompe.
IEDD especificó la separación de BCs en ADR-006, pero no proveyó un mecanismo
explícito para el wiring de callbacks cross-BC — ese gap emergió naturalmente en SP2
con la política P-08.

### H-N — app.py como composition root: concepto presente pero subutilizado
El sistema tiene `app.py` como punto de ensamble, pero el cableado cross-BC terminó
en el router del BC que lo necesitaba primero (competencia). Esto es un patrón de deuda
que se repite en proyectos reales: el composition root existe pero las dependencias
"migran" al lugar donde se necesitan. La revisión de cierre de SP es el momento para
repatriarlo.

### H-O — Inconsistencia de patrón entre aggregates: riesgo de mantenimiento
`Performance` documenta explícitamente el patrón OCP en `_apply_stored`.
`Competencia` usa una variante sin el beneficio del patrón.
Cuando un nuevo desarrollador (o una nueva US) agregue un evento a `Competencia`,
podría copiar el patrón de `Competencia` en lugar del de `Performance` — propagando
la variante subóptima. La consistencia del patrón vale más que la optimización puntual.
