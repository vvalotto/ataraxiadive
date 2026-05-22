---
title: "Ranking"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/resultados.md
  - docs/architecture/13-bc-resultados.md
---

# Ranking

Ordenamiento de [[performance|performances]] válidas de una competencia, producido por el BC [[resultados]] a partir del cierre de una [[disciplina]].

## Dos tipos de ranking

### 1. Ranking por competencia (`RankingCompetencia`)

Calcula posiciones dentro de una disciplina específica de una competencia.

**Reglas de ordenamiento:**
- Performances válidas (`Blanca` o `BlancaConPenalizaciones`) ordenadas por mejor RP descendente.
- [[dns|DNS]] y [[tarjeta|Rojas]] al final, sin posición asignada.
- Empates: misma posición, la siguiente posición se salta.
- Podio: top 3 marcado explícitamente.

**Unidad de medida:** según la [[disciplina]] (metros para distancia, segundos para tiempo).

### 2. Ranking overall (`RankingOverall`)

Agrega resultados de todas las disciplinas de un torneo, agrupados por [[categoria]] y género.

**Entrada:** colección de `ResultadosCalculados` de todas las competencias del torneo.
**Salida:** `EntradaOverall` por atleta con `EntradaRanking` anidadas por disciplina.

## Value Object: `EntradaRanking`

| Campo | Descripción |
|-------|-------------|
| `posicion` | Número de posición (1-indexed) |
| `atleta_id` | Referencia al atleta |
| `rp` | Marca efectiva (post-[[penalizacion]] si aplica) |
| `unidad` | Unidad de medida de la disciplina |
| `tarjeta` | Tipo de tarjeta asignada |
| `dns` | Booleano — Did Not Start |
| `podio` | Booleano — top 3 |

## Algoritmos diferenciados por reglamento

Los algoritmos `AlgoritmoFAAS`, `AlgoritmoFAAS_Puntaje` (SP5) y potencialmente `AlgoritmoAIDA` / `AlgoritmoCMAS` implementan variaciones reglamentarias. El [[torneo]] declara el tipo de reglamento aplicable.

## Separación cálculo / lectura

El ranking **no se recalcula en runtime** en cada consulta HTTP. El BC persiste el resultado calculado como evento `ResultadosCalculados`. Las consultas reconstitruyen el aggregate desde ese stream — la respuesta es una lectura, no un cómputo.

**Excepción:** `ObtenerRankingProvisionalHandler` (SP5) lee `competencia.db` directamente cuando no existe `ResultadosCalculados` todavía — deuda técnica documentada en [[resultados]].

## BC propietario

[[resultados]] — aggregate `RankingCompetencia`, tabla de stream en `resultados.db`.

## ADRs relacionados

- [[ADR-014-penalizaciones-acumulables]] — `BlancaConPenalizaciones` es tarjeta válida para ranking
- [[ADR-001-event-sourcing-competencia]] — fuente de datos del ranking (streams de Performance)
- [[ADR-022-categoria-shared]] — la `Categoria` agrupa entradas del overall
