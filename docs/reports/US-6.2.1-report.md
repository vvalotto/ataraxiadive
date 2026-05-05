# Reporte de Implementación — US-6.2.1

**US:** US-6.2.1 — Inicio Organizador: ordenar torneos por fecha + mostrar fecha  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.1-torneos-fecha`  
**Estado:** Completado  
**Fecha:** 2026-05-05  

---

## Resumen

Se implementó el ajuste UI-ORG-01 en el inicio del organizador. La lista de torneos ahora se filtra por estado y se ordena por `fecha_inicio` descendente dentro de cada filtro. Las tarjetas muestran la fecha del torneo usando `fecha_inicio` y `fecha_fin` ya disponibles en `TorneoDto`.

La US es frontend puro. Por instrucción operativa, se omitieron las fases BDD y se validó con build/lint de frontend.

---

## Componentes Implementados

- `frontend/src/pages/organizador/DashboardPage.tsx`
  - `filtrarTorneos` ahora ordena por `fecha_inicio` descendente.
  - El orden mantiene estabilidad relativa cuando dos torneos tienen la misma fecha.
  - La implementación evita mutar el array recibido desde React Query.
  - Se agregaron helpers de presentación para fechas de torneo.
  - Cada tarjeta muestra fecha simple o rango según `fecha_inicio`/`fecha_fin`.

---

## Documentación Actualizada

- `docs/specs/sp6/US-6.2.1.md`
  - Estado actualizado a `Done`.
  - Agregada sección `Fuente de verdad UX`, requerida por `WORKFLOW-DESARROLLO.md` para US frontend.
- `docs/plans/sp6/US-6.2.1-plan.md`
  - Plan de Fase 2 creado y actualizado con tareas completadas.
- `docs/reports/US-6.2.1-report.md`
  - Reporte final de implementación.
- `.claude/tracking/US-6.2.1-tracking.json`
  - Tracking de fases y tareas de la US.

---

## Validación

| Comando | Resultado | Observación |
|---|---:|---|
| `npm run build` | OK | TypeScript + Vite + PWA build pasan. |
| `./node_modules/.bin/eslint src/pages/organizador/DashboardPage.tsx` | OK | El archivo modificado no introduce problemas de lint. |
| `npm run lint` | Falla | Bloqueado por hallazgo preexistente en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `JuecesPanel.tsx`, fuera de esta US. |

---

## Criterios de Aceptación

- [x] Torneos vigentes ordenados por `fecha_inicio` descendente.
- [x] Torneos históricos ordenados por `fecha_inicio` descendente.
- [x] Fecha visible en cada tarjeta.
- [x] Rango visible cuando `fecha_inicio` y `fecha_fin` difieren.
- [x] Sin cambios en backend ni contratos API.

---

## Notas

La spec usa la frase "más próximo primero" junto con orden descendente por fecha. Se implementó literalmente la postcondición técnica documentada: `fecha_inicio` descendente.

