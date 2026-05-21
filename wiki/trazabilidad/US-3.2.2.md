---
title: "US-3.2.2 — Aggregate Atleta: registro, consulta y repositorio SQLite"
type: trazabilidad-us
sp: SP3
inc: INC-3.2
bc: registro
estado: completado
fecha_cierre: "2026-03-31"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
---

# US-3.2.2 — Aggregate Atleta: registro, consulta y repositorio SQLite

## Descripción

Introduce el BC Registro con el aggregate `Atleta`: registro de atletas, consulta y persistencia en SQLite.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-IN-01 | Categorías configurables por edad y género |
| RF-IN-02 | Brevet no obligatorio |
| RF-IN-08 | Género solo para categorización |
| RF-IN-09 | Atleta no puede cambiar categoría por disciplina |

## Contenido implementado

- Aggregate `Atleta` con campos: `nombre`, `apellido`, `email`, `genero`, `categoria`, `brevet` (opcional)
- `POST /registro/atletas`, `GET /registro/atletas/{id}`
- `SQLiteAtletaRepository`

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/registro | ✅ |
| integration/registro | ✅ |
| features/US-3.2.2 | ✅ |
| **Total** | **27 tests (100%)** |

## Estado

✅ Completado — 2026-03-31
