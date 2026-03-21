# Reporte de Implementación — US-1.2.1: Registrar AP

| Campo | Valor |
|-------|-------|
| **US** | US-1.2.1 |
| **Título** | Registrar AP |
| **BC** | competencia |
| **Incremento** | Inc 1.2 — El Dominio Habla |
| **Fecha** | 2026-03-21 |
| **Branch** | `feature/US-1.2.1-registrar-ap` |
| **Estado** | ✅ Completada |

---

## Resumen de Implementación

### Artefactos creados

| Capa | Archivo | Descripción |
|------|---------|-------------|
| shared/base | `src/shared/domain/base/domain_event.py` | Clase base inmutable para todos los domain events |
| shared/base | `src/shared/domain/base/aggregate_root.py` | Clase base con `_pending_events` y `pull_events()` |
| value_objects | `src/competencia/domain/value_objects/disciplina.py` | Enum con 9 disciplinas AIDA/CMAS |
| value_objects | `src/competencia/domain/value_objects/unidad_medida.py` | Enum Metros / Segundos |
| value_objects | `src/competencia/domain/value_objects/estado_performance.py` | Estados del ciclo de vida |
| value_objects | `src/competencia/domain/value_objects/ap.py` | AP con validación INV-P-01 |
| events | `src/competencia/domain/events/ap_registrado.py` | Evento APRegistrado con `to_payload()` / `from_payload()` |
| ports | `src/competencia/domain/ports/competencia_estado_port.py` | Puerto SP1→SP2 para INV-P-03/P-04 |
| aggregates | `src/competencia/domain/aggregates/performance.py` | Aggregate Performance con `registrarAP()` + `reconstitute()` |
| commands | `src/competencia/application/commands/registrar_ap.py` | RegistrarAPCommand + Handler (INV-P-02/03/04) |
| infrastructure | `src/competencia/infrastructure/competencia_estado_stub.py` | Stub SP1 para CompetenciaEstadoPort |
| tests | `tests/unit/competencia/domain/test_performance.py` | 10 tests unitarios del aggregate |
| tests | `tests/unit/competencia/application/test_registrar_ap_handler.py` | 7 tests unitarios del handler |
| tests | `tests/integration/competencia/test_registrar_ap_integration.py` | 4 tests de integración con SQLiteEventStore real |
| BDD | `tests/features/US-1.2.1-registrar-ap.feature` | 6 escenarios Gherkin |
| BDD | `tests/features/steps/registrar_ap_steps.py` | Step definitions completas |
| conftest | `tests/conftest.py` | Fixture `event_store_inmemory` compartida |
| plans | `docs/plans/US-1.2.1.md` | Especificación IEDD completa |
| plans | `docs/plans/US-1.2.1-plan.md` | Plan de implementación con checkboxes |
| quality | `quality/reports/codeguard/US-1.2.1-quality.json` | Reporte quality gates |

---

## Métricas de Calidad

| Métrica | Resultado | Umbral | Estado |
|---------|-----------|--------|--------|
| Tests unitarios | 17/17 | — | ✅ |
| Tests integración | 4/4 | — | ✅ |
| Tests BDD | 6/6 | — | ✅ |
| **Total tests** | **27/27** | — | ✅ |
| Cobertura total | 97.71% | ≥ 90% | ✅ |
| CodeGuard errores | 0 | 0 | ✅ |
| CodeGuard advertencias | 0 | 0 | ✅ |
| Violaciones hexagonales | 0 | 0 | ✅ |

---

## Invariantes implementadas

| Invariante | Dónde se valida | Excepción |
|-----------|----------------|-----------|
| INV-P-01: `valorAP > 0` | `AP.__post_init__()` (domain) | `ValorAPInvalido` |
| INV-P-02: AP único por (atleta, disciplina, competencia) | `RegistrarAPHandler.handle()` | `APYaRegistrado` |
| INV-P-03: Plazo AP no vencido | `RegistrarAPHandler.handle()` via `CompetenciaEstadoPort` | `PlazoAPVencidoError` |
| INV-P-04: Grilla no confirmada | `RegistrarAPHandler.handle()` via `CompetenciaEstadoPort` | `GrillaYaConfirmadaError` |

---

## Decisiones técnicas tomadas

1. **Stream ID encoda natural key**: `performance-{cid}-{pid}-{disciplina}` — la unicidad del AP (INV-P-02) se verifica cargando el stream. Stream vacío = no existe.
2. **CompetenciaEstadoPort**: nuevo puerto para INV-P-03/P-04. Stub en SP1 siempre retorna False. Implementación real en SP2.
3. **pytest-bdd steps síncronos**: `asyncio.run()` como wrapper — pytest-bdd no soporta async steps nativamente.
4. **pyproject.toml**: `build-backend` cambiado a `setuptools.build_meta` (fix de compatibilidad con Python 3.14 / uv).
5. **pytest-bdd** agregado a dependencias dev.

---

## Deuda técnica identificada

- INV-P-03 e INV-P-04: la implementación real del `CompetenciaEstadoPort` queda pendiente para SP2 (cuando exista el aggregate `Competencia`).
- El stub `StubCompetenciaEstadoAdapter` debe reemplazarse en SP2.

---

*Generado por `/implement-us` Fase 9 — 2026-03-21*
