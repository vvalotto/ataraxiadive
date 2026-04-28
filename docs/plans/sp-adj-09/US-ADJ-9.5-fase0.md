# US-ADJ-9.5 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Sprint:** `SP-ADJ-09`
**Spec canonica:** `docs/specs/sp-adj-09/US-ADJ-9.5.md`

---

## Historia

**US:** US-ADJ-9.5 - Reencuadrar Resultados dentro del shell aprobado - S-04

Como **organizador**, quiero que la pantalla de resultados respete el shell y el
layout aprobados para leer la disciplina activa y el overall del torneo dentro de
una experiencia coherente con el panel.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp-adj-09/US-ADJ-9.5.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md`
- `docs/specs/sp5/US-5.6.5.md`
- `docs/specs/sp5/US-5.6.6.md`
- `frontend/src/pages/organizador/ResultadosPage.tsx`
- `frontend/src/components/organizador/OrganizadorLayout.tsx`

---

## Contexto Relevante

### Estado actual de `Resultados`

- la ruta primaria `/organizador/resultados` ya existe en el shell del organizador
- `ResultadosPage.tsx` ya implementa la logica funcional de:
  - selector de torneo
  - selector de disciplina
  - tabla por disciplina
  - podios por categoria
  - overall condicionado por disciplinas cerradas

- la capa de datos parece correcta y ya reutiliza queries existentes de:
  - competencias
  - estado de competencia
  - grilla
  - ranking por disciplina
  - overall
  - inscriptos detalle

### Gap UX respecto de `S-04`

- el wireframe `S-04` define:
  - header con boton `Publicar resultados`
  - subtitulo con disciplina activa + estado del ranking + progreso
  - layout de dos columnas
  - ranking de disciplina como bloque principal
  - overall con empty state claro y jerarquia visual consistente

- la implementacion actual todavia diverge en:
  - cards claras/blancas dentro del shell dark
  - selector inicial de torneo con lenguaje visual heredado
  - jerarquia visual entre tabla, podios y overall
  - header/subtitulo poco alineados al contrato `S-04`
  - composicion mas cercana a una pagina agregada por capas que a una pantalla primaria del shell

### Relacion con US previas

- `US-ADJ-9.1` y `US-ADJ-9.2` ya estabilizaron shell y routing primario
- `US-ADJ-9.4` ya separo el `Panel` operativo del home de torneos
- esta US no debe rehacer dominio ni endpoints:
  - debe reencuadrar `ResultadosPage`
  - debe preservar las capacidades ya entregadas por `US-5.6.5` y `US-5.6.6`

---

## Validacion Arquitectonica

### Artefactos de arquitectura

- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`: esperado como base del proyecto
- `docs/adr/ADR-006-estructura-bc-first.md`: esperado como base del proyecto
- `docs/design/architecture.md`: esperado como base del proyecto
- `docs/design/domain-model.md`: esperado como base del proyecto

### Adaptacion al producto frontend

- la guia base de `/implement-us` asume verificacion sobre `src/{bc}/`
- esta US pertenece a `frontend`, por lo que la raiz real de trabajo es:
  - `frontend/src/pages/organizador/`
  - `frontend/src/components/organizador/`
  - `frontend/src/api/resultados.ts`

- no se esperan cambios en backend ni dominio para esta US

---

## Quality Gates Esperables

- `frontend/package.json` expone:
  - `npm run build`
  - `npm run lint`

- para esta US de frontend, los gates operativos siguen siendo:
  - build de Vite/TypeScript
  - lint de frontend
  - validacion visual/manual del layout `S-04`

---

## Gaps Detectados

1. `ResultadosPage` conserva capacidades funcionales correctas pero no la composicion UX aprobada.
2. El layout no expresa con claridad la relacion principal entre ranking de disciplina y overall.
3. El selector de torneo inicial y varias superficies siguen usando visuales claras dentro del shell dark.
4. El header y subtitulo no reflejan todavia el contrato narrativo de `S-04`.

---

## Riesgos Detectados

- una refactorizacion demasiado visual puede romper el join actual entre grilla, ranking e inscriptos
- si se fuerza el layout exacto del prototipo sin adaptar la tabla real, puede degradarse legibilidad
- si se mezclan cambios de dominio con cambios visuales, la US perderia foco y creceria innecesariamente

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. refactor visual/compositivo de `ResultadosPage` preservando la funcionalidad existente
