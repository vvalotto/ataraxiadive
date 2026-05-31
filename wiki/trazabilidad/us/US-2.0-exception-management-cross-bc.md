---
title: "INC-2.0 — Exception management cross-BC"
type: trazabilidad-us
sp: SP2
inc: INC-2.0
bc: competencia, shared
estado: cerrada
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
us_id: US-2.0
tests_count: null
rf: []
software_items:
  - src/competencia/api/exception_handlers.py
test_units:
  - tests/unit/competencia/api/test_exception_handlers.py
origen_tipo: adr
origen_refs:
  - ADR-012
componentes_wiki:
  - arquitectura/competencia/router-competencia
---

# INC-2.0 — Exception management cross-BC

## Descripción

Incremento transversal que establece el manejo uniforme de excepciones de dominio en toda la API. Pre-requisito para los incrementos funcionales de SP2.

## RFs cubiertos

Ninguno directamente — infraestructura transversal.

## Contenido implementado

- `domain/exceptions.py` — jerarquía de excepciones de dominio tipadas
- `exception_handlers.py` — handlers FastAPI que mapean excepciones de dominio a respuestas HTTP (ADR-013)

## Decisiones arquitectónicas aplicadas

| ADR | Aplicación |
|-----|-----------|
| [[ADR-013]] | Manejo de excepciones de dominio → HTTP responses |

## Tests

Sin suite BDD dedicada — validación integrada en tests de cada US funcional.

## Estado

✅ Completado — 2026-03-28
