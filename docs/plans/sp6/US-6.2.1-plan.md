# Plan de Implementación — US-6.2.1

**US:** US-6.2.1 — Inicio Organizador: ordenar torneos por fecha + mostrar fecha  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.1-torneos-fecha`  
**Estimación:** 35 min  
**Estado:** Completado  
**Fecha implementación:** 2026-05-05  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.1.md`
- Hallazgo fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-01
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
  - `docs/design/ux/README.md`
- Componente afectado: `frontend/src/pages/organizador/DashboardPage.tsx`
- DTO validado: `frontend/src/api/torneo.ts` — `TorneoDto.fecha_inicio`, `TorneoDto.fecha_fin`

La US es frontend puro. Por instrucción operativa del usuario, se omiten Fase 1 y Fase 6 de BDD para esta US. La validación se hará con build/lint de frontend y revisión manual del comportamiento.

---

## Hallazgos de Fase 0

- `filtrarTorneos` filtra por estado pero conserva el orden recibido desde backend.
- La tarjeta muestra nombre, sede, ciudad y estado, pero no `fecha_inicio`/`fecha_fin`.
- `TorneoDto` ya expone `fecha_inicio` y `fecha_fin`; no se requieren cambios de API/backend.
- La spec `US-6.2.1` no incluye el campo obligatorio `## Fuente de verdad UX` definido por `WORKFLOW-DESARROLLO.md` para US que tocan `frontend/`.

---

## Tareas

### 1. Implementación UI — Dashboard organizador (15 min)

- [x] Actualizar `filtrarTorneos` para ordenar por `fecha_inicio` descendente dentro de cada filtro.
- [x] Mantener estabilidad relativa para torneos con la misma fecha.
- [x] Evitar mutar el array original recibido desde React Query.
- [x] Agregar helper `formatFechaTorneo(inicio, fin)` usando `T00:00:00` para evitar off-by-one por UTC.
- [x] Renderizar la fecha bajo la línea de sede/estado en cada tarjeta.

### 2. Ajuste documental mínimo de la spec (5 min)

- [x] Agregar `## Fuente de verdad UX` a `docs/specs/sp6/US-6.2.1.md`.
- [x] Referenciar `wireframes-organizador.md`, `prototipo-organizador.html`, `PLAN-SP6.md` y el componente React comparado.

### 3. Validación frontend (10 min)

- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar `cd frontend && npm run lint` si el build pasa o si el error no bloquea lint.
- [x] Verificar que no se tocaron archivos de backend.

### 4. Cierre de US (5 min)

- [x] Actualizar estado de `US-6.2.1` de `Pending` a `Done` si la validación pasa.
- [x] Generar `docs/reports/US-6.2.1-report.md`.
- [x] Cerrar tracker de `US-6.2.1`.

---

## Validación Esperada

- Torneos vigentes ordenados por `fecha_inicio` descendente.
- Torneos históricos ordenados por `fecha_inicio` descendente.
- Fecha visible como fecha simple cuando inicio y fin coinciden.
- Fecha visible como rango cuando inicio y fin difieren.
- Sin cambios en contratos API ni modelos backend.

---

## Riesgos

- `toLocaleDateString('es-AR')` puede variar levemente el punto final de abreviaturas según runtime. El criterio es formato legible, no string exacta rígida.
- La ordenación descendente documentada en la spec dice "más próximo primero", pero descendente realmente muestra fechas futuras más lejanas antes que fechas futuras próximas. Para esta US se implementa literalmente la postcondición de la spec: `fecha_inicio` descendente.

---

## Resultado de Validación

- `npm run build`: OK.
- `./node_modules/.bin/eslint src/pages/organizador/DashboardPage.tsx`: OK.
- `npm run lint`: falla por hallazgo preexistente fuera de alcance en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `JuecesPanel.tsx`.

---

## Lecciones Aprendidas

- Las US frontend necesitan registrar explícitamente `Fuente de verdad UX` en la spec; esta spec fue creada antes de completar ese campo y se corrigió durante Fase 8.
- Para cambios de presentación sin harness UI automatizado, el gate útil de US es build + lint focalizado sobre los archivos tocados, dejando documentados los bloqueos globales ajenos.
