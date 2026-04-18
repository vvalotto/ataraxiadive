# Reporte de Implementación: US-4.2.2

**US:** US-4.2.2 — Autenticación JWT en frontend — login, contexto de sesión y rutas protegidas
**Incremento:** INC-4.2
**Sprint:** SP4 — La Plataforma
**Fecha:** 2026-04-11
**Branch:** `feature/US-4.2.2-autenticacion-jwt`
**Commit:** `9c6ca60`

---

## Resumen de Implementación

### Artefactos creados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Tipos | `frontend/src/types/auth.ts` | `RolUsuario`, `AuthState` |
| API client | `frontend/src/api/auth.ts` | `loginApi()` + `decodeJwtPayload()` |
| Store | `frontend/src/stores/useAuthStore.ts` | JWT en memoria, login/logout |
| Login UI | `frontend/src/pages/LoginPage.tsx` | Formulario + mutation + error inline |
| Guard | `frontend/src/components/RequireRole.tsx` | HOC por rol con redirects |
| Stub juez | `frontend/src/pages/juez/DisciplinasPage.tsx` | Placeholder + logout |
| Stub organizador | `frontend/src/pages/organizador/DashboardPage.tsx` | Placeholder + logout |
| App routing | `frontend/src/App.tsx` | BrowserRouter + 5 rutas |
| Main | `frontend/src/main.tsx` | BrowserRouter wrapper |
| Feature | `tests/features/US-4.2.2-autenticacion-jwt.feature` | 6 escenarios BDD |
| Plan | `docs/plans/sp4/US-4.2.2-plan.md` | Marcado como completado |
| Matrix | `docs/traceability/matrix.md` | v1.13 — US-4.2.2 implementada |

### Invariantes verificados

| Invariante | Descripción | Estado |
|-----------|-------------|--------|
| INV-AUTH-01 | Sin JWT → redirect `/login` | ✅ `RequireRole` → `<Navigate to="/login" />` |
| INV-AUTH-02 | Token solo en Zustand (memoria) | ✅ sin `localStorage`/`sessionStorage` |
| INV-AUTH-03 | Rutas `/juez/**` solo con rol juez | ✅ `RequireRole role="juez"` |
| INV-AUTH-04 | Password nunca persiste | ✅ solo en state local del form |
| INV-AUTH-05 | Logout limpia store completamente | ✅ `set({ token: null, email: null, rol: null })` |

---

## Decisiones técnicas

1. **`decodeJwtPayload` con `atob()`:** El claim `email` viene en el campo `sub` del JWT (convención estándar del backend). Se adapta `sub → email` en el store. Sin dependencia `jwt-decode` — INV-AUTH-02.

2. **`RootRedirect` como componente:** El redirect desde `/` según rol se encapsula en un componente separado (no inline en la ruta) para mantener el acceso al store limpio y sin side effects en JSX.

3. **`HOME_BY_ROL` como mapa:** El mapeo `rol → ruta home` centralizado en `RequireRole.tsx` — si se agregan roles futuros, se edita en un solo lugar.

4. **Proxy `/auth` en `vite.config.ts`:** El endpoint de login vive en `/auth/login` (prefijo del router de identidad), no en `/api/auth/login`.

---

## Escenarios BDD — Validación manual pendiente

| Escenario | Criterio | Estado |
|-----------|----------|--------|
| Login exitoso juez | store con JWT + rol "juez" + redirect `/juez/disciplinas` | ⏳ manual |
| Login exitoso organizador | store con JWT + rol "organizador" + redirect `/organizador/dashboard` | ⏳ manual |
| Credenciales inválidas | mensaje "Credenciales inválidas", store vacío | ⏳ manual |
| Ruta protegida sin sesión | redirect `/login` | ⏳ manual |
| Rol incorrecto | redirect a home del rol correcto | ⏳ manual |
| Logout | store vacío + redirect `/login` | ⏳ manual |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `npm run build` TypeScript strict | ✅ exitcode 0 — 92 módulos, 261KB bundle |
| Todos los invariantes AUTH | ✅ verificados en código |
| Validación manual escenarios BDD | ⏳ pendiente con backend corriendo |

---

## Cierre INC-4.2

Con US-4.2.2 implementada y mergeada, **INC-4.2 — Fundación Frontend** quedó
completo a nivel de código e integración en `develop`:

| US | Descripción | Estado |
|----|-------------|--------|
| US-4.2.1 | Scaffold Vite + React + PWA | ✅ mergeada a develop |
| US-4.2.2 | Autenticación JWT + rutas protegidas | ✅ mergeada a `develop` |

**Estado consolidado del incremento al 2026-04-11:**
- [x] PR US-4.2.2 → merge a `develop`
- [x] `DesignReviewer` manual consolidado del incremento (`0 CRITICAL · 142 WARNING`)
- [ ] Verificación manual de criterios de aceptación (ambas US)
- [ ] Registro en BL-004 activa

**Pendiente para el cierre funcional completo del incremento:**
- [ ] Verificación manual de criterios de aceptación (ambas US)
- [ ] Registro en BL-004 activa

---

*Generado: 2026-04-11 — `/implement-us US-4.2.2`*
