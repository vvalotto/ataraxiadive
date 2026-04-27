# US-5.6.4: RankingOverall por categoría con puntos acumulados

**Estado**: `Done`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/domain/aggregates/ranking_overall.py`, `resultados/domain/value_objects/entrada_overall.py`, `resultados/application/commands/calcular_overall.py`, `resultados/api/router.py`

---

## Descripcion

Como **organizador**,
quiero **que el Overall del torneo sume los puntos FAAS de cada atleta por disciplina y los presente agrupados por las 6 categorías**,
para **determinar el campeón de cada categoría al cerrar todas las disciplinas**.

---

## Contexto de dominio

### Elementos DDD

| Elemento | Nombre | Responsabilidad |
|----------|--------|----------------|
| Aggregate | `RankingOverall` | Calcula el overall del torneo sumando puntos de todas las disciplinas por atleta |
| Value Object | `EntradaOverall` | Extiende con `puntos_overall: Decimal` (suma algebraica de puntos por disciplina) |
| Evento | `RankingOverallCalculado` | Persistido en event store al cerrar el overall |

### Lenguaje ubicuo relevante

- **Overall**: ranking general del torneo. Solo disponible cuando todas las disciplinas están cerradas.
- **Puntos Overall**: `P_overall_i = Σ(P_i,d)` para todas las disciplinas en que el atleta compitió. Un atleta que no compitió en una disciplina aporta 0 puntos.
- **INV-ORG-05**: el Overall solo se calcula cuando todas las disciplinas del torneo están en estado FINALIZADA.

---

## Invariantes

- **INV-5.6.4-01**: `puntos_overall = Σ puntos_disciplina` para todas las disciplinas del torneo; ausencia en una disciplina = 0 puntos.
- **INV-5.6.4-02**: la posición en el overall se determina por `puntos_overall` descendente dentro de cada `Categoria`.
- **INV-5.6.4-03**: si dos atletas empatan en puntos, la posición se comparte (mismo número).
- **INV-5.6.4-04**: el Overall solo puede calcularse si todas las disciplinas del torneo están en estado FINALIZADA.
- **INV-5.6.4-05**: `puntos_overall` tiene precisión de 2 decimales.

---

## Especificacion del comportamiento

### Cambio en `EntradaOverall`

Agregar campo `puntos_overall: Decimal`.

### Operacion — `RankingOverall.calcular`

| | Descripción |
|---|---|
| **Precondición** | Todas las disciplinas del torneo tienen `RankingCompetencia` calculado con puntos (post US-5.6.3) |
| **Postcondición** | `entries` contiene un `EntradaOverall` por atleta, con `puntos_overall` = suma de puntos por disciplina; agrupados y ordenados por `Categoria` |
| **Evento generado** | `RankingOverallCalculado` con payload actualizado |
| **Excepción** | Si alguna disciplina no está finalizada → rechazar con error de dominio |

**Ejemplo concreto:**

```
Disciplinas: DNF, STA

Puntos por disciplina:
  Ana   (SENIOR_FEMENINO)  → DNF: 100.00, STA: 75.00 → Overall: 175.00
  María (SENIOR_FEMENINO)  → DNF: 80.00,  STA: 95.00 → Overall: 175.00  (empate)
  Luis  (SENIOR_MASCULINO) → DNF: 80.00,  STA: 60.00 → Overall: 140.00

Overall SENIOR_FEMENINO:
  pos=1  Ana   175.00   (empate → misma posición)
  pos=1  María 175.00
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.4 — RankingOverall con puntos acumulados

  Scenario: overall suma puntos de todas las disciplinas
    Given Ana con 100.00 puntos en DNF y 75.00 en STA (SENIOR_FEMENINO)
    When se calcula el overall
    Then Ana tiene puntos_overall = 175.00

  Scenario: atleta sin participar en una disciplina aporta 0
    Given Luis (SENIOR_MASCULINO) con 80.00 puntos en DNF y DNS en STA (0 puntos)
    When se calcula el overall
    Then Luis tiene puntos_overall = 80.00

  Scenario: empate en overall comparte posicion
    Given Ana y Maria con 175.00 puntos cada una en SENIOR_FEMENINO
    When se calcula el overall
    Then ambas aparecen con posicion = 1

  Scenario: overall rechazado si hay disciplinas sin finalizar
    Given el torneo tiene la disciplina STA sin estado FINALIZADA
    When se intenta calcular el overall
    Then el sistema rechaza la operacion con error de dominio

  Scenario: overall agrupa por las 6 categorias
    Given atletas en SENIOR_MASCULINO, SENIOR_FEMENINO, MASTER_MASCULINO
    When se calcula el overall
    Then las entries estan separadas por Categoria
    And la posicion 1 de cada grupo es el atleta con mas puntos_overall en esa categoria
```

---

## Impacto arquitectonico

- [x] Domain — `EntradaOverall` + `RankingOverall.calcular()`
- [x] Application — `CalcularOverallHandler` lee puntos de cada `RankingCompetencia`
- [x] Infrastructure — serialización del event store actualizada
- [x] API — respuesta de `GET /{torneo_id}/overall` incluye `puntos_overall` agrupado por categoría

---

## Referencias

- `US-5.6.3` — `EntradaRanking.puntos` (fuente de datos para el overall)
- `src/resultados/domain/aggregates/ranking_overall.py` — aggregate a extender
- `src/resultados/domain/value_objects/entrada_overall.py` — VO a extender
- `docs/plans/sp5/PLAN-SP5.md §Overall`

---

*Redactado: 2026-04-26 — INC-5.6*
