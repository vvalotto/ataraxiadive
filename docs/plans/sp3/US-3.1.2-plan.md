# Plan de Implementación: US-3.1.2 — API REST Torneo — CRUD + transiciones de fase

**Patrón:** Hexagonal DDD — CRUD (aiosqlite, no Event Sourcing)
**BC:** torneo
**Estimación Total:** 2h 30min
**Estado:** 0/22 tareas completadas

---

## 1. Application — Commands (torneo/application/commands/)

- [ ] `src/torneo/application/commands/crear_torneo.py` (15 min)
  - `CrearTorneoCommand`: dataclass frozen con todos los campos del torneo
  - `CrearTorneoHandler`: inyecta `TorneoRepositoryPort`, `handle()` crea `Torneo` y persiste → retorna `UUID`

- [ ] `src/torneo/application/commands/transicionar_torneo.py` (20 min)
  - `TransicionarTorneoCommand(torneo_id: UUID)`: comando base reutilizable
  - Un handler por transición (todos inyectan `TorneoRepositoryPort`):
    - `AbrirInscripcionHandler` → `torneo.abrir_inscripcion()`
    - `CerrarInscripcionHandler` → `torneo.cerrar_inscripcion()`
    - `IniciarEjecucionHandler` → `torneo.iniciar_ejecucion()`
    - `VolverAPreparacionHandler` → `torneo.volver_a_preparacion()`
    - `IniciarPremiacionHandler` → `torneo.iniciar_premiacion()`
    - `CerrarTorneoHandler` → `torneo.cerrar()`
    - `CancelarTorneoHandler` → `torneo.cancelar()`

- [ ] `src/torneo/application/commands/__init__.py` (2 min)

---

## 2. Application — Queries (torneo/application/queries/)

- [ ] `src/torneo/application/queries/obtener_torneo.py` (10 min)
  - `ObtenerTorneoQuery(torneo_id: UUID)`
  - `ObtenerTorneoHandler`: busca por id → retorna `Torneo` o lanza `TorneoNoEncontrado`
  - `ListarTorneosQuery` (sin campos)
  - `ListarTorneosHandler`: retorna `list[Torneo]`

- [ ] `src/torneo/application/queries/__init__.py` (2 min)

---

## 3. Infrastructure — Repository (torneo/infrastructure/repositories/)

- [ ] `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py` (30 min)
  - `SQLiteTorneoRepository(TorneoRepositoryPort)`: implementación con `aiosqlite`
  - `CREATE TABLE IF NOT EXISTS torneos (torneo_id TEXT PK, nombre TEXT, descripcion TEXT, fecha_inicio TEXT, fecha_fin TEXT, sede TEXT, entidad_organizadora TEXT, estado TEXT)`
  - `sede` y `entidad_organizadora` serializados como JSON en columna TEXT
  - DB path: `os.getenv("TORNEO_DB_PATH", "data/torneo.db")`
  - `save()`: upsert con `INSERT OR REPLACE`
  - `find_by_id()`: retorna `Torneo | None`
  - `find_all()`: retorna `list[Torneo]`
  - `_row_to_torneo()`: helper de deserialización

- [ ] `src/torneo/infrastructure/repositories/__init__.py` (2 min)

---

## 4. API — Exception Handlers (torneo/api/)

- [ ] `src/torneo/api/exception_handlers.py` (10 min)
  - `register_torneo_exception_handlers(app: FastAPI) → None`
  - `TorneoNoEncontrado` → 404
  - `TransicionEstadoInvalida` → 409 Conflict
  - `TorneoCerrado` → 409 Conflict
  - Body RFC 7807 (igual que patrón competencia/api/exception_handlers.py)

---

## 5. API — Router (torneo/api/)

- [ ] `src/torneo/api/router.py` (30 min)
  - `router = APIRouter(prefix="/torneos", tags=["torneos"])`
  - Schemas Pydantic: `CrearTorneoRequest`, `SedeSchema`, `EntidadOrganizadoraSchema`, `TorneoResponse`
  - Validación Pydantic: `nombre` no vacío, `fecha_fin >= fecha_inicio` (validator)
  - Endpoints:
    - `POST /torneos` → 201 `{"torneo_id": "..."}`
    - `GET /torneos` → 200 `[TorneoResponse]`
    - `GET /torneos/{torneo_id}` → 200 `TorneoResponse`
    - `PUT /torneos/{torneo_id}/abrir-inscripcion` → 200
    - `PUT /torneos/{torneo_id}/cerrar-inscripcion` → 200
    - `PUT /torneos/{torneo_id}/iniciar-ejecucion` → 200
    - `PUT /torneos/{torneo_id}/volver-preparacion` → 200
    - `PUT /torneos/{torneo_id}/iniciar-premiacion` → 200
    - `PUT /torneos/{torneo_id}/cerrar` → 200
    - `PUT /torneos/{torneo_id}/cancelar` → 200
  - DB path inyectado desde `os.getenv("TORNEO_DB_PATH", "data/torneo.db")`

- [ ] `src/torneo/api/__init__.py` (1 min)

---

## 6. Composition Root — src/app.py

- [ ] Actualizar `src/app.py` (5 min)
  - `from torneo.api.router import router as torneo_router`
  - `from torneo.api.exception_handlers import register_torneo_exception_handlers`
  - `app.include_router(torneo_router)`
  - `register_torneo_exception_handlers(app)`

---

## 7. Tests unitarios (tests/unit/torneo/)

- [ ] `tests/unit/torneo/application/test_crear_torneo.py` (15 min)
  - `CrearTorneoHandler` con repo mock: happy path, nombre vacío, fechas inválidas

- [ ] `tests/unit/torneo/application/test_transiciones_handlers.py` (15 min)
  - Cada handler de transición: happy path + `TorneoNoEncontrado` + transición inválida

- [ ] `tests/unit/torneo/application/test_obtener_torneo.py` (10 min)
  - `ObtenerTorneoHandler`: found, not found
  - `ListarTorneosHandler`: vacío, varios

---

## 8. Tests de integración (tests/integration/torneo/)

- [ ] `tests/integration/torneo/test_sqlite_torneo_repository.py` (15 min)
  - save + find_by_id, find_all, not found — aiosqlite en memoria (`:memory:`)

---

## 9. Tests BDD (tests/features/steps/)

- [ ] `tests/features/steps/torneo_api_steps.py` (20 min)
  - Steps para los 10 escenarios de `US-3.1.2-api-rest-torneo.feature`
  - `AsyncClient` de `httpx` sobre `app` de FastAPI

---

## Notas de implementación

- `SQLiteTorneoRepository` usa `aiosqlite` directamente (sin ORM), igual que `SQLiteEventStore`
- Handlers de transición son todos análogos — un `TransicionarTorneoCommand` base es suficiente
- `TorneoResponse` serializa `Sede` y `EntidadOrganizadora` como objetos anidados (no JSON string)
- Validación de negocio (`fecha_fin >= fecha_inicio`, nombre no vacío) duplicada en Pydantic + `Torneo.__post_init__()` — Pydantic para 422, dominio para integridad del objeto
- Fixture `torneo_payload()` centralizado en conftest o steps para reutilizar entre tests
