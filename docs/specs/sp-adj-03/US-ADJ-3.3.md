# US-ADJ-3.3: Refactorizar `app.py` + constante event type en `calcular_overall`

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: ADJ-03 · ADJ-04 · SOLID-04
**Bounded Context**: `src/` (composition root) · `resultados`
**Capas afectadas**: `src/app.py` · `resultados/application/commands/calcular_overall.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **extraer helpers de `app.py` en funciones con nombre y reemplazar el literal `"IntervaloOTConfigurado"` por una constante**
para **mejorar la legibilidad del composition root y eliminar la dependencia de un string mágico en lógica de aplicación**.

---

## Contexto de la deuda

### ADJ-03 + ADJ-04 — `app.py` mezcla composition root con lógica de negocio

`build_on_finalizada_callback` tiene 57 líneas e incluye dos subfunciones auxiliares:
- `_verificar_todas_disciplinas_finalizadas` (15 líneas) — lógica de negocio: "¿todas las disciplinas del torneo finalizaron?"
- `_obtener_disciplinas_torneo` (10 líneas) — consulta al repo de torneo

Estas funciones implementan parte de la política P-09 (disparar CalcularOverall cuando
todas las disciplinas del torneo finalizaron). Esa lógica no debería vivir anónima
dentro de un closure en el composition root.

### SOLID-04 — Literal hardcodeado en `calcular_overall.py`

`resultados/application/commands/calcular_overall.py:76`:

```python
if event["event_type"] != "IntervaloOTConfigurado":
```

El string `"IntervaloOTConfigurado"` es un nombre de evento de dominio de BC Competencia
hardcodeado en la application layer de BC Resultados. Si el nombre del evento cambia,
hay que buscarlo con grep. Viola OCP.

---

## Especificación

### Postcondición — `app.py`

Las tres funciones auxiliares (`build_on_finalizada_callback`, `_verificar_todas_disciplinas_finalizadas`,
`_obtener_disciplinas_torneo`) se mantienen pero con responsabilidades más claras y nombres
que expresen su rol en la política P-09:

- `build_on_finalizada_callback` mantiene la misma firma pero su cuerpo se reduce a
  ensamblar el flujo P-08 + P-09 en ~20 líneas
- `_verificar_todas_disciplinas_finalizadas` y `_obtener_disciplinas_torneo` permanecen
  como helpers de módulo con docstrings explícitos de su rol en P-09
- Ninguna lógica nueva se extrae a otro módulo — el objetivo es legibilidad, no mover código

### Postcondición — `calcular_overall.py`

```python
# Antes (línea 76):
if event["event_type"] != "IntervaloOTConfigurado":

# Después:
_EVENTO_INTERVALO_OT = "IntervaloOTConfigurado"
# ...
if event["event_type"] != _EVENTO_INTERVALO_OT:
```

La constante se define al nivel de módulo en `calcular_overall.py`. No se mueve a un
archivo compartido — el propósito es eliminar el string mágico, no crear acoplamiento
adicional.

### Invariantes

- `INV-ADJ-3.3-1`: el comportamiento de P-08 y P-09 es idéntico antes y después del refactor
- `INV-ADJ-3.3-2`: todos los tests existentes pasan sin modificación
- `INV-ADJ-3.3-3`: `app.py` no importa módulos nuevos

---

## Criterios de aceptación

```gherkin
Scenario: build_on_finalizada_callback tiene menos de 30 líneas
  Given el app.py refactorizado
  Then build_on_finalizada_callback tiene <= 30 líneas
  And _verificar_todas_disciplinas_finalizadas tiene docstring con rol en P-09
  And _obtener_disciplinas_torneo tiene docstring con rol en P-09

Scenario: calcular_overall no contiene string mágico
  Given el archivo resultados/application/commands/calcular_overall.py
  Then no contiene el literal "IntervaloOTConfigurado" sin asignar a constante
  And existe la constante _EVENTO_INTERVALO_OT = "IntervaloOTConfigurado"

Scenario: P-09 sigue disparando Overall cuando todas las disciplinas finalizan
  Given un torneo con 2 disciplinas, ambas en estado Finalizada
  When se dispara el callback on_finalizada para la última
  Then CalcularOverall se ejecuta
  And GET /resultados/{torneo_id}/overall retorna el overall calculado
```

---

## Notas de implementación

- Esta US es de **legibilidad y OCP**, no de extracción estructural. No crear nuevos módulos.
- El cambio en `calcular_overall.py` es de una línea + agregar la constante — riesgo mínimo.
- Los tests de integración E2E (US-3.3.2, US-3.5.3) cubren P-08 y P-09 — sirven como
  regresión automática.

---

## Referencias

- Revisión SP3: `.work/revision-sp3/03-analisis-handlers.md` (ADJ-03, ADJ-04)
- Revisión SOLID: `.work/revision-sp3/05b-revision-solid-sp3.md` (SOLID-04)
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
