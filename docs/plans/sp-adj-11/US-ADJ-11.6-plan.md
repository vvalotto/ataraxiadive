# Plan de Implementación — US-ADJ-11.6
# Frontend — Registro multi-rol

**Fecha:** 2026-05-16  
**Track:** Informal (vibe coding) — solo `frontend/`  
**Estimación:** 3 puntos (~90 min)  
**Branch:** `feature/US-ADJ-11.6-registro-multi-rol`

---

## Artefactos a modificar

| Archivo | Cambio |
|---------|--------|
| `frontend/src/api/identidad.ts` | `CrearUsuarioRequest.rol` → `roles: RolGestionUsuario[]`; agregar `CrearUsuarioResponse` con `requires_role_selection?`, `access_token?`, `token_type?` |
| `frontend/src/pages/RegistroPage.tsx` | Reemplazar `<select>` por checkboxes multi-rol; agregar secciones colapsables Juez/Organizador; manejar `requires_role_selection` en `onSuccess` |

---

## Tareas

### T1 — `api/identidad.ts`: actualizar tipos (~15 min)

1. Cambiar `CrearUsuarioRequest.rol: RolGestionUsuario` → `roles: RolGestionUsuario[]`
2. Ampliar `CrearUsuarioResponse` para cubrir ambas formas de respuesta del backend:
   - Flujo directo: `{ usuario_id, access_token, token_type }`
   - Flujo multi-rol: `{ usuario_id, requires_role_selection: true, roles }`

### T2 — `RegistroPage.tsx`: estado y tipos (~20 min)

1. Reemplazar `FormState` — quitar `rol: RolGestionUsuario`, agregar:
   - `roles: RolGestionUsuario[]` (checkboxes activos)
   - `numero_licencia: string`, `federacion: string` (Juez)
   - `nombre_organizacion: string` (Organizador)
2. Actualizar `INITIAL_FORM` con los nuevos campos
3. Actualizar `handleSubmit` — construir payload con `roles` y campos condicionales por rol

### T3 — `RegistroPage.tsx`: selector de roles (~20 min)

1. Reemplazar `<select>` por grupo de checkboxes (ATLETA / JUEZ / ORGANIZADOR)
2. Handler `toggleRol(rol)` que agrega/quita del array `form.roles`
3. Mostrar error "Seleccioná al menos un rol" si `roles` está vacío al submit
4. Botón "Registrarme" deshabilitado si `roles.length === 0`

### T4 — `RegistroPage.tsx`: secciones colapsables (~20 min)

1. Sección Juez: visible si `form.roles.includes('JUEZ')` → campos `numero_licencia` y `federacion` (opcionales)
2. Sección Organizador: visible si `form.roles.includes('ORGANIZADOR')` → campo `nombre_organizacion` (opcional)
3. Al desmarcar un rol, ocultar la sección pero NO limpiar los campos (UX no intrusiva)

### T5 — `RegistroPage.tsx`: `onSuccess` multi-rol (~10 min)

1. Si `data.requires_role_selection === true`: redirigir a `/login` con `state: { requiresRoleSelection: true }`
2. Si `data.access_token`: auto-login y redirect al portal del primer rol de `form.roles`
3. Mantener el fallback actual a `/login` si el auto-login falla

### T6 — Quality gate: `npm run build` (~5 min)

Compilar TypeScript — sin errores de tipo ni imports rotos.

---

## Criterios de Done

- [ ] `CrearUsuarioRequest` usa `roles: RolGestionUsuario[]`
- [ ] Checkboxes multi-rol reemplazan el `<select>`
- [ ] Sección Juez aparece/desaparece según checkbox
- [ ] Sección Organizador aparece/desaparece según checkbox
- [ ] Submit deshabilitado / error si `roles` vacío
- [ ] `requires_role_selection` redirige a `/login` con state
- [ ] `npm run build` sin errores TypeScript

---

## Notas

- Los campos de rol (numero_licencia, federacion, nombre_organizacion) son **opcionales** — se omiten del payload si están vacíos (enviar `null` o no incluirlos).
- La lógica de crear perfil en BC Registro post-login queda **fuera de alcance** (US posterior).
- El redirect post-registro usa el primer rol activo para elegir el portal (o `/atleta` como fallback).
