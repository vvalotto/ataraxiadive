# Plan de Implementación: US-3.1.1 — Aggregate Torneo — máquina de estados

**Patrón:** Hexagonal DDD — CRUD (no Event Sourcing)
**BC:** torneo
**Estimación Total:** 1h 30min
**Estado:** 0/12 tareas completadas

---

## 1. Value Objects — torneo/domain/value_objects/

- [ ] `src/torneo/domain/value_objects/estado_torneo.py` (5 min)
  - `EstadoTorneo(StrEnum)`: CREADO, INSCRIPCION_ABIERTA, PREPARACION, EJECUCION, PREMIACION, CERRADO, CANCELADO

- [ ] `src/torneo/domain/value_objects/sede.py` (5 min)
  - `Sede`: dataclass frozen — `nombre: str`, `ciudad: str`, `pais: str`

- [ ] `src/torneo/domain/value_objects/entidad_organizadora.py` (5 min)
  - `EntidadOrganizadora`: dataclass frozen — `nombre: str`, `tipo: str`
  - `tipo` debe ser uno de: FEDERACION, CLUB, ORGANIZACION

- [ ] `src/torneo/domain/value_objects/__init__.py` (2 min)

---

## 2. Excepciones — torneo/domain/

- [ ] `src/torneo/domain/exceptions.py` (5 min)
  - `TorneoNoEncontrado(Exception)`
  - `TransicionEstadoInvalida(Exception)`
  - `TorneoYaCancelado(Exception)` — no usar, unificar en TransicionEstadoInvalida
  - `TorneoCerrado(Exception)`

---

## 3. Puerto de repositorio — torneo/domain/ports/

- [ ] `src/torneo/domain/ports/torneo_repository_port.py` (5 min)
  - `TorneoRepositoryPort(ABC)`: `save`, `find_by_id`, `find_all`

- [ ] `src/torneo/domain/ports/__init__.py` (2 min)

---

## 4. Aggregate — torneo/domain/aggregates/

- [ ] `src/torneo/domain/aggregates/torneo.py` (25 min)
  - `Torneo`: dataclass con `__post_init__` para INV-T-01 e INV-T-02
  - 7 métodos de transición con validación de grafo de estados
  - `cancelar()` verifica CERRADO → lanza `TorneoCerrado`
  - Grafo de transiciones implementado con dict `_TRANSICIONES_VALIDAS`

- [ ] `src/torneo/domain/aggregates/__init__.py` (2 min)

---

## 5. Exports — torneo/domain/

- [ ] `src/torneo/domain/__init__.py` (3 min)
  - Re-exportar `Torneo`, `EstadoTorneo`, `Sede`, `EntidadOrganizadora`
  - Re-exportar excepciones y `TorneoRepositoryPort`

---

## Notas de implementación

- `Torneo` es dataclass simple — sin `AggregateRoot`, sin `_pending_events`
- Grafo de transiciones como dict de clase: `_TRANSICIONES_VALIDAS: dict[EstadoTorneo, set[EstadoTorneo]]`
- `cancelar()` es un método separado (no está en el grafo) — verifica CERRADO/CANCELADO explícitamente
- `EntidadOrganizadora.tipo` se valida como string libre en SP3; enum formal queda para SP4 si se necesita
- Sin eventos de dominio en SP3 (opcionales según la spec, se añaden en SP4 para Notificaciones)
