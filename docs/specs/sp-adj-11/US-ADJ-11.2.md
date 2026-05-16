# US-ADJ-11.2: BC Identidad — agregar y quitar rol a usuario existente

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: nuevo comando backend
**Agregado principal afectado**: `Usuario`
**Bounded Context**: `identidad`
**Dependencia**: US-ADJ-11.1 (aggregate `Usuario.roles`)

---

## Descripcion (lenguaje de negocio)

Como **usuario autenticado**,
quiero poder agregar un nuevo rol a mi cuenta desde "Mis Datos"
para ampliar mi participación en la plataforma sin crear una cuenta nueva.

Como **usuario autenticado con rol JUEZ u ORGANIZADOR**,
quiero poder quitar ese rol de mi cuenta
para mantener mi perfil actualizado si dejo de ejercer esa función.

---

## Contexto del dominio

### Problema

US-ADJ-11.1 habilita el registro multi-rol inicial, pero no provee un mecanismo para que
un usuario ya registrado adquiera un nuevo rol o lo retire post-registro. Eso se hace desde
la página "Mis Datos" de cada portal, que necesita endpoints dedicados.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Usuario` | Expone `agregar_rol()` y `quitar_rol()` con invariantes |
| Command | `AgregarRolUsuarioCommand` | Agrega un rol al usuario autenticado |
| Command | `QuitarRolUsuarioCommand` | Quita un rol JUEZ u ORGANIZADOR del usuario autenticado |
| Endpoint | `POST /auth/usuarios/me/roles` | Agrega rol al usuario de la sesión actual |
| Endpoint | `DELETE /auth/usuarios/me/roles/{rol}` | Quita rol del usuario de la sesión actual |

---

## Especificacion del comportamiento

### Precondicion

- El usuario está autenticado (JWT válido).
- Para agregar: el rol solicitado no es ADMIN.
- Para quitar: el rol a quitar es JUEZ u ORGANIZADOR (no ATLETA).

### Postcondicion

- **Agregar:** el rol queda añadido a `Usuario.roles`. El cambio se refleja en el próximo login.
- **Quitar:** el rol queda removido de `Usuario.roles`. El perfil en BC Registro (Juez u Organizador) **no** se elimina automáticamente — eso es responsabilidad de una acción explícita del usuario en el portal correspondiente.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.2-01 | No se puede agregar un rol que el usuario ya posee — lanza `RolYaAsignado`. |
| INV-11.2-02 | No se puede agregar el rol ADMIN desde este endpoint — lanza `RolNoPermitido`. |
| INV-11.2-03 | No se puede quitar el rol ATLETA — lanza `RolNoRemovible`. |
| INV-11.2-04 | No se puede quitar un rol que el usuario no posee — lanza `RolNoEncontrado`. |
| INV-11.2-05 | No se puede dejar al usuario sin roles — si es el último, lanza `UltimoRolNoRemovible`. |
| INV-11.2-06 | Quitar un rol no elimina el perfil de ese rol en BC Registro. |

---

## Criterios de aceptacion

```gherkin
Feature: Gestión de roles de usuario post-registro

  Scenario: Usuario ATLETA agrega el rol JUEZ
    Given existe un usuario autenticado con roles ["ATLETA"]
    When hace POST /auth/usuarios/me/roles con {"rol": "JUEZ"}
    Then el usuario queda con roles ["ATLETA", "JUEZ"]
    And la respuesta retorna 200 con la lista de roles actualizada

  Scenario: Usuario intenta agregar un rol que ya posee
    Given existe un usuario autenticado con roles ["ATLETA", "JUEZ"]
    When hace POST /auth/usuarios/me/roles con {"rol": "JUEZ"}
    Then el sistema retorna 409 con detalle "El usuario ya posee el rol JUEZ"

  Scenario: Usuario intenta agregar el rol ADMIN
    Given existe un usuario autenticado con cualquier rol
    When hace POST /auth/usuarios/me/roles con {"rol": "ADMIN"}
    Then el sistema retorna 403 con detalle "Rol no permitido"

  Scenario: Usuario JUEZ+ATLETA quita el rol JUEZ
    Given existe un usuario autenticado con roles ["JUEZ", "ATLETA"]
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then el usuario queda con roles ["ATLETA"]
    And la respuesta retorna 200 con la lista de roles actualizada
    And el perfil Juez en BC Registro permanece intacto

  Scenario: Usuario intenta quitar el rol ATLETA
    Given existe un usuario autenticado con roles ["ATLETA", "JUEZ"]
    When hace DELETE /auth/usuarios/me/roles/ATLETA
    Then el sistema retorna 409 con detalle "El rol ATLETA no puede ser removido"

  Scenario: Usuario intenta quitar un rol que no posee
    Given existe un usuario autenticado con roles ["ATLETA"]
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then el sistema retorna 404 con detalle "El usuario no posee el rol JUEZ"

  Scenario: Usuario intenta quitar su único rol
    Given existe un usuario autenticado con roles ["JUEZ"]
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then el sistema retorna 409 con detalle "No se puede quitar el único rol del usuario"
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — extiende el patrón de comando/handler/endpoint ya establecido en US-ADJ-11.1.

**Capa(s) afectadas:**
- [x] Domain — métodos `agregar_rol()` y `quitar_rol()` en `Usuario`
- [x] Application — `AgregarRolUsuarioCommand/Handler` · `QuitarRolUsuarioCommand/Handler`
- [x] API — `POST /auth/usuarios/me/roles` · `DELETE /auth/usuarios/me/roles/{rol}`

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/identidad/domain/aggregates/usuario.py` | Agregar `agregar_rol(rol: Rol)` con INV-11.2-01/02 y `quitar_rol(rol: Rol)` con INV-11.2-03/04/05. |
| `src/identidad/domain/exceptions.py` | Agregar `RolNoRemovible`, `UltimoRolNoRemovible` (si no se agregaron en 11.1). |
| `src/identidad/application/commands/agregar_rol_usuario.py` | Nuevo archivo. `AgregarRolUsuarioCommand(usuario_id, nuevo_rol)` + handler: carga usuario, llama `agregar_rol()`, guarda. |
| `src/identidad/application/commands/quitar_rol_usuario.py` | Nuevo archivo. `QuitarRolUsuarioCommand(usuario_id, rol)` + handler: carga usuario, llama `quitar_rol()`, guarda. |
| `src/identidad/api/router.py` | `POST /auth/usuarios/me/roles` (requiere JWT válido). `DELETE /auth/usuarios/me/roles/{rol}` (requiere JWT válido). Manejo de excepciones: 409 para `RolYaAsignado`, `RolNoRemovible`, `UltimoRolNoRemovible`; 404 para `RolNoEncontrado`; 403 para `RolNoPermitido`. |

---

## Notas de implementacion

1. Los endpoints usan `get_current_user` (JWT válido) pero no `require_rol` — cualquier rol puede agregar o quitar roles propios.

2. `agregar_rol()` y `quitar_rol()` se implementan en el aggregate, no en el handler, para que las invariantes sean parte del dominio y testeable en unit tests sin infraestructura.

3. El `usuario_id` para los commands se extrae del JWT: `UUID(current_user["sub"])`.

4. El endpoint `DELETE` recibe el rol como path parameter string y lo convierte a `Rol` enum. Si el string no es un valor válido del enum, retorna 422.

5. La respuesta de ambos endpoints incluye la lista de roles actualizada para que el frontend pueda refrescar la UI sin necesidad de un GET adicional.

---

*Spec creada: 2026-05-16 — ADR-020 · PLAN-SP-ADJ-11*
