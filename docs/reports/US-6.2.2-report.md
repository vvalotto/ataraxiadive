# Reporte de Implementación — US-6.2.2

**US:** US-6.2.2 — Inscriptos + Grilla: categoría legible + AP como Anuncio  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.2-inscriptos-grilla-anuncios`  
**Estado:** Completado  
**Fecha:** 2026-05-05  

---

## Resumen

Se implementaron los ajustes UI-ORG-03 y UI-ORG-04. En la tabla de inscriptos, las categorías estándar dejan de exponerse como claves técnicas y las columnas de disciplina explicitan que el valor corresponde al anuncio. En la tabla de grilla, la columna `AP` fue renombrada a `Anuncio` sin cambiar el dato renderizado.

La US es frontend puro. Por instrucción operativa, se omitieron las fases BDD y se validó con build/lint de frontend.

---

## Componentes Implementados

- `frontend/src/components/organizador/TablaInscriptos.tsx`
  - Se agregó `CATEGORIA_LABELS`.
  - Se agregó `formatCategoria(categoria)` con fallback al valor raw.
  - La columna `Categoria` muestra etiquetas legibles para Junior, Senior y Master por género.
  - Los headers dinámicos de disciplina muestran `Anuncio · {disciplina}`.
- `frontend/src/components/organizador/TablaGrilla.tsx`
  - El header `AP` fue reemplazado por `Anuncio`.
  - No se modificó el valor ni el formateo de la marca anunciada.

---

## Documentación Actualizada

- `docs/specs/sp6/US-6.2.2.md`
  - Estado actualizado a `Done`.
  - Agregada sección `Fuente de verdad UX`, requerida por `WORKFLOW-DESARROLLO.md` para US frontend.
- `docs/plans/sp6/US-6.2.2-plan.md`
  - Plan de Fase 2 creado y actualizado con tareas completadas.
- `docs/reports/US-6.2.2-report.md`
  - Reporte final de implementación.
- `.claude/tracking/US-6.2.2-tracking.json`
  - Tracking de fases y tareas de la US.

---

## Validación

| Comando | Resultado | Observación |
|---|---:|---|
| `npm run build` | OK | TypeScript + Vite + PWA build pasan. |
| `./node_modules/.bin/eslint src/components/organizador/TablaInscriptos.tsx src/components/organizador/TablaGrilla.tsx` | OK | Los archivos modificados no introducen problemas de lint. |
| `npm run lint` | Falla | Bloqueado por hallazgo preexistente en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `JuecesPanel.tsx`, fuera de esta US. |

---

## Criterios de Aceptación

- [x] `SENIOR_MASCULINO` se muestra como `Senior M`.
- [x] `JUNIOR_FEMENINO` se muestra como `Junior F`.
- [x] Categorías no mapeadas mantienen fallback raw.
- [x] Headers de inscriptos muestran `Anuncio · DNF`, `Anuncio · STA`, etc.
- [x] Header de grilla muestra `Anuncio`, no `AP`.
- [x] Sin cambios en backend ni contratos API.

---

## Notas

Se usó singular `Anuncio` en headers porque cada columna/celda representa un único anuncio por disciplina, aunque algunos hallazgos estén redactados en plural.

