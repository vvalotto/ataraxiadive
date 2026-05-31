---
title: "US-4.3.4 — Estado EnRevision + ResolverRevision + UI tarjeta amarilla"
type: trazabilidad-us
sp: SP4
inc: INC-4.3
bc: competencia, frontend
estado: cerrada
fecha_cierre: "2026-04-12"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §14
us_id: US-4.3.4
tests_count: null
rf: []
software_items:
  - src/competencia/application/commands/resolver_revision.py
  - src/competencia/domain/value_objects/tipo_tarjeta.py
test_units:
  - tests/features/US-4.3.4-tarjeta-amarilla.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/competencia/command-handlers
  - arquitectura/competencia/competencia-aggregate
---

# US-4.3.4 — Estado EnRevision + ResolverRevision + UI tarjeta amarilla

## Descripción

Introduce el estado intermedio `EnRevision` para performances bajo impugnación y el flujo UI correspondiente, incluyendo la tarjeta amarilla (período de revisión).

## Wireframes cubiertos

wireframes-juez S-10, S-15

## Contenido implementado

**Backend:**
- Nuevo estado `EnRevision` en `Performance`
- `ResolverRevisionCommand` + `ResolverRevisionHandler`
- Evento `RevisionResuelta`
- `POST /competencia/{id}/resolver-revision`
- BUG-01: `es_disciplina_tiempo` condiciona `INV-DQ-01` en `TarjetaAsignacion` (STA no aplica regla de distancia mínima)

**Frontend:**
- `ResultadoAmarilla` (S-10) — pantalla de resultado con tarjeta amarilla + timer informativo 3 min
- `RevisionDesdeGrilla` (S-15) — acceso a revisión desde la grilla
- `AlertaRevision` — badge de alerta en grilla para performances en revisión

## Tests

unit/competencia/domain (`EnRevision` + `ResolverRevision`) · integration/competencia · frontend build+lint. UAT INC-4.3 — 2026-04-12.

## Estado

✅ Completado — 2026-04-12
