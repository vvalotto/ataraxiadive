---
title: "RF-US-04 — Sí. Se asigna un juez a cada [[disciplina]]."
type: trazabilidad-rf-item
rf_id: RF-US-04
area: usuarios-roles
parent_page: "[[RF-usuarios-roles]]"
us_refs:
  - US-3.2.1-bc-identidad-usuario-jwt-minimo-auth
  - US-3.4.2-auth-por-rol-en-apis-escribibles-con-jwt-middleware
estado: implementado
last_updated: "2026-05-28"
---

# RF-US-04

**Área:** [[RF-usuarios-roles|Usuarios, Roles y Permisos]]  
**BCs:** [[identidad]]

---

**Requerimiento:** ¿Un juez necesita ser asignado a disciplinas específicas?  
**Respuesta:** **Sí.** Se asigna un juez a cada [[disciplina]].

## US que implementan este RF

### [[US-3.2.1-bc-identidad-usuario-jwt-minimo-auth]]
*BC Identidad: Usuario + JWT mínimo + /auth*

**Tests:**
- `tests/features/US-3.2.1-bc-identidad-jwt.feature`
- `tests/integration/identidad/test_sqlite_usuario_repository.py`

### [[US-3.4.2-auth-por-rol-en-apis-escribibles-con-jwt-middleware]]
*Auth por rol en APIs escribibles con JWT middleware*

**Tests:**
- `tests/features/US-3.4.2-auth-jwt-middleware.feature`
