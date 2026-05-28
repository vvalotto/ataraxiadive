---
title: "RF-GT-02 — Configurable. Inicialmente: STA, DNF, DBF, DYN, SPE."
type: trazabilidad-rf-item
rf_id: RF-GT-02
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.2
  - US-3.3.2
  - US-4.1.3
  - US-ADJ-4.1
estado: implementado
last_updated: "2026-05-28"
---

# RF-GT-02

**Área:** [[RF-gestion-torneo|Gestión del Torneo]]  
**BCs:** [[torneo]], [[competencia]]

---

**Requerimiento:** ¿Qué disciplinas soporta el sistema?  
**Respuesta:** **Configurable.** Inicialmente: STA, DNF, DBF, DYN, SPE.

## US que implementan este RF

### [[US-3.1.2]]
*API REST Torneo: CRUD + transiciones + repositorio SQLite*

**Tests:**
- `tests/features/US-3.1.2-api-rest-torneo.feature`
- `tests/integration/torneo/test_sqlite_torneo_repository.py`

### [[US-3.3.2]]
*ACL Torneo/Registro → Competencia: crear competencias por disciplina*

**Tests:**
- `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature`

### [[US-4.1.3]]
*Subdisciplinas SPE: SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50*

### [[US-ADJ-4.1]]
*US-ADJ-4.1 — Renombrar DYNB→DBF y SPE2X50→SPE (acrónimos dominio real)*
