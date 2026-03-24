# Plan de Implementación: US-1.2.4 — Asignar Tarjeta

**Patrón:** Hexagonal DDD + Event Sourcing
**BC:** competencia
**Estimación Total:** 55 min

---

## 1. Domain — Value Object TipoTarjeta (5 min)

- [ ] `src/competencia/domain/value_objects/tipo_tarjeta.py`
  - `class TipoTarjeta(StrEnum)` — Blanca / Amarilla / Roja

## 2. Domain — Evento TarjetaAsignada (10 min)

- [ ] `src/competencia/domain/events/tarjeta_asignada.py`
  - `@dataclass(frozen=True)` hereda de `DomainEvent`
  - Campos: `performance_id`, `participante_id`, `disciplina`, `tipo: str`, `motivo: str | None`, `asignada_por: str`, `asignada_en: str`
  - Métodos: `to_payload()`, `from_payload()`
- [ ] `src/competencia/domain/events/__init__.py` — exportar `TarjetaAsignada`

## 3. Domain — Aggregate Performance: método asignar_tarjeta() (15 min)

- [ ] `src/competencia/domain/aggregates/performance.py`
  - Import: `from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta`
  - Import: `from competencia.domain.events.tarjeta_asignada import TarjetaAsignada`
  - Nueva excepción inline: `EstadoInvalidoParaAsignarTarjeta(Exception)`
  - Nueva excepción inline: `MotivoObligatorio(Exception)`
  - Nuevo campo: `_tarjeta: TipoTarjeta | None = None`
  - Método `asignar_tarjeta(tipo: TipoTarjeta, asignada_por: str, motivo: str | None = None) -> None`
    - INV-P-07: `self._estado != EstadoPerformance.ResultadoRegistrado` → raise `EstadoInvalidoParaAsignarTarjeta`
    - INV-P-11: `tipo in (Amarilla, Roja) and not motivo` → raise `MotivoObligatorio`
    - Emite `TarjetaAsignada`
    - `self._estado = EstadoPerformance.Ejecutada`
    - `self._tarjeta = tipo`
  - Extender `_apply_stored()` para `TarjetaAsignada`:
    - `self._estado = EstadoPerformance.Ejecutada`
    - `self._tarjeta = TipoTarjeta(payload["tipo"])`
  - Agregar propiedad `tarjeta: TipoTarjeta | None`

## 4. Application — Command y Handler AsignarTarjeta (10 min)

- [ ] `src/competencia/application/commands/asignar_tarjeta.py`
  - `@dataclass(frozen=True) AsignarTarjetaCommand`:
    - `competencia_id: UUID`, `participante_id: UUID`, `disciplina: Disciplina`, `tipo: TipoTarjeta`, `asignada_por: str`, `motivo: str | None = None`
  - `class AsignarTarjetaHandler`:
    - Constructor: `event_store: EventStorePort`
    - `async handle(command) -> None`:
      1. `stream_id = f"performance-{competencia_id}-{participante_id}-{disciplina.value}"`
      2. `events = await event_store.load(stream_id)`
      3. `performance = Performance.reconstitute(events)`
      4. `performance.asignar_tarjeta(command.tipo, command.asignada_por, command.motivo)`
      5. Persistir evento via `event_store.append()`
- [ ] `src/competencia/application/commands/__init__.py` — exportar ambas clases

---

## Estimación por tarea

| Tarea | Estimado |
|-------|----------|
| TipoTarjeta VO | 5 min |
| TarjetaAsignada event | 10 min |
| Performance.asignar_tarjeta() + _apply_stored | 15 min |
| AsignarTarjetaCommand + Handler | 10 min |
| Tests unitarios (Fase 4) | 20 min |
| Tests integración (Fase 5) | 10 min |
| BDD steps (Fase 6) | 10 min |
| Quality gates (Fase 7) | 5 min |
| **Total** | **~1h 25min** |

---

## Dependencias de código

| Nuevo/modificado | Depende de |
|-----------------|-----------|
| `tipo_tarjeta.py` (nuevo) | — |
| `tarjeta_asignada.py` (nuevo) | `shared/domain/base/domain_event.py` ✅ |
| `performance.py` (extensión) | `tipo_tarjeta.py`, `tarjeta_asignada.py` |
| `asignar_tarjeta.py` (nuevo) | `performance.py`, `event_store_port.py` ✅ |

**Nota CBO:** `TipoTarjeta` y `TarjetaAsignada` son 2 imports nuevos en `performance.py`.
CBO actual = 13, límite = 14 → **queda en 14 exacto** — no excede el umbral.

---

*2026-03-22 — Fase 2 /implement-us US-1.2.4*
