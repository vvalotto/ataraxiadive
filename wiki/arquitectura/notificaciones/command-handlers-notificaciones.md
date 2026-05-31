---
title: "Notificaciones — Command Handlers y Políticas"
type: arquitectura-componente
bc: notificaciones
capa: application
tipo_componente: handler
responsabilidad: "2 handlers base (SolicitarEnvio, EnviarNotificacion) + 2 políticas P-10/P-11 que orquestan el flujo completo"
interfaces_out:
  - NotificacionRepository
  - EmailPort
adr_refs: [ADR-017, ADR-016]
last_updated: "2026-05-23"
sources:
  - src/notificaciones/application/commands/solicitar_envio.py
  - src/notificaciones/application/commands/enviar_notificacion.py
  - src/notificaciones/application/policies/politica_p10.py
  - src/notificaciones/application/policies/politica_p11.py
  - src/notificaciones/application/policies/_helpers.py
us_origen:
  - US-4.5.3-politica-p-10-email-al-atleta-al-confirmar-inscripcion
  - US-4.5.4-politica-p-11-email-a-atletas-al-publicar-resultados
  - US-ADJ-6.4-eliminar-duplicacion-p-10-p-11-y-staticmethod
---

# Command Handlers y Políticas — BC Notificaciones

El BC organiza la lógica de aplicación en dos capas: **handlers base** (primitivas atómicas) y **políticas** (orquestadores que combinan los handlers para un evento de dominio concreto).

---

## Handlers base

### SolicitarEnvioHandler

Registra una solicitud de envío en el event store (idempotente).

```python
async def handle(self, command: SolicitarEnvioCommand) -> NotificacionId | None
```

**Flujo:**
1. Construye `EventoFuenteId` desde `command.evento_fuente_id`
2. Consulta `repository.exists_success_by_evento_fuente_id()` — si ya existe envío exitoso → retorna `None` inmediatamente
3. Llama `Notificacion.solicitar_envio()` — si retorna `None` (idempotencia del aggregate) → retorna `None`
4. Persiste eventos pendientes con `persistir_eventos_pendientes()`
5. Retorna `NotificacionId` del nuevo aggregate

**`SolicitarEnvioCommand`** (frozen dataclass): `evento_fuente_id: str`, `destinatario: Destinatario`, `contenido: ContenidoEmail`, `canal: CanalEnvio = EMAIL`.

**`persistir_eventos_pendientes()`** — función utilitaria compartida: itera `aggregate.pull_events()` y llama `repository.append()` por cada evento.

---

### EnviarNotificacionHandler

Realiza el envío real vía `EmailPort` y registra el resultado en el event store.

```python
async def handle(self, command: EnviarNotificacionCommand) -> None
```

**Flujo:**
1. Carga el stream `notificacion-{notificacion_id}` desde el repository
2. Reconstituye el aggregate con `Notificacion.reconstitute(events)`
3. Si `destinatario` o `contenido` son `None` → `aggregate.registrar_fallo("notificacion_sin_contenido")` + persiste + sale
4. `await email_port.enviar(destinatario, contenido)` → obtiene `proveedor_id`
5. Si éxito → `aggregate.registrar_envio_exitoso(proveedor_id)`
6. Si excepción → `aggregate.registrar_fallo(str(exc))` (captura `Exception` genérica — `BLE001`)
7. Persiste eventos pendientes

El aggregate queda en estado `"Enviada"` o `"Fallida"` tras la operación.

---

## Políticas

Las políticas son los puntos de entrada desde el sistema de callbacks in-process. Reciben DTOs de eventos externos y coordinan ambos handlers.

### PoliticaP10Handler — Inscripción Confirmada

**Trigger:** `InscripcionConfirmada` (emitido por BC Registro al confirmar inscripción).

**Evento fuente:** `InscripcionConfirmada.id` (uno por inscripción).

**Destinatario:** atleta de la inscripción.

```python
async def handle(self, evento: InscripcionConfirmada) -> None
```

**Flujo:**
1. Si `evento.atleta_email` está vacío → `registrar_fallo_sin_email(evento.id)` + sale
2. `template.render(evento)` → `ContenidoEmail`
3. `solicitar_envio_handler.handle(SolicitarEnvioCommand(...))` → `notificacion_id | None`
4. Si `notificacion_id` es `None` → ya enviado, sale (idempotencia)
5. `enviar_notificacion_handler.handle(EnviarNotificacionCommand(notificacion_id))`

**Template:** `InscripcionConfirmadaTemplate` (nombre torneo, fecha, sede, disciplinas).

---

### PoliticaP11Handler — Resultados Publicados

**Trigger:** `ResultadosPublicados` (emitido por BC Resultados al publicar ranking).

**Evento fuente:** `"{evento.id}:{atleta_id}"` (compuesto — una notificación por atleta por publicación).

**Destinatarios:** todos los atletas de la disciplina (itera `evento.resultados`).

```python
async def handle(self, evento: ResultadosPublicados) -> None
```

**Flujo:**
- Por cada `resultado` en `evento.resultados`:
  - Si `resultado.estado == "Retirado"` → omitir
  - Llamar `_procesar_resultado(evento, resultado)`

**`_procesar_resultado()`:**
1. Genera `evento_fuente_id = "{evento.id}:{resultado.atleta_id}"`
2. Si sin email → `registrar_fallo_sin_email(evento_fuente_id)` + continúa con el siguiente
3. `template.render(evento=evento, resultado=resultado)` → `ContenidoEmail`
4. `solicitar_envio_handler.handle(...)` + `enviar_notificacion_handler.handle(...)`

---

## Helper compartido: `registrar_fallo_sin_email()`

```python
async def registrar_fallo_sin_email(evento_fuente_id: str, repository) -> None
```

Registra `NotificacionFallida` con `motivo="destinatario_sin_email"` cuando el atleta no tiene email.

- Es idempotente: verifica `exists_success_by_evento_fuente_id` antes de crear el aggregate
- Llamado desde P-10 y P-11 sin interrumpir el flujo del BC productor

---

## Integración con composition root

Las políticas son registradas como callbacks desde `app.py`:

```python
# BC Registro recibe el callback como parámetro opcional
configure_inscripcion_notificaciones(politica_p10_handler.handle)
# BC Resultados recibe el callback para publicación
configure_resultados_notificaciones(politica_p11_handler.handle)
```

Ningún BC funcional importa tipos de Notificaciones — la dependencia es solo en dirección: Notificaciones ← (callbacks from) Registro / Resultados.

---

## Relaciones

**Contenedor:** [[arquitectura/notificaciones]]

- Operan sobre [[notificacion-aggregate]]
- Usan [[sqlite-notificacion-event-store]] vía `NotificacionRepository`
- Inyectados vía composition root en `app.py`
- P-10 registrado en [[router-registro]] vía `configure_inscripcion_notificaciones()`
- P-11 registrado en [[router-resultados]] vía `configure_resultados_notificaciones()`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/notificaciones/application/commands/solicitar_envio.py` | Handler: SolicitarEnvioHandler |
| `src/notificaciones/application/commands/enviar_notificacion.py` | Handler: EnviarNotificacionHandler |
| `src/notificaciones/application/policies/politica_p10.py` | Política P-10 — email de confirmación de inscripción |
| `src/notificaciones/application/policies/politica_p11.py` | Política P-11 — email de resultados publicados |
| `src/notificaciones/application/policies/_helpers.py` | Helpers internos de políticas de notificación |
