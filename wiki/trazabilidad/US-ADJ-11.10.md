---
title: "US-ADJ-11.10 — Creación automática de perfiles al registrarse"
type: trazabilidad-us
sp: SP-ADJ-11
inc: SP-ADJ-11
bc: registro
estado: cerrada
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §33
us_id: US-ADJ-11.10
tests_count: null
---

# US-ADJ-11.10 — Creación automática de perfiles al registrarse

## Descripción

Al completar el registro, el sistema crea automáticamente los perfiles de BC Registro (Atleta, y Juez u Organizador según los roles seleccionados). Elimina el paso manual de creación de perfil post-registro.

## Contenido implementado

- Creación automática de `Atleta` en BC Registro al registrarse con rol ATLETA
- Creación automática de `Juez` / `Organizador` según roles seleccionados en [[US-ADJ-11.6]]

## Estado

✅ Completado · PR #190
