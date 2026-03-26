# Reporte Final — US-2.1.4: Confirmar Grilla + Iniciar Competencia

**Fecha:** 2026-03-26
**Branch:** `feature/US-2.1.4-confirmar-grilla`
**Estado:** ✅ Done

---

## Resumen

Implementación de las operaciones `ConfirmarGrilla` e `IniciarCompetencia` del
aggregate Competencia, completando el ciclo de vida de la Grilla de Salida
(Incremento 2.1 — SP2).

---

## Artefactos producidos

### Domain
- `domain/events/grilla_confirmada.py` — nuevo evento `GrillaConfirmada`
- `domain/events/competencia_iniciada.py` — nuevo evento `CompetenciaIniciada`
- `domain/exceptions.py` — `CompetenciaNoConfirmada` (INV-C-03)
- `domain/aggregates/competencia.py` — `confirmar_grilla()` + `iniciar_competencia()` + `grilla_confirmada` property

### Application
- `application/commands/confirmar_grilla.py` — `ConfirmarGrillaCommand` + `ConfirmarGrillaHandler`
- `application/commands/iniciar_competencia.py` — `IniciarCompetenciaCommand` + `IniciarCompetenciaHandler`
- `application/queries/obtener_grilla.py` — `ObtenerGrillaQuery` + `ObtenerGrillaHandler`
- `application/queries/obtener_estado_competencia.py` — `ObtenerEstadoCompetenciaQuery` + `ObtenerEstadoCompetenciaHandler`

### Infrastructure
- `infrastructure/repositories/competencia_estado_adapter.py` — `CompetenciaEstadoAdapter` (reemplaza stub)

### API
- `api/router.py` — 5 nuevos endpoints:
  - `POST /{id}/ajustar-grilla` (US-2.1.3, diferido)
  - `POST /{id}/confirmar-grilla`
  - `POST /{id}/iniciar`
  - `GET /{id}/grilla`
  - `GET /{id}/estado`

### Tests
- `tests/unit/competencia/domain/test_confirmar_grilla.py` — 13 tests
- `tests/unit/competencia/application/test_confirmar_grilla_handler.py` — 3 tests
- `tests/unit/competencia/application/test_iniciar_competencia_handler.py` — 3 tests
- `tests/integration/competencia/test_confirmar_grilla_integration.py` — 6 tests
- `tests/features/steps/confirmar_grilla_steps.py` — 7 escenarios BDD

---

## Métricas de Calidad

| Métrica | Valor | Umbral |
|---------|-------|--------|
| Cobertura domain/ + application/ | 97.72% | ≥ 90% |
| CRITICAL DesignReviewer | 0 | 0 |
| Errores CodeGuard | 0 | 0 |
| Tests totales pasando | 297 | — |
| Escenarios BDD | 7/7 | — |

---

## Invariantes verificados

- **INV-C-02 (completo):** `confirmar_grilla()` → irreversible; bloquea `generar_grilla()`, `ajustar_grilla()` y `configurar_intervalo_ot()`
- **INV-C-03:** `iniciar_competencia()` requiere estado `Confirmada`
- Transiciones de estado: `Preparacion → Confirmada → EnEjecucion`

---

## Decisiones técnicas

1. **`CompetenciaEstadoAdapter` reemplaza `StubCompetenciaEstadoAdapter`** en el DI del router.
   El stub queda disponible exclusivamente como test double en tests.

2. **`grilla_confirmada` property** agregada al aggregate para queries sin exponer estado privado.

3. **Endpoints de grilla y estado** reciben `disciplina` como query param — necesario para
   reconstituir el aggregate, consistente con los handlers de commands.

---

## DoD Inc 2.1 — verificación final

- ✅ `confirmar_grilla()` + `iniciar_competencia()` pasan precondiciones
- ✅ Transiciones de estado correctas
- ✅ `CompetenciaEstadoAdapter` retorna estado real desde stream
- ✅ Endpoints API funcionan end-to-end
- ✅ Cobertura ≥ 90% en domain/ y application/
- ✅ 0 CRITICAL DesignReviewer
- ✅ Todos los escenarios BDD passing
