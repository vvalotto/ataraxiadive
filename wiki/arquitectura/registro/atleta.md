---
title: "Registro — Aggregate Atleta"
type: arquitectura-componente
bc: registro
capa: domain
tipo_componente: aggregate
responsabilidad: "Perfil deportivo del atleta: identidad, categoría, club y brevet. CRUD sobre registro.db"
interfaces_out:
  - AtletaRepositoryPort
adr_refs: [ADR-005, ADR-007, ADR-020, ADR-022]
last_updated: "2026-05-23"
sources:
  - src/registro/domain/aggregates/atleta.py
---

# Aggregate Atleta

## Responsabilidad

Modela el **perfil deportivo de un participante**. Contiene los datos de identidad del atleta necesarios para inscribirse en torneos, aparecer en la grilla y los rankings. Persiste en `registro.db` vía CRUD (no Event Sourcing).

## Campos

| Campo | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `atleta_id` | ✅ | UUID — coincide con `usuario_id` de BC Identidad |
| `nombre` | ✅ | No puede ser vacío (INV-A-01) |
| `apellido` | ✅ | No puede ser vacío (INV-A-01) |
| `email` | ✅ | Formato válido (INV-A-02) |
| `fecha_nacimiento` | — | Debe ser en el pasado (INV-A-04) |
| `categoria` | — | `Categoria` StrEnum de `shared/` (ADR-022) |
| `club` | — | No vacío si presente |
| `dni` | — | No vacío si presente |
| `telefono` | — | No vacío si presente |
| `brevet` | — | Número de licencia federativa (opcional) |

## Invariantes

| Inv | Descripción |
|-----|-------------|
| INV-A-01 | nombre y apellido no pueden ser vacíos |
| INV-A-02 | email debe tener formato válido |
| INV-A-04 | fecha_nacimiento debe ser en el pasado |

## Operaciones

- `__post_init__()` — valida invariantes al construir
- `actualizar(...)` — actualiza campos opcionales con validación inline

## Nota de implementación

Es un `@dataclass` (no hereda de `AggregateRoot`). El BC Registro usa CRUD puro — no Event Sourcing. La persistencia está delegada en [[atleta-repository-port]].

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- `atleta_id` = `usuario_id` del BC [[identidad]] — vinculado al crear el perfil via [[perfil-registro-adapter]]
- Leído por BC Competencia vía [[atleta-nombre-port]] (cross-BC, lectura directa de `registro.db`)
- `categoria` es un `StrEnum` importado de `shared/` (ADR-022) — también usado por [[competencia]] y [[resultados]]
- Participa en [[inscripcion]] como `atleta_id`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/domain/aggregates/atleta.py` | Aggregate Atleta — perfil deportivo, categoría, brevet |
