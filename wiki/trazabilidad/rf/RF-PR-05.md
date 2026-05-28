---
title: "RF-PR-05 — Depende de la [[disciplina]]: por distancia → menor a mayor;…"
type: trazabilidad-rf-item
rf_id: RF-PR-05
area: preparacion
parent_page: "[[RF-preparacion]]"
us_refs:
  - US-2.1.2
  - US-4.1.4
  - US-ADJ-4.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-PR-05

**Área:** [[RF-preparacion|Preparación de Competencias]]  
**BCs:** [[competencia]], [[torneo]]

---

**Requerimiento:** ¿Cómo se determina el orden de salida?  
**Respuesta:** Depende de la [[disciplina]]: **por distancia → menor a mayor; por tiempo → mayor a menor.**

## US que implementan este RF

### [[US-2.1.2]]
*GenerarGrilla / RegenerarGrilla*

**Tests:**
- `tests/features/US-2.1.2-generar-grilla.feature`
- `tests/integration/competencia/test_generar_grilla_integration.py`

### [[US-4.1.4]]
*Orden SPE descendente en GrillaDeSalida*

**Tests:**
- `tests/features/US-4.1.4-orden-grilla-reglamentario.feature`

### [[US-ADJ-4.2]]
*US-ADJ-4.2 — Corregir orden grilla STA: ascendente*
