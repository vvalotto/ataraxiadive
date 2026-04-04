# US-3.1.2: API REST Torneo — CRUD + transiciones de fase

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.1
**Bounded Context**: `torneo`
**Capas afectadas**: `torneo/application/`, `torneo/infrastructure/`, `torneo/api/`, `src/app.py`

---

## Descripción

Como **organizador**,
quiero **crear y gestionar torneos via API REST**
para **controlar el ciclo de vida del torneo desde la creación hasta el cierre**.

---

## Especificación

### Precondición

```
US-3.1.1 implementada: aggregate Torneo + TorneoRepositoryPort en torneo/domain/
torneo/application/, torneo/infrastructure/, torneo/api/ — vacíos
```

### Postcondición

```python
# torneo/application/commands/crear_torneo.py
@dataclass(frozen=True)
class CrearTorneoCommand:
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede_nombre: str
    sede_ciudad: str
    sede_pais: str
    entidad_nombre: str
    entidad_tipo: str

class CrearTorneoHandler:
    async def handle(self, cmd: CrearTorneoCommand) -> UUID: ...  # retorna torneo_id

# torneo/application/commands/transicionar_torneo.py
# Un handler por transición:
class AbrirInscripcionHandler, CerrarInscripcionHandler,
      IniciarEjecucionHandler, VolverAPreparacionHandler,
      IniciarPremiacionHandler, CerrarTorneoHandler, CancelarTorneoHandler

# torneo/application/queries/obtener_torneo.py
class ObtenerTorneoHandler:
    async def handle(self, torneo_id: UUID) -> Torneo: ...

class ListarTorneosHandler:
    async def handle(self) -> list[Torneo]: ...

# torneo/infrastructure/repositories/sqlite_torneo_repository.py
class SQLiteTorneoRepository(TorneoRepositoryPort):
    # aiosqlite — tabla `torneos` con columnas para todos los campos
    async def save(self, torneo: Torneo) -> None: ...
    async def find_by_id(self, torneo_id: UUID) -> Torneo | None: ...
    async def find_all(self) -> list[Torneo]: ...

# torneo/api/router.py
router = APIRouter(prefix="/torneos", tags=["torneos"])

POST   /torneos                              → 201 { torneo_id }
GET    /torneos                              → 200 [{ torneo }]
GET    /torneos/{torneo_id}                  → 200 { torneo }
PUT    /torneos/{torneo_id}/abrir-inscripcion    → 200
PUT    /torneos/{torneo_id}/cerrar-inscripcion   → 200
PUT    /torneos/{torneo_id}/iniciar-ejecucion    → 200
PUT    /torneos/{torneo_id}/volver-preparacion   → 200
PUT    /torneos/{torneo_id}/iniciar-premiacion   → 200
PUT    /torneos/{torneo_id}/cerrar               → 200
PUT    /torneos/{torneo_id}/cancelar             → 200

# src/app.py — incluir torneo_router
app.include_router(torneo_router)
```

### Invariantes

- `INV-T-API-01`: `POST /torneos` retorna 422 si nombre vacío o fecha_fin < fecha_inicio
- `INV-T-API-02`: Transición inválida retorna 409 Conflict con mensaje descriptivo
- `INV-T-API-03`: Torneo no encontrado retorna 404
- `INV-T-API-04`: Todos los campos del torneo son visibles en `GET /torneos/{id}`

### Schema de respuesta `GET /torneos/{id}`

```json
{
  "torneo_id": "uuid",
  "nombre": "string",
  "descripcion": "string",
  "fecha_inicio": "YYYY-MM-DD",
  "fecha_fin": "YYYY-MM-DD",
  "sede": { "nombre": "...", "ciudad": "...", "pais": "..." },
  "entidad_organizadora": { "nombre": "...", "tipo": "..." },
  "estado": "CREADO | INSCRIPCION_ABIERTA | ..."
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.1.2 — API REST Torneo

  Scenario: crear torneo exitosamente
    Given un payload válido con nombre, fechas, sede y entidad
    When POST /torneos
    Then 201 con torneo_id en respuesta
    And GET /torneos/{id} retorna el torneo con estado CREADO

  Scenario: crear torneo con datos inválidos
    Given fecha_fin anterior a fecha_inicio
    When POST /torneos
    Then 422 Unprocessable Entity

  Scenario: ciclo completo de transiciones via API
    Given un torneo en estado CREADO
    When se llaman secuencialmente los endpoints de transición
    Then cada endpoint retorna 200
    And el estado final es CERRADO

  Scenario: transición inválida via API
    Given un torneo en estado CREADO
    When PUT /torneos/{id}/iniciar-ejecucion
    Then 409 Conflict con mensaje de error

  Scenario: torneo inexistente
    Given un UUID que no existe
    When GET /torneos/{uuid}
    Then 404 Not Found

  Scenario: listar torneos
    Given 3 torneos creados
    When GET /torneos
    Then 200 con lista de 3 torneos
```

---

## Notas de implementación

- `SQLiteTorneoRepository` usa `aiosqlite` con `CREATE TABLE IF NOT EXISTS torneos (...)`.
- DB path: `os.getenv("TORNEO_DB_PATH", "data/torneo.db")`.
- Serialización de `Sede` y `EntidadOrganizadora` como JSON en columnas TEXT.
- Excepciones de dominio mapeadas a HTTP: `TorneoNoEncontrado` → 404, `TransicionEstadoInvalida` → 409, `TorneoCerrado` → 409.
- Los exception handlers para `torneo/` viven en `torneo/api/exception_handlers.py` (siguiendo el patrón de ADR-013).

---

## Referencias

- US-3.1.1: aggregate Torneo
- ADR-013: exception management
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
