---
title: "Resultados — Aggregate RankingCompetencia"
type: arquitectura-componente
bc: resultados
capa: domain
tipo_componente: aggregate
responsabilidad: "Calcula y persiste el ranking de una disciplina dentro de una competencia — Event Sourcing, dos paths: FAAS (puntos) y legacy (RP directo)"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001, ADR-008, ADR-014]
last_updated: "2026-05-23"
sources:
  - src/resultados/domain/aggregates/ranking_competencia.py
---

# Aggregate RankingCompetencia

## Stream ID

```
ranking-{competencia_id}-{disciplina}
```

Ejemplo: `ranking-a1b2c3d4-DNF`

## Responsabilidad

Calcula el ranking de una disciplina a partir de los `ResultadoFinal` obtenidos desde BC Competencia. Persiste el resultado como evento `ResultadosCalculados` en el Event Store del BC Resultados (`resultados.db`). Soporta dos paths de cálculo.

## Estado interno

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_competencia_id` | UUID | Identifica la competencia |
| `_disciplina` | Disciplina | Disciplina del ranking |
| `_entries` | `list[EntradaRanking]` | Ranking calculado y ordenado |
| `_calculado` | bool | True si ya fue calculado |

## Comando: `calcular(resultados, algoritmo)`

```python
def calcular(
    self,
    resultados: list[ResultadoFinal],
    algoritmo: AlgoritmoPuntaje | None = None,
) -> None
```

Lanza `ResultadosIncompletos` si `resultados` está vacío.

### Path FAAS (algoritmo provisto)

1. Agrupa resultados por `Categoria`
2. Calcula puntos via `algoritmo.calcular(resultados, disciplina)` → `dict[UUID, Decimal]`
3. Por categoría: ordena válidas por puntos desc → tie-break por RP desc
4. DNS / Tarjeta Roja: puntos=0.00, al final, sin podio

### Path legacy (sin algoritmo)

1. Agrupa por categoría
2. Ordena válidas por RP desc
3. Empates de RP → comparten posición; la siguiente se omite
4. DNS / roja al final

### Podio

Posiciones 1, 2, 3. `en_podio=True` si `posicion <= 3`. Los empates en pos 2 ó 3 incluyen múltiples atletas en podio.

## Evento emitido: `ResultadosCalculados`

```json
{
  "competencia_id": "...",
  "disciplina": "DNF",
  "total": 12,
  "entries": [...],
  "calculado_en": "..."
}
```

## Reconstitución

```python
ranking = RankingCompetencia.reconstitute(competencia_id, disciplina, events)
```

Aplica `_rehidratar_resultados_calculados` para restaurar `_entries` y `_calculado` desde el payload del evento almacenado.

## Value Object: EntradaRanking

| Campo | Tipo |
|-------|------|
| `posicion` | int |
| `atleta_id` | UUID |
| `categoria` | Categoria |
| `rp` | Decimal \| None |
| `unidad` | str \| None |
| `tarjeta` | str |
| `es_dns` | bool |
| `en_podio` | bool |
| `puntos` | Decimal |

## Relaciones

- `AggregateRoot` de `shared/domain/base/` — hereda `_record()` y `pull_events()`
- Emite evento consumido por [[calculador-ranking-handler-resultados]] via `pull_events()`
- Recibe datos desde [[resultados-competencia-port]] (ACL a BC Competencia)
- Usa [[algoritmo-faas]] como implementación concreta de `AlgoritmoPuntaje`
- Leído por [[query-handlers-resultados]] para consultas y exportación
