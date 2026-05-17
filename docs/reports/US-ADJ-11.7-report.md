# Reporte de Implementación — US-ADJ-11.7
## Frontend — Login con selector de rol

**Fecha:** 2026-05-16  
**SP:** SP-ADJ-11  
**Branch:** `feature/US-ADJ-11.7-login-selector-rol`  
**Tiempo total:** ~40 min (estimado: 50 min) · **Varianza:** +20%  
**Track:** informal (vibe coding) — frontend-only

---

## Resumen Ejecutivo

Implementado el selector de rol inline en `LoginPage` para usuarios multi-rol. El flujo de login ahora maneja correctamente la respuesta discriminada del backend: token directo (un rol) o solicitud de selección (múltiples roles). El store guarda `roles[]` completo y expone `setRol()`.

---

## Artefactos Modificados

| Artefacto | Tipo de cambio |
|-----------|----------------|
| `frontend/src/types/auth.ts` | Agregar `roles: RolUsuario[] \| null` y `setRol` a `AuthState` |
| `frontend/src/api/auth.ts` | Discriminated union `LoginResponse`, `loginApi` con `rolElegido?` opcional |
| `frontend/src/stores/useAuthStore.ts` | Extrae `roles[]` del JWT payload, `setRol()`, persistir `roles` en localStorage |
| `frontend/src/pages/LoginPage.tsx` | Selector inline, aviso post-registro multi-rol, error INV-11.7-04 |
| `frontend/src/pages/RegistroPage.tsx` | Fix type-narrowing en auto-login post-registro |
| `docs/specs/sp-adj-11/US-ADJ-11.7.md` | Notas actualizadas con contrato backend real |
| `tests/features/US-ADJ-11.7-login-selector-rol.feature` | Escenarios BDD documentales (5 scenarios) |
| `docs/plans/sp-adj-11/US-ADJ-11.7-plan.md` | Plan de implementación |

---

## Decisiones Técnicas

### Contrato backend real
La spec mencionaba `POST /auth/seleccionar-rol` (inexistente). El endpoint real es `POST /auth/login` con `rol_elegido?: string` (uppercase). La selección de rol se implementó re-llamando `loginApi(email, password, rol)` con las credenciales guardadas en estado local de `LoginPage`.

### Discriminated union en lugar de interfaz única
`LoginResponse = LoginResponseToken | LoginResponseRoleSelection` fuerza al consumidor a narrowar el tipo antes de acceder a los campos. TypeScript detecta accesos incorrectos en compile-time (bug en `RegistroPage.tsx` descubierto y corregido durante implementación).

### Fix colateral en RegistroPage
El auto-login post-registro llamaba `loginApi` y asumía respuesta `{ access_token }`. Ahora maneja el caso multi-rol: si el backend retorna `requires_role_selection`, redirige a `/login` con `state: { requiresRoleSelection: true }` en lugar de crashear.

---

## Invariantes Implementados

| ID | Estado |
|----|--------|
| INV-11.7-01 | ✅ Selector solo aparece si `pendingRoles.length >= 2` |
| INV-11.7-02 | ✅ `ADMIN` filtrado: `data.roles.filter(r => r !== 'ADMIN')` |
| INV-11.7-03 | ✅ `login(token)` en `rolMutation.onSuccess` actualiza `rol` activo en store |
| INV-11.7-04 | ✅ `roles.length === 0` → banner de error, sin selector |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| TypeScript (`tsc -b`) | ✅ 0 errores |
| Vite build | ✅ 190 módulos · 2.61s |
| CodeGuard | N/A (frontend-only) |
| DesignReviewer | N/A (frontend-only) |
| BDD steps | N/A (sin browser test framework) |

---

*Reporte generado: 2026-05-16 — US-ADJ-11.7 SP-ADJ-11*
