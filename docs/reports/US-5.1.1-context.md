# US-5.1.1 — Contexto Validado

**Historia de Usuario:** Crear/editar torneo — formulario del organizador  
**Sprint:** SP5 — La Puesta en Marcha  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Puntos:** 3  
**Estado inicial:** To Do

## Arquitectura

- Patron confirmado: hexagonal DDD BC-first para backend; React/Vite PWA para frontend.
- Contexto obligatorio leido: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- US-IEDD encontrada: `docs/specs/sp5/US-5.1.1.md`.
- Documentacion arquitectonica requerida encontrada:
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`

## Alcance Validado

- La US afecta solo frontend:
  - `frontend/src/pages/organizador/`
  - `frontend/src/api/torneo.ts`
- Consume endpoints existentes:
  - `POST /torneos`
  - `PUT /torneos/{torneo_id}/disciplinas`
- No requiere cambios de dominio ni API backend.

## Quality Gates

- `CLAUDE.md` presente.
- `tests/` presente con estructura `unit`, `integration`, `features`.
- `pyproject.toml` contiene configuracion de:
  - `tool.coverage`
  - `tool.codeguard`
  - `tool.designreviewer`
- Frontend presente con `frontend/package.json` y scripts `build`/`lint`.

## Listo Para Fase 1

Se puede proceder con generacion de escenarios BDD para `tests/features/US-5.1.1-crear-torneo-ui.feature`.
