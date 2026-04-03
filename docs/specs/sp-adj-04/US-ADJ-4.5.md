# US-ADJ-4.5: Ranking y Overall por (disciplina/torneo, categoría) en BC Resultados

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: `RankingCompetencia` · `RankingOverall`
**Bounded Context**: `resultados` (con ACL hacia `registro`)

---

## Descripción (lenguaje de negocio)

Como **juez de una competencia de apnea**,
quiero que el sistema calcule rankings separados por categoría dentro de cada disciplina
y overalls separados por categoría dentro de cada torneo
para que los resultados oficiales muestren quién ganó en cada categoría,
tal como lo requieren los reglamentos AIDA y la documentación oficial del torneo.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `RankingCompetencia` | Calcula y persiste el ranking de una disciplina |
| Aggregate | `RankingOverall` | Calcula y persiste el overall de un torneo |
| Value Object | `EntradaRanking` | Una línea del ranking (posición, atleta, RP, tarjeta) |
| DTO (port) | `ResultadoFinal` | Datos de una performance al cierre de la disciplina |
| Port | `ResultadosCompetenciaPort` | ACL hacia BC Competencia — provee los resultados finales |
| Port nuevo | `AtletaCategoriaPort` | ACL hacia BC Registro — provee la categoría de un atleta dado su `atleta_id` |

### Lenguaje ubicuo relevante

- **Ranking por categoría**: tabla de posiciones dentro de un grupo `(disciplina, categoría)`. Cada categoría tiene su propio ranking independiente con posiciones 1, 2, 3...
- **Overall por categoría**: tabla de posiciones dentro de un grupo `(torneo, categoría)`, calculada a partir de todas las disciplinas del torneo. No existe overall flat que mezcle categorías.
- **Categoría**: en este contexto, el valor de `Categoria` del atleta (`SENIOR_MASCULINO`, `MASTER_FEMENINO`, etc.), que encoda sexo y grupo etario.
- **RF-PM-05** (requerimiento funcional existente): "¿Se deben generar rankings separados por categoría y género dentro de cada disciplina?" → **"Sí"** — este RF existía pero nunca fue implementado.

### Origen de la brecha

`domain-model.md` ya describe `RankingCompetencia` como "Ranking por disciplina y
categoría/género". RF-PM-05 lo requería explícitamente. Sin embargo, la implementación
hizo un ranking flat. El dataset real expuso la brecha (HITO-17, DISC-01).

La misma brecha aplica al `overall`: el ranking general del torneo también debe publicarse
por categoría/género, no como una tabla única cross-categoría.

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-R-01: el ranking de una disciplina está siempre segmentado por categoría. No existe ranking flat que mezcle categorías.
- INV-R-02: dentro de cada categoría se aplican las mismas reglas de ordenamiento: válidas (Blanca/Amarilla) por RP desc, inválidas (DNS/Roja) al final. Empates comparten posición.
- INV-R-03: el podio (posiciones 1, 2, 3) se determina dentro de cada categoría de forma independiente.
- INV-R-04: `RankingCompetencia` no consulta BC Registro directamente — lo hace a través del puerto `AtletaCategoriaPort` inyectado en el handler.
- INV-R-05: el `overall` del torneo está siempre segmentado por categoría. No existe overall flat cross-categoría.
- INV-R-06: `RankingOverall` solo combina posiciones de rankings pertenecientes a la misma categoría.

### Operación principal

**`RankingCompetencia.calcular(resultados: list[ResultadoFinal], descriptor: DisciplinaDescriptor)`**

**Cambios en `ResultadoFinal`:**
```python
@dataclass(frozen=True)
class ResultadoFinal:
    atleta_id: UUID
    categoria: Categoria     # ← nuevo campo
    rp: Decimal | None
    unidad: str | None
    tarjeta: str | None
    es_dns: bool
```

**Comportamiento de `calcular()`:**
1. Agrupar `resultados` por `categoria`.
2. Para cada grupo, aplicar las reglas de ordenamiento existentes (válidas por RP desc, inválidas al final, empates comparten posición).
3. El resultado es un dict `{Categoria → list[EntradaRanking]}`.

**Cambios en `EntradaRanking`:**
```python
@dataclass(frozen=True)
class EntradaRanking:
    posicion: int
    atleta_id: UUID
    categoria: Categoria     # ← nuevo campo
    rp: Decimal | None
    unidad: str | None
    tarjeta: str | None
    es_dns: bool
    en_podio: bool
```

**Nuevo port `AtletaCategoriaPort` en `resultados/domain/ports/`:**
```python
class AtletaCategoriaPort(ABC):
    @abstractmethod
    async def get_categoria(self, atleta_id: UUID) -> Categoria: ...
```

**Implementación en `resultados/infrastructure/` (ACL):**
Consulta BC Registro (SQLite directamente, igual que el patrón `ResultadosCompetenciaAdapter`).

**Cambio en `CalcularRankingHandler`:**
Antes de invocar `ranking.calcular()`, enriquecer cada `ResultadoFinal` con la categoría
del atleta via `AtletaCategoriaPort`.

**Precondición:** `CompetenciaFinalizada` fue emitido — todos los atletas tienen resultado (Ejecutada o DNS).
**Postcondición:** `ResultadosCalculados` persiste entradas agrupadas por categoría, cada una con `categoria` en el payload. `GET /resultados/{id}/ranking` retorna resultados segmentados.

### Overall del torneo

`CalcularOverall` y `RankingOverall` deben aplicar la misma segmentación:

1. Agrupar las entradas de ranking por `categoria`.
2. Combinar solo disciplinas del mismo torneo y la misma categoría.
3. Calcular posiciones y podio dentro de cada categoría.

**Postcondición adicional:** `GET /resultados/{torneo_id}/overall` retorna el overall agrupado
por categoría/género. No existe respuesta flat que mezcle categorías.

**Ejemplo concreto:**

```
Entradas (STA, 4 atletas):
  atleta_A: SENIOR_FEMENINO,  RP=277s, Blanca
  atleta_B: SENIOR_FEMENINO,  RP=225s, Blanca
  atleta_C: MASTER_MASCULINO, RP=196s, Blanca
  atleta_D: MASTER_MASCULINO, DNS

Postcondición — ranking calculado:
  SENIOR_FEMENINO:
    pos.1 → atleta_A (277s, en_podio=True)
    pos.2 → atleta_B (225s, en_podio=True)
  MASTER_MASCULINO:
    pos.1 → atleta_C (196s, en_podio=True)
    pos.2 → atleta_D (DNS, en_podio=False)

Overall del torneo:
  SENIOR_FEMENINO:
    pos.1 → atleta_A
    pos.2 → atleta_B
  MASTER_MASCULINO:
    pos.1 → atleta_C
    pos.2 → atleta_D
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Ranking por categoría en una disciplina

  Background:
    Given una competencia STA finalizada con atletas de distintas categorías

  Scenario: Ranking SENIOR FEMENINO independiente de MASTER MASCULINO
    Given atleta_A (SENIOR_FEMENINO) con RP=277s blanca
    And   atleta_B (SENIOR_FEMENINO) con RP=225s blanca
    And   atleta_C (MASTER_MASCULINO) con RP=300s blanca
    When  se calcula el ranking de la disciplina STA
    Then  en SENIOR_FEMENINO: atleta_A es pos.1, atleta_B es pos.2
    And   en MASTER_MASCULINO: atleta_C es pos.1
    And   atleta_C no aparece en el ranking SENIOR_FEMENINO

  Scenario: Empate dentro de una categoría
    Given atleta_A y atleta_B (ambos SENIOR_MASCULINO) con RP=180s blanca
    And   atleta_C (SENIOR_MASCULINO) con RP=150s blanca
    When  se calcula el ranking
    Then  atleta_A y atleta_B comparten pos.1 en SENIOR_MASCULINO
    And   atleta_C queda en pos.3

  Scenario: DNS al final dentro de su categoría
    Given atleta_A (MASTER_FEMENINO) con RP=240s blanca
    And   atleta_B (MASTER_FEMENINO) con DNS
    When  se calcula el ranking
    Then  atleta_A es pos.1 en MASTER_FEMENINO
    And   atleta_B queda al final del ranking MASTER_FEMENINO

  Scenario: GET ranking retorna resultado agrupado por categoría
    Given el ranking de STA fue calculado con 3 categorías
    When  GET /resultados/{id}/ranking?disciplina=STA
    Then  la respuesta incluye una sección por cada categoría presente
    And   cada sección tiene sus propias posiciones comenzando en 1

  Scenario: Overall del torneo se calcula y publica por categoría
    Given existen rankings calculados de varias disciplinas y categorías para un torneo
    When  se calcula el overall del torneo
    Then  cada categoría obtiene su propio overall independiente
    And   no se mezclan atletas de categorías distintas en la misma tabla

  Scenario: GET overall retorna resultado agrupado por categoría
    Given el overall del torneo fue calculado con 2 categorías
    When  GET /resultados/{torneo_id}/overall
    Then  la respuesta incluye una entrada por cada categoría presente
    And   cada entrada tiene sus propias posiciones comenzando en 1
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — implementa un requerimiento existente (RF-PM-05) con el patrón de ports/ACL ya establecido

**Capa(s) afectadas:**
- [x] Domain (`ResultadoFinal`, `EntradaRanking`, `RankingCompetencia.calcular()`, `RankingOverall`, nuevo `AtletaCategoriaPort`)
- [x] Application (`CalcularRankingHandler` — enriquecer con categoría; `ObtenerRankingHandler` — adaptar respuesta; `CalcularOverallHandler` y `ObtenerOverallHandler` — segmentación por categoría)
- [x] Infrastructure (`AtletaCategoriaAdapter` — consulta BC Registro; `ResultadosCompetenciaAdapter` — no necesita cambio en el DTO si la categoría viene del port separado)
- [x] API (`GET /resultados/{id}/ranking` y `GET /resultados/{torneo_id}/overall` — respuesta agrupada por categoría)

## Contrato HTTP acordado

La respuesta HTTP para `ranking` y `overall` usa listas de categorías, no keys dinámicas.

**GET `/resultados/{id}/ranking?disciplina=STA`**

```json
{
  "calculado": true,
  "rankings": [
    {
      "categoria": "SENIOR_FEMENINO",
      "entradas": [
        {
          "posicion": 1,
          "atleta_id": "uuid",
          "rp": "277",
          "unidad": "Segundos",
          "tarjeta": "Blanca",
          "es_dns": false,
          "en_podio": true
        }
      ]
    }
  ]
}
```

**GET `/resultados/{torneo_id}/overall`**

```json
{
  "calculado": true,
  "rankings": [
    {
      "categoria": "SENIOR_FEMENINO",
      "entradas": [
        {
          "posicion": 1,
          "atleta_id": "uuid",
          "puntaje": 4,
          "detalle": {
            "STA": 1,
            "DNF": 3
          },
          "en_podio": true
        }
      ]
    }
  ]
}
```

Si no fue calculado aún, ambos endpoints responden `200` con `calculado=false` y `rankings=[]`.

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/design/domain-model.md` | BC Resultados — `RankingCompetencia` y `EntradaRanking` | Actualizar diagramas y descripciones para reflejar la segmentación por categoría |
| `docs/design/domain-model.md` | BC Resultados — `RankingOverall` | Actualizar diagramas y descripciones para reflejar overall por categoría |
| `docs/design/domain-model.md` | BC Resultados — Ports | Agregar `AtletaCategoriaPort` como nuevo puerto hacia BC Registro |
| `docs/design/domain-model.md` | Context Map / ACLs | Documentar nueva dependencia: Resultados consulta Registro via port |
| `docs/dominio/05-requerimientos_funcionales.md` | RF-PM-05 | Marcar como implementado (era "sí" pero nunca fue implementado) |
| `docs/design/context-map.md` | Relación Resultados ↔ Registro | Agregar ACL: Resultados consulta categoría de atletas en Registro |
| `docs/specs/sp-adj-04/US-ADJ-4.5.md` | Contrato HTTP | Mantener sincronizados los shapes de `ranking` y `overall` por categoría |

---

## Notas de implementación

1. `ResultadoFinal` recibe `categoria` desde `CalcularRankingHandler`, que la obtiene via `AtletaCategoriaPort`. El aggregate `RankingCompetencia` no sabe nada de BC Registro.
2. El patrón de ACL es el mismo que `ResultadosCompetenciaAdapter`: consulta SQLite de BC Registro directamente desde `resultados/infrastructure/`.
3. `ResultadosCalculados` (evento) debe incluir `categoria` en cada entrada del payload para poder reconstituir el aggregate con los datos correctos.
4. El contrato HTTP acordado usa `rankings: [{categoria, entradas}]` tanto para `ranking` como para `overall`. No usar keys dinámicas por categoría.
5. `RankingOverall` debe recalcularse y exponerse con la misma segmentación por categoría/género que `RankingCompetencia`.
6. Esta US tiene el mayor scope del SP-ADJ-04. Ir sola en su propio branch.

---

*Spec creada: 2026-04-03 — derivada de DISC-01 del análisis HITO-17 · RF-PM-05 existente*
