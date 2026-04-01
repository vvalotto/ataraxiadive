# US-ADJ-3.2: Extraer `TarjetaAsignacion` como Value Object

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/value_objects/` · `competencia/domain/aggregates/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **extraer las invariantes de asignación de tarjeta a un Value Object `TarjetaAsignacion`**
para **resolver el DataClumps en `Performance.asignar_tarjeta()` y co-ubicar las reglas INV-P-11 y RF-EJ-07 con los datos que gobiernan**.

---

## Contexto de la deuda

DesignReviewer reporta DataClumps en `Performance`: los campos `(tipo, motivo, distancia_blackout)`
siempre viajan juntos y sus invariantes están dispersas en el cuerpo de `asignar_tarjeta()`.

### Código actual en `Performance.asignar_tarjeta()`

```python
def asignar_tarjeta(
    self,
    tipo: TipoTarjeta,
    asignada_por: str,
    motivo: str | None = None,
    distancia_blackout: Decimal | None = None,
) -> None:
    if self._estado != EstadoPerformance.ResultadoRegistrado:
        raise EstadoInvalidoParaAsignarTarjeta(...)

    # INV-P-11 — disperso en el cuerpo del método
    if tipo in (TipoTarjeta.Amarilla, TipoTarjeta.Roja) and not motivo:
        raise MotivoObligatorio(...)

    # RF-EJ-07 — disperso en el cuerpo del método
    if motivo == "black-out" and (distancia_blackout is None or distancia_blackout <= 0):
        raise DistanciaBlackoutObligatoria(...)

    event = TarjetaAsignada(...)
    ...
```

El problema: INV-P-11 y RF-EJ-07 son invariantes del concepto "asignación de tarjeta",
no del ciclo de vida de Performance. `Performance` no debería conocer las reglas de qué
constitutye una tarjeta válida.

---

## Especificación

### Postcondición

```
competencia/domain/value_objects/tarjeta_asignacion.py   ← NUEVO
competencia/domain/aggregates/performance.py              ← MODIFICADO
```

### `TarjetaAsignacion` value object

```python
class TarjetaAsignacion:
    """Value Object que encapsula la asignación de tarjeta con sus invariantes.

    INV-P-11: Tarjeta Amarilla o Roja requieren motivo obligatorio.
    RF-EJ-07: motivo "black-out" requiere distancia_blackout > 0.

    Inmutable: una vez creado, tipo/motivo/distancia_blackout no cambian.
    """
    def __init__(
        self,
        tipo: TipoTarjeta,
        motivo: str | None,
        distancia_blackout: Decimal | None,
    ) -> None:
        if tipo in (TipoTarjeta.Amarilla, TipoTarjeta.Roja) and not motivo:
            raise MotivoObligatorio(
                f"Tarjeta {tipo} requiere motivo obligatorio (INV-P-11)"
            )
        if motivo == "black-out" and (distancia_blackout is None or distancia_blackout <= 0):
            raise DistanciaBlackoutObligatoria(
                "Tarjeta roja por black-out requiere distancia_blackout > 0 (RF-EJ-07)"
            )
        self.tipo = tipo
        self.motivo = motivo
        self.distancia_blackout = distancia_blackout
```

### `Performance.asignar_tarjeta()` post-refactor

```python
def asignar_tarjeta(
    self,
    tipo: TipoTarjeta,
    asignada_por: str,
    motivo: str | None = None,
    distancia_blackout: Decimal | None = None,
) -> None:
    if self._estado != EstadoPerformance.ResultadoRegistrado:
        raise EstadoInvalidoParaAsignarTarjeta(...)

    ta = TarjetaAsignacion(tipo, motivo, distancia_blackout)  # valida INV-P-11 + RF-EJ-07

    event = TarjetaAsignada(
        ..., tipo=ta.tipo.value, motivo=ta.motivo,
        distancia_blackout=str(ta.distancia_blackout) if ta.distancia_blackout else None,
    )
    self._tarjeta = ta.tipo
    self._distancia_blackout = ta.distancia_blackout
    self._estado = EstadoPerformance.Ejecutada
    self._record(event)
```

### Impacto en métricas

| Métrica | Antes | Después |
|---------|-------|---------|
| `asignar_tarjeta` CC | ~5 | ~2 |
| Performance WMC | ~42 | ~40 |
| DataClumps | 2/2 | 0/2 |
| Archivos nuevos | — | 1 |
| Tests existentes | sin cambio | sin cambio |

---

## Criterios de aceptación

```gherkin
Scenario: INV-P-11 validada en TarjetaAsignacion
  Given un TarjetaAsignacion con tipo=Amarilla y sin motivo
  When se construye el VO
  Then lanza MotivoObligatorio

Scenario: RF-EJ-07 validada en TarjetaAsignacion
  Given un TarjetaAsignacion con motivo="black-out" y distancia_blackout=None
  When se construye el VO
  Then lanza DistanciaBlackoutObligatoria

Scenario: asignar_tarjeta en Performance delega validacion al VO
  Given una Performance en estado ResultadoRegistrado
  When se llama asignar_tarjeta con tipo=Roja y sin motivo
  Then lanza MotivoObligatorio (proveniente del VO)
  And la Performance no cambia de estado
```

---

## Notas de implementación

- Los tests unitarios de `asignar_tarjeta` existentes no requieren cambios: las mismas
  excepciones, desde los mismos inputs, con el mismo comportamiento externo.
- `TarjetaAsignacion` no requiere `__eq__` ni `__hash__` especiales — Python los
  hereda de `object`. Si se necesita comparación en el futuro, es una mejora separada.
- Esta extracción es **independiente de US-ADJ-3.1** — puede implementarse en cualquier
  orden.

---

## Referencias

- Análisis: sesión 2026-04-01 — análisis DataClumps Performance
- DesignReviewer warnings: LongMethod + DataClumps en `performance.py`
- US-ADJ-3.1: extracción de `GrillaDeSalida` (puede ejecutarse en el mismo PR)
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-01 — SP-ADJ-03*
