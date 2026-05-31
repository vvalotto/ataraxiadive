---
title: "US-ADJ-9.7 — SP-ADJ-09: declarar AP en el wizard de inscripción"
type: trazabilidad-us
sp: SP-ADJ-09
inc: SP-ADJ-09
bc: registro, competencia
estado: cerrada
fecha_cierre: "2026-04-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §27
  - docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md
us_id: US-ADJ-9.7
tests_count: null
rf: []
software_items:
  - src/registro/application/commands/declarar_ap_inscripcion.py
test_units:
  - tests/features/US-ADJ-9.7-ap-inscripcion-preparacion.feature
origen_tipo: plataforma
---

# US-ADJ-9.7 — SP-ADJ-09: declarar AP en el wizard de inscripción

## Descripción

Integra la declaración de anuncio previo (AP) directamente en el wizard de inscripción del atleta. El atleta puede declarar su AP por disciplina desde el mismo flujo de inscripción, sin necesidad de volver a la pantalla de AP separada.

## Contenido implementado

- Paso de AP en el wizard de inscripción ([[US-5.5.1-portal-atleta-completo-shell-inscripcion-ap]])
- BC Registro + BC Competencia: AP declarada al momento de inscribir

## Estado

✅ Completado — 2026-04-28 · PR #136
