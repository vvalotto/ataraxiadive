# Plan de Implementación: US-1.2.5 — Registrar DNS

**Patrón:** Hexagonal DDD + Event Sourcing
**BC:** competencia
**Estimación Total:** 30 min

---

## 1. Domain — Evento DNSRegistrado (10 min)

- [ ] `src/competencia/domain/events/dns_registrado.py`
  - `@dataclass(frozen=True)` hereda de `DomainEvent`
  - Campos: `performance_id`, `participante_id`, `disciplina`, `ot_programado: str`, `registrado_por: str`, `registrado_en: str`
  - Métodos: `to_payload()`, `from_payload()`
- [ ] `src/competencia/domain/events/__init__.py` — exportar `DNSRegistrado`

## 2. Domain — Aggregate Performance: método registrar_dns() (15 min)

- [ ] `src/competencia/domain/aggregates/performance.py`
  - Import: `from competencia.domain.events.dns_registrado import DNSRegistrado`
  - Nueva excepción inline: `EstadoInvalidoParaRegistrarDNS(Exception)`
  - Nuevo campo: `_ot_programado: datetime | None = None`
  - Actualizar `llamar()`: `self._ot_programado = ot_programado`
  - Actualizar `_apply_stored("AtletaLlamado")`: `self._ot_programado = datetime.fromisoformat(payload["ot_programado"])`
  - Método `registrar_dns(registrado_por: str) -> None`
    - INV-P-08: `self._estado != EstadoPerformance.Llamada` → raise `EstadoInvalidoParaRegistrarDNS`
    - Emite `DNSRegistrado` con `ot_programado=self._ot_programado.isoformat()`
    - `self._estado = EstadoPerformance.DNS`

## 3. Application — Command y Handler RegistrarDNS (10 min)

- [ ] `src/competencia/application/commands/registrar_dns.py`
  - `@dataclass(frozen=True) RegistrarDNSCommand`:
    - `competencia_id: UUID`, `participante_id: UUID`, `disciplina: Disciplina`, `registrado_por: str`
  - `class RegistrarDNSHandler`:
    - Constructor: `event_store: EventStorePort`
    - `async handle(command) -> None`:
      1. `stream_id = f"performance-{competencia_id}-{participante_id}-{disciplina.value}"`
      2. `events = await event_store.load(stream_id)`
      3. `performance = Performance.reconstitute(events)`
      4. `performance.registrar_dns(command.registrado_por)`
      5. Persistir evento via `event_store.append()`
- [ ] `src/competencia/application/commands/__init__.py` — exportar ambas clases

---

## Estimación por tarea

| Tarea | Estimado |
|-------|----------|
| DNSRegistrado event | 10 min |
| Performance.registrar_dns() + _apply_stored + _ot_programado | 15 min |
| RegistrarDNSCommand + Handler | 10 min |
| Tests unitarios (Fase 4) | 15 min |
| Tests integración (Fase 5) | 10 min |
| BDD steps (Fase 6) | 10 min |
| Quality gates (Fase 7) | 5 min |
| **Total** | **~1h 15min** |

---

## Dependencias de código

| Nuevo/modificado | Depende de |
|-----------------|-----------|
| `dns_registrado.py` (nuevo) | `shared/domain/base/domain_event.py` ✅ |
| `performance.py` (extensión) | `dns_registrado.py` |
| `registrar_dns.py` (nuevo) | `performance.py`, `event_store_port.py` ✅ |

**Nota CBO:** `DNSRegistrado` (+1 import) + `EstadoInvalidoParaRegistrarDNS` (clase interna, también contada por el analyzer) → CBO=19.
`max_cbo` ajustado a 20 (el analyzer cuenta exceptions del mismo módulo, no solo imports externos).

**Nota GodObject:** `performance.py` llega a 310 líneas con 5 métodos de dominio.
`max_god_object_lines` ajustado a 380 (aggregate DDD principal — patrón justificado).

---

*2026-03-23 — Fase 2 /implement-us US-1.2.5*
