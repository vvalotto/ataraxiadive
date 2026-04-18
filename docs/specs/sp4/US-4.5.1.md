# US-4.5.1: Aggregate `Notificacion` — ciclo de vida e idempotencia

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.5
**Bounded Context**: `notificaciones`
**Capas afectadas**: `notificaciones/domain/aggregates/`, `notificaciones/domain/events/`, `notificaciones/domain/value_objects/`, `notificaciones/domain/ports/`, `notificaciones/infrastructure/event_store/`

---

## Descripción

Como **sistema**,
quiero **un aggregate `Notificacion` con ciclo de vida persistido en event store propio**
para **garantizar idempotencia estructural exactly-once: un mismo evento fuente nunca
dispara dos notificaciones**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Notificacion` | Ciclo de vida: Solicitada → Enviada \| Fallida; rechaza envíos duplicados |
| Value Object | `NotificacionId` | UUID inmutable del aggregate |
| Value Object | `EventoFuenteId` | UUID del evento de dominio que originó la solicitud (clave de idempotencia) |
| Value Object | `Destinatario` | Email + nombre del destinatario |
| Value Object | `ContenidoEmail` | Asunto + cuerpo (texto plano y/o HTML) |
| Value Object | `CanalEnvio` | Enum: `Email` \| `Push` (SP4 implementa solo `Email`) |
| Port | `NotificacionRepository` | Lectura del event store para rehidratación |
| Port | `EmailPort` | Envío de email — definido en domain, implementado en infrastructure |
| Event | `NotificacionSolicitada` | Primera transición — captura todos los datos necesarios |
| Event | `NotificacionEnviada` | Confirmación de entrega al canal externo |
| Event | `NotificacionFallida` | Fallo definitivo con `motivo` |

### Lenguaje ubicuo relevante

- **Idempotencia exactly-once:** un evento fuente (`evento_fuente_id`) produce como máximo una notificación enviada. La garantía es estructural: el aggregate verifica en el event store antes de aceptar el comando.
- **Rehidratación:** el aggregate se reconstruye leyendo todos sus eventos desde el store — mismo patrón que `Performance` en BC Competencia.
- **Notificación duplicada:** solicitud de envío con un `evento_fuente_id` que ya tiene un `NotificacionEnviada` en el store → el aggregate la rechaza silenciosamente (no lanza error, simplemente no emite nuevos eventos).

---

## Especificación del comportamiento

### Invariantes

- **INV-4.5.1-01:** `SolicitarEnvio` con un `evento_fuente_id` que ya tiene `NotificacionEnviada` en el store → el aggregate no emite nuevos eventos (idempotencia).
- **INV-4.5.1-02:** `SolicitarEnvio` con un `evento_fuente_id` que tiene `NotificacionFallida` → se permite reintentar (fallo definitivo ≠ éxito — no aplica idempotencia).
- **INV-4.5.1-03:** `NotificacionEnviada` y `NotificacionFallida` son estados terminales — ningún comando adicional es válido después de alcanzarlos.
- **INV-4.5.1-04:** `Destinatario` debe tener email válido (formato `@`). El aggregate rechaza destinatarios malformados.
- **INV-4.5.1-05:** `ContenidoEmail` debe tener `asunto` no vacío. El aggregate rechaza contenido sin asunto.

### Ciclo de vida del aggregate

```
[nuevo]
   │
   ▼
NotificacionSolicitada
   │
   ├── envío exitoso → NotificacionEnviada   [terminal]
   │
   └── error de canal  → NotificacionFallida [terminal — reintentable desde outside]
```

### Operaciones del aggregate

#### `SolicitarEnvio(evento_fuente_id, destinatario, contenido, canal)`

| | Descripción |
|---|---|
| **Precondición** | `evento_fuente_id` no tiene `NotificacionEnviada` previa en el store para este aggregate |
| **Postcondición** | Se emite `NotificacionSolicitada` con todos los datos de envío |
| **Idempotencia** | Si `NotificacionEnviada` ya existe → no se emite ningún evento, operación silenciosa |

**Ejemplo concreto:**

```
Solicitud: evento_fuente_id=abc-123, destinatario=juan@example.com, canal=Email
Verificación store: no existe NotificacionEnviada con evento_fuente_id=abc-123
→ emite: NotificacionSolicitada { id: uuid, evento_fuente_id: abc-123, destinatario: ..., contenido: ..., canal: Email }

Segunda solicitud con mismo evento_fuente_id=abc-123:
Verificación store: existe NotificacionEnviada con evento_fuente_id=abc-123
→ no emite ningún evento (idempotencia)
```

#### `RegistrarEnvioExitoso()`

| | Descripción |
|---|---|
| **Precondición** | Estado actual: `Solicitada` |
| **Postcondición** | Se emite `NotificacionEnviada`; aggregate en estado terminal |

#### `RegistrarFallo(motivo)`

| | Descripción |
|---|---|
| **Precondición** | Estado actual: `Solicitada` |
| **Postcondición** | Se emite `NotificacionFallida` con `motivo`; aggregate en estado terminal |
| **Nota** | El fallo es definitivo para esta instancia. El application layer decide si reintenta creando una nueva solicitud. |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.5.1 — Aggregate Notificacion con idempotencia

  Scenario: solicitud de envío nueva
    Given el event store no tiene eventos para evento_fuente_id "reg-001"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-001" y destinatario "juan@example.com"
    Then el aggregate emite NotificacionSolicitada
    And el evento persiste en el event store de notificaciones

  Scenario: idempotencia — solicitud duplicada con NotificacionEnviada previa
    Given el event store tiene NotificacionEnviada para evento_fuente_id "reg-001"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-001"
    Then el aggregate no emite ningún evento
    And no se realiza ningún envío al canal externo

  Scenario: reintento permitido tras fallo
    Given el event store tiene NotificacionFallida para evento_fuente_id "reg-002"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-002" y nuevos datos de destinatario
    Then el aggregate emite NotificacionSolicitada (reintento permitido)

  Scenario: destinatario con email inválido
    When se ejecuta SolicitarEnvio con destinatario email "no-es-un-email"
    Then el aggregate lanza error de validación de dominio
    And no emite ningún evento

  Scenario: registro de envío exitoso
    Given el aggregate está en estado Solicitada
    When se ejecuta RegistrarEnvioExitoso
    Then el aggregate emite NotificacionEnviada
    And el estado es terminal — no acepta más comandos

  Scenario: registro de fallo definitivo
    Given el aggregate está en estado Solicitada
    When se ejecuta RegistrarFallo con motivo "SMTP connection refused"
    Then el aggregate emite NotificacionFallida con el motivo
    And el estado es terminal
```

---

## Impacto arquitectónico

- [ ] No → no requiere cambios fuera del BC Notificaciones

**Event store:** tabla `notificaciones_events` en `notificaciones.db` (SQLite propio del BC).
Mismo patrón que `events` en `competencia.db`.

```sql
CREATE TABLE notificaciones_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE INDEX idx_notificaciones_stream ON notificaciones_events(stream_id);
CREATE INDEX idx_notificaciones_fuente ON notificaciones_events(
    json_extract(payload, '$.evento_fuente_id')
);
```

**Stream ID:** `notificacion-{notificacion_id}` — un stream por aggregate.

**Búsqueda de idempotencia:**
```sql
SELECT 1 FROM notificaciones_events
WHERE event_type = 'NotificacionEnviada'
  AND json_extract(payload, '$.evento_fuente_id') = ?
```

**Capa(s) afectadas:**
- [x] Domain — `notificaciones/domain/aggregates/notificacion.py`
- [x] Domain — `notificaciones/domain/events/` (3 eventos)
- [x] Domain — `notificaciones/domain/value_objects/` (NotificacionId, EventoFuenteId, Destinatario, ContenidoEmail, CanalEnvio)
- [x] Domain — `notificaciones/domain/ports/notificacion_repository.py`
- [x] Domain — `notificaciones/domain/ports/email_port.py`
- [x] Infrastructure — `notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py`

---

## Referencias

- Prerrequisitos: ninguno
- ADR-005: justificación Event Sourcing en Notificaciones (idempotencia estructural)
- Context Map §3.6: relación downstream de Notificaciones con todos los BCs
- Plan SP4 §INC-4.5: descripción del incremento

---

*Redactado: 2026-04-14 — INC-4.5 BC Notificaciones*
