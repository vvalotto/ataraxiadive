# Plan de Implementacion: US-4.6.2 - Hash SHA-256 al cierre de disciplina

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.6  
**Bounded Context:** `competencia`  
**Patron:** `hexagonal-ddd-bc`  
**Estimacion total:** 3h 10min  
**Estado:** Pendiente de aprobacion

## Objetivo

Extender el cierre de disciplina para que el evento `CompetenciaFinalizada`
persista un `hash_sha256` calculado sobre la secuencia canonica de eventos de la
disciplina, reforzando la integridad post-cierre sin introducir infraestructura
adicional fuera del event store actual.

## Componentes a ajustar

### 1. Domain - servicio de hash e invariantes de cierre

- [ ] `src/competencia/domain/services/calculador_hash_competencia.py` o modulo equivalente (25 min)
  - Implementar calculo SHA-256 puro con `hashlib`
  - Serializar eventos a JSON canonico con claves ordenadas
  - Cubrir caso del conjunto vacio

- [ ] `src/competencia/domain/events/competencia_finalizada.py` (20 min)
  - Agregar campo `hash_sha256`
  - Extender `to_payload()` y `from_payload()`

- [ ] `src/competencia/domain/aggregates/competencia.py` (25 min)
  - Extender `finalizar()` para recibir `hash_sha256`
  - Persistirlo dentro de `CompetenciaFinalizada`
  - Mantener invariantes actuales de `CompetenciaNoFinalizable`

### 2. Application - politica P-08 de finalizacion

- [ ] `src/competencia/application/_p08_finalizacion.py` (30 min)
  - Recuperar los eventos de la disciplina antes de emitir `CompetenciaFinalizada`
  - Filtrar solo streams `performance-{competencia_id}-*` de la disciplina actual
  - Calcular hash canonico y pasarlo al aggregate `Competencia`
  - Confirmar que el cierre automatico sigue disparando callback P-09

### 3. Infrastructure - soporte de lectura para hashing

- [ ] Revisar `SQLiteEventStore` / `EventStorePort` (20 min)
  - Evaluar si alcanza con `load_all_events_ordered(prefix)`
  - Si hace falta, agregar helper de lectura plana por prefijo/disciplina
  - Evitar introducir duplicacion de consultas SQL en application

### 4. Tests

- [ ] `tests/unit/competencia/domain/test_competencia_finalizar.py` (20 min)
  - `CompetenciaFinalizada` incluye `hash_sha256`
  - hash del conjunto vacio
  - reconstitucion con hash

- [ ] `tests/unit/competencia/domain/test_calculador_hash_competencia.py` (20 min)
  - determinismo
  - cambio ante alteracion de evento
  - orden canonico estable

- [ ] `tests/unit/competencia/application/test_p08_finalizacion.py` (20 min)
  - P-08 persiste `CompetenciaFinalizada` con hash
  - no finaliza si quedan pendientes

- [ ] `tests/integration/competencia/test_competencia_finalizada_integration.py` (25 min)
  - payload real con `hash_sha256`
  - hash de 64 hex
  - caso de disciplina vacia si el flujo actual lo soporta

### 5. Validacion

- [ ] Ejecutar pytest focalizado de domain + application + integration (10 min)
- [ ] Ejecutar quality gate focalizado con `codeguard` sobre archivos tocados (10 min)
- [ ] Evaluar si corresponde waiver de BDD automatizado, igual que en `US-4.6.1` (5 min)

## Dependencias y decisiones

- `US-4.6.2` depende de la politica P-08 ya existente; no introduce un comando manual nuevo.
- El nombre del evento sigue siendo `CompetenciaFinalizada`; la US extiende su payload.
- El hash debe tomar solo los eventos de la disciplina que cierra, no el stream completo de competencia.
- La secuencia canonica se calcula sobre la lectura ordenada global del event store, no por version local de stream.

## Riesgos

- Hoy P-08 finaliza automaticamente desde `AsignarTarjetaHandler` y `RegistrarDNSHandler`; cualquier cambio puede romper `US-2.4.1` y `US-2.4.2`.
- El filtro por disciplina necesita respetar el formato real del `stream_id` de performance.
- Si el hash se calcula despues de persistir `CompetenciaFinalizada`, puede quedar autorreferencial; debe calcularse antes.

## Checklist de salida

- [ ] `CompetenciaFinalizada` persiste `hash_sha256`
- [ ] El hash es determinista y de 64 hex
- [ ] No se rompe el cierre automatico actual de P-08
- [ ] Tests focalizados y quality gate en verde

*Plan generado: 2026-04-16 - US-4.6.2 INC-4.6 SP4*
