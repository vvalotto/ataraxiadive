---
title: "US-6.3.1 — Inicio atleta: indicador En línea + disciplinas por OT"
type: trazabilidad-us
sp: SP6
inc: INC-6.3
bc: frontend
estado: completado
fecha_cierre: "2026-05-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §31
---

# US-6.3.1 — Inicio atleta: indicador En línea + disciplinas por OT

## Descripción

Mejoras en la pantalla de inicio del portal del atleta: indicador "En línea" para estado de conectividad, eliminación del saludo redundante "Hola" y disciplinas de torneos activos ordenadas por orden de turno (OT).

## Contenido implementado

- `AtletaShell.tsx` — indicador de conectividad "En línea"
- `AtletaHomePage.tsx` — sin saludo "Hola"; disciplinas activas ordenadas por OT

DesignReviewer INC-6.3: **0 CRITICAL · 258 WARNING** · CodeGuard: 0 errores.

## Estado

✅ Completado — 2026-05-08 · PR #154
