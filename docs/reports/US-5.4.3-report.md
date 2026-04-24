# Reporte de Implementacion: US-5.4.3

## Resumen Ejecutivo

- **Historia de Usuario:** US-5.4.3 - Olvidé contraseña
- **Puntos estimados:** 5
- **Estado:** COMPLETADO
- **Fecha completado:** 2026-04-24
- **Branch de trabajo:** `feature/US-5.4.3-recuperar-password`

## Componentes Implementados

- [x] Extension de `TokenServicePort` y `JWTService` para tokens de recuperacion de password.
- [x] Nueva excepcion `TokenResetInvalido`.
- [x] Nuevos command/handler `SolicitarResetPassword` y `ResetPassword`.
- [x] Nuevos endpoints publicos `POST /auth/solicitar-reset` y `POST /auth/reset-password`.
- [x] Inyeccion de `EmailPort` en identidad desde el composition root.
- [x] Envio de email con enlace a `/reset-password?token=...`.
- [x] Cliente frontend actualizado con `solicitarResetPassword()` y `resetPassword()`.
- [x] Nuevas paginas `frontend/src/pages/RecuperarPasswordPage.tsx` y `frontend/src/pages/ResetPasswordPage.tsx`.
- [x] `LoginPage` con link a recuperacion y mensaje post-reset.
- [x] Cobertura de tests para flujo exitoso, token de sesion y token expirado.

## Comportamiento Entregado

- Una persona no autenticada puede pedir recuperacion de password desde el login.
- El backend siempre responde `200` al solicitar reset sin filtrar si el email existe o no.
- Si el usuario existe, se genera un JWT de recuperacion con tipo `password_reset` y expiracion corta.
- El enlace enviado apunta a la pantalla publica de reset y permite definir una nueva password.
- El backend rechaza tokens invalidos, expirados o de sesion con `400`.
- Al completar el reset, el usuario vuelve al login con mensaje de exito.

## Validacion Ejecutada

| Gate | Resultado |
|------|-----------|
| `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad` | OK |
| `npm run build` | OK |
| `npm run lint` | OK |
| Validacion BDD/UI en navegador | Pendiente manual |

## Riesgos y Observaciones

- El enlace de recuperacion usa `FRONTEND_BASE_URL` y cae en `http://localhost:5173` si no esta configurado.
- El adapter de email en desarrollo sigue siendo `LoggingEmailAdapter` cuando `RESEND_API_KEY` no existe.
- La advertencia de chunk >500 kB en Vite sigue presente, pero no bloquea el build.
- Los tests JWT siguen emitiendo `InsecureKeyLengthWarning` por el fixture existente de secret corto.

## Archivos Relevantes

- `src/identidad/application/commands/solicitar_reset_password.py`
- `src/identidad/application/commands/reset_password.py`
- `src/identidad/api/router.py`
- `src/identidad/api/dependencies.py`
- `src/identidad/infrastructure/jwt_service.py`
- `src/app.py`
- `frontend/src/pages/RecuperarPasswordPage.tsx`
- `frontend/src/pages/ResetPasswordPage.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `tests/unit/identidad/api/test_reset_password.py`

## Criterios de Aceptacion

- [x] Solicitar reset con email existente responde sin exponer existencia y dispara email.
- [x] Solicitar reset con email inexistente responde igual.
- [x] Reset con token valido actualiza la password.
- [x] Reset con token expirado retorna `400`.
- [x] Reset con token de sesion retorna `400`.
- [x] Login muestra link a recuperacion.
