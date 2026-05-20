---
title: "RF — Notificaciones"
type: trazabilidad
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
---

# RF — Notificaciones

Requerimientos funcionales del área de notificaciones. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-NT-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| RF-NT-01 | ¿Notificaciones solo por email o también push? | **Email + push.** |
| RF-NT-02 | ¿Se notifica al atleta cuando se acerca la fecha límite de anuncios? | **Sí.** |
| RF-NT-03 | ¿El juez/organizador recibe notificaciones durante la ejecución? | **Pendiente.** |
| RF-NT-04 | ¿Se notifica a los atletas cuando se publican resultados finales? | **Sí.** |

## Triggers de notificación definidos

| Evento | Destinatario | Canal |
|--------|-------------|-------|
| Inscripción confirmada | [[atleta]] | Mail |
| Apertura de período de anuncios | Atletas inscriptos | Mail |
| Recordatorio de fecha límite de anuncios | Atletas sin anuncio | Mail / Push |
| Resultados finales publicados | Atletas del torneo | Mail / Push |

## Pendientes en elicitación

| ID | Pendiente |
|----|-----------|
| RF-NT-03 | Notificaciones al juez u organizador durante ejecución |

## BCs que implementan esta área

- [[notificaciones]] — envío de notificaciones por mail y push
- Ver [[ADR-016-resend-email-provider]] para la decisión de proveedor de email.
- Ver [[ADR-017-notificaciones-event-sourcing]] para la decisión de arquitectura de notificaciones.
