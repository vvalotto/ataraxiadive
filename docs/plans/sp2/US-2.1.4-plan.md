# Plan de Implementación — US-2.1.4: Confirmar Grilla + Iniciar Competencia

**Fecha:** 2026-03-26
**Branch:** `feature/US-2.1.4-confirmar-grilla`
**Estimación:** 3 puntos

---

## Análisis de impacto

| Capa | Artefactos nuevos | Artefactos modificados |
|------|-------------------|----------------------|
| Domain | `GrillaConfirmada` event · `CompetenciaIniciada` event · `CompetenciaNoConfirmada` excepción | `competencia.py` (confirmar_grilla + iniciar_competencia + _apply_stored) · `exceptions.py` · `estado_competencia.py` (si aplica) |
| Application | `ConfirmarGrillaCommand+Handler` · `IniciarCompetenciaCommand+Handler` | — |
| Infrastructure | `CompetenciaEstadoAdapter` (implementación real) | — |
| API | endpoints `POST /confirmar-grilla` · `POST /iniciar` · `GET /grilla` · `GET /estado` | `router.py` (registrar nuevos endpoints + DI del adaptador real) |

---

## Tareas

### T1 — `exceptions.py` — nueva excepción
- Agregar `CompetenciaNoConfirmada` bajo el grupo Competencia

### T2 — `GrillaConfirmada` domain event
- Archivo: `src/competencia/domain/events/grilla_confirmada.py`
- Campos: `competencia_id`, `disciplina`, `confirmada_en`
- Nota: el evento ya era reconocido en `_apply_stored` (applica `_grilla_confirmada = True`); formalizar como dataclass

### T3 — `CompetenciaIniciada` domain event
- Archivo: `src/competencia/domain/events/competencia_iniciada.py`
- Campos: `competencia_id`, `disciplina`, `juez_id`, `iniciada_en`

### T4 — `Competencia.confirmar_grilla()` + `iniciar_competencia()`
- `confirmar_grilla()`: precondiciones `GrillaNoGenerada` + `GrillaYaConfirmada`; emite `GrillaConfirmada`; `_estado = Confirmada`
- `iniciar_competencia(juez_id)`: precondición `EstadoCompetencia != Confirmada` → `CompetenciaNoConfirmada`; emite `CompetenciaIniciada`; `_estado = EnEjecucion`
- `_apply_stored`: agregar handlers para `GrillaConfirmada` (actualizar `_estado`) y `CompetenciaIniciada`

### T5 — `ConfirmarGrillaCommand+Handler` y `IniciarCompetenciaCommand+Handler`
- Archivos: `src/competencia/application/commands/confirmar_grilla.py` e `iniciar_competencia.py`
- Patrón idéntico a `AjustarGrillaHandler` (sin puertos externos)

### T6 — `CompetenciaEstadoAdapter` (infraestructura real)
- Archivo: `src/competencia/infrastructure/repositories/competencia_estado_adapter.py`
- Implementa `CompetenciaEstadoPort` consultando el stream desde el Event Store
- `is_grilla_confirmada`: True si `GrillaConfirmada` en stream
- `is_en_ejecucion`: True si `CompetenciaIniciada` en stream y `CompetenciaFinalizada` no existe
- `is_plazo_vencido`: True si `PlazoAPVencido` en stream (placeholder — evento no existe aún, retorna False)

### T7 — Endpoints API + DI
- `POST /competencia/{id}/confirmar-grilla` → `ConfirmarGrillaHandler`
- `POST /competencia/{id}/iniciar` → `IniciarCompetenciaHandler`
- `GET /competencia/{id}/grilla` → Read Model con lista ordenada de entradas
- `GET /competencia/{id}/estado` → estado actual + intervalo + grilla confirmada
- Registrar `CompetenciaEstadoAdapter` en el contenedor DI del router

### T8 — Tests unitarios
- `tests/unit/competencia/domain/test_confirmar_grilla.py`
- `tests/unit/competencia/application/test_confirmar_grilla_handler.py`
- `tests/unit/competencia/application/test_iniciar_competencia_handler.py`

### T9 — Tests de integración
- `tests/integration/competencia/test_confirmar_grilla_integration.py`

### T10 — BDD steps
- `tests/features/steps/confirmar_grilla_steps.py`

### T11 — Quality gates + reporte

---

## Dependencias

- `GrillaYaConfirmada` + `GrillaNoGenerada` ya existen ✅
- `_apply_grilla_confirmada` ya existe en `_apply_stored` pero como stub inline — se formalizará
- `EstadoCompetencia` enum tiene `Preparacion`, `Confirmada`, `EnEjecucion`, `Finalizada` — verificar que todos existen
- El adaptador real se registra en el router; el stub sigue como test double en tests

---

## Criterios de DoD

- [ ] `confirmar_grilla()` + `iniciar_competencia()` pasan precondiciones
- [ ] Transiciones de estado correctas: Preparacion → Confirmada → EnEjecucion
- [ ] `CompetenciaEstadoAdapter` retorna estado real desde el stream
- [ ] Endpoints API funcionan end-to-end
- [ ] Cobertura ≥ 90% en domain/ y application/
- [ ] 0 CRITICAL DesignReviewer
- [ ] Todos los escenarios BDD passing
