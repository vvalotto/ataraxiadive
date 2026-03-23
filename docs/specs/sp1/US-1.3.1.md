# US-1.3.1: Interfaz del Juez — Read Models y Endpoints

**Estado**: `Pendiente`
**Incremento**: Inc 1.3 — El Juez Ve y Toca
**Subproyecto**: SP1 — La Performance
**Tipo**: Query-side — sin nuevos eventos de dominio
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **consultar el estado actual de la competencia desde mi celular**
para **saber quién está compitiendo ahora, quiénes son los próximos atletas y cuánto
falta para terminar**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Rol |
|---|---|---|
| Aggregate | `Performance` | Fuente de verdad — se reconstituye desde el Event Store |
| Puerto (nuevo) | `EventStorePort.load_all_streams_with_prefix` | Carga todos los streams de una competencia |
| Read Models | `PerformanceActualDTO`, `ProximoAtletaDTO`, `ProgresoCompetenciaDTO` | Proyecciones de solo-lectura |

### Lenguaje ubicuo relevante

- **Performance actual**: la performance en estado `Llamada` o `ResultadoRegistrado`
  (el atleta que el juez está evaluando en este momento).
- **Próximos atletas**: performances en estado `AnunciadaAP`, ordenadas por momento de registro
  (proxy de orden de grilla en SP1 — la grilla real se implementa en SP2).
- **Progreso**: proporción ejecutadas+DNS / total, con conteo de DNS acumulados.

---

## Especificación del comportamiento

### Precondición general

- Existe al menos una `Performance` registrada para la `competencia_id` dada.
- Si no hay ninguna, los endpoints retornan estructuras vacías (no error).

### Decisión de diseño: extensión de EventStorePort

El `EventStorePort` actual solo soporta carga por `stream_id` individual.
Para proyectar read models de una competencia completa se agrega:

```python
async def load_all_streams_with_prefix(self, prefix: str) -> list[list[dict[str, Any]]]
```

- Carga todos los streams cuyo `stream_id` comienza con `prefix`.
- Cada elemento de la lista es la secuencia completa de eventos de un stream.
- Implementado en `SQLiteEventStore` con `WHERE stream_id LIKE ?`.

> **Justificación SP1**: la alternativa (PerformanceQueryPort separado) implica
> mantener una tabla de proyección — overhead desproporcionado para SP1.
> En SP2/SP3 se evaluará migrar a un read model materializado.

### Read Model 1 — PerformanceActual

**Endpoint:** `GET /competencia/{competencia_id}/performance/actual`

| Campo | Origen |
|---|---|
| `performance_id` | `APRegistrado.performance_id` |
| `nombre_atleta` | hardcodeado: `"Atleta-{participante_id[:8]}"` (SP1) |
| `ap_declarado` | `APRegistrado.valor_ap` |
| `unidad` | `APRegistrado.unidad` |
| `andarivel` | `AtletaLlamado.posicion_grilla` |
| `estado` | estado proyectado del aggregate |

**Lógica:** cargar todos los streams con prefijo `"performance-{competencia_id}-"`,
reconstituir cada `Performance`, retornar la primera en estado `Llamada` o `ResultadoRegistrado`.

**Respuesta vacía:** `null` (HTTP 200) si no hay performance activa.

### Read Model 2 — ProximosAtletas

**Endpoint:** `GET /competencia/{competencia_id}/performance/proximas`

| Campo | Origen |
|---|---|
| `nombre_atleta` | hardcodeado: `"Atleta-{participante_id[:8]}"` (SP1) |
| `ap_declarado` | `APRegistrado.valor_ap` |
| `unidad` | `APRegistrado.unidad` |
| `posicion` | índice de orden (1-based) por `APRegistrado.occurred_at` |

**Lógica:** filtrar performances en estado `AnunciadaAP`, ordenar por `occurred_at`
del primer evento, retornar las 3 primeras.

> **SP1 simplification**: en SP2, el orden será por `posicion_grilla` de la grilla
> oficial. En SP1 no existe grilla — el orden de registro es el proxy.

**Respuesta vacía:** lista vacía `[]`.

### Read Model 3 — ProgresoCompetencia

**Endpoint:** `GET /competencia/{competencia_id}/progreso`

| Campo | Origen |
|---|---|
| `total` | count de todos los streams para esta competencia |
| `ejecutadas` | count de performances en estado `Ejecutada` |
| `dns_count` | count de performances en estado `DNS` |
| `completadas` | `ejecutadas + dns_count` |

**Lógica:** cargar todos los streams, reconstituir cada `Performance`, agrupar por estado.

**Respuesta vacía:** `{total: 0, ejecutadas: 0, dns_count: 0, completadas: 0}`.

---

## Criterios de aceptación (BDD)

Ver `tests/features/US-1.3.1-interfaz-juez.feature` — 4 escenarios:

1. **Performance actual** — competencia con una performance en estado `Llamada`
2. **Próximos atletas** — competencia con 5 performances, 2 llamadas, 3 en `AnunciadaAP`
3. **Progreso** — competencia con performances en múltiples estados
4. **Competencia vacía** — sin performances registradas → estructuras vacías

---

## Impacto arquitectónico

| Capa | Cambios |
|---|---|
| Domain / ports | `EventStorePort` +1 método abstracto `load_all_streams_with_prefix` |
| Infrastructure | `SQLiteEventStore` implementa el nuevo método |
| Application / queries | 3 nuevos archivos: `obtener_performance_actual.py`, `obtener_proximas_performances.py`, `obtener_progreso.py` |
| API | `src/competencia/api/router.py` — nuevo, con 3 GET endpoints |
| `app.py` | Registra el router de `competencia` |

**Capas NO afectadas:**
- `domain/aggregates/performance.py` — sin cambios (se usa `reconstitute()` existente)
- `domain/events/` — sin nuevos eventos
- `application/commands/` — sin cambios

**Restricciones de métricas:**
- No se esperan cambios en CBO/WMC de `Performance` (solo se usa, no se modifica)
- Los nuevos query handlers son clases simples (~5 métodos públicos c/u)

---

## Componentes a crear

| Artefacto | Path |
|---|---|
| Puerto actualizado | `src/competencia/domain/ports/event_store_port.py` |
| Infra actualizada | `src/competencia/infrastructure/event_store/sqlite_event_store.py` |
| Query 1 | `src/competencia/application/queries/obtener_performance_actual.py` |
| Query 2 | `src/competencia/application/queries/obtener_proximas_performances.py` |
| Query 3 | `src/competencia/application/queries/obtener_progreso.py` |
| API router | `src/competencia/api/router.py` |
| App ensamble | `src/app.py` (actualizar) |
| Tests unitarios | `tests/unit/competencia/application/queries/test_obtener_performance_actual.py` |
| | `tests/unit/competencia/application/queries/test_obtener_proximas_performances.py` |
| | `tests/unit/competencia/application/queries/test_obtener_progreso.py` |
| | `tests/unit/competencia/infrastructure/test_sqlite_event_store_prefix.py` |
| Tests integración | `tests/integration/competencia/test_api_interfaz_juez.py` |
| BDD feature | `tests/features/US-1.3.1-interfaz-juez.feature` |

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- SP1-candidatas: `docs/plans/sp1/SP1-candidatas.md` §Inc 1.3
- ADR-008: Event Store append-only
- ADR-011: structlog (logging en handlers)
- Incremento: Inc 1.3 — El Juez Ve y Toca

---

*Redactado: 2026-03-23 — IEDD Capa 3 completa*
