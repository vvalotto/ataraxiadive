---
title: "RF — Notificaciones"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-4.5.1
  - US-4.5.2
  - US-4.5.3
  - US-4.5.4
  - US-4.5.5
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

| ID | Pendiente | Clasificación |
|----|-----------|---------------|
| RF-NT-03 | Notificaciones al juez u organizador durante ejecución | **Backlog activo** — la infraestructura de notificaciones existe; falta definir triggers |

## Estado de implementación (lint-001)

RF-NT-03 no tiene US asociada. Las notificaciones implementadas son todas hacia atletas (P-10, P-11). Notificaciones hacia el juez u organizador durante ejecución requieren:
1. Definir qué eventos disparan la notificación (¿llamado de atleta? ¿DNS? ¿inicio de disciplina?)
2. Definir canal (email no aplica durante ejecución — posiblemente push)
3. El adaptador `PushPort` está diseñado pero no implementado (solo existe `EmailPort`)

**Lo que falta:** definir triggers + implementar `PushAdapter`. El BC [[notificaciones]] está preparado para recibir nuevas políticas. Candidato a US en SP8.

## BCs que implementan esta área

- [[notificaciones]] — envío de notificaciones por mail y push
- Ver [[ADR-016-resend-email-provider]] para la decisión de proveedor de email.
- Ver [[ADR-017-notificaciones-event-sourcing]] para la decisión de arquitectura de notificaciones.
