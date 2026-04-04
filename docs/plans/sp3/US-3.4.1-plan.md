# Plan de Implementación — US-3.4.1

**US:** Torneo: AsignarDisciplinas + AsignarJuez
**Fecha:** 2026-04-01
**Incremento:** INC-3.4

---

## Artefactos a crear/modificar

| Artefacto | Tipo | Acción |
|-----------|------|--------|
| `torneo/domain/value_objects/disciplina_torneo.py` | VO nuevo | Crear |
| `torneo/domain/aggregates/torneo.py` | Aggregate | Extender |
| `torneo/domain/exceptions.py` | Excepciones | Extender |
| `torneo/application/commands/asignar_disciplinas.py` | Command+Handler | Crear |
| `torneo/application/commands/asignar_juez.py` | Command+Handler | Crear |
| `torneo/application/queries/obtener_disciplinas_juez.py` | Query+Handler | Crear |
| `torneo/infrastructure/repositories/sqlite_torneo_repository.py` | Repo | Extender (columna + deserialización) |
| `torneo/api/router.py` | Router | Extender (4 nuevos endpoints) |

---

## Tareas

### T1 — VO `DisciplinaTorneo` (5 min)
- `torneo/domain/value_objects/disciplina_torneo.py`
- `@dataclass(frozen=True)` con `disciplina: Disciplina` y `juez_id: UUID | None = None`
- Serialización/deserialización JSON

### T2 — Extender aggregate `Torneo` (15 min)
- Campo `disciplinas_torneo: list[DisciplinaTorneo]`
- `asignar_disciplinas(disciplinas: frozenset[Disciplina]) -> None` — INV-TD-01, INV-TD-02
- `asignar_juez(disciplina: Disciplina, juez_id: UUID) -> None` — INV-TD-03, INV-TD-04
- `obtener_disciplinas_de_juez(juez_id: UUID) -> list[Disciplina]`

### T3 — Excepciones nuevas (3 min)
- `DisciplinaNoEnTorneo`, `JuezYaAsignado`, `AsignacionNoPermitida` en `exceptions.py`

### T4 — Commands + Handlers (10 min)
- `AsignarDisciplinasCommand` / `AsignarDisciplinasHandler`
- `AsignarJuezCommand` / `AsignarJuezHandler`
- `ObtenerDisciplinasDeJuezHandler` (query)

### T5 — Repositorio SQLite (10 min)
- Agregar columna `disciplinas_torneo TEXT NOT NULL DEFAULT '[]'` al DDL
- Serializar/deserializar `list[DisciplinaTorneo]` como JSON
- Migración: `ADD COLUMN IF NOT EXISTS` para DBs existentes

### T6 — Router (10 min)
- `PUT /torneos/{torneo_id}/disciplinas` → 200
- `PUT /torneos/{torneo_id}/disciplinas/{disciplina}/juez` → 200
- `GET /torneos/{torneo_id}/jueces/{juez_id}/disciplinas` → 200 `[disciplinas]`
- `GET /torneos/{torneo_id}/disciplinas` → 200 `[{disciplina, juez_id}]`

---

## Notas
- `disciplinas_torneo` se serializa como JSON en columna TEXT (igual que `sede` y `entidad`)
- Estados válidos para asignar disciplinas: `CREADO`, `INSCRIPCION_ABIERTA`, `PREPARACION`
- Reasignación de juez: permitida (sobreescribe)
- `Disciplina` importada desde `shared.domain.value_objects.disciplina`
