# US-5.4.3 — Fase 0: Validacion de Contexto

**Fecha:** 2026-04-24
**Branch:** `feature/US-5.4.3-recuperar-password`
**Producto:** `identidad` + `notificaciones` + `frontend`
**Incremento:** INC-5.4 — Identidad Extendida

---

## Historia de Usuario

**US:** US-5.4.3 — Olvide contrasena

Como **usuario sin acceso a su cuenta**, quiero **recibir un email con un enlace para restablecer mi contrasena** para **recuperar el acceso sin intervencion del administrador**.

**Spec canonica:** `docs/specs/sp5/US-5.4.3.md`

---

## Contexto Validado

### Arquitectura

- Patron confirmado: Hexagonal DDD BC-first.
- BC principal: `identidad`.
- Integracion tecnica requerida: `EmailPort` de `notificaciones` via composition root en `src/app.py`.
- Producto UI afectado: `frontend` con dos paginas publicas nuevas.

### Artefactos arquitectonicos encontrados

- `docs/contexto/ATARAXIADIVE-CONTEXT.md`
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
- `docs/adr/ADR-006-estructura-bc-first.md`
- `docs/design/architecture.md`
- `docs/design/domain-model.md`

### Estructura verificada

- `src/identidad/domain/`
- `src/identidad/application/`
- `src/identidad/infrastructure/`
- `src/identidad/api/`
- `src/notificaciones/domain/ports/email_port.py`
- `src/notificaciones/infrastructure/email/resend_email_adapter.py`
- `frontend/src/pages/`
- `tests/features/`

---

## Estado Actual Relevante

### Backend identidad

- `TokenServicePort` hoy solo expone `generate()` y `verify()`; falta extenderlo para token de reset.
- `JWTService` ya firma/verifica JWT con `IDENTIDAD_JWT_SECRET`, por lo que puede reutilizarse para reset tokens con claim `type`.
- `router.py` ya tiene endpoints publicos de `registro` y autenticados de `cambiar-password`; aun no existen endpoints de recuperacion.
- `UsuarioRepositoryPort` ya expone `find_by_email()` y `save()`, suficientes para solicitar reset y persistir la nueva password.

### Notificaciones

- `EmailPort` existe y la implementacion real de Resend vive en `src/notificaciones/infrastructure/email/resend_email_adapter.py`.
- `src/app.py` ya construye `ResendEmailAdapter` y `LoggingEmailAdapter` para P-10/P-11; ese patron puede reutilizarse para el flujo de recuperacion sin romper hexagonal.

### Frontend

- `LoginPage` ya contiene CTA a `/registro`, pero aun no ofrece acceso a recuperacion de password.
- `frontend/src/api/identidad.ts` ya maneja errores de negocio y requests publicos; es un buen punto para agregar `solicitarResetPassword()` y `resetPassword()`.
- `App.tsx` ya expone rutas publicas `/login` y `/registro`; faltan `/recuperar-password` y `/reset-password`.

---

## Quality Gates

- `CLAUDE.md` encontrado.
- `pyproject.toml` encontrado.
- `[tool.codeguard]` configurado.
- `[tool.designreviewer]` configurado.
- Tests configurados en `tests/`.
- Para esta US mixta, los gates esperables son:
  - `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad`
  - `npm run build` en `frontend/`
  - `npm run lint` en `frontend/`

---

## Riesgos Detectados

- La spec cita una ruta de Resend sin subcarpeta `email/`; en el repo real el path correcto es `src/notificaciones/infrastructure/email/resend_email_adapter.py`.
- `POST /auth/solicitar-reset` no debe filtrar existencia de email en timing ni en response body.
- `verify()` hoy lanza `TokenInvalido` generico; para reset conviene diferenciar token invalido/expirado o mapearlo cuidadosamente a error de negocio `400`.
- El link de reset depende de un `FRONTEND_URL` estable para construir la URL en el email.

---

## Resultado

Contexto validado. La US esta lista para Fase 1: escenarios BDD.
