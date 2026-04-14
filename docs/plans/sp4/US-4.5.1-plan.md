# Plan de Implementación: US-4.5.1 - Aggregate Notificacion

**Sprint:** SP4 - La Plataforma
**Incremento:** INC-4.5
**Bounded Context:** `notificaciones`
**Patrón:** Hexagonal DDD BC-first + Event Sourcing
**Estimación total:** 3h 20min

## Objetivo

Implementar el aggregate `Notificacion` con ciclo de vida `Solicitada -> Enviada | Fallida`,
persistencia en event store propio del BC y chequeo de idempotencia estructural por
`evento_fuente_id`.

## Decisiones de diseño

- Se implementará un event store propio en `notificaciones/infrastructure/event_store/`.
  Motivo: la US exige tabla `notificaciones_events` e indexación por `evento_fuente_id`,
  mientras que `shared.infrastructure.event_store.SQLiteEventStore` hoy asume tabla
  genérica `events` y no expone helpers de idempotencia.
- La validación de duplicados no vivirá en `application/`: se resolverá vía puerto
  `NotificacionRepository` para preservar la regla de idempotencia como parte del
  comportamiento estructural del aggregate.
- `EmailPort` se definirá ahora por consistencia del modelo, pero quedará como contrato
  sin implementación concreta hasta `US-4.5.2`.
- Se usará `str` para `EventoFuenteId` en esta US, aunque la spec lo describe como UUID.
  Motivo: `US-4.5.4` ya anticipa claves compuestas `"{evento}:{atleta_id}"`. El VO
  preservará inmutabilidad y validación semántica sin encerrar la implementación en UUID
  puro.

## Componentes a implementar

### 1. Dominio - Value Objects

- [ ] `src/notificaciones/domain/value_objects/notificacion_id.py` (10 min)
  - VO UUID para `NotificacionId`
- [ ] `src/notificaciones/domain/value_objects/evento_fuente_id.py` (10 min)
  - VO inmutable para clave de idempotencia
- [ ] `src/notificaciones/domain/value_objects/destinatario.py` (15 min)
  - valida email y nombre opcional
- [ ] `src/notificaciones/domain/value_objects/contenido_email.py` (15 min)
  - valida asunto no vacio y cuerpo disponible
- [ ] `src/notificaciones/domain/value_objects/canal_envio.py` (5 min)
  - enum `Email | Push`
- [ ] actualizar `src/notificaciones/domain/value_objects/__init__.py` (5 min)

### 2. Dominio - Eventos

- [ ] `src/notificaciones/domain/events/notificacion_solicitada.py` (15 min)
- [ ] `src/notificaciones/domain/events/notificacion_enviada.py` (15 min)
- [ ] `src/notificaciones/domain/events/notificacion_fallida.py` (15 min)
- [ ] actualizar `src/notificaciones/domain/events/__init__.py` (5 min)

### 3. Dominio - Aggregate y puertos

- [ ] `src/notificaciones/domain/ports/notificacion_repository.py` (15 min)
  - `load(stream_id)`, `append(...)`, `exists_success_by_evento_fuente_id(...)`
- [ ] `src/notificaciones/domain/ports/email_port.py` (10 min)
  - contrato base para siguiente US
- [ ] `src/notificaciones/domain/aggregates/notificacion.py` (35 min)
  - crear solicitud
  - registrar envio exitoso
  - registrar fallo
  - reconstitucion desde stream
  - bloqueo terminal
  - no emision de eventos si ya existe exito previo
- [ ] actualizar `src/notificaciones/domain/ports/__init__.py` y `src/notificaciones/domain/aggregates/__init__.py` (5 min)

### 4. Infraestructura - Event Store propio

- [ ] `src/notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py` (35 min)
  - crear tabla `notificaciones_events` si no existe
  - append/load por stream
  - consulta de exito previo por `evento_fuente_id`
  - indice por `stream_id` y `json_extract(payload, '$.evento_fuente_id')`
- [ ] `src/notificaciones/infrastructure/repositories/sqlite_notificacion_repository.py` (20 min)
  - adapter de infraestructura al puerto de dominio
- [ ] actualizar exports en `src/notificaciones/infrastructure/event_store/__init__.py`
  y `src/notificaciones/infrastructure/repositories/__init__.py` (5 min)

### 5. Tests unitarios

- [ ] `tests/unit/notificaciones/domain/test_value_objects.py` (20 min)
  - email invalido
  - asunto vacio
  - VO ids
- [ ] `tests/unit/notificaciones/domain/test_notificacion.py` (30 min)
  - solicitud nueva
  - terminalidad
  - reintento tras fallo previo rehidratado
  - rechazo de destinatario invalido
  - idempotencia sin emitir eventos cuando repo informa envio exitoso previo

### 6. Tests de integración

- [ ] `tests/integration/notificaciones/test_sqlite_notificacion_repository.py` (30 min)
  - persistencia de eventos
  - rehidratacion desde stream
  - deteccion de `NotificacionEnviada` por `evento_fuente_id`
  - independencia de streams en mismo store

### 7. BDD y validación

- [ ] `tests/features/steps/notificacion_idempotencia_steps.py` (30 min)
  - steps para los 6 escenarios de la feature
- [ ] ejecutar pytest unitario + integración + BDD focalizado (10 min)
- [ ] ejecutar CodeGuard sobre `src/notificaciones` (5 min)

### 8. Documentación y reporte

- [ ] actualizar `docs/design/domain-model.md` con aggregate, VOs y eventos de notificaciones (10 min)
- [ ] crear `docs/reports/US-4.5.1-report.md` (10 min)

## Riesgos a vigilar

- La spec habla de chequeo en el aggregate "contra el store", pero el aggregate no debe
  depender de infraestructura. Se resolverá inyectando la decisión desde un puerto o
  factory de creación, manteniendo la garantía estructural sin romper hexagonalidad.
- `EventoFuenteId` debe quedar preparado para `US-4.5.4`, donde la clave no será un UUID
  puro sino compuesta.
- No se implementará envío real todavía; cualquier referencia al canal externo debe quedar
  sólo como contrato y no contaminar esta US.

## Criterio de cierre de la US

- Aggregate `Notificacion` funcional y rehidratable
- Persistencia ES real en SQLite del BC Notificaciones
- Idempotencia por `evento_fuente_id` verificada por tests
- Feature BDD automatizada en verde
- Reporte final de US generado en disco
