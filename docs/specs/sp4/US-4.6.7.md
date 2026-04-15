# US-4.6.7: Documentación de arquitectura — Notificaciones

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Tipo**: Documentación de arquitectura y diseño
**Artefactos producidos**: `docs/design/notificaciones.md` · `docs/adr/ADR-016-resend-email-provider.md` · `docs/adr/ADR-017-notificaciones-event-sourcing.md`

---

## Descripción

Como **equipo de desarrollo y futuros colaboradores**,
quiero **documentación completa del diseño del BC Notificaciones implementado en INC-4.5**
para **entender la arquitectura exactly-once, el modelo de políticas, la decisión de Event Sourcing en un BC genérico, y las restricciones que cualquier nueva notificación debe respetar**.

---

## Contexto

INC-4.5 implementó el BC Notificaciones completo: aggregate, event store, adaptador email, políticas P-10 y P-11, y cableado en `src/app.py`. Las decisiones de diseño (Event Sourcing para idempotencia, Resend como proveedor) fueron tomadas durante la implementación y no tienen ADRs formales. Esta US las formaliza.

**ADRs existentes relacionados:**
- Ninguno específico de Notificaciones. ADR-001 cubre Event Sourcing en Competencia, pero no justifica su uso en un BC genérico.

**Decisiones a formalizar:**
1. **Resend** como proveedor de email (vs SendGrid, SES, SMTP directo)
2. **Event Sourcing en BC Notificaciones** — motivación: idempotencia estructural, no por complejidad del dominio

---

## Especificación — qué debe contener la documentación

### ADR-016 — Resend como proveedor de email

**Contexto a documentar:**
- BC Notificaciones requiere envío de email transaccional real
- Opciones consideradas: SMTP propio, SendGrid, Amazon SES, Resend
- Decisión: Resend

**Contenido mínimo del ADR:**

| Sección | Contenido |
|---------|-----------|
| Contexto | Requisito de email transaccional; proyecto en fase de desarrollo sin dominio propio |
| Opciones | SMTP directo · SendGrid · Amazon SES · Resend |
| Decisión | Resend |
| Justificación | API simple (una sola llamada HTTP), sandbox `onboarding@resend.dev` sin verificar dominio, SDK Python oficial, pricing adecuado para el volumen esperado |
| Consecuencias positivas | Onboarding inmediato (sin verificación de dominio en sandbox), logs en dashboard, webhooks disponibles para futuros eventos de entrega |
| Consecuencias negativas | Vendor lock-in leve (el `EmailPort` abstrae esto — cambiar proveedor es cambiar el adaptador) |
| Notas de configuración | `RESEND_API_KEY` en `.env`; `NOTIFICACIONES_EMAIL_FROM` configurable; el `LoggingEmailAdapter` como fallback en dev cuando no hay key |

---

### ADR-017 — Event Sourcing en BC Notificaciones

**Contexto a documentar:**
- BC Notificaciones es genérico, sin lógica de dominio compleja
- Normalmente un BC genérico usa CRUD — ¿por qué ES aquí?

**Contenido mínimo del ADR:**

| Sección | Contenido |
|---------|-----------|
| Contexto | Notificaciones requiere garantía exactly-once: no enviar dos veces el mismo email ante reintentos del handler o reinicios del servidor |
| Problema | Sin ES: para garantizar idempotencia necesitaría una tabla de "notificaciones enviadas" con lógica ad-hoc de deduplicación |
| Decisión | Event Sourcing en BC Notificaciones |
| Justificación | El event store ya resuelve el problema: antes de enviar, consultar si `NotificacionEnviada` ya existe para ese `evento_fuente_id`. El aggregate encapsula esta lógica. La infraestructura (event store SQLite de ADR-008) ya existe en el proyecto. |
| Alternativa descartada | CRUD con tabla `notificaciones_enviadas`: más simple en la infra, pero lógica de idempotencia ad-hoc y sin audit trail natural |
| Consecuencias | El BC Notificaciones usa la misma infraestructura de event store que Competencia — bajo overhead. El aggregate `Notificacion` es simple (3 estados, 3 eventos) pero el patrón escala si se agregan nuevos canales (Push, SMS) |
| Trade-off explícito | ES en un BC genérico es inusual — se justifica únicamente por el requisito de idempotencia. No es una decisión de "usar ES siempre". |

---

### docs/design/notificaciones.md — Documento nuevo

El documento debe cubrir los siguientes bloques:

**1. Rol del BC Notificaciones en el sistema**
- BC genérico: no tiene lógica de negocio de apnea
- Consumidor de eventos de otros BCs (Registro, Competencia)
- Responsabilidad única: garantizar que cada notificación se envía exactamente una vez

**2. Modelo de dominio del BC**

```
Aggregate: Notificacion
  Estados: Solicitada → Enviada | Fallida

  Eventos:
    NotificacionSolicitada { id, evento_fuente_id, destinatario, contenido, canal }
    NotificacionEnviada    { id, timestamp_envio, proveedor_response_id }
    NotificacionFallida    { id, motivo }

  Invariante de idempotencia (INV-4.5.1-01):
    Si existe NotificacionEnviada para evento_fuente_id → ignorar nueva solicitud
```

**3. El modelo de políticas**

Diagrama del patrón Policy:

```
[Evento de dominio externo]
        │
        ▼
[Política Pn]  ← escucha el evento, orquesta los handlers
        │
        ├──► SolicitarEnvioHandler  → crea Notificacion en estado Solicitada
        │
        └──► EnviarNotificacionHandler → llama EmailPort → emite Enviada o Fallida
```

- P-10: `InscripcionConfirmada` → email al atleta
- P-11: `TarjetaAsignada(roja)` → email al atleta (motivo DQ)
- Cómo agregar una nueva política: el patrón, el archivo donde registrarla en `app.py`

**4. Garantía exactly-once**

Diagrama de secuencia mostrando el flujo normal y el flujo idempotente (segundo disparo del mismo evento):

```
Primer disparo:
  evento_fuente_id="evt-001"
  → SolicitarEnvio → [event store vacío para evt-001] → NotificacionSolicitada ✓
  → EnviarNotificacion → email enviado → NotificacionEnviada ✓

Segundo disparo (mismo evt-001):
  → SolicitarEnvio → [event store tiene NotificacionEnviada para evt-001] → SKIP ✓
  → No se envía segundo email
```

**5. Adaptadores de email y configuración**

- `ResendEmailAdapter` — producción y smoke test (requiere `RESEND_API_KEY`)
- `LoggingEmailAdapter` — desarrollo local (fallback automático sin key)
- Cómo el puerto `EmailPort` abstrae el proveedor
- Variables de entorno necesarias

**6. Límites del diseño**
- Solo email en INC-4.5. Push/SMS son extensiones futuras (SP5)
- El bus de eventos es in-process síncrono (SP4). En SP5 evaluar bus asíncrono
- Las políticas se registran en `app.py` — si el proceso cae, el evento se pierde (SP4). En SP5: outbox pattern o bus persistente

**7. Evolución futura**
- Nuevos canales: agregar adaptador nuevo que implementa `EmailPort` (o `PushPort`)
- Nuevas políticas: seguir el patrón P-10/P-11
- Bus asíncrono: reemplazar el call directo en `app.py` por un dispatcher desacoplado

---

## Criterios de aceptación

```gherkin
Feature: US-4.6.7 — Documentación BC Notificaciones

  Scenario: ADR-016 creado y completo
    Given el ADR-016 creado en docs/adr/
    Then documenta la decisión de Resend con contexto, opciones, justificación y consecuencias
    And menciona el LoggingEmailAdapter como fallback de desarrollo
    And está relacionado con US-4.5.2

  Scenario: ADR-017 creado y completo
    Given el ADR-017 creado en docs/adr/
    Then justifica el uso de ES en un BC genérico exclusivamente por idempotencia
    And documenta explícitamente el trade-off (ES en BC genérico es inusual)
    And está relacionado con ADR-001 y US-4.5.1

  Scenario: docs/design/notificaciones.md existe y es completo
    Given el documento creado
    Then contiene los 7 bloques especificados
    And incluye el diagrama del aggregate Notificacion con sus estados y eventos
    And incluye el diagrama del patrón Policy (P-10, P-11)
    And incluye el diagrama de secuencia exactly-once (flujo normal + idempotente)
    And describe cómo agregar una nueva política
```

---

## Impacto arquitectónico

No aplica — esta US produce solo documentación. No modifica código.

**Artefactos a producir:**
1. `docs/adr/ADR-016-resend-email-provider.md`
2. `docs/adr/ADR-017-notificaciones-event-sourcing.md`
3. `docs/design/notificaciones.md`

---

## Referencias

- US-4.5.1 (aggregate Notificacion), US-4.5.2 (adaptador email), US-4.5.3 (P-10), US-4.5.4 (P-11), US-4.5.5 (cableado)
- ADR-001: Event Sourcing en Competencia (referencia para contraste)
- ADR-008: event store SQLite (infraestructura compartida)
- `src/notificaciones/` — código fuente a documentar
- `src/app.py` — registro de políticas

---

*Redactado: 2026-04-15 — INC-4.6 documentación transversal*
