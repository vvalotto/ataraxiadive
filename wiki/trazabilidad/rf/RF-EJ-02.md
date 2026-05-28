---
title: "RF-EJ-02 — Descalificación inmediata. Sin tiempo de espera."
type: trazabilidad-rf-item
rf_id: RF-EJ-02
area: ejecucion
parent_page: "[[RF-ejecucion]]"
us_refs:
  - US-1.2.2
  - US-1.2.5
  - US-4.3.5
estado: implementado
last_updated: "2026-05-28"
---

# RF-EJ-02

**Área:** [[RF-ejecucion|Ejecución de Competencias]]  
**BCs:** [[competencia]]

---

**Requerimiento:** ¿Qué pasa si un atleta no se presenta (DNS)?  
**Respuesta:** **Descalificación inmediata.** Sin tiempo de espera.

## US que implementan este RF

### [[US-1.2.2]]
*LlamarAtleta*

**Tests:**
- `tests/features/US-1.2.2-llamar-atleta.feature`
- `tests/integration/competencia/test_llamar_atleta_integration.py`

### [[US-1.2.5]]
*RegistrarDNS*

**Tests:**
- `tests/features/US-1.2.5-registrar-dns.feature`
- `tests/integration/competencia/test_registrar_dns_integration.py`

### [[US-4.3.5]]
*Adaptación wizard para STA (vías respiratorias)*
