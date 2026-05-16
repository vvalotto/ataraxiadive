# US-ADJ-11.6: Frontend — Registro multi-rol

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: refactor frontend
**Área**: `frontend/` — `RegistroPage.tsx` · `api/identidad.ts`
**Dependencias**: US-ADJ-11.1, US-ADJ-11.3, US-ADJ-11.4, US-ADJ-11.5
**Track de implementación**: informal (vibe coding) — solo toca `frontend/`

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-registro-roles.md` — S-02, S-02b, S-02c, S-04
- `docs/design/ux/prototipos/prototipo-registro-roles.html`

El wireframe define un flujo de 3 pasos. Esta US adapta ese flujo al contexto de multi-rol sin cambiar la estructura de pantalla única actual (la complejidad del wizard queda diferida). El foco es el selector multi-rol y las secciones de datos por rol.

---

## Descripcion

Como usuario que se registra en AtaraxiaDive,
quiero poder seleccionar uno o más roles (Atleta, Juez, Organizador)
para que mi cuenta refleje todas mis actividades desde el inicio.

---

## Estado actual vs. estado deseado

| Elemento | Estado actual | Estado deseado |
|----------|--------------|----------------|
| `RegistroPage` — selector de rol | `<select>` de un solo rol | Checkboxes múltiples (ATLETA, JUEZ, ORGANIZADOR) |
| Secciones de datos por rol | No existen | Sección colapsable por rol seleccionado |
| `CrearUsuarioRequest.rol` | `rol: RolGestionUsuario` (string) | `roles: RolGestionUsuario[]` (array) |
| Auto-login post-registro | `loginApi(email, password)` → redirect directo | Manejar `requires_role_selection` si la respuesta lo indica |

---

## Especificacion del comportamiento

### Precondicion

- El usuario no está autenticado.
- El backend (US-ADJ-11.1) acepta `roles: string[]` en `POST /auth/registro`.

### Postcondicion

- Se crea la cuenta con los roles seleccionados.
- Si el backend retorna token directo (un rol): auto-login y redirect al portal del rol.
- Si el backend retorna `requires_role_selection`: redirect a `/login` con mensaje para que el usuario elija rol al ingresar.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.6-01 | Al menos un rol debe estar seleccionado para habilitar el botón "Registrarme". |
| INV-11.6-02 | El rol ADMIN no está disponible en el auto-registro. |
| INV-11.6-03 | Las secciones de datos por rol son opcionales — no bloquean el envío si están vacías. |
| INV-11.6-04 | El campo `nombre_organizacion` (Organizador) y `numero_licencia`/`federacion` (Juez) se envían solo si el rol correspondiente está seleccionado. |

---

## Criterios de aceptacion

```gherkin
Scenario: Usuario selecciona un solo rol (ATLETA) — flujo actual sin cambios
  Given el usuario está en /registro
  When selecciona solo el checkbox ATLETA y completa el formulario
  Then se crea la cuenta con roles=["ATLETA"]
  And se hace auto-login y redirect a /atleta

Scenario: Usuario selecciona múltiples roles
  Given el usuario está en /registro
  When selecciona ATLETA y JUEZ
  Then el formulario muestra la sección de datos de Juez (numero_licencia, federacion)
  And se envía roles=["ATLETA", "JUEZ"]

Scenario: Respuesta con requires_role_selection
  Given el usuario se registra con ATLETA y ORGANIZADOR
  When el backend retorna requires_role_selection=true
  Then el frontend redirige a /login con mensaje de selección de rol

Scenario: Intento de envío sin roles seleccionados
  Given el usuario desmarcó todos los checkboxes
  When intenta enviar el formulario
  Then el botón está deshabilitado o se muestra error "Seleccioná al menos un rol"
```

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/api/identidad.ts` | `CrearUsuarioRequest.rol` → `roles: RolGestionUsuario[]`. Agregar `CrearUsuarioResponse` con campo `requires_role_selection?: boolean`. |
| `frontend/src/pages/RegistroPage.tsx` | Reemplazar `<select>` por checkboxes multi-rol. Agregar secciones colapsables con datos opcionales por rol seleccionado (Juez: `numero_licencia`, `federacion`; Organizador: `nombre_organizacion`). Manejar `requires_role_selection` en `onSuccess`. |

---

## Notas de implementacion

1. **Secciones de datos por rol:** mostrar/ocultar según checkboxes activos usando estado local. Los campos son opcionales — si el usuario los deja vacíos, se omiten del payload (o se envían como `null`).

2. **Endpoint de perfil post-registro:** el backend de US-ADJ-11.1 crea el usuario. Los perfiles de Juez/Organizador en BC Registro se crean en un segundo request post-login (responsabilidad del frontend: llamar `POST /registro/jueces` y/o `POST /registro/organizadores` en el flujo de primer acceso). Esta US NO incluye esa lógica — queda para una US posterior o como mejora incremental.

3. **`requires_role_selection`:** si el backend lo retorna, redirigir a `/login` con `state: { requiresRoleSelection: true }` para que `LoginPage` (US-ADJ-11.7) muestre el selector.

4. **`roles` en el payload:** el backend acepta array. El campo `rol` del `CrearUsuarioRequest` actual se reemplaza por `roles`. Verificar que todos los usos de `crearUsuario` en el frontend se actualicen.

---

*Spec creada: 2026-05-16 — SP-ADJ-11*
