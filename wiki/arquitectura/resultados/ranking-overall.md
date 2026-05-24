---
title: "Resultados — Aggregate RankingOverall"
type: arquitectura-componente
bc: resultados
capa: domain
tipo_componente: aggregate
responsabilidad: "Calcula el ranking general del torneo sumando puntos FAAS de todas las disciplinas — Event Sourcing"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/resultados/domain/aggregates/ranking_overall.py
---

# Aggregate RankingOverall

## Stream ID

```
ranking-overall-{torneo_id}
```

## Responsabilidad

Calcula el **ranking general (overall)** de un torneo sumando los puntos FAAS obtenidos por cada atleta en todas las disciplinas. Requiere que todas las disciplinas tengan ranking calculado antes de proceder.

## Estado interno

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_torneo_id` | UUID | Identifica el torneo |
| `_entries` | `list[EntradaOverall]` | Ranking overall ordenado |
| `_calculado` | bool | True si ya fue calculado |

## Comando: `calcular(torneo_id, rankings_por_disciplina)`

```python
def calcular(
    self,
    torneo_id: UUID,
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
) -> list[EntradaOverall]
```

### Invariante INV-5.6.4-04

Lanza `DisciplinasNoFinalizadas` si alguna disciplina tiene lista vacía de entradas — indica que no fue calculada aún.

### Algoritmo

1. Detecta categorías presentes en todos los rankings
2. Por categoría: acumula `puntos FAAS` de cada atleta sumando todas las disciplinas
   - Atleta ausente en una disciplina aporta 0 (INV-5.6.4-01)
3. Ordena por `puntos_overall` desc
4. Empates comparten posición (INV-5.6.4-03)
5. Podio: `en_podio = posicion <= 3`

## Evento emitido: `RankingOverallCalculado`

```json
{
  "torneo_id": "...",
  "disciplinas": ["DNF", "STA"],
  "total": 8,
  "entries": [...],
  "calculado_en": "..."
}
```

## Value Object: EntradaOverall

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `posicion` | int | Posición en el ranking |
| `atleta_id` | UUID | |
| `categoria` | Categoria | |
| `puntos_overall` | Decimal | Suma de puntos FAAS |
| `detalle` | `dict[str, Decimal]` | Puntos por disciplina |
| `en_podio` | bool | posicion <= 3 |

## Relaciones

- `AggregateRoot` de `shared/domain/base/` — igual que [[ranking-competencia]]
- Calculado por [[command-handlers-resultados]] (CalcularOverallHandler)
- Requiere que [[ranking-competencia]] ya haya sido calculado para cada disciplina del torneo
- Leído por [[query-handlers-resultados]] (ObtenerOverallHandler)
