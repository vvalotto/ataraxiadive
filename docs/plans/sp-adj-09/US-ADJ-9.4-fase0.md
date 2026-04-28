# US-ADJ-9.4 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Sprint:** `SP-ADJ-09`
**Spec canonica:** `docs/specs/sp-adj-09/US-ADJ-9.4.md`

---

## Historia

**US:** US-ADJ-9.4 - Dashboard operativo del organizador alineado a S-01

Como **organizador**, quiero un dashboard operativo del torneo activo con KPIs,
disciplina en ejecucion, alertas y proximos atletas para supervisar la operacion
en vivo desde un unico lugar.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp-adj-09/US-ADJ-9.4.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`
- `frontend/src/App.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `frontend/src/components/organizador/OrganizadorLayout.tsx`

---

## Contexto Relevante

### Estado actual del Panel

- la shell del organizador ya existe desde `US-ADJ-9.1` y `US-ADJ-9.2`
- la ruta primaria `Panel` ya esta montada en `/organizador/panel`
- hoy esa ruta renderiza `DetalleTorneoPage`, no un dashboard ejecutivo dedicado
- cuando no hay `torneo_id`, la vista muestra un selector de torneo
- cuando hay torneo, el contenido principal sigue centrado en:
  - detalle del torneo
  - tabs locales `Detalle / Inscriptos / Ejecucion`
  - acciones de fase

### Gap funcional respecto de la spec `S-01`

- el wireframe `S-01` define un dashboard operativo con:
  - KPI strip de 4 metricas
  - disciplina activa destacada
  - alertas activas o empty state
  - tabla de proximos atletas
  - otras disciplinas en modo informativo

- la implementacion actual del `Panel` no presenta esa jerarquia:
  - no hay KPI strip operativo
  - no hay seccion de alertas activas
  - no hay lista compacta de proximos atletas
  - la navegacion local por tabs mezcla detalle de torneo con panel operativo

### Separacion conceptual ya confirmada

- `US-ADJ-9.3` formalizo `/organizador/torneo` como home de torneos vigentes e historico
- por lo tanto, `US-ADJ-9.4` no debe reutilizar esa pagina como dashboard
- la pantalla `Panel` tiene que representar el torneo operativo activo, no el catalogo

### Datos y composicion esperable

- la pagina debera resolver un `torneo_id` operativo desde query param o seleccion
- ya existen piezas reutilizables del dominio frontend para consultar:
  - torneos
  - competencias por torneo
  - estado de competencia
  - grilla de competencia
- probablemente haga falta componer nuevos view models UI para:
  - KPIs operativos
  - alertas visibles
  - proximos atletas
  - resumen de disciplinas no activas

---

## Validacion Arquitectonica

### Artefactos de arquitectura

- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`: encontrado
- `docs/adr/ADR-006-estructura-bc-first.md`: encontrado
- `docs/design/architecture.md`: encontrado
- `docs/design/domain-model.md`: encontrado

### Adaptacion al producto frontend

- la guia base de `/implement-us` asume verificacion sobre `src/{bc}/`
- esta US pertenece al producto `frontend`, por lo que la raiz real de trabajo es:
  - `frontend/src/pages/organizador/`
  - `frontend/src/components/organizador/`
  - `frontend/src/api/`
- la arquitectura hexagonal del backend sigue siendo contexto valido, pero la
  implementacion de esta US no modifica BCs de `src/`

---

## Quality Gates Esperables

- `frontend/package.json` expone:
  - `npm run build`
  - `npm run lint`
- `pyproject.toml` mantiene configurados `codeguard` y `designreviewer` para `src/`
- para esta US de frontend, los gates operativos del skill quedan ajustados a:
  - build de Vite/TypeScript
  - lint de frontend
  - validacion manual/BDD documental de la UI

---

## Gaps Detectados

1. `Panel` sigue renderizando una vista de detalle de torneo, no el dashboard `S-01`.
2. El contenido principal mezcla supervision operativa con tabs locales de detalle.
3. No existe todavia una composicion UI para KPIs, alertas y proximos atletas.
4. La seleccion del torneo operativo existe, pero no esta expresada como contexto
   del dashboard ejecutivo.

---

## Riesgos Detectados

- si la US se implementa encima de `DetalleTorneoPage` sin separar responsabilidades,
  la ruta `Panel` seguira acumulando deuda conceptual
- si no se define claramente la disciplina activa, los KPIs y proximos pueden quedar
  inconsistentes con la competencia realmente en ejecucion
- si se intenta resolver alertas reales sin soporte de backend dedicado, convendra
  modelar un fallback UI consistente en esta fase

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. definicion de la estrategia concreta para separar `Panel` de `DetalleTorneoPage`
