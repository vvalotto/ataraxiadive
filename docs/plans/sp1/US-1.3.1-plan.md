# Plan de Implementación: US-1.3.1 — Interfaz del Juez: Read Models y Endpoints

**Patrón:** Hexagonal DDD BC-first (Query-side)
**BC:** competencia
**Estimación Total:** 1h 40min

---

## Componentes a Implementar

### 1. Puerto — ExtendER EventStorePort (Domain)

- [ ] `src/competencia/domain/ports/event_store_port.py` (10 min)
  - Agregar método abstracto `load_all_streams_with_prefix(prefix: str) -> list[list[dict[str, Any]]]`
  - Carga todos los streams cuyo `stream_id` comienza con `prefix`
  - Orden: por `stream_id` y luego por `version ASC`

### 2. Infraestructura — SQLiteEventStore (implementar nuevo método)

- [ ] `src/competencia/infrastructure/event_store/sqlite_event_store.py` (15 min)
  - Implementar `load_all_streams_with_prefix` con:
    ```sql
    SELECT stream_id, event_type, payload, version, occurred_at
    FROM events WHERE stream_id LIKE ? ORDER BY stream_id, version ASC
    ```
  - Agrupar resultados por `stream_id` → `list[list[dict]]`
  - `prefix` se convierte en `prefix + "%"` para el LIKE

### 3. Application — Query handlers y DTOs

- [ ] `src/competencia/application/queries/obtener_performance_actual.py` (20 min)
  - `PerformanceActualDTO` (dataclass): `performance_id`, `nombre_atleta`, `ap_declarado`, `unidad`, `andarivel`, `estado`
  - `ObtenerPerformanceActualQuery` (dataclass frozen): `competencia_id: UUID`
  - `ObtenerPerformanceActualHandler`:
    - Usa `event_store.load_all_streams_with_prefix(f"performance-{competencia_id}-")`
    - Para cada stream, llama `Performance.reconstitute(events)`
    - Retorna la primera en estado `Llamada` o `ResultadoRegistrado`
    - Extrae `andarivel` de payload de `AtletaLlamado`
    - `nombre_atleta` = `f"Atleta-{participante_id[:8]}"` (SP1 hardcode)
    - Retorna `PerformanceActualDTO | None`

- [ ] `src/competencia/application/queries/obtener_proximas_performances.py` (20 min)
  - `ProximoAtletaDTO` (dataclass): `nombre_atleta`, `ap_declarado`, `unidad`, `posicion`
  - `ObtenerProximasPerformancesQuery` (dataclass frozen): `competencia_id: UUID`, `limit: int = 3`
  - `ObtenerProximasPerformancesHandler`:
    - Carga todos los streams con prefijo
    - Filtra performances en estado `AnunciadaAP`
    - Ordena por `occurred_at` del primer evento (proxy de grilla SP1)
    - Retorna las primeras `limit` como `list[ProximoAtletaDTO]`

- [ ] `src/competencia/application/queries/obtener_progreso.py` (15 min)
  - `ProgresoCompetenciaDTO` (dataclass): `total`, `ejecutadas`, `dns_count`, `completadas`
  - `ObtenerProgresoQuery` (dataclass frozen): `competencia_id: UUID`
  - `ObtenerProgresoHandler`:
    - Carga todos los streams con prefijo
    - Cuenta por estado: Ejecutada, DNS, resto
    - `completadas = ejecutadas + dns_count`
    - Retorna `ProgresoCompetenciaDTO`

### 4. API — Router FastAPI

- [ ] `src/competencia/api/router.py` (20 min)
  - `APIRouter(prefix="/competencia")`
  - `GET /{competencia_id}/performance/actual` → `PerformanceActualDTO | None`
  - `GET /{competencia_id}/performance/proximas` → `list[ProximoAtletaDTO]`
  - `GET /{competencia_id}/progreso` → `ProgresoCompetenciaDTO`
  - Dependency injection: `SQLiteEventStore` desde `settings.DB_PATH`
  - Respuestas vacías: `null` / `[]` / `{total:0, ...}` con HTTP 200

- [ ] `src/app.py` (5 min)
  - Importar y registrar `router` del BC competencia

### 5. Tests unitarios

- [ ] `tests/unit/competencia/infrastructure/test_sqlite_event_store_prefix.py` (15 min)
  - `load_all_streams_with_prefix` con múltiples streams
  - Streams de otra competencia no se retornan (prefix correcto)
  - Stream vacío de competencia → lista vacía

- [ ] `tests/unit/competencia/application/queries/test_obtener_performance_actual.py` (15 min)
  - Performance en `Llamada` → retorna DTO con datos correctos
  - Performance en `ResultadoRegistrado` → retorna DTO
  - Solo performances `AnunciadaAP` → retorna `None`
  - Sin performances → retorna `None`

- [ ] `tests/unit/competencia/application/queries/test_obtener_proximas_performances.py` (15 min)
  - 5 performances, 2 llamadas → retorna 3 en AnunciadaAP
  - Menos de 3 disponibles → retorna las que hay
  - Sin performances en AnunciadaAP → lista vacía

- [ ] `tests/unit/competencia/application/queries/test_obtener_progreso.py` (10 min)
  - Mix de estados → conteos correctos
  - Sin performances → `{total:0, ejecutadas:0, dns_count:0, completadas:0}`

### 6. Tests de integración (API)

- [ ] `tests/integration/competencia/test_api_interfaz_juez.py` (20 min)
  - Stack completo: SQLite in-memory + FastAPI TestClient
  - Los 4 escenarios BDD: actual, proximas, progreso, vacío
  - Verificar status codes y estructura de respuesta

---

## Notas de implementación

- **`nombre_atleta` hardcode:** `f"Atleta-{str(participante_id)[:8]}"` — placeholder hasta SP3 (BC Registro)
- **Orden "proximas":** `occurred_at` del evento `APRegistrado` — proxy de grilla SP1; en SP2 será `posicion_grilla` de la grilla oficial
- **Sin Pydantic Response models separados:** los DTOs son dataclasses; FastAPI los serializa directamente con `response_model=None` y `jsonable_encoder`
- **Settings para DB_PATH:** usar `os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")`
- **`pyproject.toml`:** verificar si CBO/WMC de nuevos handlers requiere ajuste (handlers nuevos, no tocan `Performance`)

---

## Orden de implementación (bottom-up)

1. Puerto → Infra (EventStorePort + SQLiteEventStore)
2. Query handlers (obtener_performance_actual → proximas → progreso)
3. API router + app.py
4. Tests unitarios (infra → queries)
5. Tests de integración
6. BDD (Fase 6)

---

**Estado:** 0/16 tareas completadas
