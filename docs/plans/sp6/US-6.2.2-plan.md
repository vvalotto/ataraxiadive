# Plan de Implementación — US-6.2.2

**US:** US-6.2.2 — Inscriptos + Grilla: categoría legible + AP como Anuncio  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.2-inscriptos-grilla-anuncios`  
**Estimación:** 35 min  
**Estado:** Completado  
**Fecha implementación:** 2026-05-05  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.2.md`
- Hallazgos fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-03, UI-ORG-04
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
  - `docs/design/ux/README.md`
- Componentes afectados:
  - `frontend/src/components/organizador/TablaInscriptos.tsx`
  - `frontend/src/components/organizador/TablaGrilla.tsx`

La US es frontend puro. Por instrucción operativa del usuario, se omiten Fase 1 y Fase 6 de BDD. La validación se hará con build/lint de frontend y revisión manual del comportamiento.

---

## Hallazgos de Fase 0

- `TablaInscriptos` muestra `row.categoria` sin formateo.
- `TablaInscriptos` usa el código de disciplina como header de columna, sin indicar que representa el anuncio/AP.
- `TablaGrilla` muestra el header `AP`.
- La spec `US-6.2.2` no incluye el campo obligatorio `## Fuente de verdad UX` definido por `WORKFLOW-DESARROLLO.md` para US que tocan `frontend/`.

---

## Tareas

### 1. Implementación UI — TablaInscriptos (15 min)

- [x] Agregar mapeo local `CATEGORIA_LABELS`.
- [x] Agregar helper `formatCategoria(categoria)`.
- [x] Renderizar categoría como `Senior M`, `Senior F`, `Master M`, `Master F`, `Junior M`, `Junior F`.
- [x] Mantener fallback al valor raw para categorías no mapeadas.
- [x] Cambiar headers dinámicos de disciplina a `Anuncio · {disciplina}`.

### 2. Implementación UI — TablaGrilla (5 min)

- [x] Cambiar header `AP` por `Anuncio`.
- [x] No modificar el dato mostrado ni el formato de marca.

### 3. Ajuste documental mínimo de la spec (5 min)

- [x] Agregar `## Fuente de verdad UX` a `docs/specs/sp6/US-6.2.2.md`.
- [x] Referenciar wireframes, prototipo, PLAN-SP6 y componentes React comparados.

### 4. Validación frontend (10 min)

- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar ESLint focalizado sobre los archivos modificados.
- [x] Ejecutar `cd frontend && npm run lint` para registrar estado global.
- [x] Verificar que no se tocaron archivos de backend.

### 5. Cierre de US (5 min)

- [x] Actualizar estado de `US-6.2.2` de `Pending` a `Done` si la validación pasa.
- [x] Generar `docs/reports/US-6.2.2-report.md`.
- [x] Cerrar tracker de `US-6.2.2`.
- [ ] Commit atómico con referencia `[US-6.2.2]`.

---

## Validación Esperada

- La columna `Categoria` no expone claves técnicas para las seis categorías estándar.
- Categorías no reconocidas mantienen fallback raw.
- Los headers de anuncio en inscriptos dicen `Anuncio · DNF`, `Anuncio · STA`, etc.
- La columna de grilla dice `Anuncio`, no `AP`.
- Sin cambios en backend ni contratos API.

---

## Riesgos

- El término de la spec alterna singular/plural entre `Anuncio` y `Anuncios`. Para mantener consistencia con la tarea detallada, se usará singular en headers de columna (`Anuncio` y `Anuncio · DNF`), porque cada celda contiene un anuncio por disciplina.

---

## Resultado de Validación

- `npm run build`: OK.
- `./node_modules/.bin/eslint src/components/organizador/TablaInscriptos.tsx src/components/organizador/TablaGrilla.tsx`: OK.
- `npm run lint`: falla por hallazgo preexistente fuera de alcance en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `frontend/src/components/organizador/JuecesPanel.tsx`.

---

## Lecciones Aprendidas

- El mapeo de categorías se mantuvo local porque esta US es la única que lo requiere por ahora; se puede extraer a `frontend/src/utils/formatters.ts` cuando otra pantalla lo consuma.
- Para lenguaje de columna conviene usar singular cuando el dato por fila representa un único valor, aunque el hallazgo esté redactado en plural.
