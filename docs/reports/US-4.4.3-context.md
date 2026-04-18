# Contexto de Implementación — US-4.4.3

**US:** US-4.4.3 — Sincronización Background Sync + indicador de pendientes  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13

---

## Objetivo validado

Sincronizar automáticamente la cola offline del juez cuando vuelve la conectividad:

- procesando `comando_queue` en orden FIFO;
- exponiendo estado de sincronización en la UI;
- rehidratando la grilla desde servidor al vaciar la cola.

## Alcance técnico confirmado

- `frontend/src/hooks/useSyncQueue.ts`.
- `frontend/src/stores/useConnectionStore.ts`.
- `frontend/src/components/juez/JuezLayout.tsx`.
- `frontend/src/components/juez/SyncStatusBadge.tsx`.
- `frontend/src/sw.ts`.
- `frontend/vite.config.ts`.

## Arquitectura y calidad verificadas

- Contexto obligatorio leído: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- ADRs base presentes: `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`, `docs/adr/ADR-006-estructura-bc-first.md`.
- Documentación base presente: `docs/design/architecture.md`, `docs/design/domain-model.md`.
- Configuración de quality gates presente en `pyproject.toml`:
  - `[tool.coverage.run]`
  - `[tool.codeguard]`
  - `[tool.designreviewer]`
- Estructura de tests presente: `tests/`, `tests/conftest.py`, `tests/features/`.

## Hallazgos relevantes para la US

- El producto afectado es `frontend`, por lo que aplica el ajuste local del skill:
  implementación en `frontend/src/` y validación técnica principal con `npm run build` y `npm run lint`.
- La branch `feature/US-4.4.3-sync-reconexion` ya contiene artefactos parciales asociados a esta US:
  `tests/features/US-4.4.3-sync-reconexion.feature`, `frontend/src/hooks/useSyncQueue.ts` y `frontend/src/sw.ts`.
- Existen trackers históricos abiertos en `.claude/tracking/`; para evitar ambigüedad se está usando
  tracking explícito de `US-4.4.3`.
