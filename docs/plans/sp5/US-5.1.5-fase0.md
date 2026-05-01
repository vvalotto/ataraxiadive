# Fase 0 — Validación de Contexto: US-5.1.5

**Historia de Usuario:** US-5.1.5 — Asignación de jueces a disciplinas desde la UI
**Producto:** frontend
**Puntos:** 3
**Prioridad:** Media

## Arquitectura

- Patrón: frontend React/Vite consumiendo APIs de `torneo` e `identidad`.
- Contexto obligatorio leído: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- Spec canónica encontrada: `docs/specs/sp5/US-5.1.5.md`.
- Documentación arquitectónica encontrada:
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`

## Endpoints Verificados

- `PUT /torneos/{torneo_id}/disciplinas/{disciplina}/juez` existe.
- `GET /torneos/{torneo_id}/disciplinas` existe.
- `GET /torneos/{torneo_id}/jueces/{juez_id}/disciplinas` existe.
- No se encontró `GET /identidad/usuarios` ni equivalente para listar usuarios por rol.

## Estructura Frontend Validada

- Página afectada: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`.
- API afectadas: `frontend/src/api/torneo.ts` y nueva `frontend/src/api/identidad.ts`.
- Componentes organizador existentes: `frontend/src/components/organizador/`.
- Tab `Jueces` existe como placeholder desde US-5.1.2.

## Quality Gates

- `frontend/package.json` define `npm run build` y `npm run lint`.
- Para esta US frontend, los gates Python del skill se sustituyen por build/lint frontend.
- Si se agrega endpoint de Identidad, se validará con `py_compile` y tests Python focalizados.

## Observaciones

- La US necesita un endpoint de consulta en Identidad para listar usuarios con rol `JUEZ`.
- El plan de Fase 2 debe decidir si agregar `GET /auth/usuarios?rol=JUEZ` o una ruta bajo
  otro prefijo. En el código actual el router de Identidad expone `/auth`, no `/identidad`.

**Estado:** contexto validado para continuar con Fase 1.
