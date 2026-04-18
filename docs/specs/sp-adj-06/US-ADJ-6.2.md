# US-ADJ-6.2: Eliminar ciclo ADP — `reconstituir_performance` como classmethod

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero mover `reconstituir_performance()` al aggregate `Performance` como classmethod
para eliminar el ciclo de dependencias acíclicas (ADP) detectado por ArchitectAnalyst
entre `performance.py` y `performance_state.py`.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate Root | `Performance` | Registra el ciclo de vida de una performance de apnea |
| Módulo helper | `performance_state` | Funciones `apply_*` para reconstituir Performance desde eventos |

### Hallazgo que origina esta US

ArchitectAnalyst BL-004 detectó un ciclo ADP:

```
competencia.domain.aggregates.performance
  → competencia.domain.aggregates.performance_state
    → competencia.domain.aggregates.performance   ← ciclo
```

La causa: `performance_state.py` contiene `reconstituir_performance()`, una función
factory que necesita instanciar `Performance`. Para evitar el ciclo al cargar el módulo,
usa un lazy import dentro del cuerpo de la función:

```python
# performance_state.py — línea 33
def reconstituir_performance(events: list[dict]) -> "Performance":
    from competencia.domain.aggregates.performance import Performance
    performance = Performance(...)
```

El runtime no falla porque el lazy import resuelve el ciclo en tiempo de ejecución,
pero el ciclo existe a nivel de código y ArchitectAnalyst lo detecta como violación ADP.

### Por qué es importante resolverlo

Una función factory de un aggregate (`reconstituir_performance`) pertenece al aggregate,
no a un módulo helper externo. El aggregate es quien sabe cómo reconstituirse a sí mismo
desde su stream de eventos — es una responsabilidad intrínseca del aggregate root en
Event Sourcing.

---

## Especificación del comportamiento

### Precondición

- `performance_state.py` contiene `reconstituir_performance(events)` con un lazy import de `Performance`
- ArchitectAnalyst reporta un ciclo en `competencia/domain/aggregates/`

### Cambio propuesto

Mover `reconstituir_performance` como `Performance.reconstituir(events)` classmethod:

```python
# competencia/domain/aggregates/performance.py
@classmethod
def reconstituir(cls, events: list[dict[str, Any]]) -> "Performance":
    if not events:
        raise ValueError("No se puede reconstituir Performance sin eventos")
    performance = cls.__new__(cls)
    performance._pendientes = []
    for event in events:
        performance_state.apply_stored(performance, event)
    return performance
```

`performance_state.py` queda solo con las funciones `apply_*` que reciben
`performance: Performance` como parámetro — sin necesidad de instanciar, sin ciclo inverso.

### Postcondición

- `performance_state.py` no importa `Performance` en ninguna forma (ni lazy, ni TYPE_CHECKING)
- `Performance.reconstituir(events)` existe y reconstituye el aggregate correctamente
- Todos los llamadores de `reconstituir_performance(events)` usan `Performance.reconstituir(events)`
- `architectanalyst src/` reporta 0 ciclos en `competencia/domain/aggregates/`

### Invariante

> Las funciones factory de un aggregate deben ser classmethods del aggregate, no
> funciones externas que importan de vuelta al aggregate.

---

## Criterios de aceptación

```gherkin
Feature: Performance sin ciclo ADP en su módulo helper

  Scenario: Performance se reconstituye correctamente desde su classmethod
    Given un stream de eventos de una performance completa (AP → llamada → resultado → tarjeta)
    When se ejecuta Performance.reconstituir(events)
    Then el aggregate reconstituido tiene el estado final correcto
    And los eventos pendientes están vacíos (no se emiten nuevos eventos)

  Scenario: performance_state no importa Performance
    Given el módulo performance_state está cargado
    Then no hay ningún import de Performance en performance_state
    And architectanalyst no reporta ciclos en competencia/domain/aggregates/

  Scenario: Los llamadores existentes funcionan con el nuevo classmethod
    Given un repositorio de performances con eventos persistidos
    When el repositorio carga una performance (internamente usa reconstituir)
    Then la performance tiene el estado correcto para responder comandos
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — es un refactor de responsabilidades dentro de la misma capa de dominio

**Capa(s) afectadas:**
- [x] Domain (`competencia/domain/aggregates/performance.py` + `performance_state.py`)
- [x] Infrastructure (repositorios que llamen a `reconstituir_performance()`)

---

## Notas de implementación

1. Buscar todos los llamadores de `reconstituir_performance(events)` con grep antes de cambiar.
2. El nuevo classmethod puede importar `performance_state` a nivel de módulo (sin ciclo):
   `performance.py` → `performance_state.py` ya existe; solo se elimina la vuelta.
3. Mantener los tests existentes de reconstituir como red de seguridad — no deben cambiar.
4. Ejecutar `architectanalyst src/ --sprint-id BL-004` al final para confirmar 0 ciclos.

---

*Spec creada: 2026-04-16 — AA-01 de revisión ArchitectAnalyst BL-004*
