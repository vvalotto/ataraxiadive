---
title: "RF-EJ-08 — Sí. Metros con decimales."
type: trazabilidad-rf-item
rf_id: RF-EJ-08
area: ejecucion
parent_page: "[[RF-ejecucion]]"
us_refs:
  - US-1.2.1-registrarap
  - US-2.2.1-disciplinadescriptor-value-object-port
  - US-2.2.2-api-disciplina-aware-validacion-de-unidades
  - US-4.3.3-wizard-extendido-dns-bko-tarjeta-roja-con-motivodq-y
estado: implementado
last_updated: "2026-05-28"
---

# RF-EJ-08

**Área:** [[RF-ejecucion|Ejecución de Competencias]]  
**BCs:** [[competencia]]

---

**Requerimiento:** ¿Las distancias usan decimales?  
**Respuesta:** **Sí.** Metros con decimales.

## US que implementan este RF

### [[US-1.2.1-registrarap]]
*RegistrarAP*

**Tests:**
- `tests/features/US-1.2.1-registrar-ap.feature`
- `tests/integration/competencia/test_registrar_ap_integration.py`

### [[US-2.2.1-disciplinadescriptor-value-object-port]]
*DisciplinaDescriptor value object + port*

**Tests:**
- `tests/features/US-2.2.1-disciplina-descriptor.feature`
- `tests/integration/competencia/test_disciplina_descriptor_integration.py`

### [[US-2.2.2-api-disciplina-aware-validacion-de-unidades]]
*API disciplina-aware + validación de unidades*

**Tests:**
- `tests/features/US-2.2.2-api-disciplina-aware.feature`

### [[US-4.3.3-wizard-extendido-dns-bko-tarjeta-roja-con-motivodq-y]]
*Wizard extendido: DNS, BKO, tarjeta roja con MotivoDQ y BlancaConPenalizaciones*
