# US-5.4.3: Olvidé contraseña

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.4
**Bounded Context**: `identidad` + `notificaciones` + `frontend`
**Capas afectadas**: `identidad/domain/ports/`, `identidad/infrastructure/`, `identidad/application/commands/`, `identidad/api/router.py`, `frontend/src/pages/`

---

## Descripcion

Como **usuario sin acceso a su cuenta**,
quiero **recibir un email con un enlace para restablecer mi contraseña**
para **recuperar el acceso sin intervención del administrador**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Descripcion |
|---|---|---|
| Metodo nuevo en port | `TokenServicePort.generate_reset_token(email)` | JWT `{sub: email, type: "password_reset", exp: now+1h}` |
| Command nuevo | `SolicitarResetPasswordCommand` | `email: str` |
| Handler nuevo | `SolicitarResetPasswordHandler` | Busca usuario; si existe genera token y delega envio de email; siempre retorna sin revelar si el email existe |
| Command nuevo | `ResetPasswordCommand` | `token: str`, `password_nueva: str` |
| Handler nuevo | `ResetPasswordHandler` | Verifica JWT type=="password_reset"; actualiza password_hash |
| Excepcion nueva | `TokenResetInvalido` | Token expirado, mal formado o de tipo incorrecto |
| Endpoint 1 nuevo | `POST /auth/solicitar-reset` | Publico; body `{email}`; siempre 200 |
| Endpoint 2 nuevo | `POST /auth/reset-password` | Publico; body `{token, password_nueva}`; 204 en exito |
| Pagina 1 nueva | `RecuperarPasswordPage` | Formulario con campo email; ruta `/recuperar-password` |
| Pagina 2 nueva | `ResetPasswordPage` | Formulario nueva password; ruta `/reset-password?token=...` |

### Lenguaje ubicuo relevante

- **token de reset:** JWT de uso unico con claim `type: "password_reset"` y expiracion de 1 hora. Firmado con el mismo secreto que los tokens de sesion.
- **solicitar-reset:** endpoint publico que no revela si el email existe — siempre responde 200 para evitar enumeracion de usuarios.
- **reset-password:** endpoint que acepta el token del link y la nueva password; invalida el token al cambiar la password (el token tiene exp 1h — es de uso temporal, no se persiste ni se invalida explicitamente).

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.4.3-01:** `POST /auth/solicitar-reset` siempre responde 200 independientemente de si el email existe — previene enumeracion de usuarios.
- **INV-5.4.3-02:** el token de reset tiene `type: "password_reset"` y `exp: now+1h` firmado con `IDENTIDAD_JWT_SECRET`.
- **INV-5.4.3-03:** `POST /auth/reset-password` rechaza con 400 si el token es invalido, expirado o su `type ≠ "password_reset"`.
- **INV-5.4.3-04:** ~~`password_nueva` debe tener ≥8 caracteres~~ → ≥10 caracteres + al menos 1 mayúscula + 1 número — rechaza con 422. Ver ADR-019.
- **INV-5.4.3-05:** el email se envía unicamente si el usuario existe en el sistema — el endpoint no revela este hecho externamente.

### Operacion 1 — solicitar reset

| | Descripcion |
|---|---|
| **Precondicion** | Ninguna (endpoint publico). |
| **Postcondicion** | Si el email existe: token generado y email enviado via Resend con link `/reset-password?token=<jwt>`. Si no existe: no se hace nada. En ambos casos la respuesta es identica. |

**Schema del endpoint:**

```
POST /auth/solicitar-reset
Body: { email }

200 OK -> { message: "Si el email está registrado, recibirás un enlace en breve." }
```

**Email enviado (si el usuario existe):**

```
Subject: Restablecé tu contraseña — AtaraxiaDive
Body:
  Hola <nombre>,

  Recibimos una solicitud para restablecer tu contraseña.
  Hacé clic en el siguiente enlace (válido por 1 hora):

  <FRONTEND_URL>/reset-password?token=<jwt>

  Si no solicitaste este cambio, ignorá este email.
```

### Operacion 2 — reset password

| | Descripcion |
|---|---|
| **Precondicion** | El usuario tiene un token valido (no expirado, type=="password_reset"). |
| **Postcondicion** | El `password_hash` del usuario queda actualizado. El token deja de ser util (exp natural). |

**Schema del endpoint:**

```
POST /auth/reset-password
Body: { token, password_nueva }

204 No Content   -> exito
400 Bad Request  -> { detail: "El enlace es inválido o ha expirado" }
422 Unprocessable -> { detail: "La contraseña debe tener al menos 10 caracteres, una mayúscula y un número" }
```

**Flujo en frontend:**

```
PAGINA 1 — /recuperar-password
1. Usuario ingresa su email
2. Submit -> POST /auth/solicitar-reset
3. Siempre muestra: "Si el email está registrado, recibirás un enlace en breve."

PAGINA 2 — /reset-password?token=<jwt>
1. Frontend extrae token de la URL
2. Usuario ingresa nueva password + confirmacion
3. Validacion frontend: nueva ≥ 8 chars; nueva == confirmacion
4. Submit -> POST /auth/reset-password { token, password_nueva }
5a. 204 -> "Contraseña actualizada. Iniciá sesión." + redirect a /login tras 2s
5b. 400 -> "El enlace es inválido o ha expirado. Solicitá uno nuevo." + link a /recuperar-password
5c. 422 -> error inline desde backend
```

**Ejemplo concreto:**

```
Usuario navega a /recuperar-password
Ingresa: email="ana@email.com"
Submit -> POST /auth/solicitar-reset 200
Muestra: "Si el email está registrado, recibirás un enlace en breve."

Ana recibe email con link: /reset-password?token=eyJ...
Navega al link -> /reset-password?token=eyJ...
Ingresa: nueva="nuevaapnea99", confirmacion="nuevaapnea99"
Submit -> POST /auth/reset-password 204
Mensaje: "Contraseña actualizada. Iniciá sesión."
Redirigida a /login

Intento con token expirado (>1h):
Submit -> POST /auth/reset-password 400
Error: "El enlace es inválido o ha expirado. Solicitá uno nuevo."
```

---

## Diseño tecnico del token de reset

`JWTService` extiende `TokenServicePort` con un nuevo metodo:

```python
# TokenServicePort (puerto abstracto)
@abstractmethod
def generate_reset_token(self, email: str) -> str:
    """JWT {sub: email, type: 'password_reset', exp: now+1h}."""

# JWTService (implementacion concreta)
def generate_reset_token(self, email: str) -> str:
    payload = {
        "sub": email,
        "type": "password_reset",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, self._secret, algorithm=self._algorithm)
```

`ResetPasswordHandler` valida con `token_service.verify(token)` y verifica `payload["type"] == "password_reset"` — si falla lanza `TokenResetInvalido`.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.4.3 — Olvidé contraseña

  Scenario: solicitar reset con email existente siempre responde 200
    Given el usuario "ana@email.com" esta registrado en el sistema
    When se envía POST /auth/solicitar-reset con email "ana@email.com"
    Then el sistema responde 200
    And el mensaje es "Si el email está registrado, recibirás un enlace en breve."
    And se envía un email a "ana@email.com" con un link de reset

  Scenario: solicitar reset con email inexistente tambien responde 200
    Given no existe ningun usuario con email "noexiste@email.com"
    When se envía POST /auth/solicitar-reset con email "noexiste@email.com"
    Then el sistema responde 200
    And el mensaje es "Si el email está registrado, recibirás un enlace en breve."
    And no se envía ningun email

  Scenario: reset exitoso con token valido
    Given "ana@email.com" tiene un token de reset valido "eyJ..."
    When se envía POST /auth/reset-password con el token y password_nueva "nueva_apnea99"
    Then el sistema responde 204
    And "ana@email.com" puede autenticarse con "nueva_apnea99"

  Scenario: token expirado es rechazado
    Given "ana@email.com" tiene un token de reset expirado (mas de 1h)
    When se envía POST /auth/reset-password con ese token y password_nueva "nueva_apnea99"
    Then el sistema responde 400
    And el mensaje es "El enlace es inválido o ha expirado"

  Scenario: token de sesion no es aceptado como token de reset
    Given "ana@email.com" esta autenticada y tiene un token de sesion valido
    When se envía POST /auth/reset-password con ese token de sesion
    Then el sistema responde 400
    And el mensaje es "El enlace es inválido o ha expirado"

  Scenario: nueva password menor a 8 caracteres es rechazada
    Given "ana@email.com" tiene un token de reset valido
    When se envía POST /auth/reset-password con password_nueva "abc"
    Then el sistema responde 422

  Scenario: link de recuperacion visible en la pagina de login
    Given el usuario no autenticado navega a /login
    Then ve el link "¿Olvidaste tu contraseña?" que apunta a /recuperar-password
```

---

## Impacto arquitectonico

- [x] Si — extiende el puerto `TokenServicePort`, agrega commands/handlers, dos endpoints nuevos, dos paginas nuevas.

**Capas afectadas:**

- `identidad/domain/ports/token_service_port.py` — agregar metodo abstracto `generate_reset_token(email: str) -> str`.
- `identidad/domain/exceptions.py` — agregar `TokenResetInvalido`.
- `identidad/infrastructure/jwt_service.py` — implementar `generate_reset_token()`.
- `identidad/application/commands/solicitar_reset_password.py` — nuevo: `SolicitarResetPasswordCommand` + `SolicitarResetPasswordHandler`.
- `identidad/application/commands/reset_password.py` — nuevo: `ResetPasswordCommand` + `ResetPasswordHandler`.
- `identidad/api/router.py` — dos endpoints nuevos: `POST /auth/solicitar-reset` y `POST /auth/reset-password`.
- `frontend/src/pages/RecuperarPasswordPage.tsx` — nueva pagina publica: formulario email.
- `frontend/src/pages/ResetPasswordPage.tsx` — nueva pagina publica: formulario nueva password + confirmacion; lee token de URL.
- `frontend/src/pages/LoginPage.tsx` — agregar link "¿Olvidaste tu contraseña?" apuntando a `/recuperar-password`.
- `frontend/src/api/identidad.ts` — agregar `solicitarResetPassword(email)` y `resetPassword(token, passwordNueva)`.
- `frontend/src/App.tsx` — agregar rutas `/recuperar-password` y `/reset-password` (publicas).

### Envio de email

El handler `SolicitarResetPasswordHandler` no importa directamente BC Notificaciones (violaria hexagonal). En cambio, delega el envío al mismo adaptador de email que usa BC Notificaciones: importa `EmailPort` desde `notificaciones/domain/ports/email_port.py` y lo recibe por DI.

Alternativa mas simple aceptable para MVP: `SolicitarResetPasswordHandler` recibe un `EmailPort` concreto desde el composition root (`src/app.py`), que inyecta el mismo `ResendEmailAdapter` ya instanciado para BC Notificaciones.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.4`
- Port token: `src/identidad/domain/ports/token_service_port.py`
- JWT service: `src/identidad/infrastructure/jwt_service.py`
- Email adapter: `src/notificaciones/infrastructure/resend_email_adapter.py`
- Email port: `src/notificaciones/domain/ports/email_port.py`
- Composition root: `src/app.py`
- Pagina de login: `frontend/src/pages/LoginPage.tsx`
- Política de contraseñas: `docs/adr/ADR-019-politica-contrasenas.md`

---

*Enmendado: 2026-04-24 — INV-5.4.3-04 actualizado (política contraseñas → ADR-019) · ResetPasswordPage agrega PasswordStrengthBar*

---

*Redactado: 2026-04-24 — INC-5.4 Identidad Extendida*
