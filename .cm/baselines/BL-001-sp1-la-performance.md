# BL-001 — SP1: La Performance

| Campo | Valor |
|-------|-------|
| **Tipo** | Subproyecto |
| **Fecha apertura** | 2026-03-21 |
| **Fecha cierre** | — (en curso) |
| **Git tag inicial** | `develop` @ `8bf6da7` (merge PR #12) |
| **Git tag cierre** | — (se asigna `v0.2.0` al cerrar) |
| **Estado** | 🔄 En curso — Inc 1.1 completado |
| **DoD del SP1** | 5 performances registradas desde el celular. Event Store muestra la traza completa. |

---

## Descripción

SP1 implementa el aggregate `Performance` del BC Competencia con Event Sourcing
completo, los endpoints REST para el flujo del juez, y el frontend mínimo para
operar desde el celular. Es el walking skeleton de AtaraxiaDive.

---

## Incrementos

| Inc. | Nombre | Estado | PR | Issues |
|------|--------|--------|-----|--------|
| **1.1** | Fundación técnica | ✅ Completado | #12 | #1 (cerrado) |
| **1.2** | El dominio habla | 🔄 En curso | — | #2–#7 |
| **1.3** | El juez ve y toca | ⏳ Pendiente | — | #8 |
| **1.4** | Todo conectado | ⏳ Pendiente | — | #9 |

---

## Inventario de Configuration Items

### CIs — Inc 1.1 (2026-03-21)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-C01 | `src/competencia/domain/ports/event_store_port.py` | Puerto | Contrato `append/load/load_from` — interfaz hexagonal del Event Store |
| CI-C02 | `src/competencia/infrastructure/event_store/sqlite_event_store.py` | Adaptador | Implementación SQLite append-only con control de concurrencia optimista |
| CI-C03 | `src/competencia/infrastructure/migrations/versions/0001_create_events_table.py` | Migración | Tabla `events` con índice único `(stream_id, version)` — ADR-008 |
| CI-C04 | `alembic.ini` | Configuración | Alembic configurado para BC Competencia — `sqlite:///data/competencia.db` |
| CI-C05 | `src/app.py` | API | `GET /health` → `{"status": "ok"}` |
| CI-C06 | `tests/integration/competencia/test_sqlite_event_store.py` | Test | 7 casos: append/load/load_from/concurrencia/streams independientes |
| CI-C07 | `pyproject.toml` (actualización) | Configuración | `asyncpg` → `aiosqlite`; `pythonpath = ["src"]` en pytest |

---

## Métricas al cerrar Inc 1.1

| Métrica | Valor |
|---------|-------|
| Tests (integration) | 7 / 7 pasando |
| Tests (unit) | 0 (no aplica en Inc 1.1) |
| Cobertura `domain/` | — (no hay domain code aún) |
| Violations CRITICAL (DesignReviewer) | 0 |
| Archivos nuevos | 14 |
| Líneas de código | ~490 |

---

## Decisiones técnicas relevantes del SP1

_(se completa a medida que avanzan los incrementos)_

| Decisión | Inc. | Contexto |
|----------|------|---------|
| Versión calculada via subquery en INSERT | 1.1 | `COALESCE(MAX(version), 0) + 1` — atómico en SQLite sin trigger |
| `pythonpath = ["src"]` en pytest | 1.1 | Necesario para imports BC-first sin prefijo `src.` |
| Alembic síncrono para migraciones | 1.1 | aiosqlite es solo para runtime; las migraciones usan SQLite síncrono |

---

## Retrospectiva

_(se completa al cerrar SP1)_

### ¿Qué funcionó?

### ¿Qué fue más difícil de lo esperado?

### ¿Qué ajustar en SP2?

### Métricas finales SP1

| Métrica | Objetivo | Real |
|---------|----------|------|
| Pylint ≥ 8.0 en `domain/` | ≥ 8.0 | — |
| Cobertura `domain/` + `application/` | ≥ 85% | — |
| Violations CRITICAL | 0 | — |

---

*Abierta: 2026-03-21. Se cierra con tag `v0.2.0` al completar Inc 1.4.*
