---
title: "RF-PR-03 — No. Una vez registrado, es definitivo."
type: trazabilidad-rf-item
rf_id: RF-PR-03
area: preparacion
parent_page: "[[RF-preparacion]]"
us_refs:
  - US-1.2.1
estado: implementado
last_updated: "2026-05-28"
---

# RF-PR-03

**Área:** [[RF-preparacion|Preparación de Competencias]]  
**BCs:** [[competencia]], [[torneo]]

---

**Requerimiento:** ¿Un atleta puede modificar su anuncio?  
**Respuesta:** **No.** Una vez registrado, es definitivo.

## US que implementan este RF

### [[US-1.2.1]]
*RegistrarAP*

**Tests:**
- `tests/features/US-1.2.1-registrar-ap.feature`
- `tests/integration/competencia/test_registrar_ap_integration.py`
