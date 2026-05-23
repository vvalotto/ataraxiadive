---
title: "Impacto: Categoria (valor compartido cross-BC)"
type: impacto
last_updated: "2026-05-22"
sources:
  - wiki/decisiones/ADR-022-categoria-shared.md
  - wiki/arquitectura/registro.md
  - wiki/arquitectura/resultados.md
  - wiki/arquitectura/competencia.md
componente: Categoria (shared value object)
riesgo: medio
bcs_afectados: [registro, resultados, competencia]
tipo: shared
---

# Impacto: `Categoria` (valor compartido cross-BC)

## Qué es

`Categoria` es un `StrEnum` que modela las categorías deportivas del sistema:

```python
class Categoria(StrEnum):
    SENIOR_MASCULINO = "SENIOR_MASCULINO"
    SENIOR_FEMENINO  = "SENIOR_FEMENINO"
    MASTER_MASCULINO = "MASTER_MASCULINO"
    MASTER_FEMENINO  = "MASTER_FEMENINO"
    JUNIOR_MASCULINO = "JUNIOR_MASCULINO"
    JUNIOR_FEMENINO  = "JUNIOR_FEMENINO"
```

**Ubicación actual:** `src/registro/domain/value_objects/categoria.py`

**Ubicación objetivo (ADR-022):** `src/shared/domain/value_objects/categoria.py` — el refactor fue decidido en SP6 pero **no se aplicó completamente** en el código. BC Resultados sigue importando desde `registro.domain.value_objects.categoria`.

## BCs afectados

| BC | Rol | Observación |
|----|-----|-------------|
| [[arquitectura/registro]] | Propietario físico del archivo | Aggregate `Atleta` — asigna y valida la categoría |
| [[arquitectura/resultados]] | Consumidor | Múltiples imports desde `registro.domain` — deuda técnica pendiente |
| [[arquitectura/competencia]] | Consumidor indirecto | No importa `Categoria` directamente — la recibe vía `AtletaInfoAdapter` en Resultados |

### Archivos de Resultados que importan `Categoria` desde Registro

```
src/resultados/application/commands/calcular_ranking.py
src/resultados/domain/aggregates/ranking_competencia.py
src/resultados/domain/aggregates/ranking_overall.py
src/resultados/infrastructure/repositories/atleta_categoria_adapter.py
src/resultados/application/queries/obtener_ranking.py
src/resultados/application/queries/obtener_overall.py
... (y otros en src/resultados/)
```

Todos usan `from registro.domain.value_objects.categoria import Categoria`. Esto introduce dependencia explícita del módulo de Registro en el dominio de Resultados — viola [[ADR-006-estructura-bc-first]].

## Riesgo de cambio: medio

### Agregar una nueva categoría

Impacta `Categoria` (agregar valor al enum). Consecuencias:

- Tests BDD que asumen el conjunto fijo de categorías pueden fallar.
- La lógica de ranking en Resultados que itera sobre categorías debe incluir la nueva.
- Los seeds de datos de UAT y datasets de prueba deben actualizarse.
- **No requiere migración de DB** — `Categoria` se almacena como TEXT.

### Renombrar o eliminar una categoría

Riesgo alto dentro del caso general:

- Datos históricos en `atletas.categoria` (Registro) y en rankings calculados (Resultados) quedan inconsistentes.
- Requiere migración de datos en ambas DBs.
- Los tests de regresión deben actualizarse en Registro y Resultados.

### Completar el refactor ADR-022 (mover a `shared/`)

Impacto técnico acotado pero amplio en cantidad de archivos:

- Actualizar todos los imports de `registro.domain.value_objects.categoria` → `shared.domain.value_objects.categoria` en Resultados (~8+ archivos).
- Verificar que `registro.domain.value_objects.categoria` siga existiendo (o eliminarlo y actualizar imports de Registro también).
- Sin cambio de comportamiento en runtime — es un refactor de imports.

## Estado vs ADR-022

| Aspecto | ADR-022 dice | Estado actual |
|---------|-------------|---------------|
| Ubicación de `Categoria` | `shared/domain/value_objects/` | `registro/domain/value_objects/` |
| Imports en Resultados | `from shared.domain...` | `from registro.domain...` |
| Refactor aplicado en SP6 | Sí | Parcialmente — el archivo no se movió |

Esta discrepancia es la deuda técnica de mayor superficie cross-BC abierta en el proyecto.

## Recorrido en el wiki

```
[[ADR-022-categoria-shared]]
  → [[ADR-006-estructura-bc-first]] (regla de imports cross-BC)
  → [[arquitectura/registro]] sección "Value Objects"
  → [[arquitectura/resultados]] sección "Dependencias"
  → [[impacto/atleta-nombre-port]] (patrón análogo de cross-BC directo)
```

## ADRs relacionados

- [[ADR-022-categoria-shared]] — decisión de mover `Categoria` a `shared/`; consecuencias documentadas
- [[ADR-006-estructura-bc-first]] — la única excepción cross-BC permitida es `shared/domain/`; imports desde `registro.domain` en Resultados violan esta regla
- [[ADR-005-bounded-contexts-ddd-estrategico]] — mapa estratégico de BCs; Registro y Resultados son Supporting Domains
