---
title: "RF-GT-04 — Estado cancelado conservando la información (no se elimina)."
type: trazabilidad-rf-item
rf_id: RF-GT-04
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.1
  - US-3.1.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-GT-04

**Área:** [[RF-gestion-torneo|Gestión del Torneo]]  
**BCs:** [[torneo]], [[competencia]]

---

**Requerimiento:** ¿Qué significa cancelar un torneo?  
**Respuesta:** Estado cancelado conservando la información (no se elimina).

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
