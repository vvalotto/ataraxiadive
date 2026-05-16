# PLAN-SP-ADJ-11 — Modelo de usuarios con múltiples roles

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-11 |
| **Contexto** | BT-001: un usuario no puede tener más de un rol — bloquea casos reales de producción |
| **Fuentes** | `docs/USUARIO-ROLES.md` · `docs/adr/ADR-020-modelo-usuarios-roles.md` · `docs/BACKLOG-TECNICO.md` |
| **Incremento asociado** | — (SP-ADJ autónomo, pre-requisito para go-live real) |
| **Branch base** | `develop` |
| **Estado** | Planificado |

---

## Contexto

El modelo actual asigna un único `rol: Rol` a cada `Usuario`. Un juez que también compite
necesita dos cuentas con emails distintos, lo que es inaceptable en producción.

La solución diseñada en ADR-020 implica:
- `Usuario.roles: list[Rol]` en BC Identidad
- Tres entidades de perfil en BC Registro: `Atleta` (refactorizada), `Juez` (nueva), `Organizador` (nueva)
- Login con selector de rol cuando el usuario tiene más de uno
- Registro multi-rol con datos específicos por rol
- Página "Mis Datos" en los tres portales

Este es el SP-ADJ de mayor impacto hasta la fecha: toca BC Identidad, BC Registro y el
frontend completo. Las 9 US están ordenadas por capa y dependencia.

---

## Impacto por área (relevamiento)

### BC Identidad
| Archivo | Cambio |
|---------|--------|
| `domain/aggregates/usuario.py` | `rol: Rol` → `roles: list[Rol]` |
| `domain/ports/token_service_port.py` | `generate(usuario, rol_activo)` — agrega parámetro |
| `infrastructure/jwt_service.py` | `generate()` toma `rol_activo: Rol` explícito |
| `infrastructure/repositories/sqlite_usuario_repository.py` | columna `roles TEXT` (JSON), migración, `list_by_rol` con JSON |
| `application/commands/registrar_usuario.py` | `roles: list[Rol]` en lugar de `rol: Rol` |
| `application/commands/autenticar_usuario.py` | agrega `rol_elegido: Rol | None`; retorna lista si hay múltiples roles |
| `api/router.py` | `RegistroRequest.roles`, `LoginRequest.rol_elegido`, respuesta login condicional |
| `api/dependencies.py` | `require_rol` sin cambio de interfaz |
| Nuevo command | `AgregarRolUsuarioCommand` + handler |

### BC Registro
| Archivo | Cambio |
|---------|--------|
| `domain/aggregates/atleta.py` | `club` y `categoria` opcionales; agregar `dni` y `telefono` |
| `infrastructure/repositories/sqlite_atleta_repository.py` | columnas nuevas, migración |
| `application/commands/registrar_atleta.py` | campos opcionales |
| `application/commands/actualizar_atleta.py` | exponer `dni`, `telefono` |
| `api/router.py` | actualizar schemas y endpoint PATCH |
| Nuevos | `Juez` aggregate + port + repo + commands + queries + router endpoints |
| Nuevos | `Organizador` aggregate + port + repo + commands + queries + router endpoints |

### Frontend
| Archivo | Cambio |
|---------|--------|
| `RegistroPage.tsx` | checkboxes multi-rol + secciones de datos por rol |
| `LoginPage.tsx` | selector de rol cuando backend devuelve lista de roles |
| `api/auth.ts` | manejo de respuesta condicional (token vs. lista de roles) |
| `stores/useAuthStore.ts` | sin cambio — `rol` sigue siendo string único del JWT |
| `AtletaMisDatosPage.tsx` | agregar DNI, teléfono; club y categoría opcionales |
| Nuevas páginas | `JuezMisDatosPage.tsx`, `OrganizadorMisDatosPage.tsx` |
| Portales Juez y Organizador | agregar ruta y nav a "Mis Datos" |

---

## US planificadas

### US-ADJ-11.1 — BC Identidad: aggregate Usuario multi-rol + JWT + login/registro

**Prioridad:** Crítica — desbloquea todas las demás US
**Tipo:** refactor backend + migración DB
**Área:** BC `identidad` (domain · application · infrastructure · api)
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.1.md`

**Cambios:**
1. `Usuario.roles: list[Rol]` — reemplaza `rol: Rol`.
2. `SQLiteUsuarioRepository`: columna `roles TEXT NOT NULL DEFAULT '[]'` (JSON array). Migración `_ensure_column` para usuarios existentes: valor actual de `rol` se convierte a `["ATLETA"]`, etc.
3. `TokenServicePort.generate(usuario, rol_activo)` + `JWTService`: `rol_activo: Rol` determina el `"rol"` en el JWT. El payload no cambia de estructura — sigue siendo `"rol": "ATLETA"`.
4. `AutenticarUsuarioHandler`: si el usuario tiene 1 rol, genera token directo. Si tiene N roles y no viene `rol_elegido`, retorna `{"roles": [...]}` sin token (HTTP 200, campo `requires_role_selection: true`). Si viene `rol_elegido` y el usuario lo posee, genera token.
5. `RegistrarUsuarioHandler`: acepta `roles: list[Rol]`, no rechaza `EmailYaRegistrado` — si el email existe, valida la contraseña y agrega los nuevos roles (sin duplicar). Genera token con el primer rol si hay uno solo, o devuelve lista si hay varios.
6. Routers actualizados.

**Invariantes a respetar:**
- Un usuario no puede tener el mismo rol dos veces.
- `ADMIN` no puede registrarse por la UI.
- `requires_role_selection` solo se emite cuando el usuario tiene ≥ 2 roles y no envió `rol_elegido`.

---

### US-ADJ-11.2 — BC Identidad: agregar rol a usuario existente

**Prioridad:** Alta
**Tipo:** nuevo comando backend
**Área:** BC `identidad` (application · api)
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.2.md`

**Cambios:**
1. `AgregarRolUsuarioCommand(usuario_id, nuevo_rol)` + handler: agrega el rol si no existe ya. Lanza `RolYaAsignado` si el usuario ya lo tiene.
2. `DELETE /auth/usuarios/me/roles/{rol}`: quita el rol JUEZ u ORGANIZADOR. Lanza error si intenta quitar ATLETA o si quedaría sin roles.
3. `POST /auth/usuarios/me/roles`: agrega un rol al usuario autenticado.

**Nota:** quitar un rol no elimina el perfil en BC Registro (Juez u Organizador). Eso es responsabilidad del usuario explícitamente desde Mis Datos.

---

### US-ADJ-11.3 — BC Registro: refactor Atleta (campos opcionales + BT-002) ✅

**Prioridad:** Alta
**Tipo:** refactor backend + migración DB
**Área:** BC `registro` (domain · application · infrastructure · api) — solo entidad Atleta
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.3.md`
**Estado:** Implementada — branch `feature/US-ADJ-11.3-atleta-refactor` — 104 tests pasando

**Cambios implementados:**
1. `Atleta.club: str | None` y `Atleta.categoria: Categoria | None` — opcionales. INV-A-05: si se informa club, no puede ser vacío.
2. `Atleta.dni: str | None` y `Atleta.telefono: str | None` — nuevos campos (BT-002 resuelto).
3. `SQLiteAtletaRepository`: columnas `dni TEXT`, `telefono TEXT`, migración automática vía `_ensure_columns` (idempotente).
4. `RegistrarAtletaCommand` / `ActualizarAtletaCommand`: incluyen los nuevos campos.
5. Router: `RegistrarAtletaRequest`, `AtletaResponse`, `ActualizarAtletaMeRequest` actualizados.

**Decisión tomada en implementación:** `atleta_id` ya no se recibe del cliente — el backend lo genera internamente (UUID). La detección de duplicados se hace por `email` en lugar de `atleta_id`. Patrón sentinel (None = "no actualizar") diferido; PATCH club=null no soportado en esta US.

---

### US-ADJ-11.4 — BC Registro: entidad Juez

**Prioridad:** Alta
**Tipo:** nueva entidad backend
**Área:** BC `registro` (domain · application · infrastructure · api)
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.4.md`

**Cambios:**
1. `Juez` aggregate: `juez_id: UUID`, `email: str`, `numero_licencia: str | None`, `federacion: str | None`. Método `actualizar()`.
2. `JuezRepositoryPort` con `save`, `find_by_email`, `find_by_id`.
3. `SQLiteJuezRepository` con tabla `jueces` en la misma DB de registro.
4. `RegistrarJuezCommand` + handler, `ActualizarJuezCommand` + handler, `ObtenerJuezHandler`.
5. Router endpoints:
   - `POST /registro/jueces` → crea perfil Juez (requiere rol JUEZ en JWT)
   - `GET /registro/jueces/me` → obtiene perfil del juez autenticado
   - `PATCH /registro/jueces/me` → actualiza `numero_licencia`, `federacion`

---

### US-ADJ-11.5 — BC Registro: entidad Organizador

**Prioridad:** Alta
**Tipo:** nueva entidad backend
**Área:** BC `registro` (domain · application · infrastructure · api)
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.5.md`

**Cambios:**
1. `Organizador` aggregate: `organizador_id: UUID`, `email: str`, `nombre_organizacion: str | None`. Método `actualizar()`.
2. `OrganizadorRepositoryPort` + `SQLiteOrganizadorRepository` con tabla `organizadores`.
3. `RegistrarOrganizadorCommand` + handler, `ActualizarOrganizadorCommand` + handler, `ObtenerOrganizadorHandler`.
4. Router endpoints:
   - `POST /registro/organizadores` → crea perfil Organizador (requiere rol ORGANIZADOR en JWT)
   - `GET /registro/organizadores/me` → obtiene perfil del organizador autenticado
   - `PATCH /registro/organizadores/me` → actualiza `nombre_organizacion`

---

### US-ADJ-11.6 — Frontend: registro multi-rol

**Prioridad:** Alta
**Tipo:** refactor frontend
**Área:** `frontend` — `RegistroPage.tsx` + `api/identidad.ts`
**Dependencias:** US-ADJ-11.1, 11.3, 11.4, 11.5
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.6.md`

**Cambios:**
1. `RegistroPage`: el selector de rol pasa de `<select>` a checkboxes múltiples (ATLETA / JUEZ / ORGANIZADOR). Al menos uno requerido.
2. Por cada rol seleccionado se muestra una sección colapsable con sus datos específicos:
   - ATLETA: `documento_tipo`, `documento_numero`, `telefono`, `fecha_nacimiento`, opcionales `club`, `categoria`, `brevet`
   - JUEZ: opcionales `numero_licencia`, `federacion`
   - ORGANIZADOR: opcional `nombre_organizacion`
3. Al registrarse con múltiples roles, el backend puede devolver `requires_role_selection`. El frontend redirige al selector de rol (mismo que login).
4. `api/identidad.ts`: `CrearUsuarioRequest.roles: string[]` reemplaza `rol: string`.

---

### US-ADJ-11.7 — Frontend: login con selector de rol

**Prioridad:** Alta
**Tipo:** refactor frontend
**Área:** `frontend` — `LoginPage.tsx` + `api/auth.ts`
**Dependencias:** US-ADJ-11.1
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.7.md`

**Cambios:**
1. `api/auth.ts` — `loginApi()` maneja dos casos de respuesta:
   - `{access_token, token_type}` → login completo, redirigir al portal
   - `{requires_role_selection: true, roles: [...]}` → mostrar selector
2. `LoginPage`: si la respuesta tiene `requires_role_selection`, renderiza botones de selección de rol. Al seleccionar, llama `loginApi(email, password, rol_elegido)` y obtiene el token.
3. Si el usuario tiene un único rol, la UX no cambia — flujo existente sin selector.
4. Limpiar `portalPorRol()` como función reutilizable exportada (ya está en `utils/auth.ts`, verificar).

---

### US-ADJ-11.8 — Frontend: Mis Datos Atleta — revisión completa

**Prioridad:** Media
**Tipo:** refactor frontend
**Área:** `frontend` — `AtletaMisDatosPage.tsx`
**Dependencias:** US-ADJ-11.3
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.8.md`

**Cambios:**
1. Agregar campos `dni` (documento_tipo + documento_numero) y `telefono` al formulario.
2. Marcar `club` y `categoria` como opcionales en UI (quitar validación "requerido").
3. Sección "Mis roles": mostrar los roles actuales del usuario. Botón "Agregar rol" que navega a un formulario de alta de rol (llama US-ADJ-11.2 backend + crea perfil correspondiente).
4. Botón "Quitar rol ATLETA" — no disponible (rol no removible). Aclaración visual.

---

### US-ADJ-11.9 — Frontend: Mis Datos Juez y Organizador

**Prioridad:** Media
**Tipo:** nueva página frontend × 2
**Área:** `frontend` — portales Juez y Organizador
**Dependencias:** US-ADJ-11.4, 11.5, 11.2
**Spec:** `docs/specs/sp-adj-11/US-ADJ-11.9.md`

**Cambios:**
1. `JuezMisDatosPage`: formulario con datos comunes del Usuario (nombre, apellido) + datos de perfil Juez (`numero_licencia`, `federacion`). Llama `GET /registro/jueces/me` + `PATCH /registro/jueces/me`. Sección "Mis roles" con opción de quitar rol JUEZ.
2. `OrganizadorMisDatosPage`: ídem para Organizador. `GET/PATCH /registro/organizadores/me`. Sección "Mis roles" con opción de quitar rol ORGANIZADOR.
3. Agregar ruta `/juez/mis-datos` y `/organizador/mis-datos` en `App.tsx`.
4. Agregar enlace "Mis Datos" en la navegación del `JuezLayout` y del portal organizador.

---

## Secuencia de ejecución

```
US-ADJ-11.1  BC Identidad: multi-rol (fundación — bloquea todo)
  ↓
US-ADJ-11.2  BC Identidad: agregar/quitar rol
  │
  ├── US-ADJ-11.3  BC Registro: Atleta refactorizado   ┐
  ├── US-ADJ-11.4  BC Registro: Juez                   ├── paralelas entre sí
  └── US-ADJ-11.5  BC Registro: Organizador            ┘
        ↓
US-ADJ-11.6  Frontend: registro multi-rol
US-ADJ-11.7  Frontend: login con selector de rol
  ↓
US-ADJ-11.8  Frontend: Mis Datos Atleta
US-ADJ-11.9  Frontend: Mis Datos Juez y Organizador
```

US-ADJ-11.3, 11.4, 11.5 pueden ejecutarse en ramas paralelas después de mergear 11.1.
US-ADJ-11.6 y 11.7 pueden ejecutarse en paralelo entre sí (tocan archivos distintos).
US-ADJ-11.8 y 11.9 pueden ejecutarse en paralelo entre sí.

---

## Criterio de cierre de SP-ADJ-11

- [ ] Un usuario puede registrarse con más de un rol desde la UI.
- [ ] Un juez-atleta puede loguearse con email+contraseña, elegir el rol activo y acceder al portal correspondiente.
- [ ] El JWT mantiene la estructura actual — 0 cambios en los guards de autorización.
- [ ] `GET /registro/jueces/me` y `GET /registro/organizadores/me` funcionan.
- [x] Atleta tiene `dni` y `telefono` persistidos (BT-002 resuelto) — US-ADJ-11.3 ✅
- [ ] `AtletaMisDatosPage`, `JuezMisDatosPage`, `OrganizadorMisDatosPage` funcionan.
- [ ] Usuarios existentes en DB migran correctamente (`rol` → `roles` JSON).
- [ ] Tests backend: cobertura ≥ 90% en domain/ y application/ de los cambios.
- [ ] DesignReviewer 0 CRITICAL al cierre.
- [ ] Frontend build/lint OK.

---

## Riesgos

**R1 — Migración de usuarios existentes en producción**
La columna `rol TEXT` debe convertirse a `roles TEXT` (JSON) sin pérdida de datos.
Mitigación: `_ensure_column` + UPDATE que convierte `"ATLETA"` → `'["ATLETA"]'` para cada fila existente. Testear con DB real antes de mergear 11.1.

**R2 — Flujo de registro multi-rol y creación de perfiles en BC Registro**
Hoy el `Atleta` se crea con un endpoint separado (`POST /registro/atletas`). Con el nuevo modelo, al registrarse como ATLETA el perfil debería crearse automáticamente.
Mitigación: en US-ADJ-11.1 o 11.3, decidir si `RegistrarUsuarioHandler` dispara la creación del perfil via anti-corrupción layer, o si el frontend lo hace con un segundo request post-registro. Documentar la decisión en la spec.

**R3 — Auto-login post-registro con múltiples roles**
Si el usuario se registra con ATLETA+JUEZ, el auto-login actual redirige según `variables.rol`. Con múltiples roles, debe mostrar el selector.
Mitigación: `RegistroPage` detecta `requires_role_selection` en la respuesta y redirige al selector antes de navegar al portal.

**R4 — Impacto en tests existentes**
Los tests actuales de `RegistrarUsuarioHandler` y `AutenticarUsuarioHandler` usan `rol: Rol`. Todos rompen con la migración de 11.1.
Mitigación: actualizar tests como parte de US-ADJ-11.1, no post-hoc.

**R5 — DesignReviewer CBO**
Agregar Juez y Organizador con sus respectivos ports, repos, commands y queries aumenta el CBO del router de BC Registro.
Mitigación: ajustar `max_cbo` en `pyproject.toml` al inicio de 11.4 para el total esperado.

---

## Items fuera de alcance

- Panel de administración para gestión de usuarios — diferir a post-v1.0.
- Validación de `categoria` contra criterios federativos — la categoría es autodeclarada.
- Quitar el rol ATLETA — intencional: el historial de competencias no se puede disociar.
- Gestión de múltiples perfiles Atleta para el mismo usuario — no aplica (un email = un Atleta).

---

*Creado: 2026-05-16 — BT-001 relevamiento completo post-UAT SP6*
