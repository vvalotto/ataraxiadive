---
title: "US-ADJ-11.6 — RegistroPage: checkboxes multi-rol + secciones Juez/Organizador"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: frontend, identidad
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.6
tests_count: null
---

# US-ADJ-11.6 — RegistroPage: checkboxes multi-rol + secciones Juez/Organizador

## Descripción

Actualiza el formulario de registro público para soportar selección de múltiples roles. Muestra secciones adicionales de datos (Juez u Organizador) cuando se selecciona el rol correspondiente.

## Contenido implementado

- `RegistroPage` — checkboxes de roles (ATLETA por defecto + JUEZ + ORGANIZADOR)
- Secciones condicionales de datos por rol seleccionado
- `CrearUsuarioRequest.roles[]` — payload multi-rol

## Estado

✅ Completado · PR #189
