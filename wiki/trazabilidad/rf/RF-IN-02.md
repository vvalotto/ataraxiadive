---
title: "RF-IN-02 — No."
type: trazabilidad-rf-item
rf_id: RF-IN-02
area: inscripcion-atletas
parent_page: "[[RF-inscripcion-atletas]]"
us_refs:
  - US-3.2.2
  - US-3.3.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-IN-02

**Área:** [[RF-inscripcion-atletas|Inscripción de Atletas]]  
**BCs:** [[registro]], [[identidad]]

---

**Requerimiento:** ¿El brevet es obligatorio?  
**Respuesta:** **No.**

## US que implementan este RF

### [[US-3.2.2]]
*Aggregate Atleta: registro, consulta y repositorio SQLite*

**Tests:**
- `tests/features/US-3.2.2-bc-registro-aggregate-atleta.feature`
- `tests/integration/registro/test_sqlite_atleta_repository.py`

### [[US-3.3.2]]
*ACL Torneo/Registro → Competencia: crear competencias por disciplina*

**Tests:**
- `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature`
