---
title: "ADR-017: Event Sourcing en BC Notificaciones para exactly-once delivery"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-017-notificaciones-event-sourcing.md
estado: Aceptada
fecha: 2026-04-16
bcs_afectados: [notificaciones]
rnf_refs:
  - RNF-08-interoperabilidad-exportacion-resultados
---

# ADR-017: Event Sourcing en BC Notificaciones para exactly-once delivery

## Decisión

Se adopta Event Sourcing en BC Notificaciones — a pesar de ser un BC genérico — para garantizar exactly-once delivery de emails sin lógica de deduplicación ad-hoc en infraestructura.

## Por qué

BC Notificaciones no tiene lógica de negocio de apnea. En condiciones normales sería CRUD. Pero el requisito de **exactly-once** es no negociable: un email duplicado de "descalificado" o "inscripción confirmada" es un error visible para el atleta.

La alternativa (tabla `notificaciones_enviadas` con `evento_fuente_id UNIQUE`) tiene lógica de idempotencia fuera del aggregate, sin audit trail, y debe duplicarse por cada canal (Push, SMS).

El event store resuelve el problema de forma estructural:

1. `SolicitarEnvioHandler` consulta si existe `NotificacionEnviada` para ese `evento_fuente_id` en el store.
2. Si existe → `Notificacion.solicitar_envio()` retorna `None`. No se envía nada.
3. Si no existe → se crea la `Notificacion`, se persiste `NotificacionSolicitada`, se procede.

La infraestructura del event store SQLite ([[ADR-008-event-store-sqlite]]) ya existe — el BC la reutiliza sin overhead adicional.

## Eventos del aggregate `Notificacion`

| Evento | Trigger |
|--------|---------|
| `NotificacionSolicitada` | Handler recibe evento de dominio de otro BC |
| `NotificacionEnviada` | Adaptador de email confirma entrega |
| `NotificacionFallida` | Error en el adaptador |
| `NotificacionReintentada` | Reintento tras fallo |

## Consecuencias vigentes

- ES en un BC genérico es **inusual y justificado exclusivamente por el requisito de idempotencia**. La regla general del proyecto sigue siendo: ES solo donde el dominio lo justifica (Competencia) o donde hay un requisito de infraestructura que ES resuelve naturalmente (Notificaciones).
- Audit trail natural: cada transición `Solicitada → Enviada | Fallida` queda en el store con timestamp.
- El modelo escala a nuevos canales (Push, SMS en SP5) sin cambiar la lógica de idempotencia.
- Mayor complejidad que CRUD para un BC que no la necesitaría por su dominio.

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — patrón ES que este ADR reutiliza
- [[ADR-008-event-store-sqlite]] — infraestructura compartida
- [[ADR-016-resend-email-provider]] — el proveedor de email que este BC usa
