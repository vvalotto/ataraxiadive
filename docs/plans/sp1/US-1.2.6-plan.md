# Plan de Implementación — US-1.2.6: Corregir Resultado

| Campo | Valor |
|-------|-------|
| **US** | US-1.2.6 — CorregirResultado |
| **Incremento** | Inc 1.2 — El Dominio Habla |
| **BC** | `competencia` |
| **Aggregate** | `Performance` |
| **Fecha** | 2026-03-23 |

---

## Análisis de impacto

### Estado actual de métricas (post US-1.2.5)
- CBO Performance: 19/20 (`max_cbo=20`)
- WMC Performance: ~30/36 (`max_wmc=36`)
- Líneas Performance: ~353 (`max_god_object_lines=380`)

### Impacto de US-1.2.6
| Cambio | CBO delta | WMC delta |
|--------|-----------|-----------|
| Import `ResultadoCorregido` | +1 | — |
| Excepción inline `EstadoInvalidoParaCorregirResultado` | +1 | — |
| Método `corregir_resultado()` (2 guards + 1 evento) | — | +4 |
| `_apply_stored` (1 elif) | — | +1 |
| **Total estimado** | **21** | **~35** |

**Acción requerida:** ajustar `max_cbo=22` en `pyproject.toml` antes de la implementación.

---

## Artefactos a crear

### Domain (src/competencia/domain/)

| Artefacto | Ruta | Descripción |
|-----------|------|-------------|
| Evento | `events/resultado_corregido.py` | `ResultadoCorregido` — nuevo domain event |
| Excepción | inline en `aggregates/performance.py` | `EstadoInvalidoParaCorregirResultado` |
| Método | `aggregates/performance.py` | `corregir_resultado(valor_rp, unidad, registrado_por, motivo)` |
| Apply | `aggregates/performance.py` | rama `ResultadoCorregido` en `_apply_stored` |

### Application (src/competencia/application/commands/)

| Artefacto | Ruta | Descripción |
|-----------|------|-------------|
| Command + Handler | `commands/corregir_resultado.py` | `CorregirResultadoCommand` + `CorregirResultadoHandler` |

### Tests

| Artefacto | Ruta |
|-----------|------|
| Tests unitarios | `tests/unit/competencia/domain/test_performance.py` (añadir casos) |
| Tests unitarios handler | `tests/unit/competencia/application/test_corregir_resultado_handler.py` |
| Tests integración | `tests/integration/competencia/test_corregir_resultado_integration.py` |
| Steps BDD | `tests/features/steps/corregir_resultado_steps.py` |

---

## Tareas de implementación

### T1 — Ajustar `pyproject.toml` [~2 min]
- Subir `max_cbo` de 20 a 22

### T2 — Crear `ResultadoCorregido` event [~10 min]
- Campos: `performance_id`, `participante_id`, `disciplina`, `valor_rp_anterior`, `valor_rp_nuevo`, `unidad`, `motivo`, `registrado_por`, `corregido_en`
- Mismo patrón que `ResultadoRegistrado`

### T3 — Actualizar `Performance` aggregate [~15 min]
- Agregar excepción `EstadoInvalidoParaCorregirResultado`
- Importar `ResultadoCorregido`
- Implementar `corregir_resultado()`:
  - Guard: `self._estado != EstadoPerformance.Ejecutada` → lanza `EstadoInvalidoParaCorregirResultado`
  - Guard: `not motivo` → lanza `MotivoObligatorio`
  - Emite `ResultadoCorregido` con `valor_rp_anterior=str(self._rp)`
  - Actualiza `self._rp = valor_rp`
  - Estado permanece `Ejecutada`
- Agregar rama `ResultadoCorregido` en `_apply_stored`:
  - `self._rp = Decimal(payload["valor_rp_nuevo"])`

### T4 — Crear `CorregirResultadoCommand` + `CorregirResultadoHandler` [~10 min]
- Mismo patrón que `RegistrarDNSHandler`
- Handler: load → reconstitute → `corregir_resultado()` → persist

### T5 — Tests unitarios [~20 min]
- `test_corregir_resultado_handler.py` (camino feliz + PerformanceNoEncontrada + EstadoInvalido + MotivoObligatorio)
- Casos nuevos en `test_performance.py` para `corregir_resultado()`

### T6 — Tests de integración [~15 min]
- Flujo completo: AP → Llamada → Resultado → Tarjeta → Corrección
- Verificar payload `ResultadoCorregido` en stream
- Verificar rechazo desde DNS

### T7 — Steps BDD [~15 min]
- `corregir_resultado_steps.py` con los 3 escenarios del feature

---

## Diseño del evento `ResultadoCorregido`

```python
@dataclass(frozen=True)
class ResultadoCorregido(DomainEvent):
    performance_id: str
    participante_id: str
    disciplina: str
    valor_rp_anterior: str   # RP previo (para trazabilidad)
    valor_rp_nuevo: str      # RP corregido
    unidad: str
    motivo: str
    registrado_por: str
    corregido_en: str
```

## Diseño del método `corregir_resultado()`

```python
def corregir_resultado(
    self, valor_rp: Decimal, unidad: UnidadMedida,
    registrado_por: str, motivo: str
) -> None:
    if self._estado != EstadoPerformance.Ejecutada:
        raise EstadoInvalidoParaCorregirResultado(...)
    if not motivo:
        raise MotivoObligatorio(...)
    # emitir ResultadoCorregido
    self._rp = valor_rp
    # self._estado permanece Ejecutada
```

---

## Tiempo estimado total

| Tarea | Estimado |
|-------|---------|
| T1 pyproject.toml | 2 min |
| T2 evento | 10 min |
| T3 aggregate | 15 min |
| T4 command/handler | 10 min |
| T5 tests unitarios | 20 min |
| T6 tests integración | 15 min |
| T7 steps BDD | 15 min |
| **Total** | **~87 min** |
