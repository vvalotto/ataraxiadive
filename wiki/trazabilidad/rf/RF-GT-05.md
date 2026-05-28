---
title: "RF-GT-05 — Sí. Se puede volver de etapas (ej: Ejecución → Preparación)."
type: trazabilidad-rf-item
rf_id: RF-GT-05
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.1
  - US-3.1.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-GT-05

**Área:** [[RF-gestion-torneo|Gestión del Torneo]]  
**BCs:** [[torneo]], [[competencia]]

---

**Requerimiento:** ¿Hay restricciones para transición entre fases?  
**Respuesta:** **Sí.** Se puede volver de etapas (ej: Ejecución → Preparación).

## US que implementan este RF

### [[US-3.1.1]]
*Aggregate Torneo: máquina de estados*

**Tests:**
- `tests/features/US-3.1.1-aggregate-torneo.feature`
- `tests/integration/torneo/test_torneo_domain_integration.py`

### [[US-3.1.2]]
*API REST Torneo: CRUD + transiciones + repositorio SQLite*

**Tests:**
- `tests/features/US-3.1.2-api-rest-torneo.feature`
- `tests/integration/torneo/test_sqlite_torneo_repository.py`
