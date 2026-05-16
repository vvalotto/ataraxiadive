# Reporte de Implementación — US-ADJ-11.6

**Historia:** Frontend — Registro multi-rol  
**Sprint:** SP-ADJ-11  
**Track:** Informal (vibe coding) — solo `frontend/`  
**Fecha:** 2026-05-16  
**Branch:** `feature/US-ADJ-11.6-registro-multi-rol`  
**Tiempo total:** ~6 min de ejecución de skill (implementación ~3.5 min + build fix ~2 min)

---

## Artefactos generados / modificados

| Artefacto | Tipo | Cambio |
|-----------|------|--------|
| `tests/features/US-ADJ-11.6-registro-multi-rol.feature` | Nuevo | Escenarios BDD (6 escenarios) |
| `docs/plans/sp-adj-11/US-ADJ-11.6-plan.md` | Nuevo | Plan de implementación (6 tareas) |
| `frontend/src/api/identidad.ts` | Modificado | `CrearUsuarioRequest.rol` → `roles: RolGestionUsuario[]`; `CrearUsuarioResponse` ampliado |
| `frontend/src/pages/RegistroPage.tsx` | Modificado | `<select>` → checkboxes; secciones colapsables Juez/Organizador; `onSuccess` multi-rol |
| `frontend/src/pages/organizador/UsuariosPage.tsx` | Modificado | `rol: form.rol` → `roles: [form.rol]` (adaptar al tipo actualizado) |
| `frontend/src/pages/atleta/AtletaHomePage.tsx` | Modificado | Eliminadas funciones `sortDisciplinasPorOt`/`getOtTimestamp` sin uso (build fix pre-existente) |

---

## Invariantes implementadas

| ID | Invariante | Estado |
|----|------------|--------|
| INV-11.6-01 | Al menos un rol seleccionado para habilitar "Registrarme" | ✅ botón `disabled` si `roles.length === 0` + error en submit |
| INV-11.6-02 | Rol ADMIN no disponible en auto-registro | ✅ no está en la lista de checkboxes; el backend lo enforce |
| INV-11.6-03 | Secciones de datos por rol son opcionales | ✅ campos no bloquean el envío si están vacíos |
| INV-11.6-04 | Campos de rol no seleccionado no se envían | ✅ `handleSubmit` construye payload condicionalmente |

---

## Quality Gate

| Gate | Resultado |
|------|-----------|
| `npm run build` (TypeScript) | ✅ 190 módulos, 0 errores |

---

## Decisiones técnicas

1. **`onSuccess` tri-path:** (a) `requires_role_selection` → redirect `/login`; (b) `access_token` en respuesta → auto-login directo; (c) fallback a `loginApi` explícito. Cubre todos los casos del backend US-ADJ-11.1.

2. **Redirect post-registro usa `roles[0]`:** cuando hay múltiples roles y el backend retorna token directo, se navega al portal del primer rol del array. Decisión pragmática — el flujo multi-rol completo se termina en US-ADJ-11.7 (selector de rol en login).

3. **Secciones colapsables no limpian al desmarcar:** al desmarcar un rol, el formulario oculta la sección pero conserva los valores. Evita pérdida de datos si el usuario alterna checkboxes.

4. **`UsuariosPage.tsx`:** el formulario de alta del organizador mantiene `<select>` de un solo rol (su UX es correcta — el admin elige un rol por vez). Solo se adapta el `mutate` para enviar `roles: [form.rol]`.

---

## Pendiente (fuera de alcance)

- Crear perfiles Juez/Organizador en BC Registro post-login (US posterior según spec §Notas puntio 2)
- Selector de rol al iniciar sesión con múltiples roles → US-ADJ-11.7

---

*Generado: 2026-05-16 · /implement-us US-ADJ-11.6*
