# Reporte de Implementación: US-3.1.2 — API REST Torneo

| Campo | Valor |
|-------|-------|
| **US** | US-3.1.2 |
| **Sprint** | SP3 — El Torneo |
| **Incremento** | INC-3.1 |
| **Fecha** | 2026-03-30 |
| **Branch** | `feature/US-3.1.2-api-rest-torneo` |
| **Estado** | ✅ Completada |

---

## Métricas

| Métrica | Valor |
|---------|-------|
| Tests totales (US-3.1.2) | 33 (17 unit + 6 integration + 10 BDD) |
| Cobertura `torneo/` | 100% (234 stmts, 0 miss) |
| CodeGuard errores | 0 |
| CodeGuard advertencias | 0 |
| Tiempo de implementación | ~20 min |

---

## Artefactos generados

### Application
- `src/torneo/application/commands/crear_torneo.py` — `CrearTorneoCommand` + `CrearTorneoHandler`
- `src/torneo/application/commands/transicionar_torneo.py` — `TransicionarTorneoCommand` + 7 handlers
- `src/torneo/application/queries/obtener_torneo.py` — `ObtenerTorneoHandler` + `ListarTorneosHandler`

### Infrastructure
- `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py` — `SQLiteTorneoRepository` (aiosqlite, upsert)

### API
- `src/torneo/api/exception_handlers.py` — 3 handlers (404, 409, 409)
- `src/torneo/api/router.py` — 10 endpoints (`POST /torneos`, `GET /torneos`, `GET /torneos/{id}`, 7 `PUT` de transición)

### Composition Root
- `src/app.py` — torneo router + exception handlers registrados

### Tests
- `tests/unit/torneo/application/test_crear_torneo.py` (4 tests)
- `tests/unit/torneo/application/test_transiciones_handlers.py` (9 tests)
- `tests/unit/torneo/application/test_obtener_torneo.py` (4 tests)
- `tests/integration/torneo/test_sqlite_torneo_repository.py` (6 tests)
- `tests/features/US-3.1.2-api-rest-torneo.feature` (10 escenarios)
- `tests/features/steps/torneo_api_steps.py` (step definitions)

---

## Invariantes verificados

| Invariante | Mecanismo | Estado |
|------------|-----------|--------|
| INV-T-API-01: 422 si nombre vacío o fecha_fin < fecha_inicio | Pydantic validator | ✅ |
| INV-T-API-02: Transición inválida → 409 Conflict | Exception handler `TransicionEstadoInvalida` | ✅ |
| INV-T-API-03: Torneo no encontrado → 404 | Exception handler `TorneoNoEncontrado` | ✅ |
| INV-T-API-04: Todos los campos en `GET /torneos/{id}` | `TorneoResponse.from_torneo()` | ✅ |

---

## Decisiones de diseño

- **`_TransicionHandler` base**: los 7 handlers de transición heredan de una clase privada con método `_ejecutar()` — elimina repetición sin over-engineering
- **`sede`/`entidad_organizadora` como JSON en TEXT**: simple y sin joins, suficiente para SP3
- **Validación duplicada Pydantic + `__post_init__`**: Pydantic para el contrato HTTP (422), dominio para la integridad del objeto (ValueError)
- **`_repo()` helper en router**: instancia el repositorio por request con env var — simple para SP3, se refactorizará con DI en SP4

---

## DoD INC-3.1

| Criterio | Estado |
|----------|--------|
| `POST /torneos` crea un torneo | ✅ |
| 7 fases transicionan correctamente | ✅ |
| Retroceso Ejecución→Preparación | ✅ |
| Tests 100% pass | ✅ |
| Cobertura ≥ 90% | ✅ (100%) |
| CodeGuard 0 errores | ✅ |

**INC-3.1 — DoD cumplida ✅**
