# Plan de Implementación — US-2.1.3: Ajustar Grilla Manualmente

**Fecha:** 2026-03-26
**Branch:** `feature/US-2.1.3-ajustar-grilla`
**Estimación:** 3 puntos

---

## Análisis de impacto

| Capa | Artefactos nuevos | Artefactos modificados |
|------|-------------------|----------------------|
| Domain | `CambioGrilla` VO · `GrillaDeSalidaAjustada` event · `GrillaNoGenerada` · `PerformanceNoEncontrada` excepciones | `competencia.py` (ajustar_grilla + _apply_stored) · `exceptions.py` (doc + nuevas clases) |
| Application | `AjustarGrillaCommand` · `AjustarGrillaHandler` | — |
| Infrastructure | — | — |
| API | — | endpoints en US-2.1.4 |

---

## Tareas

### T1 — `exceptions.py` — nuevas excepciones
- Agregar `GrillaNoGenerada` bajo el grupo Competencia
- Agregar `PerformanceNoEncontrada` bajo el grupo Competencia
- Actualizar docstring del módulo con el nuevo árbol

### T2 — `CambioGrilla` VO
- Archivo: `src/competencia/domain/value_objects/cambio_grilla.py`
- `campo: Literal["posicion", "andarivel"]`
- `performance_id: UUID`
- `valor_nuevo: int`
- Dataclass frozen=True

### T3 — `GrillaDeSalidaAjustada` domain event
- Archivo: `src/competencia/domain/events/grilla_de_salida_ajustada.py`
- Campos: `competencia_id`, `disciplina`, `cambios: tuple[dict, ...]`, `ajustada_en`
- Implementa `to_payload()` y `from_payload()` (patrón GrillaDeSalidaGenerada)

### T4 — `Competencia.ajustar_grilla()`
- Archivo: `src/competencia/domain/aggregates/competencia.py`
- Precondiciones: `_grilla` no vacía (else `GrillaNoGenerada`), `_grilla_confirmada` False (else `GrillaYaConfirmada`)
- Para cada `CambioGrilla`:
  - Validar que `performance_id` existe en `_grilla` (else `PerformanceNoEncontrada`)
  - Aplicar cambio (posición o andarivel)
- Si hubo cambios de posición: recalcular OTs con P-02
- Construir payload de cambios (campo, valorAnterior, valorNuevo)
- Emitir `GrillaDeSalidaAjustada`
- Actualizar `self._grilla`
- Agregar `_apply_grilla_de_salida_ajustada` en `_apply_stored`

### T5 — `AjustarGrillaCommand` + `AjustarGrillaHandler`
- Archivo: `src/competencia/application/commands/ajustar_grilla.py`
- Command: `competencia_id`, `disciplina`, `cambios: list[CambioGrilla]`
- Handler: reconstituye Competencia → `ajustar_grilla()` → persiste evento
  (patrón idéntico a `GenerarGrillaHandler`, sin puerto externo)

### T6 — Tests unitarios
- `tests/unit/competencia/domain/test_ajustar_grilla.py`
  - ajuste de posición recalcula OTs correctamente
  - ajuste de andarivel no afecta OTs
  - ajuste acumulativo (dos eventos)
  - `GrillaNoGenerada` si grilla vacía
  - `GrillaYaConfirmada` si grilla confirmada
  - `PerformanceNoEncontrada` si performance_id desconocido
- `tests/unit/competencia/application/test_ajustar_grilla_handler.py`
  - handler persiste evento en event store

### T7 — Tests de integración
- `tests/integration/competencia/test_ajustar_grilla_integration.py`
  - flujo completo: configurar → generar → ajustar → event store

### T8 — BDD steps
- `tests/features/steps/ajustar_grilla_steps.py`
  - implementar todos los steps del feature US-2.1.3

### T9 — Quality gates + reporte
- `codeguard src/`
- `designreviewer src/`
- Reporte final en `docs/reports/`

---

## Dependencias

- `GrillaYaConfirmada` ya existe en `exceptions.py` ✅
- `EntradaGrilla` VO ya existe ✅
- `_build_stream_id()` helper ya existe en `generar_grilla.py` — se replica
- No requiere cambios en infrastructure ni API

---

## Criterios de DoD

- [ ] `ajustar_grilla()` pasa todas las precondiciones
- [ ] OTs recalculados correctamente tras cambio de posición
- [ ] `GrillaDeSalidaAjustada` persiste en el stream
- [ ] `_apply_stored` reconstituye correctamente tras ajuste
- [ ] Cobertura ≥ 90% en domain/ y application/
- [ ] Pylint ≥ 8.0
- [ ] 0 CRITICAL DesignReviewer
- [ ] Todos los escenarios BDD passing
