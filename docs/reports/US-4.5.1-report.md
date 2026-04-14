# Reporte de Implementación — US-4.5.1
## Aggregate `Notificacion` — ciclo de vida e idempotencia

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.5  
**Branch:** `feature/US-4.5.1-notificacion-idempotencia`  
**Fecha:** 2026-04-14

---

## Resumen

Se implementó el núcleo del BC `notificaciones` con Event Sourcing propio:

- aggregate `Notificacion`
- value objects del dominio
- eventos `NotificacionSolicitada`, `NotificacionEnviada` y `NotificacionFallida`
- event store SQLite específico del BC sobre tabla `notificaciones_events`
- repositorio con consulta de idempotencia por `evento_fuente_id`

La idempotencia queda resuelta de forma estructural: si el repositorio detecta una
`NotificacionEnviada` previa para un `evento_fuente_id`, la operación de solicitud no
crea aggregate ni emite nuevos eventos.

---

## Cambios implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/notificaciones/domain/aggregates/notificacion.py` | Aggregate con rehidratación, transición `Solicitada -> Enviada/Fallida` y terminalidad |
| `src/notificaciones/domain/events/*.py` | Tres eventos de dominio del ciclo de vida |
| `src/notificaciones/domain/value_objects/*.py` | `NotificacionId`, `EventoFuenteId`, `Destinatario`, `ContenidoEmail`, `CanalEnvio` |
| `src/notificaciones/domain/ports/notificacion_repository.py` | Puerto de persistencia e idempotencia |
| `src/notificaciones/domain/ports/email_port.py` | Contrato para el canal email a usar en `US-4.5.2` |
| `src/notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py` | Event store SQLite propio con tabla `notificaciones_events` e índice por `evento_fuente_id` |
| `src/notificaciones/infrastructure/repositories/sqlite_notificacion_repository.py` | Adaptador al puerto de repositorio |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/unit/notificaciones/domain/test_value_objects.py` | Validaciones de VOs |
| `tests/unit/notificaciones/domain/test_notificacion.py` | Solicitud, terminalidad, idempotencia y reintento |
| `tests/integration/notificaciones/test_sqlite_notificacion_repository.py` | Persistencia real, rehidratación y búsqueda por `evento_fuente_id` |
| `tests/features/US-4.5.1-notificacion-idempotencia.feature` | Escenarios BDD de la US |
| `tests/features/steps/notificacion_idempotencia_steps.py` | Steps automatizados sobre SQLite real |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp4/US-4.5.1-plan.md` | Plan aprobado de implementación |
| `docs/design/domain-model.md` | BC Notificaciones actualizado al estado real de `US-4.5.1` |

---

## Decisiones de diseño

### 1. Event store propio del BC

No se reutilizó `shared.infrastructure.event_store.SQLiteEventStore` porque la US exige:

- tabla específica `notificaciones_events`
- indexación por `json_extract(payload, '$.evento_fuente_id')`
- consulta explícita para idempotencia por evento fuente

Esto deja al BC preparado para evolucionar sin forzar abstracciones prematuras en el
store compartido.

### 2. `EventoFuenteId` como VO basado en `str`

Aunque la spec lo describe como UUID, se implementó como VO inmutable sobre `str`.
Motivo: `US-4.5.4` requiere claves compuestas del tipo `"{evento}:{atleta_id}"`.
La decisión evita rediseñar el VO en la siguiente US.

### 3. `EmailPort` se define ahora pero no se usa aún

`US-4.5.1` sólo implementa el ciclo de vida y la persistencia del aggregate.
El envío real queda desacoplado y pendiente para `US-4.5.2`.

---

## Resultados de calidad

### Pytest focalizado

Comando ejecutado:

```bash
./.venv/bin/pytest tests/features/steps/notificacion_idempotencia_steps.py \
  tests/unit/notificaciones/domain/test_value_objects.py \
  tests/unit/notificaciones/domain/test_notificacion.py \
  tests/integration/notificaciones/test_sqlite_notificacion_repository.py -q
```

Resultado:

```text
18 passed in 0.22s
```

### CodeGuard

Comando ejecutado:

```bash
./.venv/bin/codeguard src/notificaciones
```

Resultado:

```text
0 errores
0 advertencias
```

---

## Estado respecto de la spec

### Cumplido

- aggregate `Notificacion` con ciclo `Solicitada -> Enviada/Fallida`
- eventos persistidos en event store propio del BC
- rehidratación desde stream
- idempotencia por `evento_fuente_id`
- reintento permitido tras fallo previo
- validación de destinatario y contenido
- estados terminales bloqueando comandos posteriores

### Diferencia menor respecto de la redacción original

- La validación de duplicado se decide con información provista por repositorio en el
  momento de `solicitar_envio`, en lugar de hacer que el aggregate consulte infraestructura
  directamente. La garantía sigue siendo estructural, pero sin romper la arquitectura
  hexagonal.

---

## Riesgos y próximos pasos

- `US-4.5.2` debe introducir el adaptador concreto de `EmailPort` para habilitar
  envío real a un proveedor gestionado.
- `US-4.5.3` debe introducir el handler/política de aplicación para orquestar
  rehidratación, llamada a `EmailPort` y persistencia de `NotificacionEnviada/Fallida`.
- `US-4.5.3` y `US-4.5.4` siguen bloqueadas por la ausencia de sus eventos fuente reales
  (`InscripcionConfirmada`, `ResultadosPublicados`) en los BC productores.
- Si en el futuro más BCs requieren índices por payload en sus event stores, convendrá
  evaluar una abstracción compartida de event store con hooks de schema específicos por BC.
