# US-ADJ-11.10: Creación automática de perfiles en BC Registro al registrarse

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: feat backend
**Área**: `src/identidad/` · `src/registro/`
**Dependencias**: US-ADJ-11.1, US-ADJ-11.3, US-ADJ-11.4, US-ADJ-11.5
**Track de implementación**: formal — toca `src/`

---

## Descripcion

Como usuario que se registra en AtaraxiaDive,
quiero que mi perfil en BC Registro sea creado automáticamente al registrarme,
para que pueda acceder a "Mis Datos" y completarlo sin pasos adicionales.

---

## Estado actual vs. estado deseado

| Elemento | Estado actual | Estado deseado |
|----------|--------------|----------------|
| `POST /auth/registro` | Crea usuario en BC Identidad únicamente | Crea usuario en BC Identidad **y** perfil stub en BC Registro por cada rol |
| `Atleta.fecha_nacimiento` | Campo obligatorio | Campo opcional — se completa en "Mis Datos" |
| `GET /registro/atletas/{id}` post-registro | 404 — perfil no existe | 200 — perfil stub con nombre, apellido, email |
| `GET /registro/jueces/{email}` post-registro | 404 | 200 — perfil stub con email |
| `GET /registro/organizadores/{email}` post-registro | 404 | 200 — perfil stub con email |

---

## Especificacion del comportamiento

### Precondicion

- El usuario no está registrado.
- BC Registro tiene endpoints de alta para Atleta, Juez y Organizador.

### Postcondicion

- El usuario existe en BC Identidad con sus roles.
- Por cada rol en `roles`:
  - `ATLETA` → existe un `Atleta` en BC Registro con `nombre`, `apellido`, `email` (sin `fecha_nacimiento`).
  - `JUEZ` → existe un `Juez` en BC Registro con `email`.
  - `ORGANIZADOR` → existe un `Organizador` en BC Registro con `email`.
- El usuario puede acceder a "Mis Datos" para completar su perfil.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.10-01 | Si el rol ATLETA está en `roles`, se crea el perfil de Atleta. |
| INV-11.10-02 | Si el rol JUEZ está en `roles`, se crea el perfil de Juez. |
| INV-11.10-03 | Si el rol ORGANIZADOR está en `roles`, se crea el perfil de Organizador. |
| INV-11.10-04 | Si la creación de un perfil falla, el registro completo falla (no se crea el usuario). |
| INV-11.10-05 | `fecha_nacimiento` en Atleta es opcional — si está presente, debe ser una fecha en el pasado. |
| INV-11.10-06 | Si el perfil ya existe (email duplicado en BC Registro), se ignora sin error — idempotente. |

---

## Criterios de aceptacion

```gherkin
Scenario: Registro solo ATLETA crea perfil de atleta en BC Registro
  Given el usuario no está registrado
  When se registra con roles=["ATLETA"]
  Then existe un Atleta en BC Registro con su nombre, apellido y email
  And fecha_nacimiento es null

Scenario: Registro con ATLETA + JUEZ crea ambos perfiles
  Given el usuario no está registrado
  When se registra con roles=["ATLETA", "JUEZ"]
  Then existe un Atleta en BC Registro
  And existe un Juez en BC Registro con el mismo email

Scenario: Registro con ORGANIZADOR crea perfil de organizador
  Given el usuario no está registrado
  When se registra con roles=["ORGANIZADOR"]
  Then existe un Organizador en BC Registro con su email

Scenario: Atleta completa fecha_nacimiento en Mis Datos
  Given el atleta tiene perfil stub sin fecha_nacimiento
  When actualiza su perfil con fecha_nacimiento válida
  Then el perfil se actualiza correctamente

Scenario: Atleta stub sin fecha_nacimiento es válido
  Given un Atleta creado sin fecha_nacimiento
  Then el aggregate no lanza error de invariante
```

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/domain/aggregates/atleta.py` | `fecha_nacimiento: date` → `fecha_nacimiento: date \| None`. INV-A-04 solo se valida si el campo está presente. |
| `src/registro/application/commands/registrar_atleta.py` | `fecha_nacimiento` → opcional (`date \| None = None`) |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Soportar `fecha_nacimiento` null en INSERT/SELECT |
| `src/identidad/domain/ports/perfil_registro_port.py` | Nuevo puerto ABC: `crear_perfiles(usuario_id, nombre, apellido, email, roles, ...)` |
| `src/registro/infrastructure/perfil_registro_adapter.py` | Implementación del puerto — orquesta `RegistrarAtletaHandler`, `RegistrarJuezHandler`, `RegistrarOrganizadorHandler` |
| `src/identidad/application/commands/registrar_usuario.py` | `RegistrarUsuarioHandler.handle()` llama `PerfilRegistroPort` después de crear el usuario |
| `src/app.py` | Inyectar `PerfilRegistroAdapter` como `PerfilRegistroPort` en el handler de registro |

---

## Notas de implementacion

1. **Puerto en BC Identidad:** `PerfilRegistroPort` define la interfaz. BC Identidad no conoce los detalles de BC Registro — solo le dice "crear perfiles para estos roles". Cumple la regla arquitectónica de comunicación exclusivamente por puertos.

2. **Adapter en BC Registro:** `PerfilRegistroAdapter` vive en `src/registro/infrastructure/` e implementa el puerto de BC Identidad. Internamente usa los handlers existentes (`RegistrarAtletaHandler`, etc.).

3. **Datos opcionales de Juez/Organizador:** `numero_licencia`, `federacion` y `nombre_organizacion` se pasan al puerto si el frontend los envió en el registro (ya disponibles en `RegistrarUsuarioCommand`). Si están vacíos, se crean los perfiles sin ellos.

4. **Idempotencia (INV-11.10-06):** si el perfil ya existe (reintento de registro con el mismo email), el adapter captura `AtletaYaRegistrado` / `JuezYaRegistrado` / `OrganizadorYaRegistrado` y continúa sin error.

5. **`RegistrarUsuarioCommand`** ya tiene `roles`, `nombre`, `apellido`, `email` — no necesita campos adicionales. Los campos opcionales de Juez/Organizador (`numero_licencia`, `federacion`, `nombre_organizacion`) deben agregarse al comando como opcionales.

---

*Spec creada: 2026-05-16 — SP-ADJ-11*
