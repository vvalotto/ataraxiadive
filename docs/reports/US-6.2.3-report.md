# Reporte de Implementación — US-6.2.3

**US:** US-6.2.3 — Resultados: quitar PTS FAAS + andarivel numérico + AP como Anuncio  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.3-resultados-anuncio-andarivel`  
**Estado:** Completado  
**Fecha:** 2026-05-05  

---

## Resumen

Se implementó el ajuste UI-ORG-05 para la tabla de resultados del organizador. La vista ya no muestra puntuación FAAS en la tabla de ejecución, el andarivel se presenta como número literal y la columna de marca anunciada usa lenguaje operativo (`Anuncio`) en lugar de la sigla interna `AP`.

La US es frontend puro. Por instrucción operativa, se omitieron las fases BDD y se validó con build/lint de frontend.

---

## Componentes Implementados

- `frontend/src/components/organizador/TablaDisciplinaResultados.tsx`
  - `formatearLinea` fue reemplazado por `formatearAndarivel`.
  - El andarivel se muestra como número literal.
  - Andarivel `null`, `undefined` o `0` se muestra como `—`.
  - Header `AP` reemplazado por `Anuncio`.
  - Header `Pts FAAS` eliminado.
- `frontend/src/components/organizador/FilaResultado.tsx`
  - Celda de puntos FAAS eliminada.
  - Columnas restantes mantienen alineación con el header.
- `frontend/src/pages/organizador/ResultadosPage.tsx`
  - Copy visible actualizado para no mencionar `AP` ni `puntos FAAS`.

---

## Documentación Actualizada

- `docs/specs/sp6/US-6.2.3.md`
  - Estado actualizado a `Done`.
  - Agregada sección `Fuente de verdad UX`, requerida por `WORKFLOW-DESARROLLO.md` para US frontend.
- `docs/plans/sp6/US-6.2.3-plan.md`
  - Plan de Fase 2 creado y actualizado con tareas completadas.
- `docs/reports/US-6.2.3-report.md`
  - Reporte final de implementación.
- `.claude/tracking/US-6.2.3-tracking.json`
  - Tracking de fases y tareas de la US.

---

## Validación

| Comando | Resultado | Observación |
|---|---:|---|
| `npm run build` | OK | TypeScript + Vite + PWA build pasan. |
| `./node_modules/.bin/eslint src/components/organizador/TablaDisciplinaResultados.tsx src/components/organizador/FilaResultado.tsx src/pages/organizador/ResultadosPage.tsx` | OK | Los archivos modificados no introducen problemas de lint. |
| `npm run lint` | Falla | Bloqueado por hallazgo preexistente en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `JuecesPanel.tsx`, fuera de esta US. |

---

## Criterios de Aceptación

- [x] No existe columna visible `Pts FAAS` en la tabla de resultados.
- [x] Andarivel `1` se muestra como `1`, no `A`.
- [x] Andarivel faltante o `0` se muestra como `—`.
- [x] Header de marca anunciada muestra `Anuncio`.
- [x] Copy visible no menciona puntos FAAS.
- [x] Sin cambios en backend ni contratos API.

---

## Notas

El dato de puntos/ranking puede seguir existiendo en DTOs o queries, pero dejó de formar parte de la tabla de ejecución del organizador según el alcance de la US.

