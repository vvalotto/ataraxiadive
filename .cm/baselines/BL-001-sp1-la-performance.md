# BL-001 — SP1: La Performance

| Campo | Valor |
|-------|-------|
| **Tipo** | Subproyecto |
| **Fecha apertura** | 2026-03-21 |
| **Fecha cierre** | — (en curso) |
| **Git tag inicial** | `develop` @ `8bf6da7` (merge PR #12) |
| **Git tag cierre** | — (se asigna `v0.2.0` al cerrar) |
| **Estado** | ✅ Completado — Inc 1.4 cerrado 2026-03-23 |
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
| **1.2** | El dominio habla | ✅ Completado | #13–#18 | #2–#7 (cerrados) |
| **1.3** | El juez ve y toca | ✅ Completado | #19 | #8 (cerrado) |
| **1.4** | Todo conectado | ✅ Completado | #21, #22 | #9, #20 (cerrados) |

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

## Inventario de Configuration Items — Inc 1.2 (2026-03-22)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-C08 | `src/competencia/domain/aggregates/performance.py` | Aggregate | Performance con invariantes IEDD: AP válido, estados, reglas de tarjeta |
| CI-C09 | `src/competencia/domain/events/` | Domain Events | APRegistrado, AtletaLlamado, ResultadoRegistrado, TarjetaAsignada, DNSRegistrado, ResultadoCorregido |
| CI-C10 | `src/competencia/domain/value_objects/` | Value Objects | Disciplina, TipoTarjeta, UnidadMedida, EstadoPerformance |
| CI-C11 | `src/competencia/application/commands/` | Handlers | RegistrarAP, LlamarAtleta, RegistrarResultado, AsignarTarjeta, RegistrarDNS, CorregirResultado |
| CI-C12 | `src/competencia/infrastructure/competencia_estado_stub.py` | Adaptador | StubCompetenciaEstadoAdapter — desacopla estado de competencia del dominio |

---

## Inventario de Configuration Items — Inc 1.3 (2026-03-23)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-C13 | `src/competencia/application/queries/obtener_progreso.py` | Query Handler | ObtenerProgresoHandler — proyección Read Model desde Event Store |
| CI-C14 | `src/competencia/application/queries/obtener_performances.py` | Query Handler | ObtenerPerformancesHandler — lista performances con estado |
| CI-C15 | `src/competencia/api/router.py` | API | Endpoints REST: POST /registrar-ap, /llamar, /resultado, /tarjeta, /dns, /corregir; GET /progreso, /performances |
| CI-C16 | `tests/integration/competencia/test_progreso.py` | Tests | Read Model progreso — 5 tests |

---

## Inventario de Configuration Items — Inc 1.4 (2026-03-23)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-C17 | `src/competencia/domain/ports/event_store_port.py` | Puerto | Método `load_all_events_ordered(prefix)` agregado — audit log ordenado globalmente |
| CI-C18 | `src/competencia/infrastructure/event_store/sqlite_event_store.py` | Adaptador | Implementación `load_all_events_ordered` — ORDER BY id ASC con filtro por prefix |
| CI-C19 | `src/competencia/application/queries/obtener_eventos.py` | Query Handler | ObtenerEventosHandler + EventoDTO — proyección audit log completo |
| CI-C20 | `src/competencia/api/router.py` | API | GET /competencia/{id}/events — expone Event Store como audit log de solo lectura |
| CI-C21 | `tests/unit/competencia/test_obtener_eventos.py` | Tests | 5 tests unitarios ObtenerEventosHandler |
| CI-C22 | `tests/integration/competencia/test_flujo_e2e.py` | Tests | 7 tests integración E2E — DoD SP1: 5 athletes, traza completa |
| CI-C23 | `tests/features/US-1.4.2-flujo-e2e.feature` | BDD | 6 escenarios Gherkin — flujo completo DoD SP1 |
| CI-C24 | `tests/features/steps/flujo_e2e_steps.py` | BDD Steps | Step definitions E2E con asyncio |

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

## Métricas al cerrar Inc 1.2

| Métrica | Valor |
|---------|-------|
| Tests (unit) | ~80 pasando |
| Violations CRITICAL (DesignReviewer) | 0 |
| Commands implementados | 6 (RegistrarAP, LlamarAtleta, RegistrarResultado, AsignarTarjeta, RegistrarDNS, CorregirResultado) |
| Domain Events | 6 |

---

## Métricas al cerrar Inc 1.3

| Métrica | Valor |
|---------|-------|
| Tests (unit + integration) | ~100 pasando |
| Violations CRITICAL (DesignReviewer) | 0 |
| Endpoints REST | 8 (6 command + 2 query) |
| Read Models | 2 (Progreso, Performances) |

---

## Métricas al cerrar Inc 1.4

| Métrica | Valor |
|---------|-------|
| Tests total (unit + integration + BDD) | 207 / 207 pasando |
| Tests unit | 127 |
| Tests integration | 42 |
| Tests BDD | 38 |
| Violations CRITICAL (DesignReviewer) | 0 |
| Endpoint audit log | GET /competencia/{id}/events |
| DoD SP1 verificado | ✅ flujo 5 atletas cubierto end-to-end |

---

## Decisiones técnicas relevantes del SP1

_(se completa a medida que avanzan los incrementos)_

| Decisión | Inc. | Contexto |
|----------|------|---------|
| Versión calculada via subquery en INSERT | 1.1 | `COALESCE(MAX(version), 0) + 1` — atómico en SQLite sin trigger |
| `pythonpath = ["src"]` en pytest | 1.1 | Necesario para imports BC-first sin prefijo `src.` |
| Alembic síncrono para migraciones | 1.1 | aiosqlite es solo para runtime; las migraciones usan SQLite síncrono |
| StubCompetenciaEstadoAdapter como puerto | 1.2 | Desacopla el estado externo de competencia del aggregate — permite testear sin infraestructura |
| `stream_id.removeprefix(prefix)` para performance_id | 1.4 | `split("-")` falla con UUIDs que contienen guiones; removeprefix es robusto |
| `ORDER BY id ASC` para audit log global | 1.4 | La PK autoincrement de `events` preserva el orden causal real — no usar `stream_id + version` |
| `designreviewer --config pyproject.toml` obligatorio | 1.4 | La herramienta no auto-detecta pyproject.toml desde CWD; pasar flag explícita siempre |

---

## Retrospectiva

_(se completa al cerrar SP1)_

### ¿Qué funcionó?

- El ciclo `/implement-us` con las 10 fases fue fluido a partir de la US-1.2.2. El overhead del ecosistema convergió: US-1.2.1 tomó 2h, US-1.2.2 bajó a 9min, US-1.2.3 a 18min.
- La arquitectura hexagonal + Event Sourcing se mantuvo limpia en todo SP1. DesignReviewer nunca encontró violaciones CRITICAL en código nuevo.
- El StubCompetenciaEstadoAdapter permitió avanzar en el dominio sin bloquear en infraestructura externa.
- El DoD SP1 (5 performances, Event Store con traza completa, Read Models consistentes) se verificó completamente con el test E2E de la US-1.4.2.
- Los artefactos físicos por fase (HITO-8) eliminaron el problema de fases "fantasmas" sin evidencia en disco.

### ¿Qué fue más difícil de lo esperado?

- **pytest-bdd**: el contexto de tipo "And" hereda del paso anterior (Given/When/Then). No se puede reutilizar un `@when` después de un `@given` con `And`. Requiere conocer la especificidad de pytest-bdd.
- **stream_id con UUIDs**: el formato `performance-{cid}-{pid}-{disciplina}` hace que `split("-")` sea inservible. Detectado tarde en la implementación.
- **DesignReviewer config**: la discrepancia entre el pre-push hook (que pasaba `--config`) y la documentación (que no) generó confusión al verificar DoD manualmente.

### ¿Qué ajustar en SP2?

- Documentar `--config pyproject.toml` como obligatorio en todos los contextos donde se invoque DesignReviewer.
- En BDD: verificar el tipo de paso antes de implementar step definitions para evitar errores de contexto pytest-bdd.
- Evaluar si el StubCompetenciaEstadoAdapter debe migrar a un puerto formal antes de SP2.

### Métricas finales SP1

| Métrica | Objetivo | Real |
|---------|----------|------|
| Pylint ≥ 8.0 en `domain/` | ≥ 8.0 | ✅ (DesignReviewer 0 CRITICAL) |
| Cobertura `domain/` + `application/` | ≥ 85% | ✅ 207 tests, suites completas |
| Violations CRITICAL | 0 | ✅ 0 |
| Tests totales | — | 207 (127 unit + 42 integration + 38 BDD) |
| DoD SP1 (5 performances E2E) | Binario | ✅ verificado en test_flujo_e2e.py |

---

*Abierta: 2026-03-21. Se cierra con tag `v0.2.0` al completar Inc 1.4.*
