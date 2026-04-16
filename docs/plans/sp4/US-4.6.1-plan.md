# Plan de Implementacion: US-4.6.1 - API de audit log

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.6  
**Bounded Context:** `competencia`  
**Patron:** `hexagonal-ddd-bc`  
**Estimacion total:** 2h 20min  
**Estado:** Pendiente de aprobacion

## Objetivo

Exponer un endpoint de solo lectura para que un organizador consulte la secuencia
cronologica de eventos de una performance individual, reutilizando el event store
como fuente del audit log oficial.

## Componentes a ajustar

### 1. Application - query especifica de audit log

- [ ] `src/competencia/application/queries/obtener_audit_log.py` (30 min)
  - Definir `AuditLogEventoDTO` y `ObtenerAuditLogQuery`
  - Implementar `ObtenerAuditLogHandler`
  - Filtrar por stream de una performance puntual
  - Mantener orden cronologico estricto por `sequence`
  - Fallar con caso explicito cuando la performance no exista

### 2. Infrastructure - lectura puntual desde event store

- [ ] `src/shared/infrastructure/event_store/sqlite_event_store.py` (20 min)
  - Agregar metodo de lectura ordenada para un stream individual con `sequence`
  - Evitar duplicar consultas ad hoc en application
  - Preservar compatibilidad con `load()` y `load_all_events_ordered()`

### 3. API - endpoint REST audit log

- [ ] `src/competencia/api/router.py` (25 min)
  - Agregar `GET /competencias/{competencia_id}/performances/{atleta_id}/audit-log`
  - Cablear dependencia del nuevo handler
  - Mapear respuesta a contrato de la spec
  - Retornar `404` si no existe la performance

- [ ] `src/competencia/api/schemas.py` o respuesta inline (10 min)
  - Evaluar si conviene schema dedicado para la respuesta del audit log
  - Mantener consistencia con el estilo actual del BC

### 4. Seguridad y autorizacion

- [ ] Revisar dependencias de autenticacion/autorizacion existentes (15 min)
  - Verificar como se resuelve rol `organizador` / `admin`
  - Reutilizar mecanismo existente en lugar de introducir uno nuevo
  - Si no existe enforcement real en router, documentar gap y aplicar minimo viable consistente

### 5. Tests

- [ ] `tests/integration/competencia/test_audit_log_api.py` (25 min)
  - Caso nominal con 3 eventos
  - Caso con correccion historica
  - Caso 404 por performance inexistente
  - Caso 403 para rol juez si la capa actual lo soporta

- [ ] `tests/unit/competencia/test_obtener_audit_log.py` (15 min)
  - Orden cronologico
  - Mapeo de DTO
  - Error cuando no hay stream

### 6. Validacion

- [ ] Ejecutar tests unitarios y de integracion de `competencia` (10 min)
- [ ] Ejecutar BDD relevante o dejar waiver si el harness actual no cubre este endpoint (5 min)
- [ ] Ejecutar quality gates del BC (`codeguard` o suite equivalente local) (10 min)

## Dependencias y decisiones

- Reutilizar el event store SQLite ya existente; no crear tabla nueva de auditoria.
- No mezclar auditoria de competencia completa con auditoria de performance: esta US es por stream individual.
- Mantener compatibilidad con el endpoint legado `GET /competencias/{competencia_id}/events`.
- La seguridad depende del wiring actual de identidad en FastAPI; validar primero antes de codificar.

## Riesgos

- El modelo actual identifica `performance_id` por `atleta_id` en varios puntos; hay que confirmar el contrato exacto antes de implementar.
- El endpoint legado expone `event_type`; la spec nueva usa `tipo`. Hay que decidir adaptacion de payload sin romper consistencia.
- La autorizacion por rol puede estar parcial en algunos routers; si falta, hay que aplicar la solucion mas pequena coherente con SP4.

## Checklist de salida

- [ ] Endpoint observable responde el contrato de `US-4.6.1`
- [ ] Tests nominales y de error en verde
- [ ] No se rompen endpoints existentes de `competencia`
- [ ] Reporte final y trazabilidad quedan listos para fases posteriores

*Plan generado: 2026-04-16 - US-4.6.1 INC-4.6 SP4*
