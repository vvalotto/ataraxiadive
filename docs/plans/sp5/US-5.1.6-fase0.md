# Fase 0 — Validacion de Contexto: US-5.1.6

**Historia de Usuario:** US-5.1.6 — Monitor de ejecucion del organizador durante la competencia
**Producto:** frontend
**Puntos:** 3
**Incremento:** INC-5.1

## Arquitectura

- Patron: frontend React/Vite consumiendo APIs existentes de `competencia`.
- Contexto obligatorio leido: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- Spec canonica encontrada: `docs/specs/sp5/US-5.1.6.md`.
- Pagina afectada: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`.
- API afectada: `frontend/src/api/competencia.ts`.
- Componentes organizador existentes: `frontend/src/components/organizador/`.

## Endpoints Verificados

- `GET /competencia?torneo_id={id}` existe, pero retorna solo `competencia_id`, `disciplina` y `torneo_id`.
- `GET /competencia/{id}/estado?disciplina={disciplina}` existe y permite conocer `estado`.
- `GET /competencia/{id}/progreso` existe y retorna `total`, `ejecutadas`, `dns_count`, `completadas`.
- `GET /competencia/{id}/performance/actual` existe y retorna `PerformanceActualDTO | null`.
- `GET /competencia/{id}/performance/proximas?disciplina={disciplina}` existe. La spec lo nombra como `/proximas`, pero el router real expone `/performance/proximas`.

## Brechas y Decisiones

- Para cumplir `INV-5.1.6-01`, la UI debe consultar estado por competencia antes de filtrar `EnEjecucion`.
- Para detectar que todas las competencias estan completas, la UI debe usar el estado de cada competencia y considerar `Finalizada` o `CompetenciaFinalizada` como final.
- El boton real de transicion a premiacion vive en `AccionesPanel`; el monitor solo mostrara el estado informativo requerido.
- No se requiere cambio backend: los datos necesarios estan disponibles mediante endpoints existentes.

## Quality Gates

- Para esta US frontend, los gates Python del skill se sustituyen por `npm run build` y `npm run lint`.
- No se esperan cambios Python.

**Estado:** contexto validado para continuar con Fase 1.
