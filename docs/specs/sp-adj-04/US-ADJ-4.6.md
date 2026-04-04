# US-ADJ-4.6: Value Object `TiempoAP` — parsear formato MM:SS a segundos

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: ninguno (nuevo Value Object compartido)
**Bounded Context**: `shared/domain`

---

## Descripción (lenguaje de negocio)

Como **desarrollador que ingesta datos reales de un torneo de apnea**,
quiero que el dominio provea una conversión explícita del formato `MM:SS`
(usado en documentos oficiales de la federación) a segundos (Decimal)
para que esa conversión sea parte del modelo y no quede delegada a código externo
sin validaciones.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object nuevo | `TiempoAP` | Encapsula un AP expresado en tiempo, con parsing y validación de formato `MM:SS` |

### Lenguaje ubicuo relevante

- **AP en tiempo**: Para disciplinas STA y SPE, el AP (Announced Performance) se expresa en minutos y segundos. Los documentos oficiales de la federación usan el formato `MM:SS` (e.g., `"02:30"`, `"04:01"`, `"05:30"`).
- **`MM:SS`**: formato canónico para APs de tiempo en apnea. También puede aparecer como `HH:MM:SS` para APs largos (> 59:59).

### Origen de la brecha

Los APs de STA y SPE en el dataset Buenos Aires 2025 están expresados en `MM:SS`.
El dominio solo acepta `Decimal` en segundos. Sin un VO que encapsule el parsing,
la conversión queda en los seeds, scripts de ingesta o frontend — sin validaciones
ni semántica de dominio (HITO-17, DISC-06).

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-T-01: el valor en segundos resultante debe ser > 0.
- INV-T-02: el formato de entrada `MM:SS` debe ser válido — minutos y segundos numéricos, segundos en [0, 59].
- INV-T-03: el formato `HH:MM:SS` también es válido (para APs > 59:59, aunque infrecuente en STA).

### Value Object

```python
@dataclass(frozen=True)
class TiempoAP:
    """AP expresado en tiempo — encapsula segundos con parsing desde MM:SS."""
    segundos: Decimal  # siempre positivo

    @classmethod
    def desde_mmss(cls, texto: str) -> "TiempoAP":
        """Parsea 'MM:SS' o 'HH:MM:SS' y retorna TiempoAP en segundos.

        Raises:
            FormatoTiempoInvalido: si el formato no es MM:SS o HH:MM:SS válido.
            ValorTiempoInvalido: si el resultado en segundos es <= 0.
        """

    @classmethod
    def desde_segundos(cls, valor: Decimal) -> "TiempoAP":
        """Constructor alternativo cuando el valor ya está en segundos.

        Raises:
            ValorTiempoInvalido: si valor <= 0.
        """
```

**Precondición:** se recibe un string con formato `MM:SS` o `HH:MM:SS`, o un `Decimal` positivo.
**Postcondición:** `TiempoAP.segundos` contiene el valor en segundos como `Decimal`.

**Ejemplos concretos (datos reales Buenos Aires 2025):**

```
TiempoAP.desde_mmss("00:30")  → TiempoAP(segundos=Decimal("30"))
TiempoAP.desde_mmss("02:30")  → TiempoAP(segundos=Decimal("150"))
TiempoAP.desde_mmss("04:01")  → TiempoAP(segundos=Decimal("241"))
TiempoAP.desde_mmss("05:30")  → TiempoAP(segundos=Decimal("330"))
TiempoAP.desde_segundos(Decimal("196"))  → TiempoAP(segundos=Decimal("196"))

TiempoAP.desde_mmss("02:60")  → FormatoTiempoInvalido (segundos > 59)
TiempoAP.desde_mmss("00:00")  → ValorTiempoInvalido (resultado = 0)
TiempoAP.desde_mmss("abc")    → FormatoTiempoInvalido
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Parseo de AP en formato MM:SS

  Scenario: Parsear AP STA válido en formato MM:SS
    When se crea TiempoAP desde "02:30"
    Then el valor en segundos es 150

  Scenario: Parsear AP largo válido en formato HH:MM:SS
    When se crea TiempoAP desde "01:00:00"
    Then el valor en segundos es 3600

  Scenario: Formato inválido es rechazado
    When se intenta crear TiempoAP desde "abc"
    Then el sistema lanza FormatoTiempoInvalido

  Scenario: Segundos fuera de rango son rechazados
    When se intenta crear TiempoAP desde "02:60"
    Then el sistema lanza FormatoTiempoInvalido

  Scenario: Valor cero es rechazado
    When se intenta crear TiempoAP desde "00:00"
    Then el sistema lanza ValorTiempoInvalido

  Scenario: Constructor desde segundos directo
    When se crea TiempoAP desde segundos Decimal("196")
    Then el valor en segundos es 196

  Scenario: Segundos negativos o cero son rechazados desde constructor directo
    When se intenta crear TiempoAP desde segundos Decimal("0")
    Then el sistema lanza ValorTiempoInvalido
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — nuevo VO utilitario en `shared/domain`

**Capa(s) afectadas:**
- [x] Domain (nuevo `shared/domain/value_objects/tiempo_ap.py`)

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/design/domain-model.md` | BC Shared — Value Objects | Agregar `TiempoAP` con descripción: "Encapsula un AP de tiempo, parsing de MM:SS a segundos" |
| `CLAUDE.md` | §8 Lenguaje Ubicuo | Agregar entrada: **MM:SS**: formato de APs de tiempo en documentos oficiales AIDA |

---

## Notas de implementación

1. Ubicar en `shared/domain/value_objects/tiempo_ap.py` — es transversal a BC Competencia y potencialmente a BC Registro (para APs anunciados en inscripción futura).
2. Usar `Decimal` para el valor en segundos, consistente con el tipo ya usado en `AP` value object de Competencia.
3. Las excepciones `FormatoTiempoInvalido` y `ValorTiempoInvalido` pueden ir en `shared/domain/exceptions.py` o ser `ValueError` con mensaje claro — seguir el patrón existente del proyecto.
4. Este VO no reemplaza al `AP` value object de Competencia — lo complementa como parser de entrada. El seed del UAT usará `TiempoAP.desde_mmss("02:30").segundos` para obtener el `Decimal` que pasa a `RegistrarAP`.

---

*Spec creada: 2026-04-03 — derivada de DISC-06 del análisis HITO-17*
