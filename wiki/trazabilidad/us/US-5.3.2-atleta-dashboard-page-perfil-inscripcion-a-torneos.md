---
title: "US-5.3.2 — AtletaDashboardPage: perfil + inscripción a torneos"
type: trazabilidad-us
sp: SP5
inc: INC-5.3
bc: identidad, registro
estado: cerrada
fecha_cierre: "2026-04-23"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §23
  - docs/plans/sp5/US-5.3.2-plan.md
us_id: US-5.3.2
tests_count: null
rf: []
software_items:
  - src/identidad/application/commands/autenticar_usuario.py
test_units:
  - tests/features/US-5.3.2-vista-atleta.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/identidad/command-handlers-identidad
---

# US-5.3.2 — AtletaDashboardPage: perfil + inscripción a torneos

## Descripción

Dashboard del atleta con perfil personal (email/rol del JWT), lista de torneos en `INSCRIPCION_ABIERTA` e `InscripcionPanel` con selección de disciplinas. Esta US adelantó scope de INC-5.4 al incluir la mutación de inscripción.

## Contenido implementado

- `AtletaDashboardPage` — perfil (datos del JWT) + torneos disponibles
- `InscripcionPanel` — selección de disciplinas y `POST /registro/inscripciones`

## Estado

✅ Completado — 2026-04-23 · PR #111
