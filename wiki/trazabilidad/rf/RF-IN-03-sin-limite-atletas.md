---
title: "RF-IN-03 — No."
type: trazabilidad-rf-item
rf_id: RF-IN-03
area: inscripcion-atletas
parent_page: "[[RF-inscripcion-atletas]]"
us_refs:
  - US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar
  - US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por
estado: implementado
last_updated: "2026-05-28"
---

# RF-IN-03

**Área:** [[RF-inscripcion-atletas|Inscripción de Atletas]]  
**BCs:** [[registro]], [[identidad]]

---

**Requerimiento:** ¿Hay límite de atletas por torneo o disciplina?  
**Respuesta:** **No.**

## US que implementan este RF

### [[US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar]]
*Aggregate Inscripcion: inscribir, cancelar y listar*

**Tests:**
- `tests/features/US-3.2.3-inscripcion-atleta.feature`
- `tests/integration/registro/test_sqlite_inscripcion_repository.py`

### [[US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por]]
*ACL Torneo/Registro → Competencia: crear competencias por disciplina*

**Tests:**
- `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature`
