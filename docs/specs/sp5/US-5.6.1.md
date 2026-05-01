# US-5.6.1: Puerto AlgoritmoPuntaje + implementación FAAS

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/domain/ports/`, `resultados/domain/services/`

---

## Descripcion

Como **sistema de resultados**,
quiero **un puerto de dominio `AlgoritmoPuntaje` con una implementación FAAS concreta**,
para **calcular los puntos de cada atleta en una disciplina sin acoplar el dominio a un reglamento específico**.

---

## Contexto de dominio

### Elementos DDD

| Elemento | Nombre | Responsabilidad |
|----------|--------|----------------|
| Puerto | `AlgoritmoPuntaje` | Contrato: recibe resultados de una disciplina, retorna mapa atleta_id → puntos |
| Servicio de dominio | `AlgoritmoPuntajeFAAS` | Implementa el reglamento FAAS según fórmulas de distancia y tiempo |

### Lenguaje ubicuo relevante

- **FAAS**: Federación Argentina de Apnea Submarina — reglamento vigente para torneos locales
- **Puntos FAAS**: valor decimal 0–100 calculado relativamente al mejor resultado de la disciplina
- **DNS / Tarjeta Roja**: rendimiento inválido → puntos = 0 y excluidos del denominador del cálculo

---

## Algoritmo FAAS

### Disciplinas de distancia (DNF, DYN, DBF)

```
P_i = (d_i / d_max) × 100

d_max = max(RP) entre atletas con tarjeta blanca en la disciplina
Tarjeta Roja / DNS → P_i = 0, excluidos del cálculo de d_max
```

### Disciplinas de tiempo (STA, SPE)

```
P_i = (t_max - t_i) / (t_max - t_min) × 100

t_min = menor tiempo (más rápido) → 100 puntos
t_max = mayor tiempo (más lento) → 0 puntos
Caso borde: t_max == t_min → todos reciben 100 puntos
Tarjeta Roja / DNS → P_i = 0, excluidos del cálculo
```

---

## Invariantes

- **INV-5.6.1-01**: atletas con tarjeta roja o DNS siempre reciben 0 puntos y NO participan del cálculo de referencia (d_max, t_max, t_min).
- **INV-5.6.1-02**: si no hay atletas con tarjeta blanca en la disciplina, todos reciben 0 puntos (ningún denominador calculable).
- **INV-5.6.1-03**: el resultado de `calcular` es un mapa completo: cada `atleta_id` del input tiene exactamente una entrada en el output.
- **INV-5.6.1-04**: los puntos tienen precisión de 2 decimales.

---

## Especificacion del comportamiento

### Puerto `AlgoritmoPuntaje`

```python
# resultados/domain/ports/algoritmo_puntaje.py
class AlgoritmoPuntaje(ABC):
    @abstractmethod
    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]:
        """Retorna mapa atleta_id → puntos (0–100, 2 decimales)."""
```

### Operacion principal — `AlgoritmoPuntajeFAAS.calcular`

| | Descripción |
|---|---|
| **Precondición** | `resultados` es una lista no vacía de `ResultadoFinal` de la misma disciplina |
| **Postcondición** | Retorna `dict[UUID, Decimal]` con un entry por cada atleta; los valores están en [0, 100] con 2 decimales |
| **Excepciones** | Si `resultados` está vacío → retorna dict vacío (sin error) |

**Ejemplo concreto (distancia — DNF):**

```
Resultados:
  Ana   → RP=70m, Blanca
  Luis  → RP=56m, Blanca
  Pedro → DNS

d_max = 70

P_Ana   = (70/70) × 100 = 100.00
P_Luis  = (56/70) × 100 = 80.00
P_Pedro = 0.00
```

**Ejemplo concreto (tiempo — STA):**

```
Resultados:
  Ana   → RP=4min30s=270s, Blanca
  Luis  → RP=3min10s=190s, Blanca
  Pedro → Roja

t_min=190, t_max=270

P_Luis = (270-190)/(270-190) × 100 = 100.00
P_Ana  = (270-270)/(270-190) × 100 = 0.00
P_Pedro = 0.00
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.1 — Algoritmo de puntaje FAAS

  Scenario: distancia — puntuacion proporcional al maximo
    Given una disciplina de tipo distancia (DNF)
    And resultados: Ana 70m Blanca, Luis 56m Blanca
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 80.00 puntos

  Scenario: tiempo — el mas rapido recibe 100 puntos
    Given una disciplina de tipo tiempo (STA)
    And resultados: Luis 190s Blanca, Ana 270s Blanca
    When se calcula el puntaje FAAS
    Then Luis recibe 100.00 puntos
    And Ana recibe 0.00 puntos

  Scenario: DNS recibe 0 y no altera el denominador
    Given una disciplina de tipo distancia (DNF)
    And resultados: Ana 70m Blanca, Pedro DNS
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Pedro recibe 0.00 puntos
    And d_max = 70 (DNS excluido)

  Scenario: caso borde tiempo — todos igual
    Given una disciplina de tipo tiempo (STA)
    And resultados: Ana 180s Blanca, Luis 180s Blanca
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 100.00 puntos

  Scenario: todos invalidos — todos reciben 0
    Given una disciplina de tipo distancia (DNF)
    And todos los resultados son Roja o DNS
    When se calcula el puntaje FAAS
    Then todos reciben 0.00 puntos
```

---

## Impacto arquitectonico

- [x] Domain — puerto en `resultados/domain/ports/` + servicio en `resultados/domain/services/`
- [ ] Application — wired en US-5.6.2 (DI desde `CalcularRanking`)

### Estructura a crear

```
resultados/domain/ports/
└── algoritmo_puntaje.py       ← puerto abstracto AlgoritmoPuntaje

resultados/domain/services/
└── algoritmo_faas.py          ← AlgoritmoPuntajeFAAS implementa AlgoritmoPuntaje
```

---

## Referencias

- `docs/plans/sp5/PLAN-SP5.md §Algoritmo de Puntaje FAAS`
- `src/resultados/domain/ports/resultados_competencia_port.py` — patrón de puerto existente
- `src/registro/domain/value_objects/categoria.py` — Categoria ya encapsula género

---

*Redactado: 2026-04-26 — INC-5.6*
