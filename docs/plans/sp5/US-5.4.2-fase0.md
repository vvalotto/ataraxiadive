# US-5.4.2 — Fase 0: Validacion de Contexto

**Fecha:** 2026-04-24
**Branch:** `feature/US-5.4.2-cambiar-password`
**Producto:** `identidad` + `frontend`
**Incremento:** INC-5.4 — Identidad Extendida

---

## Historia de Usuario

**US:** US-5.4.2 — Cambiar contraseña

Como **usuario autenticado**, quiero **cambiar mi contraseña ingresando la contraseña actual y la nueva** para **mantener el control de la seguridad de mi cuenta**.

**Spec canonica:** `docs/specs/sp5/US-5.4.2.md`

---

## Contexto Validado

### Arquitectura

- Patron confirmado: Hexagonal DDD BC-first.
- BC principal: `identidad`.
- Producto UI afectado: `frontend`.
- La autenticacion ya emite JWT con `sub`, `email` y `rol`; el cambio de password debe reutilizar el `userId` persistido en `useAuthStore`.

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
- `frontend/src/pages/`
- `frontend/src/api/`
- `tests/features/`

---

## Estado Actual Relevante

### Backend identidad

- `PasswordHashingPort` ya expone `hash()` y `verify()`, y `BcryptPasswordHasher` implementa ambas operaciones.
- `UsuarioRepositoryPort` ya permite `find_by_id()` y `save()`, suficientes para un command de cambio de password sin tocar el aggregate.
- `router.py` ya usa `get_current_user` indirectamente en dependencias de rol, pero no tiene aun un endpoint autenticado transversal para cambio de contraseña.
- Las excepciones actuales cubren password corta, email duplicado y roles; falta una excepcion especifica para password actual incorrecta.

### Frontend

- `useAuthStore` persiste `userId`, `email`, `rol` y `token`, por lo que la UI puede redirigir al home correcto luego del cambio.
- Existe `RequireRole`, pero hoy las rutas estan segmentadas por rol; no hay una pantalla comun de cambio de password para todos los usuarios autenticados.
- `LoginPage` y `RegistroPage` ya existen, pero no hay navegacion a una pantalla de cambio de password.

---

## Quality Gates

- `CLAUDE.md` encontrado.
- `pyproject.toml` encontrado.
- `[tool.codeguard]` configurado.
- `[tool.designreviewer]` configurado.
- Tests configurados en `tests/`.
- Para esta US mixta, los gates esperables son:
  - `pytest` sobre identidad
  - `npm run build` en `frontend/`
  - `npm run lint` en `frontend/`

---

## Riesgos Detectados

- La ruta frontend debe ser transversal a los tres roles sin abrir acceso a usuarios anonimos.
- El endpoint debe usar el `sub` del JWT como fuente de verdad del usuario y no aceptar `usuario_id` en el body.
- El token actual sigue siendo valido tras el cambio; la UI no puede asumir logout automatico.
- Si el acceso a la pantalla queda escondido en la navegacion, la funcionalidad puede estar implementada pero no ser alcanzable en UAT.

---

## Resultado

Contexto validado. La US esta lista para Fase 1: escenarios BDD.
