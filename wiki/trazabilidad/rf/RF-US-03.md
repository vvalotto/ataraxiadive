---
title: "RF-US-03 — Mail + contraseña."
type: trazabilidad-rf-item
rf_id: RF-US-03
area: usuarios-roles
parent_page: "[[RF-usuarios-roles]]"
us_refs:
  - US-3.2.1
  - US-3.4.2
estado: implementado
last_updated: "2026-05-28"
---

# RF-US-03

**Área:** [[RF-usuarios-roles|Usuarios, Roles y Permisos]]  
**BCs:** [[identidad]]

---

**Requerimiento:** ¿Cómo se autentican los atletas?  
**Respuesta:** Mail + contraseña.

## US que implementan este RF

### [[US-3.2.1]]
*BC Identidad: Usuario + JWT mínimo + /auth*

**Tests:**
- `tests/features/US-3.2.1-bc-identidad-jwt.feature`
- `tests/integration/identidad/test_sqlite_usuario_repository.py`

### [[US-3.4.2]]
*Auth por rol en APIs escribibles con JWT middleware*

**Tests:**
- `tests/features/US-3.4.2-auth-jwt-middleware.feature`
