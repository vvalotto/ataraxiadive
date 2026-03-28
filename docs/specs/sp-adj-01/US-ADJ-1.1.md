# US-ADJ-1.1: Domain Cleanup — Performance property + OCP Competencia + snake_case

**Estado**: `Done`
**Sprint**: SP-ADJ-01 — Ajuste Técnico Post-SP2
**Issues**: ADJ-03 · ADJ-06 · ADJ-08
**Bounded Context**: `competencia`
**Capas afectadas**: `domain/aggregates/`

---

## Descripción

Como **desarrollador del BC Competencia**,
quiero **limpiar tres deudas menores en los aggregates de dominio**
para **eliminar violaciones de encapsulación, inconsistencias de patrón y convenciones de naming**.

---

## Contexto de la deuda

### ADJ-03 — Atributo privado `_ot_programado` accedido desde infraestructura

`AndarivelesActivosAdapter` accede directamente a `perf._ot_programado` con `# noqa: SLF001`.
El aggregate `Performance` no expone `ot_programado` como propiedad pública.

```python
# infrastructure/repositories/andariveles_activos_adapter.py línea 61:
ot: datetime | None = perf_activa._ot_programado  # noqa: SLF001  ← viola encapsulación
```

### ADJ-06 — `_apply_stored` en `Competencia` recrea el dict de handlers en cada llamada

`Performance` inicializa `_event_handlers` en `__init__` (documentado como OCP).
`Competencia` recrea un dict local `_handlers` en cada invocación de `_apply_stored`.
Inconsistencia de patrón y overhead innecesario en reconstituciones largas.

### ADJ-08 — `registrarAP` usa camelCase en lugar de snake_case

```python
# performance.py:
def registrarAP(self, valor, unidad):  ← viola PEP8 y convención del proyecto
```
Todos los demás métodos del aggregate usan snake_case.

---

## Especificación

### ADJ-03: agregar `@property ot_programado` en Performance

| | |
|---|---|
| **Precondición** | `Performance._ot_programado` accedido directamente desde `AndarivelesActivosAdapter` con noqa |
| **Postcondición** | `Performance.ot_programado` es una propiedad pública; el adapter usa `perf.ot_programado` sin noqa |
| **Invariante** | Nada externo accede a `_ot_programado` directamente |

```python
@property
def ot_programado(self) -> datetime | None:
    """OT programado, disponible tras ser llamado. None si aún no fue llamado."""
    return self._ot_programado
```

### ADJ-06: mover `_handlers` dict a `__init__` en Competencia

| | |
|---|---|
| **Precondición** | `_apply_stored` recrea el dict en cada llamada |
| **Postcondición** | `self._event_handlers` inicializado en `__init__`, igual que `Performance` |
| **Invariante** | Comportamiento de reconstitución idéntico al actual; todos los tests pasan |

### ADJ-08: renombrar `registrarAP` → `registrar_ap`

| | |
|---|---|
| **Precondición** | `registrarAP` viola PEP8 y la convención snake_case del proyecto |
| **Postcondición** | `registrar_ap` en aggregate + todos los sitios de llamada actualizados |
| **Invariante** | Misma firma de parámetros; ningún test roto por cambio de nombre |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-1.1 — Domain cleanup

  Scenario: ot_programado accesible como propiedad pública
    Given una Performance en estado Llamada con ot_programado asignado
    When se accede a performance.ot_programado
    Then retorna el datetime del OT programado sin acceder a atributos privados

  Scenario: AndarivelesActivosAdapter usa propiedad pública
    Given el adapter reconstruye performances desde el Event Store
    When proyecta el estado de andariveles
    Then no hay ningún acceso a _ot_programado (sin noqa SLF001)

  Scenario: Competencia reconstitución con dict en __init__
    Given un stream de 10 eventos de Competencia
    When se llama a Competencia.reconstitute(events)
    Then el estado final es idéntico al actual
    And _event_handlers se inicializa una sola vez en __init__

  Scenario: registrar_ap acepta los mismos parámetros que registrarAP
    Given una Performance nueva
    When se llama a performance.registrar_ap(valor=Decimal("100"), unidad=Metros)
    Then emite APRegistrado con los datos correctos
    And el estado transiciona a AnunciadaAP
```

---

## Notas de implementación

- `registrar_ap` debe actualizarse en todos los handlers que lo llaman (`RegistrarAPHandler`)
  y en todos los tests que lo referencian.
- El `# noqa: SLF001` en `andariveles_activos_adapter.py` debe eliminarse junto con el refactor.
- El dict `_event_handlers` en `Competencia.__init__` debe seguir el mismo patrón que `Performance`:
  usar `self._event_handlers` y eliminar el dict local en `_apply_stored`.

---

## Referencias

- Análisis: `.work/revision-sp2/02-analisis-aggregates.md` (H-F)
- Análisis: `.work/revision-sp2/04-analisis-infra-queries.md` (H-J)
- Plan: `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`

---

*Redactado: 2026-03-28 — SP-ADJ-01*
