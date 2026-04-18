# US-4.2.2: Autenticación JWT en frontend — login, contexto de sesión y rutas protegidas

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.2
**Bounded Context**: `frontend` + `identidad` (consumido, sin cambios en backend)
**Capas afectadas**: `frontend/src/stores/`, `frontend/src/pages/`, `frontend/src/api/`

---

## Descripción

Como **juez u organizador**,
quiero **iniciar sesión con mis credenciales y que la aplicación recuerde mi rol**
para **acceder únicamente a las pantallas que me corresponden y que mis acciones
queden registradas con mi identidad**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Store (Zustand) | `useAuthStore` | JWT, email, rol activo, métodos login/logout |
| API client | `api/auth.ts` | Llama a `POST /auth/login` del BC Identidad |
| Componente | `LoginPage` | Formulario email + password |
| HOC / Guard | `RequireRole` | Protege rutas — redirige a `/login` si no autenticado o rol incorrecto |
| Tipo | `RolUsuario` | `"juez"` \| `"organizador"` |

### Lenguaje ubicuo relevante

- **JWT (JSON Web Token):** credencial firmada que el backend emite al autenticar
  al usuario. El frontend la incluye en cada request como `Authorization: Bearer <token>`.
- **Rol:** perfil de acceso del usuario — `juez` u `organizador`. Determina
  qué rutas puede ver.
- **Ruta protegida:** ruta de la aplicación que requiere sesión activa con un rol
  específico para ser accedida.
- **Sesión:** estado de autenticación del usuario mientras el token sea válido.

---

## Especificación del comportamiento

### Invariantes de autenticación

- **INV-AUTH-01:** Ninguna ruta de negocio es accesible sin JWT válido en el store.
  Cualquier intento de acceso directo redirige a `/login`.
- **INV-AUTH-02:** El JWT se almacena únicamente en el store Zustand (memoria).
  Nunca en `localStorage` ni `sessionStorage` — se pierde al cerrar la pestaña.
- **INV-AUTH-03:** Las rutas `/juez/**` son accesibles solo con rol `juez`.
  Las rutas `/organizador/**` solo con rol `organizador`. Rol incorrecto →
  redirect a la home del rol correcto.
- **INV-AUTH-04:** Las credenciales (password) nunca se almacenan en el store
  ni en ningún mecanismo de persistencia del cliente.
- **INV-AUTH-05:** Al hacer logout, el store se limpia completamente y el usuario
  es redirigido a `/login`.

### Operación principal

**Nombre**: `login(email, password)`

| | Descripción |
|---|---|
| **Precondición** | El usuario no tiene sesión activa. Las credenciales corresponden a un usuario registrado y activo en BC Identidad. |
| **Postcondición** | `useAuthStore` contiene `{ token, email, rol }`. El usuario es redirigido a la home de su rol: `/juez/disciplinas` (juez) o `/organizador/dashboard` (organizador). |
| **Eventos generados** | N/A — la autenticación ocurre en el backend (BC Identidad ya implementado). El frontend solo consume el JWT resultante. |
| **Excepciones** | `CredencialesInvalidas` (HTTP 401 del backend) → mensaje de error en el formulario, sin redirect. |

**Ejemplo concreto:**

```
Precondición:  usuario "juez@ataraxia.com" registrado con rol juez, sin sesión activa.
Operación:     login(email="juez@ataraxia.com", password="secreto")
Postcondición: useAuthStore = { token: "eyJ...", email: "juez@ataraxia.com", rol: "juez" }
               Redirect → /juez/disciplinas

Precondición:  usuario intenta acceder a /organizador/dashboard sin sesión.
Operación:     navegación directa a URL
Postcondición: RequireRole redirige a /login
               Después del login exitoso como organizador → redirect a /organizador/dashboard
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.2.2 — Autenticación JWT con rutas protegidas por rol

  Background:
    Given la aplicación React está corriendo
    And el backend BC Identidad está disponible en localhost:8000

  Scenario: login exitoso como juez
    Given el usuario "juez@ataraxia.com" existe con rol juez
    When ingresa email "juez@ataraxia.com" y password correcto en la pantalla de login
    Then el store useAuthStore contiene el JWT y rol "juez"
    And el usuario es redirigido a /juez/disciplinas

  Scenario: login exitoso como organizador
    Given el usuario "org@ataraxia.com" existe con rol organizador
    When ingresa email "org@ataraxia.com" y password correcto
    Then el store useAuthStore contiene el JWT y rol "organizador"
    And el usuario es redirigido a /organizador/dashboard

  Scenario: login con credenciales inválidas
    When ingresa credenciales incorrectas en el formulario de login
    Then el formulario muestra el mensaje "Credenciales inválidas"
    And el store useAuthStore permanece vacío
    And el usuario permanece en /login

  Scenario: acceso a ruta protegida sin sesión
    Given el usuario no tiene sesión activa
    When navega directamente a /juez/disciplinas
    Then es redirigido a /login

  Scenario: acceso a ruta de rol incorrecto
    Given el usuario tiene sesión activa con rol "juez"
    When intenta navegar a /organizador/dashboard
    Then es redirigido a /juez/disciplinas

  Scenario: logout limpia la sesión
    Given el usuario tiene sesión activa
    When ejecuta logout
    Then useAuthStore queda vacío
    And el usuario es redirigido a /login
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — el backend BC Identidad ya está implementado (SP3).
  El frontend consume `POST /auth/login` sin modificar el backend.

**Capa(s) afectadas:**
- [x] Infrastructure / Frontend — `api/auth.ts`, `stores/useAuthStore.ts`, `pages/LoginPage.tsx`, HOC `RequireRole`
- [ ] Domain — no aplica (BC Identidad no se modifica)
- [ ] Application — no aplica

---

## Referencias

- Decisiones de stack: `docs/design/ux/decisiones-frontend.md` §D-02 (routing + guards), §D-03 (Zustand)
- BC Identidad — endpoint: `POST /auth/login` → `{ access_token, token_type }`
- BC Identidad — dependencia: `GET /api/**` con header `Authorization: Bearer <token>`
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.2`
- US precedente: `US-4.2.1` (el scaffold debe estar listo)

---

## Notas de implementación

- **Endpoint de login:** `POST /auth/login` con body `{ email, password }`.
  Responde `{ access_token: string, token_type: "bearer" }`.
  El `rol` no viene en la respuesta del login — hay que decodificar el payload
  del JWT (campo `rol` en el claim) sin verificar la firma (eso es del backend).
- **`useAuthStore`** con Zustand — estructura mínima:
  ```ts
  interface AuthState {
    token: string | null
    email: string | null
    rol: 'juez' | 'organizador' | null
    login: (token: string) => void
    logout: () => void
  }
  ```
  El método `login(token)` decodifica el JWT con `atob()` para extraer `email` y `rol`.
  No uses `jwt-decode` como dependencia — el payload es Base64 estándar.
- **`RequireRole`** — wrapper de React Router:
  ```tsx
  <RequireRole role="juez">
    <JuezLayout />
  </RequireRole>
  ```
  Si no autenticado → `<Navigate to="/login" />`.
  Si rol incorrecto → `<Navigate to="/{rol_correcto}" />`.
- **Sin persistencia del token:** al recargar la página, el store se vacía y el
  usuario debe loguearse de nuevo. Esto es intencional (INV-AUTH-02) — la persistencia
  offline de sesión se evalúa en INC-4.4.
- **Rutas configuradas en esta US** (base para INC-4.3 y siguientes):
  - `/login` → `LoginPage` (pública)
  - `/` → redirect según rol del store
  - `/juez/*` → protegida con `RequireRole role="juez"`
  - `/organizador/*` → protegida con `RequireRole role="organizador"`
  Las páginas internas (`/juez/disciplinas`, etc.) son stubs vacíos en esta US.
- **Skip BDD en Fase 1:** los escenarios son de UI — se validan manualmente.

---

*Redactado: 2026-04-09 — INC-4.2 Fundación Frontend*
