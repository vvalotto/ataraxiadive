---
title: "RF-GT-02 — Configurable. Inicialmente: STA, DNF, DBF, DYN, SPE."
type: trazabilidad-rf-item
rf_id: RF-GT-02
area: gestion-torneo
parent_page: "[[RF-gestion-torneo]]"
us_refs:
  - US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite
  - US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por
  - US-4.1.3-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50
  - US-ADJ-4.1-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real
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

### [[US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite]]
*API REST Torneo: CRUD + transiciones + repositorio SQLite*

**Tests:**
- `tests/features/US-3.1.2-api-rest-torneo.feature`
- `tests/integration/torneo/test_sqlite_torneo_repository.py`

### [[US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por]]
*ACL Torneo/Registro → Competencia: crear competencias por disciplina*

**Tests:**
- `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature`

### [[US-4.1.3-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50]]
*Subdisciplinas SPE: SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50*

### [[US-ADJ-4.1-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real]]
*US-ADJ-4.1 — Renombrar DYNB→DBF y SPE2X50→SPE (acrónimos dominio real)*
