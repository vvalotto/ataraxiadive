---
title: "RF-NT-04 — Sí."
type: trazabilidad-rf-item
rf_id: RF-NT-04
area: notificaciones
parent_page: "[[RF-notificaciones]]"
us_refs:
  - US-4.5.4
estado: implementado
last_updated: "2026-05-28"
---

# RF-NT-04

**Área:** [[RF-notificaciones|Notificaciones]]  
**BCs:** [[notificaciones]]

---

**Requerimiento:** ¿Se notifica a los atletas cuando se publican resultados finales?  
**Respuesta:** **Sí.**

## US que implementan este RF

### [[US-4.5.4]]
*Política P-11: email a atletas al publicar resultados*

**Tests:**
- `tests/features/US-4.5.4-politica-p11.feature`
- `tests/integration/notificaciones/test_politica_p11_integration.py`
