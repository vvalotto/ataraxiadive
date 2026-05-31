---
title: "RF-PR-02 — No se permiten valores 0 o negativos."
type: trazabilidad-rf-item
rf_id: RF-PR-02
area: preparacion
parent_page: "[[RF-preparacion]]"
us_refs:
  - US-1.2.1-registrarap
estado: implementado
last_updated: "2026-05-28"
---

# RF-PR-02

**Área:** [[RF-preparacion|Preparación de Competencias]]  
**BCs:** [[competencia]], [[torneo]]

---

**Requerimiento:** ¿Hay valores mínimos/máximos para anuncios?  
**Respuesta:** No se permiten valores 0 o negativos.

## US que implementan este RF

### [[US-1.2.1-registrarap]]
*RegistrarAP*

**Tests:**
- `tests/features/US-1.2.1-registrar-ap.feature`
- `tests/integration/competencia/test_registrar_ap_integration.py`
