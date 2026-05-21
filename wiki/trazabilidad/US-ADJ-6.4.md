---
title: "US-ADJ-6.4 — Eliminar duplicación P-10/P-11 y @staticmethod innecesario"
type: trazabilidad-us
sp: SP-ADJ-06
inc: SP-ADJ-06
bc: notificaciones
estado: completado
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §18
---

# US-ADJ-6.4 — Eliminar duplicación P-10/P-11 y @staticmethod innecesario

## Descripción

Refactoring DRY en la capa de application del BC Notificaciones: elimina la duplicación entre los handlers de P-10 y P-11 y quita el decorador `@staticmethod` innecesario.

## Capas afectadas

`notificaciones/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| DRY | Lógica común de P-10 y P-11 extraída a método base compartido |
| — | `@staticmethod` eliminado donde no correspondía (rompía DI) |

## Estado

✅ Completado — 2026-04-18
