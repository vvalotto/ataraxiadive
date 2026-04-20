# Fase 0 — Validación de Contexto: US-5.1.4

**Historia de Usuario:** US-5.1.4 — Generación y ajuste de grilla desde la UI del organizador
**Producto:** frontend
**Puntos:** 3
**Prioridad:** Media

## Arquitectura

- Patrón: frontend React/Vite consumiendo API hexagonal DDD BC-first.
- Contexto obligatorio leído: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- Spec canónica encontrada: `docs/specs/sp5/US-5.1.4.md`.
- Documentación arquitectónica encontrada:
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`

## Estructura validada

- Implementación frontend: `frontend/src/`.
- Página afectada: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`.
- API client afectado: `frontend/src/api/competencia.ts`.
- Componentes organizador existentes: `frontend/src/components/organizador/`.
- Tab `Grilla` existe como placeholder desde US-5.1.2.

## Quality Gates

- `frontend/package.json` define `npm run build` y `npm run lint`.
- Para esta US frontend, los gates Python del skill se sustituyen por build/lint frontend.
- Validación BDD/UI será documental/manual salvo que exista harness browser automatizado.

## Observaciones

- La spec indica usar `@dnd-kit/core`, pero no aparece declarado en `frontend/package.json`.
- El plan de Fase 2 debe decidir entre agregar esa dependencia o implementar reordenamiento con drag nativo HTML5 para evitar instalar paquetes.

**Estado:** contexto validado para continuar con Fase 1.
