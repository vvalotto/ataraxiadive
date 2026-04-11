# Plan de Implementación: US-4.2.2 — Autenticación JWT

**Patrón:** Frontend React (Zustand + React Router v6)
**Producto:** frontend
**Estimación Total:** 1h 30min
**BDD:** 6 escenarios — validación manual (UI/E2E)

---

## Componentes a Implementar

### 1. Tipos compartidos: `src/types/auth.ts` (5 min)
- [ ] `type RolUsuario = 'juez' | 'organizador'`
- [ ] `interface AuthState { token, email, rol, login, logout }`

### 2. API client: `src/api/auth.ts` (10 min)
- [ ] `loginApi(email, password)` → `POST /auth/login`
  - Body: `{ email, password }`
  - Respuesta: `{ access_token: string, token_type: "bearer" }`
- [ ] Helper `decodeJwtPayload(token)` → extrae `email` y `rol` con `atob()` (sin dependencia externa)

### 3. Store: `src/stores/useAuthStore.ts` (15 min)
- [ ] Zustand store con `{ token, email, rol, login, logout }`
- [ ] `login(token)`: decodifica JWT → extrae `{ email, rol }` → setea estado
- [ ] `logout()`: limpia todo el estado → `{ token: null, email: null, rol: null }`
- [ ] Sin persistencia (`localStorage`/`sessionStorage`) — INV-AUTH-02

### 4. Componente: `src/pages/LoginPage.tsx` (20 min)
- [ ] Formulario: inputs `email` + `password` + botón "Iniciar sesión"
- [ ] `useMutation` (TanStack Query) → llama `loginApi`
- [ ] En éxito: `authStore.login(token)` → `navigate` a home del rol
- [ ] En error 401: muestra mensaje "Credenciales inválidas" inline
- [ ] Sin redirect si ya autenticado (manejo en `RequireRole`)

### 5. HOC/Guard: `src/components/RequireRole.tsx` (15 min)
- [ ] Props: `role: RolUsuario`, `children: ReactNode`
- [ ] Sin JWT → `<Navigate to="/login" replace />`
- [ ] JWT presente, rol incorrecto → `<Navigate to="/{rol_correcto}" replace />`
- [ ] JWT y rol correcto → renderiza `children`

### 6. Páginas stub (10 min)
- [ ] `src/pages/juez/JuezLayout.tsx` — placeholder "Panel del Juez"
- [ ] `src/pages/juez/DisciplinasPage.tsx` — placeholder (ruta `/juez/disciplinas`)
- [ ] `src/pages/organizador/OrganizadorLayout.tsx` — placeholder "Panel del Organizador"
- [ ] `src/pages/organizador/DashboardPage.tsx` — placeholder (ruta `/organizador/dashboard`)

### 7. Routing: `src/App.tsx` (15 min)
- [ ] Integrar `BrowserRouter` + rutas con React Router v6:
  - `/login` → `LoginPage` (pública)
  - `/` → redirect según rol del store (o `/login` si no autenticado)
  - `/juez/*` → `RequireRole role="juez"` → `JuezLayout` + subrutas
  - `/organizador/*` → `RequireRole role="organizador"` → `OrganizadorLayout` + subrutas
- [ ] `main.tsx`: wrappear con `BrowserRouter`

---

## Quality Gates

> US frontend — quality gate es `npm run build` exitcode 0 + validación manual de escenarios.

- [ ] `npm run build` sin errores TypeScript strict
- [ ] Escenarios BDD verificados manualmente en browser

---

**Estado:** 0/7 secciones completadas

*Plan generado: 2026-04-11 — US-4.2.2 INC-4.2 SP4*
