---
title: "ADR-016: Resend como proveedor de email transaccional"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-016-resend-email-provider.md
estado: Aceptada
fecha: 2026-04-16
bcs_afectados: [notificaciones]
---

# ADR-016: Resend como proveedor de email transaccional

## Decisión

Resend como proveedor de email. El `EmailPort` abstrae completamente el proveedor — cambiar a SES o SendGrid solo cambia el adaptador en `infrastructure/email/`.

## Por qué

- Sandbox `onboarding@resend.dev` permite enviar emails reales durante el desarrollo sin registrar dominio propio.
- API minimalista: una sola llamada `POST /emails` con JSON.
- Plan gratuito: 3000 emails/mes — holgadamente suficiente para torneos de apnea.

## Consecuencias vigentes

| Variable de entorno | Descripción |
|--------------------|-------------|
| `RESEND_API_KEY` | API key de Resend |
| `NOTIFICACIONES_EMAIL_FROM` | Remitente (`onboarding@resend.dev` en sandbox) |

- **Fallback de desarrollo:** si `RESEND_API_KEY` no está configurada, se inyecta `LoggingEmailAdapter` — registra el email en el log sin enviarlo.
- Webhooks disponibles para bounces/opens — no usados en SP4, disponibles para SP5.
- Vendor lock-in leve, mitigado por el `EmailPort`.

## ADRs relacionados

- [[ADR-017-notificaciones-event-sourcing]] — el BC que usa este proveedor
