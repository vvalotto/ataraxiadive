---
title: "RF-US-01 — No. Un organizador por torneo."
type: trazabilidad-rf-item
rf_id: RF-US-01
area: usuarios-roles
parent_page: "[[RF-usuarios-roles]]"
us_refs:
  - US-3.2.1-bc-identidad-usuario-jwt-minimo-auth
estado: implementado
last_updated: "2026-05-28"
---

# RF-US-01

**Área:** [[RF-usuarios-roles|Usuarios, Roles y Permisos]]  
**BCs:** [[identidad]]

---

**Requerimiento:** ¿El administrador puede crear múltiples organizadores por torneo?  
**Respuesta:** **No.** Un organizador por torneo.

## US que implementan este RF

### [[US-3.2.1-bc-identidad-usuario-jwt-minimo-auth]]
*BC Identidad: Usuario + JWT mínimo + /auth*

**Tests:**
- `tests/features/US-3.2.1-bc-identidad-jwt.feature`
- `tests/integration/identidad/test_sqlite_usuario_repository.py`
