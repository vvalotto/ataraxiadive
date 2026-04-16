# ADR-016: Resend como proveedor de email transaccional

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-16 |
| **Autores** | Victor Valotto |
| **Relacionado con** | US-4.5.2, BC Notificaciones |

---

## Contexto

El BC Notificaciones requiere envío de email transaccional real para las políticas P-10
(inscripción confirmada) y P-11 (tarjeta roja). El proyecto se encuentra en fase de
desarrollo activo sin dominio propio verificado en producción.

Los requisitos para el proveedor son:
- Onboarding sin fricción durante el desarrollo (sin necesidad de verificar dominio propio)
- API simple para integrar desde Python
- Precio adecuado para el volumen esperado (torneos de apnea, decenas a cientos de emails por evento)
- Soporte para contenido HTML y texto plano

## Opciones Consideradas

**SMTP directo (ej. Gmail, Outlook):** Simple, sin costos. Limitaciones de rate y reputación
bajas para emails transaccionales. Requiere credenciales de cuenta personal.

**SendGrid:** Proveedor maduro con plan gratuito (100 emails/día). API REST bien documentada.
Onboarding requiere verificación de dominio o sender identity.

**Amazon SES:** Pricing muy bajo a escala. Requiere cuenta AWS y configuración de IAM.
En modo sandbox requiere verificar cada destinatario manualmente — inviable para desarrollo.

**Resend:** API REST minimalista (una sola llamada HTTP). Plan gratuito de 3000 emails/mes.
Sandbox disponible con `onboarding@resend.dev` sin necesidad de verificar dominio propio.
SDK Python oficial. Dashboard con logs de entrega y webhooks disponibles.

## Decisión

Se adopta **Resend** como proveedor de email transaccional.

## Justificación

- El sandbox `onboarding@resend.dev` permite enviar emails reales durante el desarrollo
  sin registrar ni verificar un dominio propio — cero fricción de onboarding.
- La API es una sola llamada `POST /emails` con JSON — menos superficie de integración
  que SendGrid o SES.
- El `EmailPort` en el dominio abstrae el proveedor: cambiar de Resend a otro proveedor
  en el futuro es cambiar únicamente el adaptador en `infrastructure/email/`.
- El plan gratuito cubre holgadamente el volumen de un torneo de apnea.

## Consecuencias

**Positivas:**
- Onboarding inmediato para desarrollo y testing
- Dashboard con historial de emails enviados (útil para debugging)
- Webhooks disponibles para eventos de entrega (bounces, opens) — no usados en SP4 pero disponibles para SP5
- SDK Python oficial mantenido (`resend` package)

**Negativas:**
- Vendor lock-in leve. Mitigación: el `EmailPort` abstrae completamente el proveedor.
  Cambiar a SES o SendGrid en SP5 no requiere cambios en dominio ni aplicación,
  solo un nuevo adaptador en `infrastructure/email/`.

## Configuración

Variables de entorno requeridas:

| Variable | Descripción | Valor de desarrollo |
|----------|-------------|---------------------|
| `RESEND_API_KEY` | API key de Resend | Key del proyecto en resend.com |
| `NOTIFICACIONES_EMAIL_FROM` | Dirección remitente | `onboarding@resend.dev` (sandbox) |
| `RESEND_BASE_URL` | Base URL de la API | `https://api.resend.com` (default) |

**Fallback de desarrollo:** si `RESEND_API_KEY` no está configurada, `app.py` inyecta
`LoggingEmailAdapter` en lugar de `ResendEmailAdapter`. Este adaptador registra el email
en el log de la aplicación sin enviarlo — permite ejecutar el stack completo localmente
sin credenciales reales.
