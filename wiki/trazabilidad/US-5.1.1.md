---
title: "US-5.1.1 — CrearTorneoPage: formulario de creación para el organizador"
type: trazabilidad-us
sp: SP5
inc: INC-5.1
bc: torneo, identidad
estado: completado
fecha_cierre: "2026-04-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §19
  - docs/plans/sp5/US-5.1.1-plan.md
---

# US-5.1.1 — CrearTorneoPage: formulario de creación para el organizador

## Descripción

Primera página del panel organizador: formulario que permite al organizador autenticado crear un nuevo torneo vía `POST /torneos`. Integra `useAuthStore` para verificar el rol antes de habilitar el formulario.

## Contenido implementado

- `CrearTorneoPage` — formulario con campos del torneo + validación frontend
- `POST /torneos` — endpoint de creación
- `useAuthStore` — guarda de rol organizador en la ruta

## Tests

| Suite | Resultado |
|-------|-----------|
| UAT INC-5.1 | ✅ |

DesignReviewer consolidado INC-5.1: **0 CRITICAL · 208 WARNING**.

## Estado

✅ Completado — 2026-04-21 · PR #95
