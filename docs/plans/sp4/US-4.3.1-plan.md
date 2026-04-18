# Plan de Implementación: US-4.3.1 — Mis disciplinas asignadas

**Patrón:** Frontend React (Vite + TypeScript + Zustand + TanStack Query)
**Producto:** frontend
**Estimación Total:** 2h 10min
**BDD:** validación manual UI sobre escenarios de `tests/features/US-4.3.1-mis-disciplinas.feature`

> **Ajuste al código real del repo:** la spec menciona `GET /torneo` y
> `GET /competencia?disciplina=X`, pero la API existente expone `GET /torneos`,
> `GET /torneos/{torneo_id}/jueces/{juez_id}/disciplinas` y
> `GET /competencia?torneo_id={torneo_id}`. La implementación debe consumir
> esos contratos reales sin abrir cambios backend en esta US.

---

## Componentes a Implementar

### 1. Tipos y API clients frontend (20 min)

- [ ] `frontend/src/api/torneo.ts` (10 min)
  - `fetchTorneos()`
  - `fetchDisciplinasDeJuez(torneoId, juezId)`
  - DTO mínimo para `TorneoResponse`
- [ ] `frontend/src/api/competencia.ts` (10 min)
  - `fetchCompetenciasPorTorneo(torneoId)`
  - helper para resolver `competencia_id + disciplina`

### 2. Store de contexto de competencia (15 min)

- [ ] `frontend/src/stores/useCompetenciaStore.ts` (15 min)
  - estado `{ torneoId, competenciaId, disciplinaActiva }`
  - acción `seleccionarCompetencia(...)`
  - sin persistencia

### 3. UI juez — layout y componentes base (30 min)

- [ ] `frontend/src/components/juez/JuezLayout.tsx` (10 min)
  - tema dark según `wireframes-juez.md`
  - header/base shell reutilizable para páginas del juez
- [ ] `frontend/src/components/juez/DisciplinaCard.tsx` (10 min)
  - variantes `ACTIVA` / `PENDIENTE`
  - card tappable solo si está activa
- [ ] `frontend/src/pages/juez/GrillaPage.tsx` (10 min)
  - stub para `/juez/grilla`
  - muestra disciplina activa y botón de regreso

### 4. Página Mis Disciplinas (35 min)

- [ ] `frontend/src/pages/juez/DisciplinasPage.tsx` (35 min)
  - leer `email` desde `useAuthStore`
  - resolver torneo activo desde `GET /torneos`
  - resolver disciplinas asignadas del juez
  - resolver competencias del torneo y mapear estado por disciplina
  - mostrar estados vacíos:
    - "No hay torneo en curso"
    - "Sin disciplinas asignadas"
  - seleccionar competencia activa y navegar a `/juez/grilla`

### 5. Routing e integración (10 min)

- [ ] `frontend/src/App.tsx` (10 min)
  - mantener `/juez/disciplinas`
  - agregar ruta protegida `/juez/grilla`

### 6. Validación técnica (20 min)

- [ ] `frontend`: `npm run build` (10 min)
- [ ] `frontend`: `npm run lint` si el cambio introduce reglas nuevas relevantes (10 min)

### 7. Validación manual UI (20 min)

- [ ] verificar escenario con disciplina activa y pendiente
- [ ] verificar mensaje sin torneo activo
- [ ] verificar mensaje sin disciplinas asignadas
- [ ] verificar navegación a `/juez/grilla` y store actualizado

---

## Decisiones de implementación

1. **No abrir backend en esta US.**
   Se consume la API ya disponible en `src/torneo/api/router.py` y
   `src/competencia/api/router.py`.

2. **Resolver competencias en frontend por join en memoria.**
   Flujo:
   - cargar torneo activo desde `GET /torneos`;
   - cargar disciplinas del juez;
   - cargar competencias del torneo;
   - unir por `disciplina`.

3. **`juez_id` se infiere desde el JWT por email.**
   Si durante implementación se confirma que el frontend no dispone del `user_id`,
   se evaluará una de estas dos salidas:
   - usar un endpoint/claim ya existente que exponga `user_id`;
   - o detener la implementación y pedir decisión, porque la US depende de ese dato.

4. **BDD manual en esta US.**
   El repo no tiene harness browser automatizado para React; la evidencia funcional
   será manual y el `.feature` opera como contrato de aceptación.

---

## Riesgos concretos

- El JWT actual del frontend guarda `email` y `rol`, pero no `user_id`.
- La spec de `US-4.3.1` asume contratos backend más cómodos que los reales.
- Si el listado de torneos devuelve más de uno en `EnEjecucion`, habrá que definir
  criterio de selección en frontend.

---

## Estado

**Estado:** 11/11 tareas completadas a nivel codigo y validacion tecnica

*Plan generado: 2026-04-11 — US-4.3.1 INC-4.3 SP4*
