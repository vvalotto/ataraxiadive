---
title: "Notificaciones — Aggregate Notificacion (ES)"
type: arquitectura-componente
bc: notificaciones
capa: domain
tipo_componente: aggregate
responsabilidad: "Aggregate ES con 3 estados: Nueva→Solicitada→Enviada|Fallida. Clave de idempotencia: EventoFuenteId"
interfaces_out: []
adr_refs: [ADR-017, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/notificaciones/domain/aggregates/notificacion.py
  - src/notificaciones/domain/events/notificacion_solicitada.py
  - src/notificaciones/domain/events/notificacion_enviada.py
  - src/notificaciones/domain/events/notificacion_fallida.py
  - src/notificaciones/domain/value_objects/
---

# Aggregate Notificacion — BC Notificaciones

`Notificacion(AggregateRoot)` — aggregate raíz del BC. Toda notificación nace de un evento de dominio externo y su ciclo de vida completo queda en el event store.

---

## Estados y transiciones

```
[Nueva]
   │
   ├─ solicitar_envio() ──────────────────► [Solicitada]
   │  (si existe_envio_exitoso_previo → None)      │
   │                                               ├─ registrar_envio_exitoso() ──► [Enviada]
   │                                               └─ registrar_fallo()          ──► [Fallida]
   │
   └─ registrar_fallo_de_solicitud() ─────────────► [Fallida]
      (sin email, error pre-envío)
```

- `_assert_solicitada()` protege `registrar_envio_exitoso` y `registrar_fallo`: ambos lanzan `EstadoNotificacionInvalido` si el estado no es `"Solicitada"`.

---

## Métodos de fábrica / mutación

| Método | Tipo | Descripción |
|--------|------|-------------|
| `solicitar_envio(...)` | classmethod async | Crea aggregate + emite `NotificacionSolicitada`. Retorna `None` si ya existe envío exitoso para el mismo `evento_fuente_id` (idempotencia). |
| `registrar_fallo_de_solicitud(...)` | classmethod | Crea aggregate + emite `NotificacionFallida` directamente (sin pasar por Solicitada). Usado cuando el destinatario no tiene email. |
| `registrar_envio_exitoso(proveedor_id)` | instancia | Emite `NotificacionEnviada` con `proveedor_id` del proveedor externo. |
| `registrar_fallo(motivo)` | instancia | Emite `NotificacionFallida` con `motivo` de texto. |
| `reconstitute(events)` | classmethod | Rehidrata desde lista de dicts del event store. |

---

## Idempotencia

La clave de idempotencia se implementa **antes** de crear el aggregate:

```python
aggregate = await Notificacion.solicitar_envio(
    ...
    existe_envio_exitoso_previo=await repository.exists_success_by_evento_fuente_id(evento_fuente_id)
)
if aggregate is None:
    return None  # ya fue enviado, no se crea nuevo aggregate
```

La verificación usa `json_extract(payload, '$.evento_fuente_id')` en SQLite para buscar `NotificacionEnviada` con ese `evento_fuente_id`. Si existe → el factory retorna `None` → el handler sale silenciosamente.

---

## Eventos de dominio

| Evento | Payload clave |
|--------|---------------|
| `NotificacionSolicitada` | `notificacion_id`, `evento_fuente_id`, `destinatario_email`, `destinatario_nombre`, `asunto`, `cuerpo_texto`, `cuerpo_html?`, `canal` |
| `NotificacionEnviada` | `notificacion_id`, `evento_fuente_id`, `proveedor_id?`, `enviada_en` |
| `NotificacionFallida` | `notificacion_id`, `evento_fuente_id`, `motivo`, `fallida_en` |

Todos implementan `to_payload()` y `from_payload()` — serialización/deserialización para el event store.

---

## Value Objects del BC

| VO | Descripción |
|----|-------------|
| `NotificacionId` | UUID4, identidad del aggregate |
| `EventoFuenteId` | UUID string — ID del evento de dominio fuente; clave de idempotencia |
| `Destinatario` | `email: str`, `nombre: str \| None` |
| `ContenidoEmail` | `asunto: str` (no vacío), `cuerpo_texto: str`, `cuerpo_html: str \| None` |
| `CanalEnvio` | Enum: `EMAIL` (único implementado; `PUSH` solo diseño) |

---

## Stream ID

```python
@property
def stream_id(self) -> str:
    return f"notificacion-{self._notificacion_id}"
```

Cada notificación tiene su propio stream. Los eventos del stream determinan el estado actual del aggregate.

---

## Relaciones

**Contenedor:** [[arquitectura/notificaciones]]

- Persistido por [[sqlite-notificacion-event-store]]
- Creado y mutado por [[command-handlers-notificaciones]]
- Los eventos del dominio fuente (`InscripcionConfirmada`, `ResultadosPublicados`) son DTOs externos — el BC no importa los agregados de Registro ni Resultados

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/notificaciones/domain/aggregates/notificacion.py` | Aggregate Notificacion — ciclo de vida ES + idempotencia EventoFuenteId |
| `src/notificaciones/domain/events/notificacion_solicitada.py` | Evento NotificacionSolicitada |
| `src/notificaciones/domain/events/notificacion_enviada.py` | Evento NotificacionEnviada |
| `src/notificaciones/domain/events/notificacion_fallida.py` | Evento NotificacionFallida |
| `src/notificaciones/domain/value_objects/` |  |
