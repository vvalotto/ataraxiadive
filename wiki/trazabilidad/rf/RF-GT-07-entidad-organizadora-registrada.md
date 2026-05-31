---
title: "RF-GT-07 — Sí. Además del organizador como persona."
type: trazabilidad-rf-item
rf_id: RF-GT-07
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.1-aggregate-torneo-maquina-de-estados
  - US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite
estado: implementado
last_updated: "2026-05-28"
---

# RF-GT-07

**Área:** [[RF-gestion-torneo|Gestión del Torneo]]  
**BCs:** [[torneo]], [[competencia]]

---

**Requerimiento:** ¿Se registra la entidad organizadora (federación/club)?  
**Respuesta:** **Sí.** Además del organizador como persona.

## US que implementan este RF

### [[US-3.1.1-aggregate-torneo-maquina-de-estados]]
*Aggregate Torneo: máquina de estados*

**Tests:**
- `tests/features/US-3.1.1-aggregate-torneo.feature`
- `tests/integration/torneo/test_torneo_domain_integration.py`

### [[US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite]]
*API REST Torneo: CRUD + transiciones + repositorio SQLite*

**Tests:**
- `tests/features/US-3.1.2-api-rest-torneo.feature`
- `tests/integration/torneo/test_sqlite_torneo_repository.py`
