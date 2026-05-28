---
title: "RF-IN-08 — Solo categoría."
type: trazabilidad-rf-item
rf_id: RF-IN-08
area: inscripcion-atletas
parent_page: "[[RF-inscripcion-atletas]]"
us_refs:
  - US-3.2.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-IN-08

**Área:** [[RF-inscripcion-atletas|Inscripción de Atletas]]  
**BCs:** [[registro]], [[identidad]]

---

**Requerimiento:** ¿El género tiene efecto más allá de la categoría?  
**Respuesta:** **Solo categoría.**

## US que implementan este RF

### [[US-3.2.2]]
*Aggregate Atleta: registro, consulta y repositorio SQLite*

**Tests:**
- `tests/features/US-3.2.2-bc-registro-aggregate-atleta.feature`
- `tests/integration/registro/test_sqlite_atleta_repository.py`
