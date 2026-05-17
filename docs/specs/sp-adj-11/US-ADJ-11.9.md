# US-ADJ-11.9: Frontend — Mis Datos Juez y Organizador

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: feature frontend
**Área**: `frontend/` — nuevas páginas + rutas + API client
**Dependencias**: US-ADJ-11.4, US-ADJ-11.5
**Track de implementación**: informal (vibe coding) — solo toca `frontend/`

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-registro-roles.md` — S-06 (Mi Perfil / Certificaciones de juez / Datos deportivos)
- `docs/design/ux/wireframes-juez.md`
- `docs/design/ux/wireframes-organizador.md`

S-06 muestra secciones de "Datos deportivos" (número de licencia, federación) y "Certificaciones de juez" como parte del perfil unificado. Esta US crea páginas de Mis Datos separadas para cada rol, accesibles desde sus portales respectivos, siguiendo el patrón visual de `AtletaMisDatosPage`.

---

## Descripcion

Como usuario con rol Juez u Organizador,
quiero poder ver y editar mis datos de perfil específicos de ese rol (licencia, federación, nombre de organización),
para mantener mi información actualizada en la plataforma.

---

## Estado actual vs. estado deseado

| Elemento | Estado actual | Estado deseado |
|----------|--------------|----------------|
| `JuezMisDatosPage` | No existe | Nueva página en `pages/juez/JuezMisDatosPage.tsx` |
| `OrganizadorMisDatosPage` | No existe | Nueva página en `pages/organizador/OrganizadorMisDatosPage.tsx` |
| Ruta `/juez/mis-datos` | No existe en `App.tsx` | Nueva ruta protegida con `RequireRole role="juez"` |
| Ruta `/organizador/mis-datos` | No existe en `App.tsx` | Nueva ruta protegida con `RequireRole role="organizador"` |
| `api/registro.ts` — Juez | Sin funciones para juez-me | Agregar `JuezDto`, `ActualizarJuezMePayload`, `fetchJuezMe()`, `actualizarJuezMe()` |
| `api/registro.ts` — Organizador | Sin funciones para organizador-me | Agregar `OrganizadorDto`, `ActualizarOrganizadorMePayload`, `fetchOrganizadorMe()`, `actualizarOrganizadorMe()` |
| Navegación Juez | Solo disciplinas/grilla | Agregar enlace a Mis Datos en el portal juez |
| Navegación Organizador | Solo torneos/operativo | Agregar enlace a Mis Datos en el portal organizador |

---

## Especificacion del comportamiento

### Precondicion

- El usuario está autenticado con rol JUEZ u ORGANIZADOR.
- El backend expone (US-ADJ-11.4) `GET/PATCH /registro/jueces/me` y (US-ADJ-11.5) `GET/PATCH /registro/organizadores/me`.
- Si el perfil no existe aún (`404`), la página muestra un botón "Crear mi perfil" que llama al `POST` correspondiente.

### Postcondicion

- Los datos del perfil (licencia, federación, nombre organización) se muestran y pueden editarse.
- Un perfil inexistente puede crearse desde la misma página.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.9-01 | Los campos de Juez (`numero_licencia`, `federacion`) son opcionales — el formulario no bloquea sin ellos. |
| INV-11.9-02 | El campo de Organizador (`nombre_organizacion`) es opcional. |
| INV-11.9-03 | Si el perfil no existe (404), se ofrece crearlo con un POST; no se muestra error al usuario. |
| INV-11.9-04 | Un campo vacío en el formulario se envía como `undefined` en el payload PATCH. |

---

## Criterios de aceptacion

```gherkin
Scenario: Juez accede a Mis Datos — perfil existente con licencia
  Given el usuario autenticado tiene rol JUEZ
  And existe perfil Juez con numero_licencia="LIC-001" y federacion="AIDA"
  When accede a /juez/mis-datos
  Then ve los campos Número de licencia y Federación con sus valores actuales

Scenario: Juez actualiza su federación
  Given el juez está en /juez/mis-datos
  When modifica el campo Federación a "CMAS" y guarda
  Then el PATCH a /registro/jueces/me incluye federacion="CMAS"
  And el formulario refleja el valor actualizado

Scenario: Juez sin perfil — puede crearlo desde la página
  Given el usuario autenticado tiene rol JUEZ
  And no existe perfil Juez para ese usuario
  When accede a /juez/mis-datos
  Then ve un botón "Crear mi perfil de juez"
  When hace click en ese botón
  Then se crea el perfil con POST /registro/jueces y la página muestra el formulario vacío

Scenario: Organizador actualiza nombre de organización
  Given el usuario autenticado tiene rol ORGANIZADOR
  And existe perfil Organizador con nombre_organizacion null
  When accede a /organizador/mis-datos, ingresa "Club Apnea BA" y guarda
  Then el PATCH incluye nombre_organizacion="Club Apnea BA"

Scenario: Acceso no autorizado — atleta intenta /juez/mis-datos
  Given el usuario autenticado tiene rol ATLETA
  When intenta acceder a /juez/mis-datos
  Then es redirigido (RequireRole protege la ruta)
```

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/api/registro.ts` | Agregar interfaces `JuezDto { juez_id, email, numero_licencia, federacion }`, `ActualizarJuezMePayload { numero_licencia?, federacion? }`, `OrganizadorDto { organizador_id, email, nombre_organizacion }`, `ActualizarOrganizadorMePayload { nombre_organizacion? }`. Agregar funciones: `fetchJuezMe()`, `actualizarJuezMe()`, `crearJuezMe()`, `fetchOrganizadorMe()`, `actualizarOrganizadorMe()`, `crearOrganizadorMe()`. |
| `frontend/src/pages/juez/JuezMisDatosPage.tsx` | Nueva página. Campos: `numero_licencia` (texto, opcional) y `federacion` (texto, opcional). Carga con `GET /registro/jueces/me`. Si 404, muestra botón "Crear mi perfil". Si 200, muestra formulario editable con `PATCH`. Usa `JuezLayout`. |
| `frontend/src/pages/organizador/OrganizadorMisDatosPage.tsx` | Nueva página. Campo: `nombre_organizacion` (texto, opcional). Carga con `GET /registro/organizadores/me`. Si 404, muestra botón "Crear mi perfil". Si 200, muestra formulario editable con `PATCH`. Usa el layout/shell de organizador. |
| `frontend/src/App.tsx` | Importar y registrar `JuezMisDatosPage` en ruta `/juez/mis-datos` con `RequireRole role="juez"`. Importar y registrar `OrganizadorMisDatosPage` en `/organizador/mis-datos` con `RequireRole role="organizador"`. |
| Navegación Juez (a determinar en impl.) | Agregar enlace "Mis Datos" en el portal de juez — en `JuezLayout` o en `DisciplinasPage` como acción en header. |
| Navegación Organizador (a determinar en impl.) | Agregar enlace "Mis Datos" en `DashboardPage` o nav del portal organizador. |

---

## Notas de implementacion

1. **Shell de Organizador:** no existe un `OrganizadorShell` equivalente a `AtletaShell`. `OrganizadorMisDatosPage` puede usar el mismo patrón visual de `JuezLayout` o replicar la estructura de otra página organizador (e.g., `DashboardPage`).

2. **Perfil inexistente (404):** mostrar un estado vacío amigable con CTA "Crear mi perfil de [rol]" que llama `POST /registro/jueces` o `POST /registro/organizadores` con body vacío. Después de crearlo exitosamente, mostrar el formulario editable.

3. **`null` → empty string en formulario:** mismo patrón que `AtletaMisDatosPage`: `juez.numero_licencia ?? ''`.

4. **Campo vacío → `undefined` en PATCH:** `form.campo.trim() || undefined`. Si el campo nunca fue establecido, no enviar en el payload.

5. **Navegación:** la ubicación exacta del enlace "Mis Datos" queda a criterio del implementador — lo importante es que sea accesible desde el portal del rol correspondiente sin fricción.

---

*Spec creada: 2026-05-16 — SP-ADJ-11*
