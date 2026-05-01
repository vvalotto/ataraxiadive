# Revisión UAT — INC-5.5
## Hallazgos Funcionales Durante Prueba Manual

**Fecha:** 2026-04-25
**Contexto:** UAT funcional del incremento `INC-5.5` (US-5.5.1 registro de APs + US-5.5.2 vista organizador inscriptos)
**Branch observado:** `develop` (post-merge PR #116)
**Servidores usados:** backend `http://127.0.0.1:8000` · frontend `http://127.0.0.1:5173`

> **Estado documental 2026-04-25:** esta corrida UAT quedó invalidada como
> referencia de avance porque `INC-5.5` fue revertido y reiniciado tras detectar
> desalineación entre las specs de `US-5.5.1`/`US-5.5.2` y la UX aprobada en
> `docs/design/ux/`. Se conserva solo como registro histórico del intento revertido.

---

## Hallazgos abiertos

| ID | Área | Hallazgo | Severidad | Estado |
|----|------|----------|-----------|--------|
| UAT-5.5-01 | Portal atleta · Identidad | El portal del atleta muestra solo el email del usuario en lugar del nombre y apellido del atleta | Media | Abierto |

---

## Detalle de hallazgos

### UAT-5.5-01 — Portal atleta no muestra nombre ni apellido

**Descripción:**
En el portal del atleta (`/atleta`), la interfaz identifica al usuario únicamente por su email.
No se despliega el nombre ni el apellido del atleta registrado.

**Reproducción:**
1. Login como atleta (ej. `ana@email.com`)
2. Navegar al dashboard del atleta
3. Observar: se muestra email, pero no hay nombre/apellido visible en ningún punto del portal

**Causa raíz:**
El JWT payload solo lleva `sub` (userId), `email` y `rol`. El campo `nombre`/`apellido`
no está incluido en el token. `useAuthStore` (Zustand) almacena únicamente lo que viene
del JWT: `{ token, userId, email, rol }`. No existe endpoint `GET /auth/me` que permita
al frontend obtener el perfil completo post-login. `AtletaDashboardPage.tsx` (línea 380)
renderiza solo `{email ?? 'Sin email disponible'}`.

**Impacto:** UX — el atleta se identifica solo por email en todo el portal.

**Clasificación:** Track formal. Requiere modificar `src/identidad/` (JWT o nuevo endpoint).
Opciones de solución:

- **Opción A (recomendada):** Agregar `nombre` y `apellido` al JWT payload en el handler
  de login (`src/identidad/application/commands/login_usuario.py`), actualizar
  `useAuthStore` para almacenarlos, y mostrarlos en el portal.
- **Opción B:** Crear `GET /auth/me` en BC Identidad que devuelva el perfil completo;
  el frontend lo llama al iniciar sesión y persiste los datos en el store.

**Acción propuesta:** US-IEDD en SP5 (INC a determinar). Severidad media — no bloquea
operación del torneo, pero afecta la UX del atleta en toda la plataforma.

---

## Hallazgos cerrados / sin impacto

*(ninguno en esta sesión)*
