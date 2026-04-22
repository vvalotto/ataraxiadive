# US-5.2.1 — Fase 0: Validacion de Contexto

**Fecha:** 2026-04-22
**Branch:** `feature/US-5.2.1-ejecucion-disciplinas`
**Producto:** `frontend`
**Incremento:** INC-5.2 — Ejecucion por Disciplina

---

## Historia de Usuario

**US:** US-5.2.1 — Vista maestro-detalle de disciplinas en ejecucion

Como **organizador**, quiero **ver todas las disciplinas del torneo en ejecucion en una vista maestro-detalle y habilitar individualmente cada prueba** para **controlar el inicio operativo de cada disciplina y monitorear su avance desde un unico lugar**.

**Spec canonica:** `docs/specs/sp5/US-5.2.1.md`

---

## Contexto Validado

### Arquitectura

- Patron confirmado: Hexagonal DDD BC-first.
- Producto principal de implementacion: `frontend`.
- BCs consumidos por HTTP:
  - `torneo/api/` para disciplinas configuradas y juez asignado.
  - `competencia/api/` para competencias, estado, grilla, progreso e inicio.
- No se requieren cambios de dominio backend para esta US: `POST /competencia/{id}/iniciar` ya existe.

### Artefactos arquitectonicos encontrados

- `docs/contexto/ATARAXIADIVE-CONTEXT.md`
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
- `docs/adr/ADR-006-estructura-bc-first.md`
- `docs/design/architecture.md`
- `docs/design/domain-model.md`

### Estructura verificada

- `frontend/src/components/organizador/`
- `frontend/src/api/competencia.ts`
- `frontend/src/api/torneo.ts`
- `src/competencia/domain/`
- `src/competencia/application/`
- `src/competencia/api/`
- `tests/features/`

---

## Estado Actual Relevante

### Frontend

- `EjecucionPanel` hoy carga `GET /competencia?torneo_id={id}` y filtra solo competencias en `EnEjecucion`.
- `MonitorDisciplina` ya muestra progreso, atleta actual, proximos y grilla para una competencia activa.
- `torneo.ts` ya expone `listarDisciplinasTorneo(torneoId)`, que devuelve disciplina y `juez_id`.
- `competencia.ts` no expone aun wrapper para `POST /competencia/{id}/iniciar`.

### Backend

- `POST /competencia/{competencia_id}/iniciar` existe en `src/competencia/api/router.py`.
- `IniciarCompetenciaHandler` existe en `src/competencia/application/commands/iniciar_competencia.py`.
- `Competencia.iniciar_competencia()` exige estado `Confirmada`.

---

## Quality Gates

- `CLAUDE.md` encontrado.
- `pyproject.toml` encontrado.
- `[tool.codeguard]` configurado.
- `[tool.designreviewer]` configurado.
- Tests configurados en `tests/`.
- Para frontend, el ajuste local de `implement-us` indica sustituir gates Python por:
  - `npm run build`
  - `npm run lint` si aplica.

---

## Riesgos Detectados

- El maestro debe componer dos fuentes: disciplinas del torneo y competencias materializadas.
- El estado operativo es derivado; debe evitarse mezclar estado de torneo (`EJECUCION`) con estado de competencia (`Confirmada`, `EnEjecucion`, `Finalizada`).
- La accion `Habilitar disciplina` necesita `juez_id`; debe obtenerlo desde `torneo/api`, no pedirlo manualmente.
- La UI actual usa cards del monitor solo para disciplinas activas; la nueva vista debe representar tambien pendientes, bloqueadas, listas y finalizadas.

---

## Resultado

Contexto validado. La US esta lista para Fase 1: escenarios BDD.
