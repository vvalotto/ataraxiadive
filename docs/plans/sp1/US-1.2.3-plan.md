# Plan de Implementación: US-1.2.3 — Registrar Resultado

**Patrón:** Hexagonal DDD + Event Sourcing
**BC:** competencia
**Estimación Total:** 1h 10min

---

## 1. Domain — Nuevo estado en EstadoPerformance (5 min)

- [ ] `src/competencia/domain/value_objects/estado_performance.py`
  - Agregar `ResultadoRegistrado = "ResultadoRegistrado"` al StrEnum
  - Actualizar docstring: `Llamada → ResultadoRegistrado → Ejecutada`

## 2. Domain — Evento ResultadoRegistrado (10 min)

- [ ] `src/competencia/domain/events/resultado_registrado.py`
  - `@dataclass(frozen=True)` hereda de `DomainEvent`
  - Campos: `performance_id`, `participante_id`, `disciplina`, `valor_rp: str` (Decimal como str), `unidad`, `registrado_por: str`, `registrado_en: str` (ISO 8601)
  - Métodos: `to_payload()`, `from_payload()` (mismo patrón que `APRegistrado`)
- [ ] `src/competencia/domain/events/__init__.py`
  - Exportar `ResultadoRegistrado`

## 3. Domain — Aggregate Performance: método registrar_resultado() (20 min)

- [ ] `src/competencia/domain/aggregates/performance.py`
  - Nueva excepción inline: `EstadoInvalidoParaRegistrarResultado(Exception)`
  - Nuevo campo interno: `_rp: Decimal | None = None`
  - Nuevo método `registrar_resultado(valor_rp: Decimal, unidad: UnidadMedida, registrado_por: str) -> None`
    - Precondición: `self._estado == EstadoPerformance.Llamada` → raise `EstadoInvalidoParaRegistrarResultado`
    - Emite `ResultadoRegistrado` con todos sus campos
    - Setea `self._estado = EstadoPerformance.ResultadoRegistrado`
    - Setea `self._rp = valor_rp`
  - Extender `_apply_stored()` para reconocer `ResultadoRegistrado`:
    - Setea `self._estado = EstadoPerformance.ResultadoRegistrado`
    - Setea `self._rp = Decimal(payload["valor_rp"])`
  - Agregar propiedad `rp: Decimal | None`

## 4. Application — Command y Handler RegistrarResultado (15 min)

- [ ] `src/competencia/application/commands/registrar_resultado.py`
  - `@dataclass(frozen=True) RegistrarResultadoCommand`:
    - Campos: `competencia_id: UUID`, `participante_id: UUID`, `disciplina: Disciplina`, `valor_rp: Decimal`, `unidad: UnidadMedida`, `registrado_por: str`
  - `class RegistrarResultadoHandler`:
    - Constructor: `event_store: EventStorePort`
    - `async handle(command) -> None`:
      1. Cargar Performance: `event_store.load(stream_id)` → `Performance.reconstitute(events)`
      2. `performance.registrar_resultado(command.valor_rp, command.unidad, command.registrado_por)`
      3. Persistir: `event_store.append(stream_id, event_type, payload)`
- [ ] `src/competencia/application/commands/__init__.py`
  - Exportar `RegistrarResultadoCommand`, `RegistrarResultadoHandler`

---

## Estimación por tarea

| Tarea | Estimado |
|-------|----------|
| EstadoPerformance: nuevo estado | 5 min |
| ResultadoRegistrado event | 10 min |
| Performance.registrar_resultado() + _apply_stored | 20 min |
| RegistrarResultadoCommand + Handler | 15 min |
| Tests unitarios (Fase 4) | 20 min |
| Tests integración (Fase 5) | 10 min |
| BDD steps (Fase 6) | 10 min |
| Quality gates (Fase 7) | 5 min |
| **Total** | **~1h 35min** |

---

## Dependencias de código

| Nuevo/modificado | Depende de |
|-----------------|-----------|
| `estado_performance.py` (extensión) | — |
| `resultado_registrado.py` (nuevo) | `shared/domain/base/domain_event.py` ✅ |
| `performance.py` (extensión) | `resultado_registrado.py`, `estado_performance.py` ✅ |
| `registrar_resultado.py` (nuevo) | `performance.py`, `event_store_port.py` ✅ |

**Diferencia vs US-1.2.2:** no requiere puerto externo — `registrar_resultado()` no necesita consultar estado de Competencia.

---

*2026-03-22 — Fase 2 /implement-us US-1.2.3*
