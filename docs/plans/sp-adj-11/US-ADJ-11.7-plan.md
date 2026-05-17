# Plan de Implementación — US-ADJ-11.7
## Frontend — Login con selector de rol

**Fecha:** 2026-05-16  
**Estimación total:** 50 min  
**Track:** informal (vibe coding) — solo toca `frontend/`  
**Branch:** `feature/US-ADJ-11.7-login-selector-rol`

---

## Hallazgo Fase 0 — Contrato backend real

La spec menciona `POST /auth/seleccionar-rol`, pero ese endpoint **no existe**.  
El backend (US-ADJ-11.1) maneja la selección vía `POST /auth/login` con `rol_elegido?: string` (uppercase).

Flujo real:
1. `POST /auth/login { email, password }` → si multi-rol → `{ requires_role_selection: true, roles: ["ATLETA", "JUEZ"] }`
2. `POST /auth/login { email, password, rol_elegido: "JUEZ" }` → `{ access_token, token_type }`

**Decisión:** `loginApi` acepta `rolElegido?: string` opcional. No se crea `seleccionarRolApi`.

---

## Tareas (orden obligatorio — dependencias en cadena)

### T1 — `frontend/src/types/auth.ts` (5 min)

Agregar a `AuthState`:
- `roles: RolUsuario[] | null` — lista completa de roles del usuario
- `setRol: (rol: RolUsuario) => void` — actualiza el rol activo sin re-login

### T2 — `frontend/src/api/auth.ts` (10 min)

- Renombrar `interface LoginResponse` → `LoginResponseToken` (campos: `access_token`, `token_type`)
- Agregar `interface LoginResponseRoleSelection` (campos: `requires_role_selection: true`, `roles: string[]`)
- `type LoginResponse = LoginResponseToken | LoginResponseRoleSelection`
- Agregar campo opcional `rol_elegido?: string` al body de `loginApi`
- Signature: `loginApi(email: string, password: string, rolElegido?: string): Promise<LoginResponse>`
- Actualizar `JwtPayload` para incluir `roles?: string[]` (campo opcional en JWT)

### T3 — `frontend/src/stores/useAuthStore.ts` (10 min)

- Agregar `roles: RolUsuario[] | null` al estado inicial (null)
- En `login(token)`: extraer `payload.roles` del JWT → si existe, mapear a `RolUsuario[]`; si no, construir `[payload.rol.toLowerCase()]`
- Agregar acción `setRol(rol)`: `set({ rol })`
- `logout()`: resetear `roles: null`
- Agregar `roles` y `setRol` al estado inicial del store
- Agregar `roles` a `partialize` para persistir en localStorage

### T4 — `frontend/src/pages/LoginPage.tsx` (20 min)

Estado local nuevo:
- `pendingRoles: string[] | null` — roles disponibles cuando el backend pide selección
- `pendingEmail / pendingPassword: string` — credenciales almacenadas para el segundo call

Lógica en `onSuccess(data)`:
- Si `'requires_role_selection' in data && data.requires_role_selection`:
  - Verificar que `data.roles.length > 0` (INV-11.7-04); si vacío → mostrar error
  - Guardar `pendingRoles = data.roles.filter(r => r !== 'ADMIN')` (INV-11.7-02)
  - Guardar `pendingEmail` y `pendingPassword`
- Si tiene `access_token` → flujo normal: `login(data.access_token)`

Nueva función `handleRolSelect(rol: string)`:
- Llama `loginApi(pendingEmail, pendingPassword, rol)` (rol en uppercase, ya viene así del backend)
- `onSuccess`: `login(data.access_token)` → redirect vía `portalPorRol`

Render:
- Aviso multi-rol: cuando `location.state?.requiresRoleSelection === true` — banner amber
- Selector inline: cuando `pendingRoles !== null` — reemplaza el formulario con botones tipo pill por rol
- Etiquetas legibles: `ATLETA → Atleta`, `JUEZ → Juez`, `ORGANIZADOR → Organizador`
- Error INV-11.7-04: banner rojo si `requires_role_selection` con roles vacíos

### T5 — Quality gates (5 min)

```bash
cd frontend && npm run build
```

- TypeScript sin errores de tipo
- Build exitoso sin warnings sobre los tipos nuevos

---

## Artefacto de output

`docs/reports/US-ADJ-11.7-report.md` — generado en Fase 9

---

## No aplica en esta US

- Tests unitarios Python / integración Python (frontend-only)
- BDD step definitions (sin browser test framework)
- CodeGuard / DesignReviewer (no toca `src/`)
- Phase 6 BDD validation

---

*Plan generado: 2026-05-16 — US-ADJ-11.7 SP-ADJ-11*
