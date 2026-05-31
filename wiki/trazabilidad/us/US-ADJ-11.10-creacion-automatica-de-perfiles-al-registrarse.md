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
rf: []
software_items:
  - src/registro/application/commands/registrar_atleta.py
test_units:
  - tests/features/US-ADJ-11.10-perfiles-registro.feature
origen_tipo: adr
origen_refs:
  - ADR-020
componentes_wiki:
  - arquitectura/registro/command-handlers
---

# US-ADJ-11.10 — Creación automática de perfiles al registrarse

## Descripción

Al completar el registro, el sistema crea automáticamente los perfiles de BC Registro (Atleta, y Juez u Organizador según los roles seleccionados). Elimina el paso manual de creación de perfil post-registro.

## Contenido implementado

- Creación automática de `Atleta` en BC Registro al registrarse con rol ATLETA
- Creación automática de `Juez` / `Organizador` según roles seleccionados en [[US-ADJ-11.6-registropage-checkboxes-multi-rol-secciones-juez]]

## Estado

✅ Completado · PR #190
