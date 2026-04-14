# US-4.5.3: Política P-10 — email de confirmación de inscripción al atleta

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.5
**Bounded Context**: `notificaciones` (consumidor) · `registro` (productor del evento)
**Capas afectadas**: `notificaciones/application/`, `src/app.py`

---

## Descripción

Como **atleta**,
quiero **recibir un email de confirmación cuando mi inscripción al torneo sea procesada**
para **tener evidencia de que estoy anotado y conocer los datos del evento**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Evento fuente | `InscripcionConfirmada` | Emitido por BC Registro al confirmar la inscripción de un atleta |
| Policy | P-10 | Al recibir `InscripcionConfirmada` → ejecutar `SolicitarEnvio` + `EnviarNotificacion` |
| Command | `SolicitarEnvio` | Crea el aggregate `Notificacion` en estado Solicitada |
| Command | `EnviarNotificacion` | Envía el email y registra el resultado en el aggregate |
| Plantilla | `InscripcionConfirmadaTemplate` | Contenido del email: asunto, cuerpo con datos del torneo |

### Lenguaje ubicuo relevante

- **Política P-10:** regla de negocio que conecta el evento `InscripcionConfirmada` con la notificación al atleta. Es una política del dominio, no lógica de infraestructura.
- **`evento_fuente_id`:** es el `id` del evento `InscripcionConfirmada`. Clave de idempotencia en el aggregate `Notificacion` (INV-4.5.1-01).
- **Inscripción confirmada:** el atleta tiene su inscripción aceptada (pago verificado o torneo abierto sin pago requerido). BC Registro emite el evento.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.5.3-01:** Por cada `InscripcionConfirmada` se ejecuta P-10 exactamente una vez. Si el handler se ejecuta dos veces para el mismo evento (restart, retry), el aggregate garantiza idempotencia (INV-4.5.1-01).
- **INV-4.5.3-02:** El email contiene como mínimo: nombre del atleta, nombre del torneo, fecha del torneo, disciplina(s) inscriptas.
- **INV-4.5.3-03:** Si el email del atleta no está disponible en el payload del evento, la notificación se crea en estado `Fallida` con motivo `"destinatario_sin_email"`. No se lanza excepción que interrumpa el flujo del sistema.
- **INV-4.5.3-04:** Un fallo en el envío del email (proveedor externo) no interrumpe ni revierte la inscripción. El fallo queda registrado en el event store de Notificaciones.

### Política P-10: `InscripcionConfirmada` → email al atleta

| | Descripción |
|---|---|
| **Trigger** | Evento `InscripcionConfirmada` recibido desde BC Registro |
| **Precondición** | El evento contiene `atleta_email`, `atleta_nombre`, `torneo_nombre`, `torneo_fecha`, `disciplinas` |
| **Postcondición** | Email enviado al atleta → `NotificacionEnviada` en store; o `NotificacionFallida` con motivo |

**Flujo completo:**

```
InscripcionConfirmada recibido:
  evento_fuente_id = inscripcion_confirmada.id

  1. SolicitarEnvioHandler.handle(
       evento_fuente_id = evento.id,
       destinatario     = Destinatario(email=evento.atleta_email, nombre=evento.atleta_nombre),
       contenido        = InscripcionConfirmadaTemplate.render(evento),
       canal            = CanalEnvio.Email
     )
     → emite NotificacionSolicitada (si no existe NotificacionEnviada previa)

  2. EnviarNotificacionHandler.handle(notificacion_id)
     → llama EmailPort.enviar(...)
     → emite NotificacionEnviada o NotificacionFallida
```

**Contenido del email (plantilla):**

```
Asunto: Inscripción confirmada — {torneo_nombre}

Hola {atleta_nombre},

Tu inscripción al torneo {torneo_nombre} ha sido confirmada.

Fecha: {torneo_fecha}
Sede: {torneo_sede}
Disciplinas inscriptas: {disciplinas}

¡Buena suerte!
El equipo de AtaraxiaDive
```

**Ejemplo concreto:**

```
Evento recibido:
  InscripcionConfirmada {
    id: "evt-reg-001",
    atleta_id: "ath-123",
    atleta_email: "garcia@apnea.com",
    atleta_nombre: "Martín García",
    torneo_nombre: "Open Buenos Aires 2026",
    torneo_fecha: "2026-05-15",
    torneo_sede: "Club Náutico",
    disciplinas: ["DNF", "STA"]
  }

Resultado:
  Notificacion creada con evento_fuente_id="evt-reg-001"
  Email enviado a garcia@apnea.com
  Asunto: "Inscripción confirmada — Open Buenos Aires 2026"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.5.3 — Política P-10 email de confirmación de inscripción

  Scenario: email enviado exitosamente al confirmar inscripción
    Given el sistema recibe el evento InscripcionConfirmada para Martín García
    And el evento tiene email "garcia@apnea.com" y torneo "Open BA 2026"
    When se procesa la política P-10
    Then se crea un aggregate Notificacion en estado Enviada
    And el email llega a "garcia@apnea.com" con asunto "Inscripción confirmada — Open BA 2026"
    And el cuerpo del email contiene el nombre del torneo y las disciplinas inscriptas

  Scenario: idempotencia — mismo evento procesado dos veces
    Given el evento InscripcionConfirmada "evt-reg-001" ya fue procesado exitosamente
    When el handler de P-10 recibe de nuevo el mismo evento "evt-reg-001"
    Then NO se envía un segundo email (idempotencia del aggregate)
    And el store sigue con exactamente un NotificacionEnviada para "evt-reg-001"

  Scenario: atleta sin email registrado
    Given el evento InscripcionConfirmada tiene atleta_email vacío o ausente
    When se procesa la política P-10
    Then se crea un aggregate Notificacion en estado Fallida con motivo "destinatario_sin_email"
    And el sistema NO lanza excepción (el flujo principal no se interrumpe)

  Scenario: fallo del proveedor de email
    Given el proveedor Resend devuelve error 500
    When se procesa la política P-10
    Then el aggregate Notificacion queda en estado Fallida con el motivo del error
    And la inscripción del atleta NO se revierte
    And el fallo queda registrado en el event store de notificaciones

  Scenario: datos del email son correctos
    When se procesa P-10 para un evento con disciplinas ["DNF", "STA"]
    Then el email contiene las disciplinas "DNF" y "STA" en el cuerpo
    And el asunto incluye el nombre del torneo
```

---

## Impacto arquitectónico

- [x] Sí → wiring de la política en `src/app.py`

**Implementación de la política en `src/app.py`:**

```python
# El evento InscripcionConfirmada se publica desde BC Registro
# P-10 es un listener registrado en el bus de eventos de la app

@app.on_event("startup")
async def registrar_politicas():
    event_bus.subscribe(
        InscripcionConfirmada,
        handler=PoliticaP10Handler(
            solicitar_envio_handler=solicitar_envio_handler,
            enviar_notificacion_handler=enviar_notificacion_handler,
        )
    )
```

> **Sobre el bus de eventos:** en SP4 se implementa como bus in-process síncrono
> (call directo al handler tras el comando que emite el evento). No requiere
> infraestructura de mensajería externa. El bus es una abstracción que en SP5
> podría reemplazarse por RabbitMQ/SQS sin cambiar la política.

**Capa(s) afectadas:**
- [x] Application — `notificaciones/application/commands/solicitar_envio.py`
- [x] Application — `notificaciones/application/policies/politica_p10.py`
- [x] Infrastructure — `notificaciones/infrastructure/templates/inscripcion_confirmada_template.py`
- [x] Infrastructure — `src/app.py` (registro de la política en el bus)

---

## Referencias

- Prerrequisitos: US-4.5.1 (aggregate) · US-4.5.2 (adaptador email)
- Context Map §3.6: `InscripcionConfirmada` como trigger de Notificaciones
- RF-NT-01: notificaciones por email al atleta
- Plan SP4 §INC-4.5 — US-4.5.3

---

*Redactado: 2026-04-14 — INC-4.5 BC Notificaciones*
