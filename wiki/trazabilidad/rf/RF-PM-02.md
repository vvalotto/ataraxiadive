---
title: "RF-PM-02 — Sí. Se denomina Overall."
type: trazabilidad-rf-item
rf_id: RF-PM-02
area: resultados
parent_page: "[[RF-resultados]]"
us_refs:
  - US-3.3.1
  - US-3.5.1
estado: implementado
last_updated: "2026-05-28"
---

# RF-PM-02

**Área:** [[RF-resultados|Premiación y Resultados]]  
**BCs:** [[resultados]]

---

**Requerimiento:** ¿Existe ranking general del torneo?  
**Respuesta:** **Sí.** Se denomina **Overall**.

## US que implementan este RF

### [[US-3.3.1]]
*torneo_id opcional en Competencia para overall*

**Tests:**
- `tests/features/US-3.3.1-torneo-id-competencia.feature`
- `tests/integration/competencia/test_torneo_id_integration.py`

### [[US-3.5.1]]
*Aggregate RankingOverall + CalcularOverallHandler*

**Tests:**
- `tests/features/US-3.5.1-ranking-overall.feature`
- `tests/integration/resultados/test_calcular_overall_integration.py`
