# US-4.5.4: Política P-11 — email de resultados publicados a atletas de la disciplina

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.5
**Bounded Context**: `notificaciones` (consumidor) · `resultados` (productor del evento)
**Capas afectadas**: `notificaciones/application/`, `src/app.py`

---

## Descripción

Como **atleta**,
quiero **recibir un email cuando se publiquen los resultados de mi disciplina**
para **conocer mi posición final, mi RP y el podio, sin tener que consultar activamente
la plataforma**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Evento fuente | `ResultadosPublicados` | Emitido por BC Resultados al publicar el ranking de una disciplina |
| Policy | P-11 | Al recibir `ResultadosPublicados` → enviar email a cada atleta de la disciplina con su resultado individual |
| Command | `SolicitarEnvio` | Crea un aggregate `Notificacion` por atleta (uno por destinatario) |
| Command | `EnviarNotificacion` | Envía el email individual y registra resultado |
| Plantilla | `ResultadosPublicadosTemplate` | Contenido personalizado por atleta: posición, RP, podio |

### Lenguaje ubicuo relevante

- **Política P-11:** regla de negocio que conecta `ResultadosPublicados` con el envío de emails individuales a cada atleta. Una notificación por atleta.
- **`evento_fuente_id` por atleta:** `"{resultados_publicados.id}:{atleta_id}"` — clave compuesta que garantiza idempotencia por cada par (publicación, atleta).
- **Resultados publicados:** el organizador ha marcado el ranking de una disciplina como publicado. Los resultados son definitivos y visibles públicamente.
- **Email personalizado:** cada atleta recibe su posición, su RP, el tiempo/distancia, y el podio de la disciplina.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.5.4-01:** Por cada par `(ResultadosPublicados.id, atleta_id)` se envía exactamente un email. Si el handler se ejecuta dos veces (retry), la idempotencia del aggregate previene el duplicado.
- **INV-4.5.4-02:** El email de cada atleta contiene: posición final, RP (con unidad), tarjeta asignada, y el podio de la disciplina (top 3).
- **INV-4.5.4-03:** Si un atleta no tiene email registrado, su notificación se crea en estado `Fallida` con motivo `"destinatario_sin_email"`. Los demás atletas reciben su email normalmente.
- **INV-4.5.4-04:** El fallo en el envío a un atleta no impide el envío a los demás. La política itera sobre todos los atletas de forma independiente.
- **INV-4.5.4-05:** Un fallo masivo del proveedor (ej: rate limit) no revierte la publicación de resultados. Los fallos quedan en el store de Notificaciones para auditoría y posible reintento.
- **INV-4.5.4-06:** Solo se notifica a atletas que participaron en la disciplina publicada (`estado != 'Retirado'`). Atletas con DNS reciben el email (su resultado es DNS).

### Política P-11: `ResultadosPublicados` → emails a atletas

| | Descripción |
|---|---|
| **Trigger** | Evento `ResultadosPublicados` recibido desde BC Resultados |
| **Precondición** | El evento contiene la lista de resultados con `atleta_id`, `atleta_email`, `posicion`, `rp`, `tarjeta` |
| **Postcondición** | Un email enviado por atleta → `NotificacionEnviada` o `NotificacionFallida` por atleta en el store |

**Flujo completo:**

```
ResultadosPublicados recibido:
  {
    id: "evt-res-001",
    torneo_nombre: "Open Buenos Aires 2026",
    disciplina: "DNF",
    resultados: [
      { atleta_id: "ath-1", atleta_email: "garcia@apnea.com", atleta_nombre: "Martín García",
        posicion: 1, rp: "96m", tarjeta: "Blanca" },
      { atleta_id: "ath-2", atleta_email: "lopez@apnea.com", atleta_nombre: "Ana López",
        posicion: 2, rp: "88m", tarjeta: "BlancaConPenalizaciones" },
      { atleta_id: "ath-3", atleta_email: "vega@apnea.com", atleta_nombre: "Diego Vega",
        posicion: 3, rp: "DNS", tarjeta: null }
    ],
    podio: [
      { posicion: 1, atleta_nombre: "Martín García", rp: "96m" },
      { posicion: 2, atleta_nombre: "Ana López", rp: "88m" },
      { posicion: 3, atleta_nombre: "Diego Vega", rp: "DNS" }
    ]
  }

Por cada atleta en resultados:
  evento_fuente_id = "evt-res-001:ath-N"  ← clave compuesta (publicacion + atleta)

  SolicitarEnvioHandler.handle(
    evento_fuente_id = "evt-res-001:ath-N",
    destinatario     = Destinatario(email=atleta.atleta_email, nombre=atleta.atleta_nombre),
    contenido        = ResultadosPublicadosTemplate.render(atleta, podio, torneo, disciplina),
    canal            = CanalEnvio.Email
  )
  EnviarNotificacionHandler.handle(notificacion_id)
```

**Contenido del email (personalizado por atleta):**

```
Asunto: Resultados publicados — DNF · Open Buenos Aires 2026

Hola Martín García,

Ya están disponibles los resultados de la disciplina DNF
en el torneo Open Buenos Aires 2026.

Tu resultado:
  Posición: #1
  RP: 96m
  Tarjeta: Blanca ✓

Podio DNF:
  🥇 Martín García — 96m
  🥈 Ana López — 88m
  🥉 Diego Vega — DNS

Podés ver el ranking completo en: https://ataraxiadive.app/resultados/{torneo_id}

¡Felicitaciones por tu participación!
El equipo de AtaraxiaDive
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.5.4 — Política P-11 emails de resultados publicados

  Background:
    Given el evento ResultadosPublicados contiene 3 atletas con emails válidos

  Scenario: emails enviados a todos los atletas al publicar resultados
    When se procesa la política P-11
    Then se crean 3 aggregates Notificacion, uno por atleta
    And cada aggregate queda en estado Enviada
    And cada atleta recibe un email con su posición individual y el podio

  Scenario: email personalizado con datos correctos
    When Martín García recibe su email de resultados
    Then el email contiene "Posición: #1"
    And el email contiene "96m"
    And el email contiene el podio con los 3 primeros clasificados

  Scenario: idempotencia — ResultadosPublicados procesado dos veces
    Given los resultados "evt-res-001" ya fueron publicados y emails enviados
    When el handler de P-11 recibe de nuevo el evento "evt-res-001"
    Then NO se envían emails duplicados a ningún atleta
    And el store sigue con exactamente un NotificacionEnviada por par (evento, atleta)

  Scenario: atleta sin email — no interrumpe el envío a los demás
    Given uno de los 3 atletas no tiene email registrado
    When se procesa la política P-11
    Then los 2 atletas con email reciben su notificación
    And el atleta sin email tiene una Notificacion en estado Fallida con motivo "destinatario_sin_email"
    And la publicación de resultados NO se revierte

  Scenario: fallo de proveedor en un atleta — continúa con los demás
    Given el proveedor Resend falla solo para el primer atleta (error 500)
    When se procesa la política P-11
    Then el primer atleta tiene Notificacion en estado Fallida
    And los atletas restantes reciben su email exitosamente

  Scenario: atleta con DNS recibe email
    Given un atleta tiene estado DNS en los resultados
    When se procesa la política P-11
    Then ese atleta recibe el email con "DNS" como su resultado
    And el email incluye el podio de la disciplina
```

---

## Impacto arquitectónico

- [x] Sí → wiring de la política en `src/app.py`

**Nota sobre `evento_fuente_id` compuesto:**

La clave de idempotencia `"{evento.id}:{atleta_id}"` es un string compuesto que permite
al aggregate `Notificacion` distinguir entre la notificación de distintos atletas del
mismo evento de publicación. Sin esta composición, el primer atleta bloquearía el envío
al segundo (misma clave de idempotencia).

```python
# notificaciones/application/policies/politica_p11.py

class PoliticaP11Handler:
    def handle(self, evento: ResultadosPublicados) -> None:
        for resultado in evento.resultados:
            evento_fuente_id = f"{evento.id}:{resultado.atleta_id}"
            try:
                self._solicitar_envio.handle(
                    evento_fuente_id=evento_fuente_id,
                    destinatario=Destinatario(
                        email=resultado.atleta_email,
                        nombre=resultado.atleta_nombre,
                    ),
                    contenido=ResultadosPublicadosTemplate.render(
                        resultado=resultado,
                        podio=evento.podio,
                        torneo_nombre=evento.torneo_nombre,
                        disciplina=evento.disciplina,
                    ),
                    canal=CanalEnvio.Email,
                )
                self._enviar_notificacion.handle(notificacion_id=...)
            except Exception as e:
                # Fallo en un atleta no interrumpe los demás
                logger.error(f"P-11 fallo para atleta {resultado.atleta_id}: {e}")
```

**Capa(s) afectadas:**
- [x] Application — `notificaciones/application/policies/politica_p11.py`
- [x] Infrastructure — `notificaciones/infrastructure/templates/resultados_publicados_template.py`
- [x] Infrastructure — `src/app.py` (registro de P-11 en el bus de eventos)

---

## Consideración de volumen

En torneos con muchos atletas (ej: 50 por disciplina, 5 disciplinas), `ResultadosPublicados`
podría disparar 50 emails simultáneos. Para SP4 (desarrollo y UAT) esto no es un problema.
En SP5, evaluar rate limiting del proveedor y procesamiento en background (Celery, ARQ).

---

## Referencias

- Prerrequisitos: US-4.5.1 (aggregate) · US-4.5.2 (adaptador email) · US-4.5.3 (patrón de política)
- Context Map §3.6: `ResultadosPublicados` como trigger de Notificaciones
- RF-NT-04: notificar a atletas cuando se publican resultados finales
- Plan SP4 §INC-4.5 — US-4.5.4

---

*Redactado: 2026-04-14 — INC-4.5 BC Notificaciones*
