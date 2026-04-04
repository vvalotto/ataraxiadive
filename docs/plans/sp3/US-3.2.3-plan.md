# Plan de Implementación — US-3.2.3
## BC Registro — Inscripcion (inscribir + cancelar)

**Branch:** `feature/US-3.2.3-inscripcion-atleta`
**Fecha:** 2026-03-31

---

## Estructura de Archivos

### Nuevos
```
src/registro/domain/value_objects/estado_inscripcion.py
src/registro/domain/aggregates/inscripcion.py
src/registro/domain/ports/inscripcion_repository_port.py
src/registro/domain/ports/torneo_consulta_port.py
src/registro/application/commands/inscribir_atleta.py
src/registro/application/commands/cancelar_inscripcion.py
src/registro/application/queries/listar_inscriptos.py
src/registro/infrastructure/acl/sqlite_torneo_consulta.py
src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py
tests/unit/registro/test_inscripcion.py
tests/unit/registro/test_inscribir_atleta_handler.py
tests/unit/registro/test_cancelar_inscripcion_handler.py
tests/integration/registro/test_sqlite_inscripcion_repository.py
tests/features/steps/test_US_3_2_3_steps.py
```

### Modificados
```
src/registro/domain/exceptions.py          ← 5 nuevas excepciones
src/registro/api/router.py                 ← 3 nuevos endpoints
src/registro/infrastructure/__init__.py    ← (si falta carpeta acl/)
```

---

## Tareas

### T1 — Domain: value objects + aggregate + excepciones (15 min)
- `EstadoInscripcion(StrEnum)`: ACTIVA, CANCELADA
- `Inscripcion` dataclass: id, atleta_id, torneo_id, disciplinas (frozenset[Disciplina]), estado, fecha_inscripcion
  - `cancelar(fecha_actual, fecha_inicio_torneo)` → INV-I-03
- Excepciones: `InscripcionNoEncontrada`, `AtletaYaInscripto`, `TorneoNoDisponible`, `DisciplinaNoDisponible`, `PlazoCancelacionVencido`

### T2 — Domain: puertos (10 min)
- `InscripcionRepositoryPort(ABC)`: save, find_by_id, find_by_atleta_y_torneo, find_by_torneo
- `TorneoConsultaPort(ABC)`: esta_abierto_para_inscripcion, obtener_fecha_inicio, obtener_disciplinas

### T3 — Application: handlers (20 min)
- `InscribirAtletaCommand` + `InscribirAtletaHandler`
  - Valida INV-I-02 (torneo abierto), INV-I-01 (disciplinas ⊆ torneo), INV-I-04 (no duplicado), INV-I-05 (disciplinas no vacío)
- `CancelarInscripcionCommand` + `CancelarInscripcionHandler`
  - Delega INV-I-03 a `inscripcion.cancelar()`
- `ListarInscriptosHandler`

### T4 — Infrastructure: ACL TorneoConsulta (15 min)
- `SQLiteTorneoConsulta` implementa `TorneoConsultaPort`
- Lee `data/torneo.db` directamente (cross-BC read-only, permitido por context map §3.2)
- Env var: `TORNEO_DB_PATH`

### T5 — Infrastructure: SQLiteInscripcionRepository (20 min)
- Tabla `inscripciones`: inscripcion_id, atleta_id, torneo_id, disciplinas (JSON array), estado, fecha_inscripcion
- Implementa `InscripcionRepositoryPort`
- DB: `data/registro.db` (misma que Atleta, env var `REGISTRO_DB_PATH`)

### T6 — API: 3 endpoints (15 min)
- `POST /registro/inscripciones` → 201 `{ inscripcion_id }`
- `DELETE /registro/inscripciones/{inscripcion_id}` → 200
- `GET /registro/torneos/{torneo_id}/inscriptos` → 200 lista
- Inyección: `SQLiteInscripcionRepository` + `SQLiteTorneoConsulta`
- Mapeo de excepciones → HTTP 409

---

## Decisiones de Diseño

1. **ACL en infrastructure/acl/**: `SQLiteTorneoConsulta` lee torneo.db directamente.
   No hay import cross-BC en domain ni application — solo en infrastructure.

2. **`inscripcion.cancelar()` recibe `fecha_actual: date`** inyectada desde el handler
   (no `datetime.today()` interno) — facilita tests deterministas.

3. **`disciplinas` como JSON array en SQLite**: `["STA", "DNF"]` — serialización simple con `json.dumps/loads`.

4. **Misma DB `registro.db`** para `atletas` e `inscripciones`: coherente con ADR-007
   (un archivo SQLite por BC).

---

## Estimación Total: ~95 min
