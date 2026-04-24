# US-5.4.2: Cambiar contraseña

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.4
**Bounded Context**: `identidad` + `frontend`
**Capas afectadas**: `identidad/application/commands/`, `identidad/api/router.py`, `frontend/src/pages/`

---

## Descripcion

Como **usuario autenticado**,
quiero **cambiar mi contraseña ingresando la contraseña actual y la nueva**
para **mantener el control de la seguridad de mi cuenta**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Descripcion |
|---|---|---|
| Command nuevo | `CambiarPasswordCommand` | `usuario_id`, `password_actual`, `password_nueva` |
| Handler nuevo | `CambiarPasswordHandler` | Verifica bcrypt actual; hashea y persiste la nueva |
| Excepcion nueva | `PasswordActualIncorrecto` | Se lanza si la password actual no coincide |
| Endpoint nuevo | `POST /auth/cambiar-password` | JWT requerido (cualquier rol); 204 en exito |
| Pagina nueva | `CambiarPasswordPage` | Formulario con tres campos: actual, nueva, confirmacion |

### Lenguaje ubicuo relevante

- **password actual:** la contraseña vigente del usuario — se verifica con bcrypt antes de permitir el cambio.
- **password nueva:** la nueva contraseña que reemplazara a la actual — debe tener ≥8 caracteres.
- **confirmacion:** campo de UI que verifica que el usuario no cometio un typo en la nueva password; validado solo en frontend.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.4.2-01:** el usuario debe estar autenticado (JWT valido) para acceder al endpoint.
- **INV-5.4.2-02:** la `password_actual` debe coincidir con el hash almacenado — rechaza con 401 si no coincide.
- **INV-5.4.2-03:** `password_nueva` debe tener ≥8 caracteres — rechaza con 422.
- **INV-5.4.2-04:** `password_nueva` ≠ `password_actual` — validado en frontend; no es invariante de dominio.
- **INV-5.4.2-05:** la confirmacion de password nueva es validada solo en frontend — no se envía al backend.

### Operacion principal — cambiar password

| | Descripcion |
|---|---|
| **Precondicion** | Usuario autenticado con JWT valido (cualquier rol). |
| **Postcondicion** | El `password_hash` del usuario queda actualizado con el hash de `password_nueva`. El token JWT actual sigue siendo valido (no se invalida). |

**Schema del endpoint:**

```
POST /auth/cambiar-password
Authorization: Bearer <token>
Body: { password_actual, password_nueva }

204 No Content  -> exito (sin body)
401 Unauthorized -> { detail: "La contraseña actual es incorrecta" }
422 Unprocessable -> { detail: "La contraseña debe tener al menos 8 caracteres" }
```

**Flujo en frontend:**

```
1. Usuario navega al perfil (menu usuario en header) -> "Cambiar contraseña"
2. Pantalla con tres campos: Contraseña actual | Nueva contraseña | Confirmar nueva contraseña
3. Validacion frontend:
   3a. nueva ≥ 8 chars -> error inline si no
   3b. nueva == confirmacion -> error "Las contraseñas no coinciden" si no
4. Submit -> POST /auth/cambiar-password { password_actual, password_nueva }
5a. 204 -> mensaje "Contraseña actualizada correctamente" + redirect a pagina principal del rol
5b. 401 -> error inline "La contraseña actual es incorrecta"
5c. 422 -> error inline desde backend
```

**Ejemplo concreto:**

```
Juez autenticado navega a /cambiar-password.
Ingresa: actual="apnea123", nueva="nuevapass456", confirmacion="nuevapass456"
Submit -> POST /auth/cambiar-password 204
Mensaje: "Contraseña actualizada correctamente"
Redirigido a /juez/disciplinas

Segundo intento con actual incorrecta:
Ingresa: actual="wrongpass", nueva="nuevapass456"
Submit -> POST /auth/cambiar-password 401
Error inline: "La contraseña actual es incorrecta"
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.4.2 — Cambiar contraseña

  Background:
    Given el usuario "juez1@email.com" esta autenticado con password actual "apnea123"

  Scenario: cambiar password exitosamente
    When el usuario ingresa password actual "apnea123" y nueva password "nuevapass456"
    And confirma el cambio
    Then el sistema responde 204
    And el usuario puede autenticarse con "nuevapass456" en adelante

  Scenario: password actual incorrecta es rechazada
    When el usuario ingresa password actual "wrongpass" y nueva password "nuevapass456"
    And confirma el cambio
    Then el sistema responde 401
    And se muestra "La contraseña actual es incorrecta"

  Scenario: nueva password menor a 8 caracteres es rechazada antes de enviar
    When el usuario ingresa nueva password "abc"
    And intenta confirmar el cambio
    Then el formulario muestra "La contraseña debe tener al menos 8 caracteres"
    And no se envía POST /auth/cambiar-password

  Scenario: confirmacion de nueva password no coincide es rechazada en frontend
    When el usuario ingresa nueva password "nuevapass456" y confirmacion "otrapass789"
    And intenta confirmar el cambio
    Then el formulario muestra "Las contraseñas no coinciden"
    And no se envía POST /auth/cambiar-password
```

---

## Impacto arquitectonico

- [x] Si — agrega command, handler y endpoint nuevos. No modifica el aggregate.

**Capas afectadas:**

- `identidad/domain/exceptions.py` — agregar `PasswordActualIncorrecto`.
- `identidad/application/commands/cambiar_password.py` — nuevo file: `CambiarPasswordCommand` + `CambiarPasswordHandler`.
- `identidad/api/router.py` — nuevo endpoint `POST /auth/cambiar-password`; requiere `get_current_user` (cualquier rol).
- `frontend/src/pages/CambiarPasswordPage.tsx` — nueva pagina con tres campos.
- `frontend/src/api/identidad.ts` — agregar `cambiarPassword(passwordActual, passwordNueva)`.
- `frontend/src/App.tsx` — agregar ruta `/cambiar-password` con `RequireRole` para todos los roles autenticados (o usar `get_current_user` directamente).

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.4`
- Autenticacion: `src/identidad/application/commands/autenticar_usuario.py` — patron `PasswordHashingPort.verify()`
- Port hasher: `src/identidad/domain/ports/password_hashing_port.py`
- Dependencias: `src/identidad/api/dependencies.py` — `get_current_user`
- Aggregate: `src/identidad/domain/aggregates/usuario.py`
- Repo port: `src/identidad/domain/ports/usuario_repository_port.py`

---

*Redactado: 2026-04-24 — INC-5.4 Identidad Extendida*
