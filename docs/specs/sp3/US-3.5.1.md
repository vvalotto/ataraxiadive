# US-3.5.1: Aggregate RankingOverall — fórmula posicional

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.5
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/domain/`, `resultados/application/`

---

## Descripción

Como **organizador**,
quiero **calcular el ranking general (Overall) de un torneo**
para **premiar a los atletas con mejor desempeño en múltiples disciplinas**.

---

## Contexto

El Overall combina los rankings de disciplina de un mismo torneo en un único ranking general. En SP3 se usa una **fórmula posicional**: la puntuación de un atleta es la suma de sus posiciones en cada disciplina (menor es mejor). El atleta con menor suma gana.

Ejemplo: atleta con posición 1 en STA y posición 3 en DNF → puntaje 4.

Empates: si dos atletas tienen el mismo puntaje, comparten posición (igual que en `RankingCompetencia`).

Atletas DNS o tarjeta roja en una disciplina: se les asigna la peor posición + 1 (equivalente a último lugar + penalización).

---

## Especificación

### Precondición

```python
# resultados/domain/aggregates/ranking_competencia.py — ya implementado (SP2)
# No existe RankingOverall en resultados/domain/
```

### Postcondición

```python
# resultados/domain/value_objects/entrada_overall.py
@dataclass(frozen=True)
class EntradaOverall:
    posicion: int
    atleta_id: str
    puntaje: int              # suma de posiciones por disciplina
    detalle: dict[str, int]   # { disciplina.value: posicion } por disciplina
    en_podio: bool            # posicion <= 3

# resultados/domain/aggregates/ranking_overall.py
class RankingOverall:
    """Aggregate que calcula y proyecta el ranking posicional multi-disciplina.

    Stream ID: "ranking-overall-{torneo_id}"
    """

    def calcular(
        self,
        torneo_id: UUID,
        rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
        penalizacion_ausente: int | None = None,  # None = último + 1
    ) -> list[EntradaOverall]:
        """Calcula el ranking general desde rankings individuales.

        Args:
            torneo_id: ID del torneo.
            rankings_por_disciplina: mapa disciplina → entradas del ranking.
            penalizacion_ausente: posición asignada a atleta sin participación.
                Si None, se usa len(participantes_disciplina) + 1.

        Returns:
            Lista de EntradaOverall ordenada por puntaje (menor primero).
        """
        ...

# resultados/application/commands/calcular_overall.py
@dataclass(frozen=True)
class CalcularOverallCommand:
    torneo_id: UUID
    disciplinas: list[Disciplina]   # disciplinas del torneo a incluir

class CalcularOverallHandler:
    def __init__(
        self,
        ranking_store: EventStorePort,       # store de resultados
        competencia_store: EventStorePort,   # store de competencia (para leer rankings)
    ) -> None: ...

    async def handle(self, cmd: CalcularOverallCommand) -> None:
        """Lee rankings de todas las disciplinas y persiste RankingOverallCalculado."""
        ...

# resultados/domain/events (nuevo):
# RankingOverallCalculado: { torneo_id, disciplinas, entradas: [...] }
```

### Invariantes

- `INV-OV-01`: Un atleta que no participó en una disciplina recibe la peor posición + 1 de esa disciplina
- `INV-OV-02`: Empates en puntaje → misma posición (igual que `RankingCompetencia`)
- `INV-OV-03`: Solo se incluyen atletas que participaron en al menos 1 disciplina del torneo
- `INV-OV-04`: `en_podio = True` si `posicion <= 3`
- `INV-OV-05`: Si no hay rankings calculados para ninguna disciplina, `calcular()` retorna lista vacía

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.5.1 — RankingOverall

  Scenario: overall con 3 atletas en 2 disciplinas
    Given ranking STA: A=1, B=2, C=3
    And ranking DNF: A=2, B=1, C=3
    When se calcula el Overall
    Then A.puntaje=3 (pos 1), B.puntaje=3 (pos 1 empate), C.puntaje=6 (pos 3)
    And A y B en_podio=True

  Scenario: atleta ausente en una disciplina
    Given ranking STA: A=1, B=2
    And ranking DNF: solo B participa (B=1)
    When se calcula el Overall
    Then A recibe posición ausente en DNF = 2 (último + 1)
    And A.puntaje = 1 + 2 = 3, B.puntaje = 2 + 1 = 3 (empate)

  Scenario: sin rankings calculados
    Given torneo sin disciplinas finalizadas
    When CalcularOverall
    Then retorna lista vacía

  Scenario: empate total con mismo puntaje
    Given 2 atletas con puntaje idéntico
    When se calcula el Overall
    Then ambos tienen la misma posición
```

---

## Notas de implementación

- `RankingOverall` sigue el patrón de `RankingCompetencia` (SP2): aggregate con Event Sourcing, stream `"ranking-overall-{torneo_id}"`.
- `CalcularOverallHandler` usa el `competencia_store` para leer los streams de `RankingCompetencia` por disciplina (via `ResultadosCompetenciaAdapter`).
- La fórmula posicional de SP3 es simple. RF-PM-01 define fórmulas configurables — eso queda para SP4/SP5.
- Si un torneo tiene disciplinas sin rankings calculados aún, se excluyen de la suma (no se penaliza por disciplinas no ejecutadas).

---

## Referencias

- US-2.4.2: `RankingCompetencia` — patrón a seguir
- US-3.5.2: P-09 — dispara `CalcularOverall`
- RFs: RF-PM-01 (fórmula), RF-PM-02 (Overall)
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
