# Plan de Implementación: US-1.4.2 — Flujo Completo E2E: AP → Tarjeta

**Patrón:** Hexagonal DDD BC-first (Event Sourcing)
**BC:** Competencia
**Estimación Total:** 65 min

---

## Análisis de impacto

Esta US **no agrega lógica de dominio nueva** — todo el dominio ya está implementado
(US-1.2.1 a US-1.4.1). El trabajo es:
1. Agregar un nuevo método al puerto y su implementación (para exposición cruda del Event Store)
2. Nueva query handler `ObtenerEventos`
3. Nuevo endpoint `GET /competencia/{id}/events`
4. Tests unitarios del handler
5. Test de integración E2E (flujo de 5 performances)
6. Steps BDD para los 6 escenarios

Los umbrales de DesignReviewer (`max_cbo=22`, `max_wmc=44`) no requieren ajuste —
esta US no toca el aggregate `Performance`.

---

## Componentes a Implementar

### 1. Puerto + Implementación (domain/ports + infrastructure)

- [ ] `src/competencia/domain/ports/event_store_port.py` — agregar método abstracto (5 min)
  - `load_all_events_ordered(prefix: str) -> list[dict[str, Any]]`
  - Retorna todos los eventos de streams con ese prefijo, ordenados por id global (inserción)
  - Incluye `sequence` (id autoincrement), `stream_id`, `event_type`, `payload`, `occurred_at`

- [ ] `src/competencia/infrastructure/event_store/sqlite_event_store.py` — implementar (10 min)
  - `SELECT id as sequence, stream_id, event_type, payload, occurred_at FROM events WHERE stream_id LIKE ? ORDER BY id ASC`

### 2. Query Handler (application/queries)

- [ ] `src/competencia/application/queries/obtener_eventos.py` (10 min)
  - `ObtenerEventosQuery(competencia_id: UUID)`
  - `EventoDTO(sequence: int, event_type: str, performance_id: str, occurred_at: str, data: dict)`
  - `ObtenerEventosHandler.handle()` — llama `load_all_events_ordered`, mapea a `EventoDTO`

### 3. API Endpoint (api/router)

- [ ] `src/competencia/api/router.py` — agregar endpoint (10 min)
  - `GET /competencia/{competencia_id}/events`
  - Response: `{"competencia_id": str, "total_events": int, "events": [EventoDTO]}`
  - 200 siempre (lista vacía si no hay eventos)

### 4. Tests Unitarios (unit)

- [ ] `tests/unit/competencia/test_obtener_eventos.py` (10 min)
  - Mock del EventStorePort
  - Test: handler retorna lista de EventoDTO en orden
  - Test: handler retorna lista vacía si no hay eventos
  - Test: `performance_id` se extrae correctamente del `stream_id`

### 5. Test de Integración E2E (integration)

- [ ] `tests/integration/competencia/test_flujo_e2e.py` (15 min)
  - Fixture: SQLite in-memory con 5 performances ejecutadas (atletas A-E)
    - A: AP→Llamar→Resultado 60m→Tarjeta blanca
    - B: AP→Llamar→DNS
    - C: AP→Llamar→Resultado 72m→Tarjeta amarilla
    - D: AP→Llamar→Resultado 55m→Tarjeta blanca→CorregirResultado 53m
    - E: AP→Llamar→Resultado 90m→Tarjeta roja black-out distancia 45m
  - Test: GET /competencia/{id}/events → ≥15 eventos ordenados
  - Test: GET /competencia/{id}/progreso → ejecutadas=5, total=5, dns=1
  - Test: consistencia Event Store vs Read Models

### 6. BDD Steps (features/steps)

- [ ] `tests/features/steps/flujo_e2e_steps.py` (5 min)
  - Steps para los 6 escenarios de `US-1.4.2-flujo-e2e.feature`
  - Reutiliza fixtures de integración existentes (aiosqlite in-memory)

---

## Orden de ejecución

```
1. EventStorePort (método abstracto)
2. SQLiteEventStore (implementación)
3. ObtenerEventosHandler (query)
4. router.py (endpoint)
5. test_obtener_eventos.py (unit)
6. test_flujo_e2e.py (integration — incluye todos los atletas)
7. flujo_e2e_steps.py (BDD)
```

---

**Estado:** 0/7 tareas completadas
