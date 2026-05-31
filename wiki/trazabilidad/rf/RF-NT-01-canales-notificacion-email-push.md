---
title: "RF-NT-01 — Email + push."
type: trazabilidad-rf-item
rf_id: RF-NT-01
area: notificaciones
parent_page: "[[RF-notificaciones]]"
us_refs:
  - US-4.5.1-aggregate-notificacion-ciclo-de-vida-idempotencia
  - US-4.5.2-emailport-resendemailadapter
  - US-4.5.3-politica-p-10-email-al-atleta-al-confirmar-inscripcion
  - US-4.5.5-cableado-p-10-al-endpoint-post-registro-inscripciones
estado: implementado
last_updated: "2026-05-28"
---

# RF-NT-01

**Área:** [[RF-notificaciones|Notificaciones]]  
**BCs:** [[notificaciones]]

---

**Requerimiento:** ¿Notificaciones solo por email o también push?  
**Respuesta:** **Email + push.**

## US que implementan este RF

### [[US-4.5.1-aggregate-notificacion-ciclo-de-vida-idempotencia]]
*Aggregate Notificacion: ciclo de vida + idempotencia*

**Tests:**
- `tests/features/US-4.5.1-notificacion-idempotencia.feature`
- `tests/integration/notificaciones/test_sqlite_notificacion_repository.py`

### [[US-4.5.2-emailport-resendemailadapter]]
*EmailPort + ResendEmailAdapter*

**Tests:**
- `tests/features/US-4.5.2-adaptador-email.feature`
- `tests/integration/notificaciones/test_resend_email_adapter.py`

### [[US-4.5.3-politica-p-10-email-al-atleta-al-confirmar-inscripcion]]
*Política P-10: email al atleta al confirmar inscripción*

**Tests:**
- `tests/features/US-4.5.3-politica-p10.feature`
- `tests/integration/notificaciones/test_politica_p10_integration.py`

### [[US-4.5.5-cableado-p-10-al-endpoint-post-registro-inscripciones]]
*Cableado P-10 al endpoint POST /registro/inscripciones*

**Tests:**
- `tests/features/US-4.5.5-cablear-p10-inscripcion.feature`
