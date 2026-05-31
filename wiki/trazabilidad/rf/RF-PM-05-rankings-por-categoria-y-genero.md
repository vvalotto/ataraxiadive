---
title: "RF-PM-05 — Sí. Rankings por [[disciplina]], categoría y género."
type: trazabilidad-rf-item
rf_id: RF-PM-05
area: resultados
parent_page: "[[RF-resultados]]"
us_refs:
  - US-3.3.1-torneo-id-opcional-en-competencia-para-overall
  - US-3.5.2-politica-p-09-overall-automatico-al-cerrar-torneo
  - US-ADJ-4.5-ranking-por-disciplina-categoria-en-bc-resultados
estado: implementado
last_updated: "2026-05-28"
---

# RF-PM-05

**Área:** [[RF-resultados|Premiación y Resultados]]  
**BCs:** [[resultados]]

---

**Requerimiento:** ¿Hay rankings separados por categoría y género?  
**Respuesta:** **Sí.** Rankings por [[disciplina]], categoría y género.

## US que implementan este RF

### [[US-3.3.1-torneo-id-opcional-en-competencia-para-overall]]
*torneo_id opcional en Competencia para overall*

**Tests:**
- `tests/features/US-3.3.1-torneo-id-competencia.feature`
- `tests/integration/competencia/test_torneo_id_integration.py`

### [[US-3.5.2-politica-p-09-overall-automatico-al-cerrar-torneo]]
*Política P-09: overall automático al cerrar torneo*

**Tests:**
- `tests/features/US-3.5.2-politica-p09.feature`

### [[US-ADJ-4.5-ranking-por-disciplina-categoria-en-bc-resultados]]
*US-ADJ-4.5 — Ranking por (disciplina, categoría) en BC Resultados*
