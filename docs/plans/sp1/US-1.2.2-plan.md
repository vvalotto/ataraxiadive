# Plan de Implementación: US-1.2.2 — Llamar Atleta

**Patrón:** Hexagonal DDD + Event Sourcing
**BC:** competencia
**Estimación Total:** 1h 30min
**Estado:** ✅ Implementada 2026-03-22 — 12/12 tareas completadas

---

## 1. Domain — Extender puerto CompetenciaEstadoPort (5 min)

- [ ] `src/competencia/domain/ports/competencia_estado_port.py`
  - Agregar método abstracto `is_en_ejecucion(competencia_id: UUID) -> bool`
  - Docstring: INV-P-05 — verifica si Competencia está en EnEjecucion

## 2. Domain — Evento AtletaLlamado (10 min)

- [ ] `src/competencia/domain/events/atleta_llamado.py`
  - `@dataclass(frozen=True)` hereda de `DomainEvent`
  - Campos: `performance_id`, `participante_id`, `disciplina`, `posicion_grilla: int`, `ot_programado: str` (ISO 8601), `llamado_en: str`
  - Métodos: `to_payload()`, `from_payload()` (mismo patrón que `APRegistrado`)
- [ ] `src/competencia/domain/events/__init__.py`
  - Exportar `AtletaLlamado`

## 3. Domain — Aggregate Performance: método llamar() (20 min)

- [ ] `src/competencia/domain/aggregates/performance.py`
  - Nueva excepción inline: `EstadoInvalidoParaLlamar(Exception)`
  - Nuevo método `llamar(ot_programado: datetime, posicion_grilla: int) -> None`
    - Precondición: `self._estado == EstadoPerformance.AnunciadaAP` → raise `EstadoInvalidoParaLlamar`
    - Emite `AtletaLlamado` con todos sus campos
    - Setea `self._estado = EstadoPerformance.Llamada`
  - Extender `_apply_stored()` para reconocer `AtletaLlamado`:
    - Setea `self._estado = EstadoPerformance.Llamada`
  - Actualizar docstring de estados: `AnunciadaAP → Llamada → Ejecutada / DNS`

## 4. Infrastructure — Extender stub (5 min)

- [ ] `src/competencia/infrastructure/competencia_estado_stub.py`
  - Agregar `is_en_ejecucion(competencia_id: UUID) -> bool`
  - Retorna siempre `True` (SP1 — competencia siempre en EnEjecucion)

## 5. Application — Command y Handler LlamarAtleta (20 min)

- [ ] `src/competencia/application/commands/llamar_atleta.py`
  - Excepción: `CompetenciaNoEnEjecucion(Exception)` — INV-P-05
  - `@dataclass(frozen=True) LlamarAtletaCommand`:
    - Campos: `competencia_id: UUID`, `participante_id: UUID`, `disciplina: Disciplina`, `ot_programado: datetime`, `posicion_grilla: int`
  - `class LlamarAtletaHandler`:
    - Constructor: `event_store: EventStorePort`, `competencia_estado: CompetenciaEstadoPort`
    - `async handle(command) -> None`:
      1. INV-P-05: `is_en_ejecucion(command.competencia_id)` → raise `CompetenciaNoEnEjecucion`
      2. Cargar Performance: `event_store.load(stream_id)` → `Performance.reconstitute(events)`
      3. `performance.llamar(command.ot_programado, command.posicion_grilla)`
      4. Persistir: `event_store.append(stream_id, event_type, payload)`
- [ ] `src/competencia/application/commands/__init__.py`
  - Exportar `LlamarAtletaCommand`, `LlamarAtletaHandler`, `CompetenciaNoEnEjecucion`

---

## Estimación por tarea

| Tarea | Estimado |
|-------|----------|
| Extender CompetenciaEstadoPort | 5 min |
| AtletaLlamado event | 10 min |
| Performance.llamar() + _apply_stored | 20 min |
| Stub is_en_ejecucion | 5 min |
| LlamarAtletaCommand + Handler | 20 min |
| Tests unitarios (Fase 4) | 20 min |
| Tests integración (Fase 5) | 15 min |
| BDD steps (Fase 6) | 10 min |
| Quality gates (Fase 7) | 5 min |
| **Total** | **~1h 50min** |

---

## Dependencias de código

| Nuevo archivo | Depende de |
|---------------|-----------|
| `atleta_llamado.py` | `shared/domain/base/domain_event.py` ✅ |
| `performance.py` (extensión) | `atleta_llamado.py`, `estado_performance.py` ✅ |
| `competencia_estado_stub.py` (extensión) | `competencia_estado_port.py` |
| `llamar_atleta.py` | `performance.py`, `competencia_estado_port.py`, `event_store_port.py` |

---

*2026-03-22 — Fase 2 /implement-us US-1.2.2*
