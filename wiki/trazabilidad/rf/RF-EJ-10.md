---
title: "RF-EJ-10 — Solo el resultado (tarjeta blanca/amarilla/roja)."
type: trazabilidad-rf-item
rf_id: RF-EJ-10
area: ejecucion
parent_page: "[[RF-ejecucion]]"
us_refs:
  - US-1.2.4
  - US-1.4.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-EJ-10

**Área:** [[RF-ejecucion|Ejecución de Competencias]]  
**BCs:** [[competencia]]

---

**Requerimiento:** ¿Se registra el SP por separado o solo su efecto?  
**Respuesta:** **Solo el resultado** (tarjeta blanca/amarilla/roja).

## US que implementan este RF

### [[US-1.2.4]]
*AsignarTarjeta (blanca/roja)*

**Tests:**
- `tests/features/US-1.2.4-asignar-tarjeta.feature`
- `tests/integration/competencia/test_asignar_tarjeta_integration.py`

### [[US-1.4.2]]
*Flujo E2E + audit log GET /events*

**Tests:**
- `tests/features/US-1.4.2-flujo-e2e.feature`
- `tests/integration/competencia/test_flujo_e2e.py`
