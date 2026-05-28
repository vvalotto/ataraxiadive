---
title: "RF-US-05 — Solo los resultados finales. No en tiempo real."
type: trazabilidad-rf-item
rf_id: RF-US-05
area: usuarios-roles
parent_page: "[[RF-usuarios-roles]]"
us_refs:
  - US-3.2.1
estado: implementado
last_updated: "2026-05-28"
---

# RF-US-05

**Área:** [[RF-usuarios-roles|Usuarios, Roles y Permisos]]  
**BCs:** [[identidad]]

---

**Requerimiento:** ¿Los atletas pueden ver resultados de otros durante la competencia?  
**Respuesta:** **Solo los resultados finales.** No en tiempo real.

## US que implementan este RF

### [[US-3.2.1]]
*BC Identidad: Usuario + JWT mínimo + /auth*

**Tests:**
- `tests/features/US-3.2.1-bc-identidad-jwt.feature`
- `tests/integration/identidad/test_sqlite_usuario_repository.py`
