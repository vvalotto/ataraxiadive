# US-ADJ-1.2: Refactor ajustar_grilla — Extraer helpers OT y swap

**Estado**: `Done`
**Sprint**: SP-ADJ-01 — Ajuste Técnico Post-SP2
**Issues**: ADJ-01
**Bounded Context**: `competencia`
**Capas afectadas**: `domain/aggregates/competencia.py`

---

## Descripción

Como **desarrollador del BC Competencia**,
quiero **extraer la lógica de recálculo de OTs y el algoritmo de swap de posiciones de `ajustar_grilla`**
para **eliminar la triplicación de lógica y reducir el método de 127 a ~50 líneas**.

---

## Contexto de la deuda

`Competencia.ajustar_grilla` tiene 127 líneas y mezcla tres responsabilidades:

1. Validaciones de precondición (correcto)
2. Algoritmo de swap de posiciones con desplazamiento del ocupante (lógica extraíble)
3. Recálculo de OTs tras cambio de posición (duplicado en tres lugares)

**Triplicación del cálculo de OT:**
```python
# generar_grilla (líneas 183–205):
ot_atleta = ot_inicio + timedelta(minutes=(posicion - 1) * self._intervalo.minutos)

# ajustar_grilla (líneas 318–333):
ot_programado=ot_inicio + timedelta(minutes=(e.posicion - 1) * self._intervalo.minutos)

# _apply_grilla_de_salida_ajustada (líneas 524–538):
ot_programado=ot_inicio + timedelta(minutes=(e.posicion - 1) * self._intervalo.minutos)
```

El patrón modular ya existe en el mismo archivo: `_ordenar_performances` y `_calcular_andarivel`
son funciones de módulo que encapsulan lógica auxiliar.

---

## Especificación

### Nuevas funciones de módulo

| | |
|---|---|
| **Precondición** | `ajustar_grilla` tiene 127 líneas con lógica duplicada y algoritmo de swap inline |
| **Postcondición** | `ajustar_grilla` ≤ 60 líneas; lógica de OT y swap encapsulada en helpers |
| **Invariante** | Comportamiento observable idéntico; todos los tests pasan sin modificación |

```python
def _recalcular_ots(
    grilla: list[EntradaGrilla],
    ot_inicio: datetime,
    intervalo: IntervaloDisciplina,
) -> list[EntradaGrilla]:
    """Recalcula los OTs de todas las entradas según posición e intervalo (P-02)."""

def _aplicar_swap_posicion(
    grilla_mutable: dict[UUID, EntradaGrilla],
    performance_id: UUID,
    posicion_nueva: int,
    cambios_payload: list[dict],
) -> None:
    """Aplica el cambio de posición con desplazamiento del ocupante si corresponde."""
```

### Uso en `ajustar_grilla` post-refactor

```
ajustar_grilla():
  1. Validaciones (sin cambio)
  2. Por cada cambio:
     - Si campo == "posicion": _aplicar_swap_posicion(...)
     - Si campo == "andarivel": actualizar andarivel (sin cambio)
  3. Si hubo cambio de posición: nueva_grilla = _recalcular_ots(...)
  4. Emitir evento (sin cambio)
```

### Uso en `_apply_grilla_de_salida_ajustada`

Reemplazar el bloque de recálculo de OTs inline por llamada a `_recalcular_ots`.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-1.2 — Refactor ajustar_grilla

  Scenario: ajustar posición recalcula OTs correctamente
    Given una competencia con grilla de 3 atletas e intervalo 10 minutos
    And ot_inicio = 10:00
    When se ajusta la posición del atleta B de posición 2 a posición 1
    Then atleta B tiene OT 10:00 (posición 1)
    And atleta A (desplazado a posición 2) tiene OT 10:10
    And atleta C mantiene OT 10:20

  Scenario: ajustar andarivel no recalcula OTs
    Given una competencia con grilla de 3 atletas
    When se ajusta el andarivel del atleta A de 1 a 2
    Then los OTs de todos los atletas no cambian

  Scenario: reconstitución desde eventos produce el mismo estado
    Given una Competencia con eventos GrillaDeSalidaGenerada y GrillaDeSalidaAjustada
    When se llama a Competencia.reconstitute(events)
    Then el estado de la grilla es idéntico al producido por los comandos directos

  Scenario: ajustar_grilla tiene ≤ 60 líneas tras el refactor
    Given el archivo competencia.py refactorizado
    Then el método ajustar_grilla tiene como máximo 60 líneas

  Scenario: no existe triplicación del cálculo de OT
    Given el archivo competencia.py refactorizado
    Then la expresión "timedelta(minutes=" aparece solo en _recalcular_ots
```

---

## Notas de implementación

- Los tests existentes de `ajustar_grilla` deben pasar sin modificación — son el contrato.
- `_recalcular_ots` recibe la grilla ya ordenada por posición.
- `_recalcular_ots` también debe usarse en `_apply_grilla_de_salida_ajustada` para eliminar
  la tercera duplicación.
- `_aplicar_swap_posicion` modifica `grilla_mutable` in-place y agrega entradas a
  `cambios_payload` — misma semántica que el código inline actual.

---

## Referencias

- Análisis: `.work/revision-sp2/02-analisis-aggregates.md` (H-E)
- Plan: `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`

---

*Redactado: 2026-03-28 — SP-ADJ-01*
