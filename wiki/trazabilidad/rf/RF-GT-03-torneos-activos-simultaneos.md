---
title: "RF-GT-03 — Sí."
type: trazabilidad-rf-item
rf_id: RF-GT-03
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.1-aggregate-torneo-maquina-de-estados
  - US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite
  - US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por
estado: implementado
last_updated: "2026-05-28"
---

# RF-GT-03

**Área:** [[RF-gestion-torneo|Gestión del Torneo]]  
**BCs:** [[torneo]], [[competencia]]

---

**Requerimiento:** ¿Pueden existir múltiples torneos activos simultáneamente?  
**Respuesta:** **Sí.**

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

### [[US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por]]
*ACL Torneo/Registro → Competencia: crear competencias por disciplina*

**Tests:**
- `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature`
