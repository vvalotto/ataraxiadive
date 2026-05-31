---
title: "US-ADJ-4.3 — Renombrar JUVENIL→JUNIOR en enum Categoria"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: registro, shared
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.3
tests_count: null
rf: []
software_items:
  - src/registro/domain/value_objects/categoria.py
test_units: null
origen_tipo: calidad
componentes_wiki: []
---

# US-ADJ-4.3 — Renombrar JUVENIL→JUNIOR en enum Categoria

## Descripción

Corrige la nomenclatura de la categoría juvenil para alinearse con el lenguaje ubicuo AIDA/FAAS que usa "JUNIOR" en lugar de "JUVENIL".

## RFs corregidos

Sin RF directo — corrección de lenguaje ubicuo.

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-07 | `JUVENIL` ≠ `JUNIOR` — nomenclatura AIDA | MEDIO |

## Contexto

El término "JUVENIL" es una hispanización no estándar. La federación AIDA y FAAS usan "JUNIOR" en todos sus documentos y resultados oficiales.

## Tests

Corrección propagada a fixtures y tests que usaban `Categoria.JUVENIL`.

## Estado

✅ Completado — 2026-04-03
