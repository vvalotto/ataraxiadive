# US-5.3.1: UI de gestion de usuarios

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.3
**Bounded Context**: `identidad` (API) + `frontend`
**Capas afectadas**: `identidad/api/router.py`, `frontend/src/pages/organizador/`, `frontend/src/api/identidad.ts`

---

## Descripcion

Como **organizador**,
quiero **crear usuarios con su rol asignado y ver la lista de todos los usuarios registrados**
para **configurar el equipo del torneo (jueces, atletas, otros organizadores) antes de iniciar la operacion**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Usuario` | Identidad de un usuario: email, password_hash, rol, activo |
| VO | `Rol` | `ORGANIZADOR` / `JUEZ` / `ATLETA` / `ADMIN` |
| Command | `RegistrarUsuarioCommand` | Crea un usuario con email, password y rol asignado |
| Query | `list_by_rol` | Devuelve usuarios filtrados por rol |
| Endpoint nuevo | `GET /auth/usuarios` sin filtro | Devuelve todos los usuarios (rol opcional) |
| Pagina nueva | `UsuariosPage` | Lista + formulario de creacion de usuarios del organizador |

### Lenguaje ubicuo relevante

- **Crear usuario:** el organizador registra un email + password + rol para que esa persona pueda ingresar al sistema.
- **Rol asignado:** el rol determina que pantallas ve el usuario al iniciar sesion (organizador, juez, atleta).
- **Usuario activo:** puede autenticarse; inactivo no puede (campo `activo` del aggregate).

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.3.1-01:** Solo el organizador autenticado puede acceder a `/organizador/usuarios`.
- **INV-5.3.1-02:** El selector de rol en el formulario expone solo `JUEZ`, `ATLETA` y `ORGANIZADOR`; nunca `ADMIN`.
- **INV-5.3.1-03:** El email debe ser unico en el sistema; un intento de creacion con email duplicado muestra error inline sin cerrar el formulario.
- **INV-5.3.1-04:** La password debe tener al menos 8 caracteres; validado en frontend antes de enviar.
- **INV-5.3.1-05:** Al crear un usuario exitosamente, aparece en la lista sin recargar la pagina completa.

### Operacion principal — listar usuarios

| | Descripcion |
|---|---|
| **Precondicion** | Usuario autenticado con rol ORGANIZADOR. |
| **Postcondicion** | Se muestra la lista completa de usuarios del sistema con su email, rol y estado activo/inactivo. |

**Endpoint a extender:**

El endpoint existente `GET /auth/usuarios?rol={rol}` requiere `rol` obligatorio.
Esta US lo modifica para hacer `rol` opcional:

```
GET /auth/usuarios             -> devuelve todos los usuarios
GET /auth/usuarios?rol=JUEZ    -> devuelve solo jueces (comportamiento actual conservado)
```

**Layout de la lista:**

| Email | Rol | Estado |
|-------|-----|--------|
| juez1@email.com | JUEZ | Activo |
| atleta1@email.com | ATLETA | Activo |

### Operacion secundaria — crear usuario

**Formulario:**

| Campo | Tipo | Validacion |
|---|---|---|
| Email | text | Requerido, formato email |
| Password | password | Minimo 8 caracteres |
| Rol | selector | JUEZ / ATLETA / ORGANIZADOR |

**Flujo:**

```
1. Organizador llena email, password y rol
2. Submit -> POST /auth/registro { email, password, rol }
3a. 201 Created -> nuevo usuario aparece en la lista; formulario se limpia
3b. 409 Conflict -> "Este email ya esta registrado" (inline, formulario permanece abierto)
3c. 422 -> "La contrasena debe tener al menos 8 caracteres" (inline)
```

**Ejemplo concreto:**

```
Organizador abre /organizador/usuarios.
Lista muestra: [juez1@email.com — JUEZ — Activo]

Organizador llena: email=juez2@email.com, password=pass1234, rol=JUEZ
Submit -> POST /auth/registro 201
Lista pasa a mostrar: [juez1@email.com, juez2@email.com]

Organizador intenta: email=juez1@email.com, password=pass1234, rol=ATLETA
Submit -> POST /auth/registro 409
Mensaje inline: "Este email ya esta registrado"
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.3.1 — UI de gestion de usuarios

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And en el sistema existen los usuarios:
      | email              | rol  | activo |
      | juez1@email.com    | JUEZ | true   |

  Scenario: listar todos los usuarios del sistema
    When el organizador navega a la pagina de usuarios
    Then ve una lista con "juez1@email.com" con rol "JUEZ"

  Scenario: crear usuario juez exitosamente
    When el organizador completa el formulario con email "juez2@email.com", password "pass1234" y rol "JUEZ"
    And confirma la creacion
    Then el sistema responde 201
    And "juez2@email.com" aparece en la lista con rol "JUEZ"
    And el formulario queda limpio para una nueva entrada

  Scenario: crear usuario con email duplicado muestra error inline
    When el organizador intenta crear un usuario con email "juez1@email.com"
    And confirma la creacion
    Then el sistema responde 409
    And se muestra "Este email ya esta registrado" en el formulario
    And el formulario permanece abierto con los datos ingresados

  Scenario: password de menos de 8 caracteres es rechazada antes de enviar
    When el organizador ingresa password "abc"
    And intenta confirmar la creacion
    Then el formulario muestra "La contrasena debe tener al menos 8 caracteres"
    And no se envia POST /auth/registro

  Scenario: rol ADMIN no esta disponible en el selector
    When el organizador abre el formulario de creacion
    Then el selector de rol muestra solo "JUEZ", "ATLETA" y "ORGANIZADOR"
    And no muestra "ADMIN"
```

---

## Impacto arquitectonico

- [x] Si — modifica `identidad/api/router.py` para hacer `rol` opcional en `GET /auth/usuarios`.

**Capa(s) afectadas:**
- [x] `identidad/api/router.py` — hacer parametro `rol` opcional; sin filtro devuelve todos.
- [x] `frontend/src/api/identidad.ts` — agregar `listarTodosLosUsuarios()` (sin filtro) y conservar `listarUsuariosPorRol()`.
- [x] `frontend/src/pages/organizador/UsuariosPage.tsx` — nueva pagina con lista y formulario de creacion.
- [x] `frontend/src/App.tsx` — agregar ruta `/organizador/usuarios` con `RequireRole role="organizador"`.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.3`
- Endpoint actual: `src/identidad/api/router.py` — `GET /auth/usuarios`
- Command existente: `src/identidad/application/commands/registrar_usuario.py`
- Aggregate: `src/identidad/domain/aggregates/usuario.py`
- VO Rol: `src/identidad/domain/value_objects/rol.py`
- Frontend auth: `frontend/src/api/identidad.ts`

---

## Notas de implementacion

- El endpoint `GET /auth/usuarios` debe seguir requiriendo autenticacion con rol ORGANIZADOR. Solo el parametro `rol` pasa a ser opcional.
- La lista se ordena por rol y luego por email para facilitar la lectura al configurar el equipo.
- No se implementa desactivacion/edicion de usuarios en esta US — solo creacion y listado.
- La pagina se accede desde el panel del organizador como una nueva seccion de configuracion.

---

*Redactado: 2026-04-23 — INC-5.3 Gestion de usuarios y roles*
