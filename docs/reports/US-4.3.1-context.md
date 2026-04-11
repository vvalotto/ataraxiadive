# Contexto Validado — US-4.3.1

| Campo | Valor |
|-------|-------|
| **US** | `US-4.3.1` — Pantalla de selección de competencia — mis disciplinas asignadas |
| **Producto** | `frontend` |
| **Sprint** | SP4 |
| **Incremento** | INC-4.3 |
| **Puntos** | 3 (default operativo para tracking) |
| **Fecha** | 2026-04-11 |

---

## Resultado de Fase 0

La US está lista para avanzar a BDD y planificación.

### Arquitectura y stack verificados

- Arquitectura general del proyecto validada en `docs/contexto/ATARAXIADIVE-CONTEXT.md`
  y `CLAUDE.md`.
- Frontend existente en `frontend/src/` con stack Vite + React + TypeScript + Zustand
  + TanStack Query.
- Routing y auth base ya implementados en `frontend/src/App.tsx` y
  `frontend/src/stores/useAuthStore.ts`.
- Artefactos UX de referencia disponibles:
  - `docs/design/ux/wireframes-juez.md`
  - `docs/design/ux/decisiones-frontend.md`

### Endpoints backend relevantes confirmados

- `GET /torneos`
- `GET /torneos/{torneo_id}`
- `GET /torneos/{torneo_id}/jueces/{juez_id}/disciplinas`
- `GET /competencia`
- `GET /competencia/{competencia_id}/grilla`

### Hallazgo relevante para implementación

La spec de `US-4.3.1` describe el flujo con `GET /torneo`, pero el backend real
actual expone rutas bajo `/torneos` (plural). El plan y la implementación deben
alinearse con la API existente para no introducir adapters ficticios en frontend.

### Quality gates aplicables para esta US frontend

- `frontend`: `npm run build`
- `frontend`: `npm run lint` si el cambio impacta reglas de ESLint
- Validación BDD/UI: manual, salvo que durante la implementación se agregue harness
  automatizado específico

---

## Conclusión

`US-4.3.1` puede continuar con:

1. generación del feature BDD,
2. plan de implementación frontend,
3. aprobación de Fase 2,
4. implementación.
