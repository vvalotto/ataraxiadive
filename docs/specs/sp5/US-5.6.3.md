# US-5.6.3: RankingCompetencia con puntaje FAAS por categoría

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/domain/aggregates/ranking_competencia.py`, `resultados/domain/value_objects/entrada_ranking.py`, `resultados/application/commands/calcular_ranking.py`, `resultados/api/router.py`

---

## Descripcion

Como **organizador y atleta**,
quiero **que el ranking por disciplina incluya los puntos FAAS de cada atleta y esté agrupado por las 6 categorías (SENIOR/MASTER/JUNIOR × M/F)**,
para **ver los podios correctos al cerrar cada disciplina, separados por categoría y género**.

---

## Contexto de dominio

### Elementos DDD

| Elemento | Nombre | Responsabilidad |
|----------|--------|----------------|
| Aggregate | `RankingCompetencia` | Calcula y almacena el ranking de una disciplina con puntaje |
| Value Object | `EntradaRanking` | Extiende con campo `puntos: Decimal` |
| Evento | `ResultadosCalculados` | Se extiende para incluir puntos en el payload |

### Lenguaje ubicuo relevante

- **Categoría**: `Categoria` enum ya encapsula género (ej: `SENIOR_MASCULINO`); las 6 categorías son las 6 agrupaciones del podio
- **Puntos FAAS**: resultado del cálculo relativo según `AlgoritmoPuntajeFAAS`; dentro de cada categoría, el atleta con más puntos ocupa posición 1

---

## Invariantes

- **INV-5.6.3-01**: la posición dentro de cada categoría se determina por `puntos` descendente (antes era por RP absoluto).
- **INV-5.6.3-02**: en empate de puntos, se mantiene el criterio de empate por RP absoluto como desempate secundario.
- **INV-5.6.3-03**: atletas con tarjeta roja o DNS tienen `puntos = 0` y aparecen al final del ranking de su categoría sin posición de podio.
- **INV-5.6.3-04**: `EntradaRanking.puntos` tiene precisión de 2 decimales.
- **INV-5.6.3-05**: la serialización en el event store incluye `puntos` para permitir reconstitución sin recalcular.

---

## Especificacion del comportamiento

### Cambio en `EntradaRanking`

Agregar campo `puntos: Decimal` (no nullable; DNS/Roja tienen `puntos=Decimal("0.00")`).

### Operacion — `RankingCompetencia.calcular`

| | Descripción |
|---|---|
| **Precondición** | Lista de `ResultadoFinal` con al menos 1 entrada; se recibe un `AlgoritmoPuntaje` concreto |
| **Postcondición** | `entries` contiene una `EntradaRanking` por atleta con `puntos` calculado; posiciones ordenadas por `puntos` desc dentro de cada `Categoria` |
| **Evento generado** | `ResultadosCalculados` con payload actualizado (incluye `puntos`) |

**Ejemplo concreto (DNF, categoría SENIOR_MASCULINO):**

```
Resultados en DNF:
  Ana   (SENIOR_FEMENINO)  → RP=70m, Blanca  → P=100.00
  Luis  (SENIOR_MASCULINO) → RP=56m, Blanca  → P=80.00
  Pedro (SENIOR_MASCULINO) → DNS             → P=0.00

Ranking SENIOR_MASCULINO:
  pos=1  Luis   puntos=80.00
  pos=—  Pedro  puntos=0.00  (DNS, sin posición de podio)

Ranking SENIOR_FEMENINO:
  pos=1  Ana    puntos=100.00
```

### Firma de `calcular` actualizada

```python
def calcular(
    self,
    resultados: list[ResultadoFinal],
    algoritmo: AlgoritmoPuntaje,
) -> None:
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.3 — RankingCompetencia con puntos FAAS

  Scenario: ranking incluye puntos por atleta
    Given una disciplina DNF cerrada con Ana (70m Blanca, SENIOR_F) y Luis (56m Blanca, SENIOR_M)
    When se calcula el ranking FAAS
    Then Ana tiene puntos = 100.00 en su EntradaRanking
    And Luis tiene puntos = 80.00 en su EntradaRanking

  Scenario: ranking agrupa correctamente por las 6 categorias
    Given atletas en SENIOR_MASCULINO, SENIOR_FEMENINO y MASTER_MASCULINO
    When se calcula el ranking
    Then las entries estan agrupadas: primero todas las entradas de cada Categoria
    And la posicion 1 dentro de cada grupo es el atleta con mas puntos en esa categoria

  Scenario: DNS tiene puntos 0 y no tiene posicion de podio
    Given Pedro con DNS en DNF, categoria SENIOR_MASCULINO
    When se calcula el ranking
    Then Pedro tiene puntos = 0.00
    And Pedro no tiene posicion de podio (en_podio=False)

  Scenario: el evento ResultadosCalculados incluye puntos
    Given un ranking calculado con puntos
    When se serializa en el event store
    Then el payload incluye el campo puntos para cada entrada
    And al reconstituir se recuperan los mismos puntos sin recalcular
```

---

## Impacto arquitectonico

- [x] Domain — `EntradaRanking` + `RankingCompetencia.calcular()`
- [x] Application — `CalcularRankingHandler` pasa el algoritmo al aggregate
- [x] Infrastructure — serialización/deserialización del event store actualizada
- [x] API — respuesta de `GET /{competencia_id}/ranking` incluye `puntos` por entrada

### Nota de compatibilidad

Rankings existentes en el event store no tienen campo `puntos`. La deserialización debe tratar `puntos` ausente como `Decimal("0.00")` para no romper reconstitución de eventos anteriores.

---

## Referencias

- `US-5.6.1` — puerto `AlgoritmoPuntaje` y `AlgoritmoPuntajeFAAS`
- `US-5.6.2` — DI del algoritmo en el handler
- `src/resultados/domain/aggregates/ranking_competencia.py` — aggregate a modificar
- `src/resultados/domain/value_objects/entrada_ranking.py` — VO a extender
- `src/registro/domain/value_objects/categoria.py` — Categoria (ya encapsula género)

---

*Redactado: 2026-04-26 — INC-5.6*
