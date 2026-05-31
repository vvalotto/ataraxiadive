---
title: "RF-IN-09 — No. Una categoría por torneo."
type: trazabilidad-rf-item
rf_id: RF-IN-09
area: inscripcion-atletas
parent_page: "[[RF-inscripcion-atletas]]"
us_refs:
  - US-3.2.2-aggregate-atleta-registro-consulta-y-repositorio-sqlite
estado: implementado
last_updated: "2026-05-28"
---

# RF-IN-09

**Área:** [[RF-inscripcion-atletas|Inscripción de Atletas]]  
**BCs:** [[registro]], [[identidad]]

---

**Requerimiento:** ¿Un atleta puede inscribirse en categorías distintas por disciplina?  
**Respuesta:** **No.** Una categoría por torneo.

## US que implementan este RF

### [[US-3.2.2-aggregate-atleta-registro-consulta-y-repositorio-sqlite]]
*Aggregate Atleta: registro, consulta y repositorio SQLite*

**Tests:**
- `tests/features/US-3.2.2-bc-registro-aggregate-atleta.feature`
- `tests/integration/registro/test_sqlite_atleta_repository.py`
