---
title: "US-ADJ-6.1 — Renombrar FAZ→FAAS en código"
type: trazabilidad-us
sp: SP-ADJ-06
inc: SP-ADJ-06
bc: competencia, notificaciones, shared
estado: cerrada
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §18
us_id: US-ADJ-6.1
tests_count: null
rf: []
software_items:
  - src/competencia/domain/aggregates/competencia.py
test_units: null
origen_tipo: calidad
---

# US-ADJ-6.1 — Renombrar FAZ→FAAS en código

## Descripción

Corrige el acrónimo de la federación en todo el código: de "FAZ" (nombre anterior) a "FAAS" (Federación Argentina de Apnea Subacuática — nombre oficial actual).

## Capas afectadas

`shared/`, `notificaciones/`, `competencia/`

## Contenido corregido

- Enum `Disciplina`: variantes renombradas (ej: `FAZ_DNF` → `FAAS_DNF` si aplicaba)
- Eventos de dominio, handlers, ports — referencias al acrónimo
- Strings en mensajes y templates de notificaciones

## Tests

✅ 2026-04-18
