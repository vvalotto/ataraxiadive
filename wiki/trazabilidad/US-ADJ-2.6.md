---
title: "US-ADJ-2.6 — Refactoring cross-BC: VOs y EventStore a shared/"
type: trazabilidad-us
sp: SP-ADJ-02
inc: SP-ADJ-02-code
bc: shared, competencia, resultados
estado: completado
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §8
---

# US-ADJ-2.6 — Refactoring cross-BC: VOs y EventStore a shared/

## Descripción

Consolida value objects de dominio compartido y la infraestructura de Event Store en el módulo `shared/`, eliminando duplicación cross-BC.

## Capas afectadas

`shared/domain/`, `shared/infrastructure/`, `resultados/`, `competencia/domain/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| B-01 | `Disciplina` → `shared/domain/value_objects/` |
| B-02 | `DisciplinaDescriptor` → `shared/domain/value_objects/` |
| B-04 | `UnidadMedida` → `shared/domain/value_objects/` |
| B-04 | `EventStorePort` → `shared/` |
| B-04 | `SQLiteEventStore` → `shared/infrastructure/` |
| — | `DisciplinaDescriptorAdapter` creado en `resultados/infrastructure/` (ACL) |

## Motivación

Los value objects compartidos vivían en `competencia/`, obligando a `resultados/` a importar de otro BC — violación de la regla de dependencias del Context Map.

## Tests

BDD waiver — refactoring arquitectónico cross-BC.

## Estado

✅ Completado — 2026-03-28
