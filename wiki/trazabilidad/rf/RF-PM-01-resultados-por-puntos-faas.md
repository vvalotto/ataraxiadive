---
title: "RF-PM-01 — Pendiente. Es una regla de negocio configurable."
type: trazabilidad-rf-item
rf_id: RF-PM-01
area: resultados
parent_page: "[[RF-resultados]]"
us_refs:
  - US-3.3.1-torneo-id-opcional-en-competencia-para-overall
  - US-3.5.1-aggregate-rankingoverall-calcularoverallhandler
estado: implementado
last_updated: "2026-05-28"
---

# RF-PM-01

**Área:** [[RF-resultados|Premiación y Resultados]]  
**BCs:** [[resultados]]

---

**Requerimiento:** ¿Los resultados son por puntos o por marca absoluta?  
**Respuesta:** **Pendiente.** Es una regla de negocio configurable.

## US que implementan este RF

### [[US-3.3.1-torneo-id-opcional-en-competencia-para-overall]]
*torneo_id opcional en Competencia para overall*

**Tests:**
- `tests/features/US-3.3.1-torneo-id-competencia.feature`
- `tests/integration/competencia/test_torneo_id_integration.py`

### [[US-3.5.1-aggregate-rankingoverall-calcularoverallhandler]]
*Aggregate RankingOverall + CalcularOverallHandler*

**Tests:**
- `tests/features/US-3.5.1-ranking-overall.feature`
- `tests/integration/resultados/test_calcular_overall_integration.py`
