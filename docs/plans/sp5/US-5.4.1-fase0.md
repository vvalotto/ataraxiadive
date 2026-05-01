# US-5.4.1 — Fase 0: Validacion de Contexto

**Fecha:** 2026-04-24
**Branch:** `feature/US-5.4.1-auto-registro`
**Producto:** `identidad` + `frontend`
**Incremento:** INC-5.4 — Identidad Extendida

---

## Historia de Usuario

**US:** US-5.4.1 — Auto-registro de usuario

Como **persona sin cuenta**, quiero **registrarme con mi nombre, apellido, email, password y rol** para **acceder a la plataforma con el rol adecuado sin intervencion del organizador**.

**Spec canonica:** `docs/specs/sp5/US-5.4.1.md`

---

## Contexto Validado

### Arquitectura

- Patron confirmado: Hexagonal DDD BC-first.
- BC principal: `identidad`.
- Producto UI afectado: `frontend`.
- El flujo reutiliza el endpoint publico `POST /auth/registro` y extiende el aggregate `Usuario`.

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

- `Usuario` hoy persiste `email`, `password_hash`, `rol` y `activo`; aun no tiene `nombre` ni `apellido`.
- `RegistrarUsuarioCommand` y `RegistrarUsuarioHandler` aceptan solo `email`, `password` y `rol`.
- `POST /auth/registro` ya existe y devuelve `201`, `409` o `422`, pero no bloquea `ADMIN`.
- `GET /auth/usuarios` ya soporta listado completo para organizador, aunque la respuesta no incluye `nombre` ni `apellido`.
- `SQLiteUsuarioRepository` crea la tabla `usuarios` sin columnas `nombre` y `apellido`, por lo que necesita migracion compatible con bases existentes.

### Frontend

- `LoginPage` no ofrece aun link publico a `/registro`.
- `App.tsx` no expone ruta publica `/registro`.
- `frontend/src/api/identidad.ts` soporta creacion/listado de usuarios, pero el payload de alta no incluye `nombre` ni `apellido`.
- `UsuariosPage.tsx` muestra email, rol y estado; todavia no renderiza nombre/apellido.

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
  - `npm run lint` en `frontend/` si el baseline local lo permite

---

## Riesgos Detectados

- La migracion de SQLite debe ser idempotente: la tabla ya existe en entornos locales previos.
- La regla `rol != ADMIN` tiene que aplicarse en backend, no solo en el selector del frontend.
- Extender `UsuarioResponse` impacta la pagina existente `UsuariosPage`; esa pantalla no puede quedar desincronizada con la API.
- El criterio de exito del registro combina UI publica y BC `identidad`; conviene implementar primero dominio/API y luego la pagina publica.

---

## Resultado

Contexto validado. La US esta lista para Fase 1: escenarios BDD.
