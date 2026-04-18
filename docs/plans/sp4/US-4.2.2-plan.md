# Plan de Implementación: US-4.2.2 — Autenticación JWT

**Patrón:** Frontend React (Zustand + React Router v6)
**Producto:** frontend
**Estimación Total:** 1h 30min
**BDD:** 6 escenarios — validación manual (UI/E2E)

---

## Componentes a Implementar

### 1. Tipos compartidos: `src/types/auth.ts` (5 min)
- [x] `type RolUsuario = 'juez' | 'organizador'`
- [x] `interface AuthState { token, email, rol, login, logout }`

### 2. API client: `src/api/auth.ts` (10 min)
- [x] `loginApi(email, password)` → `POST /auth/login`
- [x] `decodeJwtPayload(token)` → extrae `email` (claim `sub`) y `rol` con `atob()`

### 3. Store: `src/stores/useAuthStore.ts` (15 min)
- [x] Zustand store con `{ token, email, rol, login, logout }`
- [x] `login(token)`: decodifica JWT → extrae `{ sub→email, rol }` → setea estado
- [x] `logout()`: limpia todo el estado
- [x] Sin persistencia — INV-AUTH-02 ✅

### 4. Componente: `src/pages/LoginPage.tsx` (20 min)
- [x] Formulario email + password
- [x] `useMutation` → `loginApi` → `authStore.login(token)` en éxito
- [x] Error 401 → "Credenciales inválidas" inline
- [x] Redirect automático si ya autenticado (por rol en store)

### 5. HOC/Guard: `src/components/RequireRole.tsx` (15 min)
- [x] Sin JWT → `<Navigate to="/login" replace />`
- [x] Rol incorrecto → `<Navigate to={HOME_BY_ROL[rol]} replace />`
- [x] Rol correcto → renderiza children

### 6. Páginas stub (10 min)
- [x] `src/pages/juez/DisciplinasPage.tsx` — placeholder + logout
- [x] `src/pages/organizador/DashboardPage.tsx` — placeholder + logout

### 7. Routing: `src/App.tsx` + `src/main.tsx` (15 min)
- [x] `BrowserRouter` en `main.tsx`
- [x] `Routes`: `/login`, `/` (RootRedirect), `/juez/disciplinas`, `/organizador/dashboard`, `*`
- [x] `RootRedirect`: según rol → home del rol o `/login`
- [x] Proxy `/auth` agregado a `vite.config.ts`

---

## Quality Gates

- [x] `npm run build` exitcode 0 — 92 módulos, sin errores TypeScript strict
- [ ] Escenarios BDD verificados manualmente en browser (pendiente)

---

**Estado:** 7/7 secciones completadas — verificación manual pendiente

*Plan generado: 2026-04-11 — US-4.2.2 INC-4.2 SP4*
*Implementado: 2026-04-11*
