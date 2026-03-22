# Plan de Implementación: US-1.2.1 — Registrar AP

**Patrón:** Hexagonal DDD + Event Sourcing
**BC:** competencia
**Estimación Total:** 2h 30min
**Estado:** 0/17 tareas completadas

---

## 1. Shared — Clases base (Domain)

- [ ] `src/shared/domain/base/domain_event.py` (10 min)
  - `DomainEvent`: dataclass base inmutable para todos los domain events
  - Campos: `event_type`, `occurred_at`, `aggregate_id`
- [ ] `src/shared/domain/base/aggregate_root.py` (10 min)
  - `AggregateRoot`: clase base con `_pending_events` y `_apply()`
- [ ] `src/shared/domain/base/__init__.py` (2 min)

## 2. Value Objects — competencia/domain/value_objects/

- [ ] `src/competencia/domain/value_objects/disciplina.py` (8 min)
  - `Disciplina`: enum STA, DNF, DYN, DYNB, SPE2X50, CNF, CWT, FIM, VWT
- [ ] `src/competencia/domain/value_objects/unidad_medida.py` (5 min)
  - `UnidadMedida`: enum Metros, Segundos
- [ ] `src/competencia/domain/value_objects/estado_performance.py` (5 min)
  - `EstadoPerformance`: enum AnunciadaAP, Llamada, Ejecutada, DNS
- [ ] `src/competencia/domain/value_objects/ap.py` (10 min)
  - `AP`: valor (Decimal > 0) + unidad (UnidadMedida), inmutable
  - Valida `valor > 0` en `__post_init__` → lanza `ValorAPInvalido`
- [ ] `src/competencia/domain/value_objects/__init__.py` (2 min)

## 3. Domain Events — competencia/domain/events/

- [ ] `src/competencia/domain/events/ap_registrado.py` (8 min)
  - `APRegistrado`: hereda de `DomainEvent`
  - Campos: performance_id, competencia_id, participante_id, disciplina, valor_ap, unidad
- [ ] `src/competencia/domain/events/__init__.py` (2 min)

## 4. Puertos adicionales — competencia/domain/ports/

- [ ] `src/competencia/domain/ports/competencia_estado_port.py` (8 min)
  - `CompetenciaEstadoPort`: ABC con `is_plazo_vencido()` e `is_grilla_confirmada()`

## 5. Aggregate — competencia/domain/aggregates/

- [ ] `src/competencia/domain/aggregates/performance.py` (20 min)
  - `Performance(AggregateRoot)`: aggregate raíz
  - `registrarAP(valor, unidad)` → emite `APRegistrado`, valida INV-P-01
  - `reconstitute(events)` → reconstruye estado desde eventos
  - `from_new(...)` → factory para nueva Performance

## 6. Command Handler — competencia/application/commands/

- [ ] `src/competencia/application/commands/registrar_ap.py` (20 min)
  - `RegistrarAPCommand`: dataclass con competencia_id, participante_id, disciplina, valor_ap, unidad
  - `RegistrarAPHandler`: inyecta EventStorePort + CompetenciaEstadoPort
  - Flujo: check INV-P-03/P-04 → load stream → check INV-P-02 → registrarAP → append

## 7. Stub SP1 — competencia/infrastructure/

- [ ] `src/competencia/infrastructure/competencia_estado_stub.py` (5 min)
  - `StubCompetenciaEstadoAdapter`: implementa puerto, retorna siempre `False`

## 8. Tests unitarios

- [ ] `tests/unit/competencia/domain/__init__.py` (1 min)
- [ ] `tests/unit/competencia/domain/test_performance.py` (25 min)
  - registrarAP exitoso + pending events
  - INV-P-01: valor=0 → ValueError
  - INV-P-01: valor negativo → ValueError
  - reconstitute desde eventos → estado correcto
- [ ] `tests/unit/competencia/application/__init__.py` (1 min)
- [ ] `tests/unit/competencia/application/test_registrar_ap_handler.py` (20 min)
  - happy path (stub + event store mock)
  - INV-P-02: stream existente → APYaRegistrado
  - INV-P-03: plazo vencido → PlazoAPVencidoError
  - INV-P-04: grilla confirmada → GrillaYaConfirmadaError

## 9. Tests de integración

- [ ] `tests/integration/competencia/test_registrar_ap_integration.py` (20 min)
  - SQLiteEventStore real in-memory
  - flujo completo RegistrarAPHandler → EventStore → reload
  - segunda llamada misma combinación → APYaRegistrado

## 10. BDD step definitions

- [ ] `tests/features/steps/registrar_ap_steps.py` (20 min)
  - 6 step definitions para `US-1.2.1-registrar-ap.feature`
  - `conftest.py` con fixtures de integración

## 11. Validación y documentación

- [ ] Quality gates: `codeguard src/competencia/ src/shared/` (5 min)
- [ ] Actualizar `docs/traceability/matrix.md` (5 min)

---

*Generado por `/implement-us` Fase 2 — 2026-03-21*
