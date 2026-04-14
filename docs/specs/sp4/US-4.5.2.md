# US-4.5.2: Adaptador email — puerto + implementación con proveedor gestionado

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.5
**Bounded Context**: `notificaciones`
**Capas afectadas**: `notificaciones/domain/ports/`, `notificaciones/infrastructure/`, `notificaciones/application/commands/`

---

## Descripción

Como **sistema**,
quiero **un adaptador de email concreto detrás del puerto `EmailPort`**
para **enviar emails reales a través de un proveedor gestionado (Resend) sin que el
dominio dependa de ningún SDK externo**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Port | `EmailPort` | Contrato de dominio — `enviar(destinatario, contenido) → None` |
| Adaptador | `ResendEmailAdapter` | Implementa `EmailPort` usando la API de Resend |
| Command | `EnviarNotificacion` | Orquesta: obtiene el aggregate, llama al canal, registra resultado |
| Handler | `EnviarNotificacionHandler` | Ejecuta el comando en la capa application |

> **Elección de proveedor:** Resend es el proveedor seleccionado para SP4. API REST simple,
> SDK Python disponible, plan gratuito suficiente para desarrollo y UAT. Alternativas
> equivalentes (SendGrid, AWS SES) son intercambiables sin cambios en domain/.
> La decisión se formaliza en ADR-016.

### Lenguaje ubicuo relevante

- **Puerto de email:** abstracción de dominio que define el contrato de envío. El dominio no conoce ni Resend, ni SMTP, ni ningún SDK.
- **Adaptador:** implementación concreta del puerto. Vive en `infrastructure/`. Puede reemplazarse sin tocar `domain/` ni `application/`.
- **Email transaccional:** email disparado por un evento (ej: confirmación de inscripción), no masivo ni de marketing.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.5.2-01:** `EmailPort.enviar()` es el único punto de contacto entre el dominio y el canal externo. Ninguna capa de domain/ o application/ importa SDKs de email directamente.
- **INV-4.5.2-02:** Si el proveedor externo falla (timeout, error 5xx, rate limit), el adaptador lanza `EmailEnvioFallido` con el motivo. El handler lo captura y ejecuta `RegistrarFallo` en el aggregate.
- **INV-4.5.2-03:** El adaptador NO reintenta — los reintentos son responsabilidad del application layer o de la política de scheduling externa.
- **INV-4.5.2-04:** La API key de Resend se inyecta por variable de entorno (`RESEND_API_KEY`). El adaptador falla en construcción si la variable no está presente.
- **INV-4.5.2-05:** El email de origen (`from`) es configurable por variable de entorno (`NOTIFICATION_FROM_EMAIL`). Default: `noreply@ataraxiadive.app`.

### Operación principal: `EnviarNotificacion(notificacion_id)`

| | Descripción |
|---|---|
| **Precondición** | Existe un aggregate `Notificacion` en estado `Solicitada` con el `notificacion_id` dado |
| **Postcondición** | Email enviado al destinatario → aggregate en estado `Enviada`; o error → aggregate en estado `Fallida` |

**Flujo completo:**

```
EnviarNotificacionHandler.handle(notificacion_id):
  1. Rehidratar Notificacion desde event store
  2. Si estado ≠ Solicitada → no hacer nada (idempotente — ya procesado)
  3. Llamar EmailPort.enviar(notificacion.destinatario, notificacion.contenido)
     ├── éxito → notificacion.RegistrarEnvioExitoso()
     └── fallo → notificacion.RegistrarFallo(motivo)
  4. Persistir nuevos eventos en el store
```

**Ejemplo concreto:**

```
Input: notificacion_id=uuid-xyz
Store: [NotificacionSolicitada { destinatario: juan@example.com, asunto: "Inscripción confirmada" }]

Adaptador Resend: POST https://api.resend.com/emails
  { from: "noreply@ataraxiadive.app", to: "juan@example.com", subject: "Inscripción confirmada", html: "..." }
  → HTTP 200 { id: "resend-email-id-abc" }

Store actualizado: [..., NotificacionEnviada { enviada_en: "...", proveedor_id: "resend-email-id-abc" }]

---

Error de proveedor:
Adaptador Resend: POST → HTTP 429 Too Many Requests
→ lanza EmailEnvioFallido("rate_limit: 429 Too Many Requests")
Store actualizado: [..., NotificacionFallida { motivo: "rate_limit: 429 Too Many Requests" }]
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.5.2 — Adaptador email con Resend

  Background:
    Given el aggregate Notificacion está en estado Solicitada
    And el destinatario es "atleta@example.com" con asunto "Inscripción confirmada"

  Scenario: envío exitoso a través de Resend
    Given el adaptador Resend está configurado con API key válida
    When se ejecuta EnviarNotificacion
    Then el adaptador hace POST a la API de Resend con los datos correctos
    And el aggregate emite NotificacionEnviada con el proveedor_id devuelto por Resend
    And el email llega a la bandeja de entrada de prueba

  Scenario: fallo de proveedor — error 5xx
    Given el adaptador Resend responde con 500 Internal Server Error
    When se ejecuta EnviarNotificacion
    Then el adaptador lanza EmailEnvioFallido con el motivo del error
    And el aggregate emite NotificacionFallida
    And el estado queda en Fallida

  Scenario: fallo de proveedor — timeout
    Given el adaptador Resend no responde en 10 segundos
    When se ejecuta EnviarNotificacion
    Then el adaptador lanza EmailEnvioFallido con motivo "timeout"
    And el aggregate emite NotificacionFallida

  Scenario: API key no configurada
    Given RESEND_API_KEY no está definida en el entorno
    When se construye el adaptador ResendEmailAdapter
    Then se lanza un error de configuración en el arranque de la aplicación

  Scenario: DIP verificado — domain no importa SDK
    Then ningún archivo en notificaciones/domain/ importa "resend" o "smtplib"
    And ningún archivo en notificaciones/application/ importa "resend" o "smtplib"
```

---

## Impacto arquitectónico

- [x] Sí → nueva dependencia externa: `resend` (SDK Python)

**Dependencia a agregar en `pyproject.toml`:**
```toml
resend = "^2.0"
```

**Variables de entorno requeridas (`.env`):**
```
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
NOTIFICATION_FROM_EMAIL=noreply@ataraxiadive.app
```

**Estructura del adaptador:**
```python
# notificaciones/infrastructure/adapters/resend_email_adapter.py
import resend
from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.value_objects import Destinatario, ContenidoEmail

class ResendEmailAdapter(EmailPort):
    def __init__(self, api_key: str, from_email: str) -> None:
        resend.api_key = api_key
        self._from = from_email

    def enviar(self, destinatario: Destinatario, contenido: ContenidoEmail) -> None:
        try:
            resend.Emails.send({
                "from": self._from,
                "to": destinatario.email,
                "subject": contenido.asunto,
                "html": contenido.cuerpo_html,
            })
        except Exception as e:
            raise EmailEnvioFallido(str(e)) from e
```

**Registro en composition root (`src/app.py`):**
```python
email_adapter = ResendEmailAdapter(
    api_key=settings.RESEND_API_KEY,
    from_email=settings.NOTIFICATION_FROM_EMAIL,
)
notificacion_handler = EnviarNotificacionHandler(
    repo=sqlite_notificacion_repo,
    email_port=email_adapter,
)
```

**Capa(s) afectadas:**
- [x] Domain — `notificaciones/domain/ports/email_port.py` (puerto abstracto)
- [x] Infrastructure — `notificaciones/infrastructure/adapters/resend_email_adapter.py`
- [x] Application — `notificaciones/application/commands/enviar_notificacion.py` (command + handler)
- [x] Infrastructure — `src/app.py` (composition root — inyección del adaptador)

---

## ADR requerido

**ADR-016:** Resend como proveedor de email transaccional para INC-4.5.

Puntos a documentar:
- Alternativas evaluadas: SendGrid, AWS SES, SMTP propio
- Criterio de selección: API REST simple, plan gratuito, SDK Python, sin tarjeta para desarrollo
- Trade-off: lock-in al proveedor vs. DIP via `EmailPort` (el puerto mitiga el riesgo)
- Condición de revisión: si el volumen supera el plan gratuito o se requiere SLA enterprise

---

## Referencias

- Prerrequisitos: US-4.5.1 (aggregate + puerto `EmailPort`)
- ADR-016 (a crear en esta US): Resend como proveedor
- Plan SP4 §INC-4.5: adaptador email como US independiente
- Arquitectura hexagonal: `docs/design/architecture.md §Puertos y Adaptadores`

---

*Redactado: 2026-04-14 — INC-4.5 BC Notificaciones*
