# US-5.1.2 — Contexto Validado

**Historia de Usuario:** Gestion de fases del torneo  
**Sprint:** SP5 — La Puesta en Marcha  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Puntos:** 3  
**Estado inicial:** To Do

## Arquitectura

- Contexto obligatorio leido: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- US-IEDD encontrada: `docs/specs/sp5/US-5.1.2.md`.
- Patron vigente: frontend React/Vite consumiendo BC `torneo`.
- No requiere cambios backend: los endpoints de transicion ya existen en `src/torneo/api/router.py`.

## Alcance Validado

- Extender `frontend/src/api/torneo.ts` con operaciones de transicion.
- Extender `frontend/src/pages/organizador/DetalleTorneoPage.tsx`.
- Crear componentes:
  - `FaseBadge`
  - `AccionesPanel`
- Mostrar tabs base del panel organizador para fases futuras.

## Endpoints Consumidos

- `PUT /torneos/{id}/abrir-inscripcion`
- `PUT /torneos/{id}/cerrar-inscripcion`
- `PUT /torneos/{id}/iniciar-ejecucion`
- `PUT /torneos/{id}/volver-preparacion`
- `PUT /torneos/{id}/iniciar-premiacion`
- `PUT /torneos/{id}/cerrar`
- `PUT /torneos/{id}/cancelar`
- `GET /torneos/{id}` para refresco post-transicion.

## Quality Gates

- `CLAUDE.md` presente.
- `tests/features/` presente.
- `frontend/package.json` presente.
- `pyproject.toml` contiene `tool.coverage`, `tool.codeguard` y `tool.designreviewer`.

## Listo Para Fase 1

Se puede proceder con escenarios BDD en `tests/features/US-5.1.2-gestion-fases-torneo.feature`.
