---
title: "RNF-08 — Interoperabilidad: exportación de resultados"
type: trazabilidad-rnf
rnf_id: RNF-08
atributo: Interoperabilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-016-resend-email-provider
  - ADR-017-notificaciones-event-sourcing
bcs_afectados:
  - resultados
  - notificaciones
---

# RNF-08 — Interoperabilidad

**Driver:** exportación de resultados requerida; integración con cronometraje electrónico prevista a futuro.

| Atributo | Estado |
|---|---|
| Exportación de resultados (CSV, JSON) | Requerida |
| Notificaciones por email | Requerida — Resend |
| Notificaciones push | Pendiente (Firebase/OneSignal) |
| Integración con cronometraje electrónico | Prevista a futuro |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-016-resend-email-provider]] — Resend como canal de notificación externo
- [[decisiones/ADR-017-notificaciones-event-sourcing]] — ES en Notificaciones para exactly-once delivery

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
