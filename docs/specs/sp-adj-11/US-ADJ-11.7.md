# US-ADJ-11.7: Frontend — Login con selector de rol

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: refactor frontend
**Área**: `frontend/` — `LoginPage.tsx` · `api/auth.ts` · `stores/useAuthStore.ts` · `types/auth.ts`
**Dependencias**: US-ADJ-11.1, US-ADJ-11.6
**Track de implementación**: informal (vibe coding) — solo toca `frontend/`

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-registro-roles.md` — S-01, S-04, S-05
- `docs/design/ux/prototipos/prototipo-registro-roles.html`

El wireframe S-01 define login estándar. El selector de rol no existe hoy como pantalla separada; se renderiza inline en `LoginPage` cuando aplica. El foco es la transición limpia hacia el portal correcto para usuarios con múltiples roles.

---

## Descripcion

Como usuario con múltiples roles (Atleta, Juez, Organizador),
quiero poder elegir con qué rol quiero ingresar al iniciar sesión,
para que la plataforma me muestre el portal correcto desde el primer momento.

---

## Estado actual vs. estado deseado

| Elemento | Estado actual | Estado deseado |
|----------|--------------|----------------|
| `LoginResponse` en `api/auth.ts` | `{ access_token, token_type }` | Discriminated union: token directo O `{ requires_role_selection, roles }` |
| `loginApi()` | retorna `LoginResponse` simple | retorna union tipada |
| `LoginPage` — `onSuccess` | llama `login(data.access_token)` sin más | si `requires_role_selection`, muestra selector de rol inline |
| `AuthState` en `types/auth.ts` | `rol: RolUsuario \| null` (un solo rol) | agrega `roles: RolUsuario[] \| null` (todos los roles del usuario) |
| `useAuthStore.login()` | decodifica JWT y extrae `rol` | también extrae `roles[]` del payload; si falta `roles` en JWT, construye array de un elemento con `rol` |
| `LoginPage` — redirect post-login | `portalPorRol(rol)` | si `roles.length > 1`, muestra selector; si es uno, redirect directo |

---

## Especificacion del comportamiento

### Caso A — Login desde `/registro` con `requires_role_selection`

El flujo de registro (US-ADJ-11.6) redirige a `/login` con
`state: { requiresRoleSelection: true }` cuando el usuario se registró con múltiples roles
y el backend no pudo emitir un token con rol único.

En este caso, `LoginPage` muestra un aviso informativo:
> "Tu cuenta tiene varios roles. Iniciá sesión y elegí con cuál querés entrar."

Después del login exitoso, si el usuario tiene múltiples roles, se muestra el selector.

### Caso B — Login normal de usuario multi-rol

El backend retorna `{ requires_role_selection: true, roles: ["ATLETA", "JUEZ"] }` 
en lugar de un `access_token` cuando el usuario tiene múltiples roles y el JWT no puede
expresar un solo rol.

`LoginPage.onSuccess` detecta esta respuesta y muestra el selector inline.
El usuario elige un rol → el frontend llama al endpoint de selección de rol con ese
rol seleccionado → recibe el token definitivo → `login(token)` → redirect.

### Caso C — Login normal de usuario con un solo rol

Sin cambios. `loginApi()` retorna `{ access_token, token_type }` → `login(token)` → redirect.

### Precondicion

- El usuario no está autenticado.
- El backend (US-ADJ-11.1) puede retornar `{ requires_role_selection: true, roles: [] }`.

### Postcondicion

- El usuario queda autenticado con un `rol` activo en el store.
- El store contiene `roles: RolUsuario[]` con la lista completa.
- El usuario es redirigido al portal del rol seleccionado.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.7-01 | El selector solo se muestra si el usuario tiene 2 o más roles. |
| INV-11.7-02 | El rol ADMIN nunca aparece en el selector visible al usuario. |
| INV-11.7-03 | Después de seleccionar un rol, el store refleja ese rol como `rol` activo. |
| INV-11.7-04 | Si el backend retorna `requires_role_selection` sin roles, se trata como error. |

---

## Criterios de aceptacion

```gherkin
Scenario: Login de usuario con un solo rol — sin cambios
  Given el usuario tiene únicamente el rol ATLETA
  When hace login con credenciales correctas
  Then el backend retorna access_token
  And el frontend redirige a /atleta sin mostrar selector

Scenario: Login de usuario multi-rol — backend retorna requires_role_selection
  Given el usuario tiene roles ATLETA y JUEZ
  When hace login con credenciales correctas
  Then el backend retorna requires_role_selection=true con roles=["ATLETA", "JUEZ"]
  And la LoginPage muestra el selector de rol inline
  And el usuario selecciona JUEZ
  Then el frontend emite el request de selección de rol
  And redirige a /juez/disciplinas

Scenario: Aviso informativo post-registro multi-rol
  Given el usuario fue redirigido desde /registro con state requiresRoleSelection=true
  When la LoginPage carga
  Then muestra el aviso "Tu cuenta tiene varios roles"
  And el formulario de login se muestra normalmente

Scenario: Selector no aparece para usuario de un solo rol
  Given el usuario tiene únicamente el rol ORGANIZADOR
  When hace login exitoso
  Then redirige directamente a /organizador/torneo sin mostrar selector
```

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/api/auth.ts` | Agregar `LoginResponseToken` y `LoginResponseRoleSelection` como types nombrados. `LoginResponse = LoginResponseToken \| LoginResponseRoleSelection`. Agregar `seleccionarRolApi(rol: RolUsuario): Promise<LoginResponseToken>` que llama `POST /auth/seleccionar-rol`. |
| `frontend/src/types/auth.ts` | Agregar `roles: RolUsuario[] \| null` a `AuthState`. Agregar `setRol: (rol: RolUsuario) => void`. |
| `frontend/src/stores/useAuthStore.ts` | `login()` extrae `roles[]` del JWT payload (campo `roles`). Si el campo no existe, construye `[payload.rol.toLowerCase()]`. `setRol(rol)` actualiza solo el campo `rol` activo. Persistir `roles` en localStorage. |
| `frontend/src/pages/LoginPage.tsx` | `onSuccess`: si `data.requires_role_selection === true`, guardar `data.roles` en estado local y mostrar selector. `handleRolSelect(rol)`: llama `seleccionarRolApi(rol)` → `login(token)` → redirect. Agregar aviso cuando `location.state?.requiresRoleSelection`. |

---

## Notas de implementacion

1. **Endpoint de selección de rol:** el backend (US-ADJ-11.1) expone `POST /auth/seleccionar-rol` con body `{ rol: string }` y retorna `{ access_token, token_type }`. El frontend llama este endpoint desde `seleccionarRolApi()`.

2. **Selector de rol UI:** botones tipo pill o cards (no dropdown) con los nombres de rol legibles. Mismo estilo visual que el resto de la pantalla de login.

3. **`roles` en JWT:** si el backend emite un token con `roles: []` en el payload, `useAuthStore.login()` lo extrae directamente. Si no está, deriva `[rol]` del campo `rol` existente. Retrocompatibilidad garantizada.

4. **`setRol` en store:** permite que el selector de rol post-login actualice el rol activo sin re-login completo si el token ya contiene todos los roles.

---

*Spec creada: 2026-05-16 — SP-ADJ-11*
