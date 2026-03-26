# US-2.4.2: Calcular Ranking (BC Resultados — núcleo)

**Estado**: `Backlog`
**Incremento**: Inc 2.4 — El Ranking
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `RankingCompetencia` (nuevo aggregate en BC Resultados)
**Bounded Context**: `resultados` (primer US del BC)

---

## Descripción (lenguaje de negocio)

Como **organizador**,
quiero **ver el ranking de la disciplina automáticamente al finalizar la competencia, con podio destacado**
para **publicar los resultados oficiales sin cálculo manual**.

Esta US inicializa el BC Resultados con su scaffold mínimo: el aggregate `RankingCompetencia`,
el comando `CalcularRanking`, y el endpoint de consulta.
Es el equivalente estructural de US-1.1.1 (scaffold BC Competencia) para el nuevo BC.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate (nuevo) | `RankingCompetencia` | Calcula y persiste el ranking de una disciplina a partir de los resultados finales |
| Value Object (nuevo) | `EntradaRanking` | Posición, atleta, marca efectiva, tarjeta, en podio |
| Domain Event (nuevo) | `ResultadosCalculados` | Señal de ranking disponible |
| Port (nuevo) | `ResultadosCompetenciaPort` | ACL: lee los resultados finales del BC Competencia |
| Command (nuevo) | `CalcularRankingCommand` | Disparado desde `CompetenciaFinalizada` |

### Lenguaje ubicuo relevante

- **Ranking**: lista ordenada de atletas de una disciplina según su marca efectiva. Mejor marca primero.
- **Marca efectiva**: el RP registrado. Para tarjeta amarilla: RP con deducción (pendiente en RF-EJ-03 — en SP2 se usa RP bruto).
- **Podio**: posiciones 1, 2 y 3 del ranking. Flag `en_podio: bool` en cada entrada.
- **DNS / Tarjeta roja**: van al final del ranking, después de todas las performances válidas.
- **Empate**: dos o más atletas con idéntica marca efectiva comparten posición (RF-PM-03). La posición siguiente se salta (e.g., 1, 2, 2, 4 — no hay posición 3).

---

## Especificación del comportamiento

### Reglas de ordenamiento del ranking

```
Prioridad 1: performances con tarjeta blanca o amarilla (válidas), ordenadas por:
  - STA: mayor RP primero (más tiempo es mejor)
  - Distancia (DNF, DYN, etc.): mayor RP primero (más metros es mejor)

Prioridad 2: performances con tarjeta amarilla con deducción (misma regla — en SP2
             sin deducción aplicada, RF-EJ-03 pendiente)

Prioridad 3: DNS y tarjeta roja → final del ranking, sin marca numérica

Empates: comparten posición. La siguiente posición numérica se omite.
```

### Operación: RankingCompetencia.calcular(resultados)

**Nombre**: `calcular(resultados: list[ResultadoFinal])`

| | Descripción |
|---|---|
| **Precondición** | `CompetenciaFinalizada` fue emitido para esta disciplina. La lista `resultados` contiene todas las performances (Ejecutada + DNS). |
| **Postcondición** | `ResultadosCalculados` persiste con el ranking completo ordenado. |
| **Eventos generados** | `ResultadosCalculados` |
| **Excepciones** | `ResultadosIncompletos` si la lista no cubre todas las performances esperadas |

**Ejemplo concreto:**

```
Performances STA finalizadas:
  Atleta A: RP=295s, tarjeta=blanca
  Atleta B: DNS
  Atleta C: RP=310s, tarjeta=blanca
  Atleta D: RP=295s, tarjeta=blanca   ← empate con A

CalcularRanking →

Ranking:
  pos 1: Atleta C — 310s — blanca — podio=True
  pos 2: Atleta A — 295s — blanca — podio=True   ← empate en posición 2
  pos 2: Atleta D — 295s — blanca — podio=True   ← empate en posición 2
  pos 4: Atleta B — DNS    — podio=False           (posición 3 se salta)
```

### ACL: ResultadosCompetenciaPort

BC Resultados no importa directamente de BC Competencia. El ACL traduce
los eventos de Competencia al modelo de Resultados:

```
ResultadosCompetenciaPort.get_resultados_finales(competencia_id, disciplina)
→ list[ResultadoFinal(atleta_id, rp, unidad, tarjeta, es_dns)]
```

En SP2: implementado como `ResultadosCompetenciaAdapter` que lee los streams
`performance-{cid}-*` del Event Store de BC Competencia directamente
(misma base SQLite — ADR-007 una DB por BC permitirá separación en SP4+).

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Calcular Ranking al finalizar disciplina

  Background:
    Given una competencia STA finalizada (CompetenciaFinalizada emitido)
    And los resultados son: C=310s/blanca, A=295s/blanca, D=295s/blanca, B=DNS

  Scenario: Ranking calculado correctamente — STA (mayor tiempo primero)
    When el sistema calcula el ranking
    Then el evento ResultadosCalculados persiste
    And el ranking es: posición 1 → C (310s), posición 2 → A y D (295s empate), posición 4 → B (DNS)

  Scenario: Podio destacado en las primeras 3 posiciones
    When el sistema calcula el ranking
    Then C, A y D tienen en_podio = True
    And B tiene en_podio = False

  Scenario: Empate comparte posición y salta la siguiente
    When el sistema calcula el ranking
    Then A y D tienen posición 2
    And no existe una entrada con posición 3
    And B tiene posición 4

  Scenario: DNS va al final del ranking
    When el sistema calcula el ranking
    Then B aparece después de todas las performances válidas
    And B no tiene marca numérica

  Scenario: Tarjeta roja va al final del ranking
    Given una competencia con atleta E que recibió tarjeta roja
    When el sistema calcula el ranking
    Then E aparece después de todas las performances válidas, junto con DNS

  Scenario: Ranking consultable via endpoint
    Given ResultadosCalculados persiste
    When se consulta GET /competencia/{id}/ranking?disciplina=STA
    Then la respuesta incluye el ranking completo con posición, atleta_id, rp y tarjeta

  Scenario: Ranking DNF ordena por distancia (mayor primero)
    Given una competencia DNF finalizada con resultados: X=85m/blanca, Y=92m/blanca, Z=DNS
    When el sistema calcula el ranking
    Then el orden es: posición 1 → Y (92m), posición 2 → X (85m), posición 3 → Z (DNS)
```

---

## Scaffold del BC Resultados

Esta US inicializa el BC con la estructura mínima:

```
src/
└── resultados/
    ├── domain/
    │   ├── aggregates/
    │   │   └── ranking_competencia.py    ← RankingCompetencia aggregate
    │   ├── value_objects/
    │   │   └── entrada_ranking.py        ← EntradaRanking VO
    │   ├── events/
    │   │   └── resultados_calculados.py  ← ResultadosCalculados event
    │   ├── ports/
    │   │   └── resultados_competencia_port.py
    │   └── exceptions.py
    ├── application/
    │   └── commands/
    │       └── calcular_ranking.py       ← CalcularRankingCommand + Handler
    ├── infrastructure/
    │   └── repositories/
    │       └── resultados_competencia_adapter.py   ← ACL: lee BC Competencia
    └── api/
        └── router.py                     ← GET /competencia/{id}/ranking
```

**No incluye:**
- `OverallTorneo` aggregate (SP3+ — requiere BC Torneo)
- Persistencia propia en Event Store (SP2 usa CRUD en SQLite — sin Event Sourcing en BC Resultados)
- Rankings por categoría/género (RF-PM-05 — SP3)

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] Sí — inicializa BC Resultados y define la estrategia de integración con BC Competencia en SP2

**Decisión de integración en SP2:**
BC Competencia llama directamente al handler `CalcularRankingHandler` desde `AsignarTarjetaHandler` / `RegistrarDNSHandler` tras emitir `CompetenciaFinalizada`. No hay event bus en SP2.

En SP4+: `CompetenciaFinalizada` se publica al bus; BC Resultados lo consume via subscriber. El ACL (`ResultadosCompetenciaAdapter`) absorbe el cambio de interfaz sin modificar el dominio de Resultados.

**Capas afectadas:**
- [x] Domain — scaffold completo de BC Resultados: `RankingCompetencia`, `EntradaRanking`, `ResultadosCalculados`, `ResultadosCompetenciaPort`
- [x] Application — `CalcularRankingHandler` + `CalcularRankingCommand`; integración con BC Competencia vía llamada directa
- [x] Infrastructure — `ResultadosCompetenciaAdapter` (ACL) lee streams de BC Competencia
- [x] API — `GET /competencia/{id}/ranking?disciplina=STA` en `src/resultados/api/router.py`; registrar en `src/app.py`

---

## DoD del Incremento 2.4 (y del SP2)

> **Ranking con podio generado automáticamente al cerrar disciplina**

Verificación:
1. Completar las N performances de una disciplina (STA o DNF)
2. `CompetenciaFinalizada` se emite automáticamente (US-2.4.1)
3. `ResultadosCalculados` se emite automáticamente (esta US)
4. `GET /competencia/{id}/ranking?disciplina=STA` retorna el ranking con posiciones, marcas y podio

**DoD del SP2 completo:**

> Ejecutar una disciplina STA y una DNF completas con 10 atletas cada una,
> incluyendo DNS y black-outs. Mostrar el ranking final de cada una.

---

## Referencias

- Domain Model: `docs/design/domain-model.md` — BC Resultados (§5)
- SP2 candidatas: `docs/plans/sp2/SP2-candidatas.md` — Inc 2.4, US-2.4.2
- RF-PM-03 (empates) · RF-PM-05 (rankings por categoría — diferido SP3)
- US-2.4.1: prerequisito — `CompetenciaFinalizada` debe existir antes de `CalcularRanking`
- ADR-007: un archivo SQLite por BC — BC Resultados tendrá `data/resultados.db`

---

*Redactado: 2026-03-26 — IEDD Capa 3*
