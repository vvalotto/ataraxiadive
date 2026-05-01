# Plan de Implementacion: US-5.4.3 - Olvide contrasena

**Historia:** US-5.4.3 - Olvidé contraseña
**Incremento:** INC-5.4 - Identidad Extendida
**Producto:** identidad + notificaciones + frontend
**Patron:** Hexagonal DDD BC-first + React/Vite frontend
**Estimacion:** 5 puntos
**Estado:** EN PLANIFICACION

---

## Alcance

Implementar recuperacion de acceso via email:

- Extender `TokenServicePort` y `JWTService` con generacion de reset token.
- Agregar `SolicitarResetPasswordHandler` y `ResetPasswordHandler`.
- Exponer `POST /auth/solicitar-reset` y `POST /auth/reset-password`.
- Enviar email usando `EmailPort` existente del BC Notificaciones.
- Agregar paginas publicas `/recuperar-password` y `/reset-password`.
- Agregar link desde `LoginPage` a recuperacion.

Fuera de alcance: invalidacion persistente de tokens, rate limiting, auditoria del intento de recuperacion.

---

## Componentes a Modificar

### Dominio identidad

- [ ] `src/identidad/domain/ports/token_service_port.py` (15 min)
  - Agregar `generate_reset_token(email: str) -> str`.

- [ ] `src/identidad/domain/exceptions.py` (15 min)
  - Agregar `TokenResetInvalido`.

### Infraestructura identidad

- [ ] `src/identidad/infrastructure/jwt_service.py` (30 min)
  - Implementar `generate_reset_token()`.
  - Reutilizar `verify()` y validar claim `type=password_reset` en handler de reset.

### Aplicacion identidad

- [ ] `src/identidad/application/commands/solicitar_reset_password.py` (45 min)
  - Buscar usuario por email.
  - Si existe, generar token y delegar envio por `EmailPort`.
  - Siempre retornar sin revelar existencia del email.

- [ ] `src/identidad/application/commands/reset_password.py` (45 min)
  - Verificar token, validar `type=password_reset`, localizar usuario y persistir hash nuevo.
  - Mapear token invalido o expirado a excepcion de negocio.

### API identidad

- [ ] `src/identidad/api/router.py` (45 min)
  - Agregar schemas request/response para `solicitar-reset` y `reset-password`.
  - Exponer ambos endpoints publicos.
  - Mapear `TokenResetInvalido` a `400`.

### Integracion con notificaciones

- [ ] `src/app.py` (30 min)
  - Construir/inyectar `EmailPort` para el handler de solicitar reset.
  - Resolver `FRONTEND_URL` para el link del email.

### Frontend API

- [ ] `frontend/src/api/identidad.ts` (25 min)
  - Agregar `solicitarResetPassword(email)` y `resetPassword(token, passwordNueva)`.

### Frontend paginas y routing

- [ ] `frontend/src/pages/RecuperarPasswordPage.tsx` (60 min)
  - Formulario email + mensaje neutro de confirmacion.

- [ ] `frontend/src/pages/ResetPasswordPage.tsx` (75 min)
  - Leer token de querystring.
  - Formulario password nueva + confirmacion.
  - Manejo de token invalido/expirado.

- [ ] `frontend/src/pages/LoginPage.tsx` (15 min)
  - Agregar link a `/recuperar-password`.

- [ ] `frontend/src/App.tsx` (20 min)
  - Agregar rutas publicas nuevas.

---

## Tests

### Unitarios backend

- [ ] `tests/unit/identidad/application/test_handlers.py` o archivos nuevos (45 min)
  - Cubrir solicitar-reset con email existente/inexistente.
  - Cubrir reset con token valido, token expirado y token de sesion.

- [ ] `tests/unit/identidad/api/test_reset_password.py` (40 min)
  - Cubrir `200`, `204`, `400` y `422`.

### Integracion backend

- [ ] `tests/integration/identidad/` (25 min)
  - Verificar que la password queda actualizada luego del reset completo.

### Frontend

- [ ] Validacion TypeScript/build (20 min)
  - Ejecutar `npm run build`.
  - Ejecutar `npm run lint`.

### BDD

- [ ] `tests/features/US-5.4.3-recuperar-password.feature` (15 min)
  - Feature creada en Fase 1.
  - Validacion UI/manual documentada si no hay harness browser automatizado.

---

## Quality Gates

- [ ] `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad`
- [ ] `npm run build` en `frontend/`
- [ ] `npm run lint` en `frontend/`
- [ ] `codeguard src/identidad/ --format json > quality/reports/codeguard/US-5.4.3-codeguard-raw.json`

---

## Riesgos y Decisiones

- La respuesta de `solicitar-reset` debe ser identica para emails existentes e inexistentes.
- El link de email necesita `FRONTEND_URL`; si falta configuracion, conviene fallback controlado o fallo explicito del adaptador.
- El token de reset no debe aceptar payload de token de sesion.
- La integracion usa `EmailPort` de Notificaciones por DI desde `src/app.py`, sin imports directos entre BCs en capas internas.

---

## Criterios de Aceptacion Cubiertos

- [ ] Solicitar reset responde 200 para email existente e inexistente.
- [ ] Reset exitoso con token valido.
- [ ] Token expirado o de tipo incorrecto se rechaza.
- [ ] Password nueva corta se rechaza.
- [ ] Login muestra link a recuperacion.

**Estado:** 0/10 tareas completadas
