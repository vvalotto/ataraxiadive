# US-6.4.4: Refactoring `AlgoritmoPuntajeFAAS` + correcciones CodeGuard

**Estado**: `Done`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgos**: DR-02 · CG-01/03/04/05
**Bounded Context**: `resultados`
**Capas afectadas**:
- `resultados/domain/services/algoritmo_faas.py`
- Archivos con E501 / `import os` huérfano identificados por CodeGuard

---

## Descripción

Como **desarrollador manteniendo el BC Resultados**,
quiero **que `AlgoritmoPuntajeFAAS` exponga un diseño de dispatch explícito y que los hallazgos de CodeGuard estén resueltos**
para **que DesignReviewer no reporte LCOM elevado en este servicio y la base de código esté limpia de lint**.

---

## Contexto de los Hallazgos

### DR-02 — `AlgoritmoPuntajeFAAS` LCOM 2/1 + Complejidad C=11

`AlgoritmoPuntajeFAAS` tiene dos paths de cálculo completamente independientes entre sí:
- `_calcular_distancia` — usa `d_max` de los válidos
- `_calcular_tiempo` — usa `t_min` / `t_max` de los válidos

Ninguno de los dos métodos comparte estado con el otro (ambos son pure functions sobre `resultados`). DesignReviewer detecta LCOM=2 porque forman dos "clusters" de métodos sin cohesión entre ellos. La complejidad C=11 acumula los dos paths en el método `calcular()`.

La sugerencia del plan es "dispatch por TipoDisciplina" — hacer el dispatch explícito y separar la lógica de cada path.

### CG-01/03/04/05 — E501 (líneas largas) + `import os` huérfano

CodeGuard reporta 4 líneas que superan `line-length = 100` (Black) y un `import os` sin uso en algún archivo del proyecto. Corregibles con `black` + `isort` + revisión manual.

---

## Especificación

### Tarea 1 — Refactoring dispatch explícito en `AlgoritmoPuntajeFAAS`

| | |
|---|---|
| **Precondición** | `calcular()` despacha con `if disciplina.es_tiempo()` |
| **Postcondición** | `calcular()` despacha usando un dict `{bool: callable}` o extrae los paths a funciones de módulo separadas; la lógica de negocio no cambia |
| **Invariante** | Los resultados numéricos son bit-a-bit idénticos a los actuales; todos los tests de resultados pasan |

Opción preferida — dispatch dict (mínimo cambio, máxima claridad):

```python
class AlgoritmoPuntajeFAAS(AlgoritmoPuntaje):
    _CALCULADORES = {
        True: "_calcular_tiempo",
        False: "_calcular_distancia",
    }

    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]:
        if not resultados:
            return {}
        metodo = self._CALCULADORES[disciplina.es_tiempo()]
        return getattr(self, metodo)(resultados)
```

Alternativamente, extraer `_calcular_distancia` y `_calcular_tiempo` a funciones de módulo (sin `self`) y refactorizar la clase a un thin dispatcher — esto elimina el LCOM porque la clase ya no agrupa métodos no cohesivos:

```python
class AlgoritmoPuntajeFAAS(AlgoritmoPuntaje):
    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]:
        if not resultados:
            return {}
        if disciplina.es_tiempo():
            return _calcular_tiempo(resultados)
        return _calcular_distancia(resultados)


def _calcular_distancia(resultados: list[ResultadoFinal]) -> dict[UUID, Decimal]:
    ...

def _calcular_tiempo(resultados: list[ResultadoFinal]) -> dict[UUID, Decimal]:
    ...
```

**Usar la opción que resulte en LCOM ≤ 1 según DesignReviewer.** Si ambas opciones dejan LCOM=2, documentar como falso positivo y registrar en BL-006.

### Tarea 2 — Corregir hallazgos CodeGuard (CG-01/03/04/05)

| | |
|---|---|
| **Precondición** | CodeGuard reporta E501 en 4 líneas y un `import os` sin uso |
| **Postcondición** | `codeguard src/` no reporta E501 ni imports huérfanos en esos archivos |
| **Invariante** | `black src/ tests/` y `isort src/ tests/` pasan sin cambios adicionales |

```bash
# Identificar archivos con E501:
codeguard src/ 2>&1 | grep "E501"

# Aplicar formato:
black src/ tests/
isort src/ tests/

# Verificar import os huérfano — buscar en los sospechosos:
# (resultados/api/router.py importa `os` — verificar si se usa)
grep -n "import os" src/resultados/api/router.py
grep -n "\bos\." src/resultados/api/router.py

# Si `os` no aparece en uso, eliminar el import
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.4 — AlgoritmoPuntajeFAAS refactoring + CodeGuard limpio

  Scenario: DesignReviewer no reporta LCOM elevado en AlgoritmoPuntajeFAAS
    Given los cambios de esta US aplicados
    When se ejecuta designreviewer sobre src/
    Then no hay hallazgos DR-02 en resultados/domain/services/algoritmo_faas.py

  Scenario: Resultados de cálculo no cambian
    Given un conjunto de resultados de disciplina de distancia (DYN)
    When se calcula con AlgoritmoPuntajeFAAS antes y después del refactoring
    Then los puntos por atleta son idénticos

  Scenario: Resultados de cálculo STA no cambian
    Given un conjunto de resultados de disciplina de tiempo (STA)
    When se calcula con AlgoritmoPuntajeFAAS antes y después del refactoring
    Then los puntos por atleta son idénticos

  Scenario: CodeGuard no reporta E501 ni imports huérfanos
    Given los cambios de esta US aplicados
    When se ejecuta codeguard src/
    Then no hay hallazgos CG-01/03/04/05 pendientes

  Scenario: black e isort no generan cambios
    Given los cambios de esta US aplicados
    When se ejecuta black --check src/ tests/ && isort --check src/ tests/
    Then el exit code es 0
```

---

## Notas de implementación

- `AlgoritmoPuntaje` es el port abstracto — verificar que la firma de `calcular()` no cambia
- `_es_valido` es un método estático que ambos paths usan; si se extraen los paths a funciones de módulo, mover `_es_valido` también a función de módulo
- `_redondear` ya es función de módulo — consistente con la extracción propuesta
- Ejecutar `pytest tests/unit/resultados/ tests/integration/resultados/` antes y después para verificar
- El dispatch dict con `getattr` puede confundir a mypy — preferir la opción de extraer a funciones de módulo si el typing es problemático

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — DR-02 · CG-01/03/04/05
- Código: `src/resultados/domain/services/algoritmo_faas.py`
- Port: `src/resultados/domain/ports/algoritmo_puntaje.py`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
