---
title: "RF-PM-06 — En la plataforma; descargables."
type: trazabilidad-rf-item
rf_id: RF-PM-06
area: resultados
parent_page: "[[RF-resultados]]"
us_refs:
  - US-3.5.3-api-get-resultados-{torneo-id}-overall
estado: implementado
last_updated: "2026-05-28"
---

# RF-PM-06

**Área:** [[RF-resultados|Premiación y Resultados]]  
**BCs:** [[resultados]]

---

**Requerimiento:** ¿Cómo se publican los resultados?  
**Respuesta:** En la plataforma; descargables.

## US que implementan este RF

### [[US-3.5.3-api-get-resultados-{torneo-id}-overall]]
*API GET /resultados/{torneo_id}/overall*

**Tests:**
- `tests/features/US-3.5.3-api-overall.feature`
- `tests/integration/resultados/test_obtener_overall_integration.py`
