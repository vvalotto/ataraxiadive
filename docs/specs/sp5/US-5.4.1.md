# US-5.4.1: Auto-registro de usuario

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.4
**Bounded Context**: `identidad` + `frontend`
**Capas afectadas**: `identidad/domain/`, `identidad/application/`, `identidad/infrastructure/`, `identidad/api/`, `frontend/src/pages/`, `frontend/src/api/identidad.ts`

---

## Descripcion

Como **persona sin cuenta**,
quiero **registrarme con mi nombre, apellido, email, password y rol**
para **acceder a la plataforma con el rol adecuado sin intervención del organizador**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Cambio |
|---|---|---|
| Aggregate | `Usuario` | Agrega `nombre: str` y `apellido: str` (requeridos) |
| Command | `RegistrarUsuarioCommand` | Agrega `nombre`, `apellido`; valida `rol ≠ ADMIN` |
| Handler | `RegistrarUsuarioHandler` | Rechaza `rol == ADMIN` con `RolNoPermitido` |
| Excepcion nueva | `RolNoPermitido` | Se lanza al intentar auto-registrarse con rol ADMIN |
| Repo | `SQLiteUsuarioRepository` | Migra tabla `usuarios` con columnas `nombre`, `apellido`; actualiza save/find |
| Endpoint | `POST /auth/registro` | Acepta `nombre`, `apellido`; valida `rol ≠ ADMIN` |
| Pagina nueva | `RegistroPage` | Formulario de auto-registro — publico (sin autenticacion) |

### Lenguaje ubicuo relevante

- **Auto-registro:** cualquier persona puede crear su propia cuenta con rol JUEZ, ATLETA u ORGANIZADOR. El rol ADMIN queda reservado para usuarios creados directamente en base de datos.
- **nombre / apellido:** datos del participante o funcionario requeridos para mostrarse en grillas, podios y notificaciones. No son opcionales.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.4.1-01:** `nombre` y `apellido` son requeridos — no pueden estar vacíos ni ser solo espacios.
- **INV-5.4.1-02:** el rol no puede ser `ADMIN` en el auto-registro — rechaza con 403 si se envía.
- **INV-5.4.1-03:** email único (ya existente INV-ID-01) — rechaza con 409 si ya registrado.
- **INV-5.4.1-04:** ~~password ≥ 8 caracteres~~ → password ≥ 10 caracteres + al menos 1 mayúscula + 1 número — rechaza con 422. Ver ADR-019.
- **INV-5.4.1-06:** el formulario frontend requiere campo de confirmación de contraseña — validado solo en frontend, no se envía al backend.
- **INV-5.4.1-05:** la pagina `/registro` es accesible sin autenticacion y redirige al login al completar con exito.

### Operacion principal — auto-registro

| | Descripcion |
|---|---|
| **Precondicion** | El usuario no tiene cuenta en el sistema. |
| **Postcondicion** | El `Usuario` queda persistido con nombre, apellido, email, password_hash, rol y activo=true. El usuario es redirigido a `/login`. |

**Schema del endpoint:**

```
POST /auth/registro
Body: { nombre, apellido, email, password, rol }

201 Created -> { usuario_id: UUID }
403 Forbidden -> { detail: "El rol ADMIN no está permitido en el auto-registro" }
409 Conflict  -> { detail: "Este email ya está registrado" }
422 Unprocessable -> { detail: "La contraseña debe tener al menos 10 caracteres, una mayúscula y un número" }
```

**Flujo en frontend:**

```
1. Usuario navega a /registro (link desde LoginPage: "¿No tenés cuenta? Registrate")
2. Completa: Nombre, Apellido, Email, Contraseña, Rol (selector: JUEZ / ATLETA / ORGANIZADOR)
3. Submit -> POST /auth/registro
4a. 201 -> mensaje "Cuenta creada. Iniciá sesión." + redirect a /login tras 2s
4b. 409 -> error inline "Este email ya está registrado"
4c. 422 -> error inline "La contraseña debe tener al menos 8 caracteres"
```

**Ejemplo concreto:**

```
Usuario abre /registro.
Completa: nombre="Ana", apellido="García", email="ana@email.com", password="apnea123", rol="ATLETA"
Submit -> POST /auth/registro 201
Redirigido a /login con mensaje "Cuenta creada. Iniciá sesión."

Segundo intento con mismo email:
Submit -> POST /auth/registro 409
Mensaje inline: "Este email ya está registrado"
```

### Impacto en UsuariosPage

`UsuariosPage.tsx` debe mostrar `nombre` y `apellido` en la lista junto al email y rol, ya que el aggregate extendido los provee. El endpoint `GET /auth/usuarios` actualiza su respuesta para incluirlos.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.4.1 — Auto-registro de usuario

  Scenario: auto-registro exitoso como atleta
    Given no existe ninguna cuenta con email "ana@email.com"
    When "ana@email.com" completa el formulario con nombre "Ana", apellido "García", password "apnea123" y rol "ATLETA"
    And confirma el registro
    Then el sistema responde 201
    And el usuario queda guardado con nombre "Ana", apellido "García" y rol "ATLETA"
    And el usuario es redirigido a /login

  Scenario: nombre o apellido vacíos son rechazados antes de enviar
    Given el formulario de registro está abierto
    When el usuario deja el campo "nombre" vacío
    And intenta confirmar el registro
    Then el formulario muestra "El nombre es requerido"
    And no se envía POST /auth/registro

  Scenario: email duplicado muestra error inline
    Given ya existe un usuario con email "juez1@email.com"
    When alguien intenta registrarse con email "juez1@email.com"
    Then el sistema responde 409
    And se muestra "Este email ya está registrado" en el formulario

  Scenario: rol ADMIN es rechazado por el backend
    Given el cliente envía POST /auth/registro con rol "ADMIN"
    Then el sistema responde 403
    And el mensaje es "El rol ADMIN no está permitido en el auto-registro"

  Scenario: rol ADMIN no aparece en el selector del formulario
    Given el formulario de registro está abierto
    Then el selector de rol muestra solo "JUEZ", "ATLETA" y "ORGANIZADOR"
    And no muestra "ADMIN"

  Scenario: link de registro visible en la pagina de login
    Given el usuario no autenticado navega a /login
    Then ve el link "¿No tenés cuenta? Registrate" que apunta a /registro
```

---

## Impacto arquitectonico

- [x] Si — modifica domain (aggregate + command), application (handler), infrastructure (repo + schema) y api (endpoint + schema).

**Capas afectadas:**

- `identidad/domain/aggregates/usuario.py` — agregar `nombre: str` y `apellido: str`.
- `identidad/domain/exceptions.py` — agregar `RolNoPermitido`.
- `identidad/application/commands/registrar_usuario.py` — agregar `nombre`, `apellido` al command; handler valida `rol ≠ ADMIN`.
- `identidad/infrastructure/repositories/sqlite_usuario_repository.py` — agregar columnas `nombre`, `apellido` al CREATE TABLE; actualizar save/find_by_email/find_by_id/list_by_rol/list_all.
- `identidad/api/router.py` — extender `RegistroRequest` con `nombre`, `apellido`; agregar `nombre`, `apellido` a `UsuarioResponse`; devolver 403 si rol==ADMIN.
- `frontend/src/api/identidad.ts` — extender payload de `registrarUsuario` con `nombre`, `apellido`; actualizar tipo `UsuarioResponse`.
- `frontend/src/pages/RegistroPage.tsx` — nueva pagina publica con formulario completo.
- `frontend/src/pages/LoginPage.tsx` — agregar link "¿No tenés cuenta? Registrate" apuntando a `/registro`.
- `frontend/src/pages/organizador/UsuariosPage.tsx` — mostrar `nombre` y `apellido` en la lista.
- `frontend/src/App.tsx` — agregar ruta `/registro` sin `RequireRole`.

---

## Migracion de base de datos

La tabla `usuarios` gana dos columnas. Se usa `CREATE TABLE IF NOT EXISTS` con las columnas ya presentes en la definición — el approach de `_ensure_table` implica que la tabla preexistente **no** se migra automaticamente. Estrategia: `ALTER TABLE` en `_ensure_table` con `IF NOT EXISTS` para cada columna nueva, permitiendo upgrade de DBs existentes.

```sql
ALTER TABLE usuarios ADD COLUMN nombre  TEXT NOT NULL DEFAULT '';
ALTER TABLE usuarios ADD COLUMN apellido TEXT NOT NULL DEFAULT '';
```

Los usuarios preexistentes quedan con nombre/apellido vacíos — aceptable para el MVP.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.4`
- Aggregate: `src/identidad/domain/aggregates/usuario.py`
- Command actual: `src/identidad/application/commands/registrar_usuario.py`
- Repo: `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py`
- Endpoint: `src/identidad/api/router.py` — `POST /auth/registro`
- Pagina previa: `frontend/src/pages/LoginPage.tsx`

---

*Redactado: 2026-04-24 — INC-5.4 Identidad Extendida*
*Enmendado: 2026-04-24 — INV-5.4.1-04 actualizado (política contraseñas → ADR-019) · INV-5.4.1-06 nuevo (confirmación frontend) · RegistroPage agrega campo confirmación + PasswordStrengthBar*
