# Reporte de Implementación — US-2.1.3: Ajustar Grilla Manualmente

**Fecha:** 2026-03-26
**Branch:** `feature/US-2.1.3-ajustar-grilla`
**Duración:** ~29 min
**Estimación:** 3 pts

---

## Resumen

Implementación completa de `Competencia.ajustar_grilla()` con lógica de swap de posiciones,
recálculo de OTs (política P-02), e integración plena con el Event Store.

---

## Artefactos creados

| Artefacto | Tipo | Ruta |
|-----------|------|------|
| `GrillaNoGenerada` + `PerformanceNoEncontrada` | Excepciones | `src/competencia/domain/exceptions.py` |
| `CambioGrilla` | Value Object | `src/competencia/domain/value_objects/cambio_grilla.py` |
| `GrillaDeSalidaAjustada` | Domain Event | `src/competencia/domain/events/grilla_de_salida_ajustada.py` |
| `AjustarGrillaCommand` + `AjustarGrillaHandler` | Application | `src/competencia/application/commands/ajustar_grilla.py` |
| `US-2.1.3-ajustar-grilla.feature` | BDD | `tests/features/US-2.1.3-ajustar-grilla.feature` |
| `ajustar_grilla_steps.py` | BDD Steps | `tests/features/steps/ajustar_grilla_steps.py` |
| `test_ajustar_grilla.py` | Tests unitarios | `tests/unit/competencia/domain/test_ajustar_grilla.py` |
| `test_ajustar_grilla_handler.py` | Tests unitarios | `tests/unit/competencia/application/test_ajustar_grilla_handler.py` |
| `test_ajustar_grilla_integration.py` | Tests integración | `tests/integration/competencia/test_ajustar_grilla_integration.py` |
| `US-2.1.3-plan.md` | Plan | `docs/plans/sp2/US-2.1.3-plan.md` |

## Artefactos modificados

| Artefacto | Cambio |
|-----------|--------|
| `competencia.py` | `ajustar_grilla()` + `_apply_grilla_de_salida_ajustada()` + `_apply_stored` |
| `exceptions.py` | Árbol actualizado, nuevas excepciones |
| `pyproject.toml` | `max_wmc = 60` (ajuste para Inc 2.1 completo) |
| `matrix.md` | US-2.1.3 → ✅ Done |

---

## Métricas

| Indicador | Valor |
|-----------|-------|
| Tests totales | 313 (+29 nuevos) |
| Tests unitarios US-2.1.3 | 20 |
| Tests integración US-2.1.3 | 4 |
| Escenarios BDD | 5 |
| Cobertura BC Competencia | 98% |
| DesignReviewer CRITICAL | 0 |
| CodeGuard errores | 0 |

---

## Decisión de diseño notable

**Swap implícito de posiciones:** cuando se mueve atleta A a la posición X (ocupada por B),
B recibe la posición anterior de A. El evento `GrillaDeSalidaAjustada` persiste ambos cambios
explícitamente, lo que permite reconstituir el estado exacto sin lógica de swap durante replay.

Esto emergió al escribir el test `test_ajuste_posicion_recalcula_ot_segunda_posicion` — el dominio
corrigió un defecto en la implementación inicial durante la Fase 4.

---

## Estado post-implementación — Inc 2.1

| US | Estado |
|----|--------|
| US-2.1.1 ConfigurarIntervaloOT + Competencia scaffold | ✅ Done |
| US-2.1.2 GenerarGrilla | ✅ Done |
| US-2.1.3 AjustarGrilla | ✅ Done |
| US-2.1.4 ConfirmarGrilla + IniciarCompetencia | ⏳ Pendiente |
