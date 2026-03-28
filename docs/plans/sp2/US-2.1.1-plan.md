# Plan de Implementación — US-2.1.1
# Scaffold Aggregate Competencia + ConfigurarIntervaloOT

**Fecha:** 2026-03-25
**Branch:** `feature/US-2.1.1-competencia-intervalo-ot`
**Estimación:** 45-60 min

---

## Artefactos a crear

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| T1 | NEW | `src/competencia/domain/value_objects/estado_competencia.py` | Enum `EstadoCompetencia` (Preparacion → Confirmada → EnEjecucion → Finalizada) |
| T2 | NEW | `src/competencia/domain/value_objects/intervalo_disciplina.py` | VO `IntervaloDisciplina` — valida `intervalo_minutos > 0` |
| T3 | NEW | `src/competencia/domain/events/intervalo_ot_configurado.py` | `IntervaloOTConfigurado` event (competenciaId, disciplina, intervaloDisciplina, configuradoPor) |
| T4 | NEW | `src/competencia/domain/aggregates/competencia.py` | `Competencia` aggregate con `configurar_intervalo_ot()` + reconstitución desde eventos |
| T5 | NEW | `src/competencia/application/commands/configurar_intervalo_ot.py` | `ConfigurarIntervaloOTCommand` + `ConfigurarIntervaloOTHandler` |

## Refactors de deuda SOLID (SP1)

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| R1 | REFACTOR | `src/competencia/domain/aggregates/performance.py` | OCP: reemplazar cadena if/elif en `_apply_stored` por dispatch dict `{event_type: apply_fn}` |
| R2 | REFACTOR | `src/competencia/api/router.py` | DIP: handlers instanciados directamente → mover instanciación a funciones `Depends()` |

## Tests

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| T6 | NEW | `tests/unit/competencia/domain/test_competencia.py` | Tests unitarios del aggregate Competencia (happy paths + invariantes) |
| T7 | NEW | `tests/unit/competencia/application/test_configurar_intervalo_ot_handler.py` | Tests del handler con event store in-memory |
| T8 | NEW | `tests/integration/competencia/test_configurar_intervalo_ot_integration.py` | Test integración end-to-end con SQLite real |
| T9 | NEW | `tests/features/steps/US-2.1.1_steps.py` | Step definitions BDD para los 4 escenarios |

---

## Orden de ejecución

```
T1 → T2 → T3 → T4 → T5   (dominio primero, luego aplicación)
R1 → R2                    (refactors en paralelo conceptual)
T6 → T7 → T8 → T9         (tests al final, una vez implementado)
```

## Invariantes a implementar

- **INV-C-01:** `intervaloDisciplina` debe estar configurado antes de `GenerarGrilla`
- **IntervaloInvalido:** si `intervalo_minutos <= 0`
- **GrillaYaConfirmada:** si `GrillaConfirmada` ya fue emitida — impide reconfigurar

## Stream ID

`competencia-{competencia_id}` — misma tabla `events`, distinto prefijo que `performance-*`

---

*Generado en Fase 2 de /implement-us*
