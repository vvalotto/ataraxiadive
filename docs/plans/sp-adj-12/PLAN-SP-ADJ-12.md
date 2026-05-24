# PLAN-SP-ADJ-12 — Correcciones y mejoras de producción post-SP7

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-12 |
| **Contexto** | Bugs e issues detectados en producción (https://ataraxiadive.fly.dev) durante operación real post-despliegue SP7 |
| **Fuentes** | GitHub Issues #198–#204 |
| **Incremento asociado** | INC-7.1 (SP7 en curso) |
| **Branch base** | `develop` |
| **Estado** | ✅ Cerrado 2026-05-24 |

---

## Contexto

Durante la operación real de AtaraxiaDive en producción post-SP7 se detectaron 7 issues:
5 bugs, 1 enhancement y 1 feature faltante. Los bugs bloquean flujos operativos críticos
(asignación de jueces, navegación del organizador, inscripción del atleta). El enhancement
y la feature completan el ciclo de gestión de atletas e identidad del sistema.

---

## Issues cubiertos

| # | Tipo | Área | Descripción |
|---|------|------|-------------|
| #203 | bug | Frontend | Panel jueces: selector deshabilitado — filtro `usuario.rol` en lugar de `usuario.roles.includes()` |
| #201 | bug | Frontend | Panel inscriptos: mensaje informativo sobre edición de AP innecesario |
| #199 | bug | Frontend | Portal Organizador: Mis Datos oculta opciones de menú (Inscriptos, Podios) |
| #198 | bug | Frontend | Portal Juez: botón Mis Datos desplaza Salir fuera del área visible |
| #200 | bug | Frontend | Portal Atleta: inscripción no precarga doc/tel; Mis Datos desactualizado; Club no visible |
| #202 | enhancement | Full-stack | Grilla inscriptos: popup de atleta con datos, adjuntos y control de aceptación |
| #204 | feature | Full-stack | Gestión de roles: no existe página para agregar/quitar roles a usuarios existentes |

---

## Impacto por área (relevamiento)

### BC Identidad (backend)
| Archivo | Cambio |
|---------|--------|
| `domain/aggregates/usuario.py` | Agregar métodos `agregar_rol(rol)` y `quitar_rol(rol)` |
| `application/commands/agregar_rol.py` | Nuevo: `AgregarRolCommand` + `AgregarRolHandler` |
| `application/commands/quitar_rol.py` | Nuevo: `QuitarRolCommand` + `QuitarRolHandler` |
| `api/router.py` | Nuevos endpoints `POST/DELETE /auth/usuarios/{id}/roles` (ORGANIZADOR-only) |

> Nota: el `repo.save()` ya persiste el array `roles` completo — sin cambios en infrastructure.

### BC Registro (backend) — solo para #202
| Archivo | Cambio |
|---------|--------|
| `domain/aggregates/inscripcion.py` | Agregar campo `estado_aceptacion` (ACEPTADO/RECHAZADO) |
| `infrastructure/repositories/sqlite_inscripcion_repository.py` | Columna nueva + migración |
| `api/router.py` | Nuevo endpoint `PATCH /registro/inscripciones/{id}/aceptacion` |
| `api/router.py` | Ampliar `GET /registro/inscripciones/{id}` con datos del atleta y archivos adjuntos |

### Frontend
| Archivo | Cambio |
|---------|--------|
| `api/identidad.ts` | `UsuarioDto.rol` → `roles: RolIdentidad[]`; nuevas funciones `agregarRolUsuario()` / `quitarRolUsuario()` |
| `pages/organizador/UsuariosPage.tsx` | Chips de roles por fila + botones inline agregar/quitar |
| `components/organizador/JuecesPanel.tsx` | Filtro `usuario.roles.includes('JUEZ')` |
| `components/organizador/InscriptosPanel.tsx` | Eliminar mensaje informativo AP; agregar popup inscripto |
| `components/organizador/OrganizadorLayout.tsx` | `shouldShowNavItem`: Inscriptos y Podios siempre visibles |
| `pages/juez/DisciplinasPage.tsx` | Layout Mis Datos + Salir con flex-wrap |
| `pages/atleta/AtletaInscripcionPage.tsx` | Precarga `documentoNumero` y `telefono` desde perfil |
| `pages/atleta/AtletaHomePage.tsx` | Club con fallback `'—'` cuando vacío |
| `pages/atleta/AtletaMisDatosPage.tsx` o query | Invalidación de caché post-inscripción |

---

## US planificadas

### US-ADJ-12.1 — Frontend: fixes de layout, navegación y filtros

**Prioridad:** Crítica (bugs que bloquean operación)
**Tipo:** fix frontend puro
**Issues:** #198, #199, #201, #203
**Área:** `frontend` — 4 archivos
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.1.md`

**Cambios:**
1. `JuecesPanel.tsx` — filtro `usuario.rol === 'JUEZ'` → `usuario.roles.includes('JUEZ')` (#203). Requiere actualizar `UsuarioDto` simultáneamente.
2. `InscriptosPanel.tsx` — eliminar bloque condicional con mensaje informativo AP (#201).
3. `OrganizadorLayout.tsx` — `shouldShowNavItem()`: `'inscriptos'` y `'podios'` retornan `true` siempre (no requieren `activeTournamentId`) (#199).
4. `DisciplinasPage.tsx` — acciones Mis Datos + Salir con `flex-col gap-2 shrink-0` para que ambos botones sean visibles en pantallas pequeñas (#198).

**Nota:** el fix de `UsuarioDto.rol → roles[]` (necesario para #203) se incluye aquí como prerequisito del tipo correcto.

---

### US-ADJ-12.2 — BC Identidad: agregar/quitar rol a usuario existente

**Prioridad:** Alta
**Tipo:** nuevo feature backend
**Issues:** #204 (backend)
**Área:** BC `identidad` — domain · application · api
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.2.md`

**Cambios:**
1. `Usuario.agregar_rol(rol: Rol)` — lanza `RolYaAsignado` si ya existe. Agrega al array.
2. `Usuario.quitar_rol(rol: Rol)` — lanza `RolNoEncontrado` si no existe; `RolesVacios` si quedaría sin roles.
3. `AgregarRolCommand(usuario_id, rol)` + `AgregarRolHandler` — busca usuario, llama `agregar_rol`, guarda.
4. `QuitarRolCommand(usuario_id, rol)` + `QuitarRolHandler` — busca usuario, llama `quitar_rol`, guarda.
5. `POST /auth/usuarios/{usuario_id}/roles` (body: `{rol: Rol}`) — requiere ORGANIZADOR.
6. `DELETE /auth/usuarios/{usuario_id}/roles/{rol}` — requiere ORGANIZADOR.

**Invariantes:**
- No se puede quitar el único rol que le queda al usuario.
- No se puede agregar un rol que el usuario ya tiene.
- Solo un ORGANIZADOR puede modificar roles de otros usuarios.

---

### US-ADJ-12.3 — Frontend: gestión inline de roles en UsuariosPage

**Prioridad:** Alta
**Tipo:** nuevo feature frontend
**Issues:** #204 (frontend)
**Área:** `frontend` — `api/identidad.ts` · `pages/organizador/UsuariosPage.tsx`
**Dependencias:** US-ADJ-12.2
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.3.md`

**Cambios:**
1. `identidad.ts` — agregar `agregarRolUsuario(usuarioId, rol)` y `quitarRolUsuario(usuarioId, rol)`.
2. `UsuariosPage.tsx`:
   - Tabla: columna "Roles" muestra chips (`JUEZ`, `ATLETA`, `ORGANIZADOR`) con botón `×` por chip (deshabilitado si es el único rol).
   - Al final de los chips: botón `+` que despliega un `<select>` inline con los roles disponibles para agregar.
   - Mutations con `useQueryClient().invalidateQueries(['usuarios'])` al completar.
   - `ordenarUsuarios` actualizado para operar sobre `roles[]`.

---

### US-ADJ-12.4 — Frontend: portal atleta — precarga y sincronización de datos

**Prioridad:** Alta
**Tipo:** fix frontend
**Issues:** #200
**Área:** `frontend` — `AtletaInscripcionPage.tsx` · `AtletaHomePage.tsx`
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.4.md`

**Cambios:**
1. `AtletaInscripcionPage.tsx` — agregar `documentoNumeroValue` y `telefonoValue` con fallback desde `atleta.dni` y `atleta.telefono`, con el mismo patrón que `nombreCompletoValue` / `categoriaValue` ya existentes.
2. `AtletaHomePage.tsx` — campo Club: `{query.data.atleta.club || '—'}` para no mostrar vacío.
3. `AtletaInscripcionPage.tsx` — en `onSuccess` de la mutation: llamar `queryClient.invalidateQueries(['atleta-mis-datos'])` para que Mis Datos refleje datos actualizados post-inscripción.

---

### US-ADJ-12.5 — BC Registro: inscripción con estado de aceptación

**Prioridad:** Media
**Tipo:** nuevo feature backend (enhancement)
**Issues:** #202 (backend)
**Área:** BC `registro` — domain · infrastructure · api
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.5.md`

**Cambios:**
1. `Inscripcion` aggregate — campo `estado_aceptacion: EstadoAceptacion` (enum: `ACEPTADO` / `RECHAZADO`). Default: `ACEPTADO` al inscribirse.
2. `SQLiteInscripcionRepository` — columna `estado_aceptacion TEXT DEFAULT 'ACEPTADO'` + migración `_ensure_column`.
3. Endpoint `PATCH /registro/inscripciones/{inscripcion_id}/aceptacion` — body `{estado: 'ACEPTADO' | 'RECHAZADO'}`. Requiere ORGANIZADOR.
4. Endpoint `GET /registro/inscripciones/{inscripcion_id}/detalle` — devuelve datos del atleta (nombre, categoría, club, brevet, dni, telefono) + estado_aceptacion + URLs de adjuntos (apto_medico, constancia_pago).

---

### US-ADJ-12.6 — Frontend: popup inscriptos con control de aceptación

**Prioridad:** Media
**Tipo:** nuevo feature frontend (enhancement)
**Issues:** #202 (frontend)
**Área:** `frontend` — `components/organizador/InscriptosPanel.tsx`
**Dependencias:** US-ADJ-12.5
**Spec:** `docs/specs/sp-adj-12/US-ADJ-12.6.md`

**Cambios:**
1. `InscriptosPanel.tsx` — al hacer click en una fila de la tabla, abrir un panel/drawer lateral con:
   - Datos del atleta: nombre completo, categoría, club, brevet, DNI, teléfono.
   - Links a adjuntos: apto médico y constancia de pago (si existen).
   - Estado de aceptación actual (chip ACEPTADO/RECHAZADO) con botones para cambiar.
2. Flag visual en la tabla: badge de estado por atleta (ACEPTADO = verde · RECHAZADO = rojo).
3. La tabla sigue siendo funcional para edición de AP mientras el panel lateral está abierto.

---

## Secuencia de ejecución

```
US-ADJ-12.1  Frontend: fixes layout, nav y filtros   ← sin dependencias, arrancar primero
  │
  ├── US-ADJ-12.2  BC Identidad: agregar/quitar rol  ← backend, paralelo a 12.1
  │     ↓
  │   US-ADJ-12.3  Frontend: gestión inline de roles  ← depende de 12.2
  │
  ├── US-ADJ-12.4  Frontend: portal atleta precarga   ← paralelo a 12.2/12.3
  │
  └── US-ADJ-12.5  BC Registro: estado aceptación     ← paralelo, sin dependencias
        ↓
      US-ADJ-12.6  Frontend: popup inscriptos          ← depende de 12.5
```

---

## Criterio de cierre de SP-ADJ-12

- [ ] Panel de jueces: selector habilitado cuando hay jueces JUEZ activos (#203).
- [ ] Panel inscriptos: mensaje AP eliminado (#201).
- [ ] Portal Organizador: Inscriptos y Podios visibles desde Mis Datos (#199).
- [ ] Portal Juez: Mis Datos y Salir visibles simultáneamente (#198).
- [ ] Portal Atleta: doc/tel precargados en inscripción; Club con valor en inicio (#200).
- [ ] UsuariosPage: roles visibles como chips; agregar/quitar rol inline (#204).
- [ ] Popup de inscripto con datos, adjuntos y control aceptación (#202).
- [ ] Tests backend: cobertura ≥ 90% en domain/ y application/ de cambios nuevos.
- [ ] DesignReviewer 0 CRITICAL al cierre.
- [ ] Frontend build/lint OK.

---

## Items fuera de alcance

- Gestión de inscripciones rechazadas: notificación al atleta — diferido a post-v1.1.
- Panel de administración ADMIN — diferido.
- Quitar rol ATLETA — intencional (historial de competencias vinculado).

---

*Creado: 2026-05-23 — Issues #198–#204 detectados en producción post-SP7*
