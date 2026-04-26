# US-5.6.2: TipoReglamento en Torneo + DI de AlgoritmoPuntaje en CalcularRanking

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `torneo` + `resultados`
**Capas afectadas**: `torneo/domain/value_objects/`, `torneo/domain/aggregates/torneo.py`, `torneo/infrastructure/repositories/`, `resultados/application/commands/calcular_ranking.py`

---

## Descripcion

Como **sistema**,
quiero **que el Torneo declare su reglamento y que CalcularRanking reciba el algoritmo de puntaje por inyección de dependencias**,
para **que el dominio de resultados no sepa qué reglamento está usando y sea extensible a CMAS y AIDA sin modificar el dominio**.

---

## Contexto de dominio

### Elementos DDD

| Elemento | Nombre | Responsabilidad |
|----------|--------|----------------|
| Value Object | `TipoReglamento` | Enum extensible: FAAS / CMAS / AIDA |
| Aggregate | `Torneo` | Incorpora `tipo_reglamento: TipoReglamento` con default FAAS |
| Command handler | `CalcularRankingHandler` | Recibe `AlgoritmoPuntaje` por DI; delega el cálculo sin acoplarse a la implementación |

### Lenguaje ubicuo relevante

- **Reglamento**: conjunto de reglas que determina cómo se calculan los puntos en un torneo
- **FAAS**: reglamento vigente para Argentina (implementado en US-5.6.1)

---

## Invariantes

- **INV-5.6.2-01**: `TipoReglamento` tiene valor por defecto `FAAS`; un torneo sin reglamento explícito usa FAAS.
- **INV-5.6.2-02**: `CalcularRankingHandler` nunca instancia directamente `AlgoritmoPuntajeFAAS`; lo recibe como parámetro.
- **INV-5.6.2-03**: el `tipo_reglamento` de `Torneo` se persiste y puede recuperarse desde el repositorio.

---

## Especificacion del comportamiento

### Operacion — agregar `tipo_reglamento` a Torneo

| | Descripción |
|---|---|
| **Precondición** | `Torneo` existe; si no se especifica reglamento, se usa `TipoReglamento.FAAS` |
| **Postcondición** | `torneo.tipo_reglamento` retorna el valor correcto; se persiste en el repositorio |

### Operacion — DI en `CalcularRankingHandler`

| | Descripción |
|---|---|
| **Precondición** | El handler recibe un `AlgoritmoPuntaje` concreto al construirse |
| **Postcondición** | El handler llama `algoritmo.calcular(resultados, disciplina)` sin saber qué implementación es |

**Resolución del algoritmo concreto:** el composition root (o la fábrica en `app.py` / router) selecciona `AlgoritmoPuntajeFAAS` para `TipoReglamento.FAAS`. Cuando se agreguen CMAS/AIDA, solo se toca el composition root.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.2 — TipoReglamento y DI de AlgoritmoPuntaje

  Scenario: torneo sin reglamento explicito usa FAAS por defecto
    Given un torneo creado sin campo tipo_reglamento
    When se consulta torneo.tipo_reglamento
    Then el valor es "FAAS"

  Scenario: torneo persistido con reglamento recupera el mismo valor
    Given un torneo creado con tipo_reglamento = "FAAS"
    When se persiste y luego se recupera del repositorio
    Then torneo.tipo_reglamento sigue siendo "FAAS"

  Scenario: CalcularRankingHandler usa el algoritmo recibido por DI
    Given un handler construido con AlgoritmoPuntajeFAAS
    And una disciplina con resultados de atletas
    When se ejecuta CalcularRanking
    Then el handler llama calcular() sobre el algoritmo recibido
    And no instancia ninguna implementacion concreta internamente
```

---

## Impacto arquitectonico

- [x] Domain (`torneo`) — nuevo VO `TipoReglamento`, campo en `Torneo`
- [x] Infrastructure (`torneo`) — persistir `tipo_reglamento` en repositorio SQLite
- [x] Application (`resultados`) — `CalcularRankingHandler` con inyección de `AlgoritmoPuntaje`

### Estructura a crear / modificar

```
torneo/domain/value_objects/
└── tipo_reglamento.py         ← nuevo StrEnum: FAAS / CMAS / AIDA

torneo/domain/aggregates/torneo.py
  → agregar campo tipo_reglamento: TipoReglamento = TipoReglamento.FAAS

torneo/infrastructure/repositories/sqlite_torneo_repository.py
  → persistir / recuperar tipo_reglamento

resultados/application/commands/calcular_ranking.py
  → CalcularRankingHandler recibe algoritmo: AlgoritmoPuntaje en __init__
```

---

## Referencias

- `docs/plans/sp5/PLAN-SP5.md §Algoritmo de Puntaje FAAS — Extensibilidad`
- `US-5.6.1` — define el puerto `AlgoritmoPuntaje` y `AlgoritmoPuntajeFAAS`
- `src/torneo/domain/aggregates/torneo.py` — aggregate a extender
- `src/resultados/application/commands/calcular_ranking.py` — command handler a modificar

---

*Redactado: 2026-04-26 — INC-5.6*
