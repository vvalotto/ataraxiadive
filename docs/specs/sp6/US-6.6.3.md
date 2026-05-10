# US-6.6.3: Navegación contextual — redirect al login y destino post-login por rol

**Estado**: `Pending`
**Incremento**: INC-6.6 — Portal Público
**Bounded Context**: frontend
**Capas afectadas**:
- `frontend/src/App.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/components/RequireRole.tsx` (o nuevo `useRedirectAfterLogin.ts`)

---

## Descripción

Como **visitante del portal**,
quiero **que si pulso una acción que requiere autenticación, me lleve al login y luego me dirija directamente al destino correcto**
para **no perder el contexto de lo que quería hacer**.

---

## Contexto

El flujo actual es:
1. Usuario no autenticado → `/` → `RootRedirect` → `/login`
2. Post-login → `RootRedirect` → portal según rol (sin contexto del destino original)

El nuevo flujo con el portal público:
1. Usuario no autenticado → `/torneos` (sin redirect)
2. Usuario pulsa "Inscribirse" en un torneo → necesita auth → guardar destino → `/login`
3. Post-login → navegar al destino guardado (si el rol coincide) o al portal del rol

Además, `RootRedirect` debe cambiar: un visitante no autenticado que llega a `/` debe ver `/torneos` en lugar de `/login`.

---

## Especificación

### Tarea 1 — Cambiar `RootRedirect` para visitantes no autenticados

| | |
|---|---|
| **Precondición** | `RootRedirect` en `App.tsx:38` manda a `/login` cuando no hay token |
| **Postcondición** | Un visitante sin sesión que llega a `/` es redirigido a `/torneos` |
| **Invariante** | Los usuarios autenticados siguen siendo redirigidos a su portal de rol |

```tsx
function RootRedirect() {
  const rol = useAuthStore((s) => s.rol)
  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/torneo" replace />
  if (rol === 'atleta') return <Navigate to="/atleta" replace />
  return <Navigate to="/torneos" replace />  // antes era /login
}
```

### Tarea 2 — Guardar destino antes de redirigir al login

| | |
|---|---|
| **Precondición** | El usuario no autenticado pulsa una acción que requiere login (ej: "Inscribirse") |
| **Postcondición** | El destino queda guardado en `sessionStorage` antes de navegar a `/login` |
| **Invariante** | Si el usuario cierra la pestaña, el destino guardado no persiste (sessionStorage, no localStorage) |

Crear hook `useNavigateWithRedirect`:

```tsx
// frontend/src/hooks/useNavigateWithRedirect.ts
export function useNavigateWithRedirect() {
  const navigate = useNavigate()
  const token = useAuthStore((s) => s.token)

  return (destino: string) => {
    if (!token) {
      sessionStorage.setItem('redirectAfterLogin', destino)
      navigate('/login')
    } else {
      navigate(destino)
    }
  }
}
```

Usar este hook en `PublicTorneosPage` al pulsar los botones de acción.

### Tarea 3 — Post-login: navegar al destino guardado

| | |
|---|---|
| **Precondición** | El usuario completa el login exitosamente; puede haber un `redirectAfterLogin` en sessionStorage |
| **Postcondición** | Si existe destino guardado y el rol del usuario puede acceder a él → navegar al destino; sino → portal del rol |
| **Invariante** | Limpiar `redirectAfterLogin` de sessionStorage después de usarlo |

Modificar la lógica post-login en `LoginPage.tsx`:

```tsx
// Después de login exitoso:
const redirect = sessionStorage.getItem('redirectAfterLogin')
sessionStorage.removeItem('redirectAfterLogin')

if (redirect) {
  // Verificar que el rol puede acceder al destino
  const puedeAcceder = esDestinoCompatible(redirect, rol)
  navigate(puedeAcceder ? redirect : portalPorRol(rol), { replace: true })
} else {
  navigate(portalPorRol(rol), { replace: true })
}

function portalPorRol(rol: string): string {
  if (rol === 'juez') return '/juez/disciplinas'
  if (rol === 'organizador') return '/organizador/torneo'
  return '/atleta'
}

function esDestinoCompatible(destino: string, rol: string): boolean {
  if (destino.startsWith('/atleta') && rol === 'atleta') return true
  if (destino.startsWith('/juez') && rol === 'juez') return true
  if (destino.startsWith('/organizador') && rol === 'organizador') return true
  return false
}
```

### Tarea 4 — Link "Volver al portal" en LoginPage

| | |
|---|---|
| **Precondición** | `LoginPage` no tiene link de salida para visitantes no registrados |
| **Postcondición** | `LoginPage` muestra un link "Ver torneos" que lleva a `/torneos` |
| **Invariante** | No cambiar el formulario de login |

Agregar debajo del formulario:

```tsx
<p className="text-center text-sm text-gray-500 mt-4">
  ¿Solo querés ver los torneos?{' '}
  <Link to="/torneos" className="text-blue-600 underline">
    Ver torneos
  </Link>
</p>
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.6.3 — Navegación contextual y redirect post-login

  Scenario: Visitante sin login llega a / y es redirigido a /torneos
    Given el usuario no está autenticado
    When navega a /
    Then es redirigido a /torneos (no a /login)

  Scenario: Clic en "Inscribirse" sin login guarda destino y redirige al login
    Given el usuario no está autenticado en /torneos
    When pulsa "Inscribirse" en un torneo con id "abc-123"
    Then sessionStorage["redirectAfterLogin"] = "/atleta/torneos/abc-123/inscripcion"
    And es redirigido a /login

  Scenario: Post-login con destino guardado compatible con rol
    Given el usuario tiene redirectAfterLogin="/atleta/torneos/abc-123/inscripcion" en sessionStorage
    When hace login como atleta exitosamente
    Then es redirigido a /atleta/torneos/abc-123/inscripcion
    And sessionStorage["redirectAfterLogin"] es eliminado

  Scenario: Post-login con destino guardado incompatible con rol
    Given el usuario tiene redirectAfterLogin="/atleta/torneos/abc-123/inscripcion" en sessionStorage
    When hace login como organizador
    Then es redirigido a /organizador/torneo (destino por defecto del rol)
    And sessionStorage["redirectAfterLogin"] es eliminado

  Scenario: Post-login sin destino guardado usa portal por defecto
    Given no hay redirectAfterLogin en sessionStorage
    When hace login como juez
    Then es redirigido a /juez/disciplinas

  Scenario: LoginPage muestra link para volver al portal público
    Given el usuario está en /login
    Then existe un link "Ver torneos" que navega a /torneos
```

---

## Notas de implementación

- **`sessionStorage` vs `localStorage`**: usar `sessionStorage` — el destino es contextual a la sesión, no debe persistir si el usuario abre el sistema en otra pestaña o vuelve al día siguiente.
- **Seguridad**: `esDestinoCompatible` evita que un atacante inyecte un redirect malicioso pasando una URL externa. Limitar a prefijos de rutas internas.
- **Usuarios autenticados en `/torneos`**: si un usuario ya tiene sesión y navega a `/torneos`, simplemente ve la página sin redirect — es una página pública, no un portal privado.
- **El cambio en `RootRedirect`** es el más visible para usuarios existentes: en lugar de caer en `/login` al escribir la URL raíz, caerán en `/torneos`. Los usuarios que ya saben su URL de portal no se ven afectados.

---

## Referencias

- US-6.6.2: `PublicTorneosPage` donde se usan los botones de acción
- `frontend/src/App.tsx:38` — `RootRedirect`
- `frontend/src/pages/LoginPage.tsx` — lógica post-login
- `frontend/src/components/RequireRole.tsx` — patrón de auth guard existente
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.6

---

*Redactado: 2026-05-10 — SP6 INC-6.6*
