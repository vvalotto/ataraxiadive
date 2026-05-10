# US-6.4.1: Romper ciclo ADP en `competencia/domain/aggregates`

**Estado**: `Pending`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgo**: AA-01
**Bounded Context**: `competencia`
**Capas afectadas**:
- `competencia/domain/aggregates/`

---

## Descripción

Como **desarrollador manteniendo el BC Competencia**,
quiero **que el paquete `competencia/domain/aggregates` no contenga ciclos de dependencia**
para **cumplir el Principio de Dependencias Acíclicas (ADP) y permitir que ArchitectAnalyst informe 0 DependencyCycles**.

---

## Contexto del Hallazgo

### AA-01 — DependencyCycle=2 CRITICAL

ArchitectAnalyst reporta `DependencyCycle=2 CRITICAL` en `competencia/domain/aggregates` desde BL-004, sin mejora en BL-005. Es el único hallazgo CRITICAL pendiente en el BC Competencia tras el cierre de SP5.

El paquete contiene:
- `competencia.py` — aggregate `Competencia`, importa `GrillaDeSalida` y `performance_events`
- `performance.py` — aggregate `Performance`, importa `performance_state` como módulo
- `performance_state.py` — helpers de reconstitución, usa `TYPE_CHECKING` para `Performance`
- `performance_events.py` — factories de eventos, importa value objects y domain events
- `__init__.py` — exporta `Competencia` y `Performance`

El `__init__.py` importa ambos aggregates al nivel de paquete. `performance.py` hace `from competencia.domain.aggregates import performance_state`, lo que puede activar el `__init__.py` y crear un ciclo de importación en el grafo estático que detecta ArchitectAnalyst (aunque en runtime Python lo resuelve con `TYPE_CHECKING`).

---

## Especificación

### Tarea 1 — Diagnosticar el ciclo exacto

| | |
|---|---|
| **Precondición** | ArchitectAnalyst reporta `DependencyCycle=2` en el módulo |
| **Postcondición** | Se conoce qué par(es) de módulos forman el ciclo |
| **Invariante** | No modificar código en esta tarea |

Ejecutar ArchitectAnalyst con output detallado para identificar los módulos exactos involucrados:

```bash
architectanalyst src/ --sprint-id BL-006 --format json | \
  python -c "import sys,json; d=json.load(sys.stdin); \
  [print(m) for m in d.get('dependency_cycles',[])]"
```

Candidatos probables basados en lectura de código:
- `aggregates/__init__.py` → `performance.py` → `aggregates` (package re-import)
- `competencia.py` → `performance_events.py` → (transitivo)

### Tarea 2 — Romper el ciclo

| | |
|---|---|
| **Precondición** | Ciclo identificado en Tarea 1 |
| **Postcondición** | El grafo de dependencias estático entre módulos dentro de `aggregates/` es acíclico |
| **Invariante** | No cambiar la API pública de `Competencia` ni `Performance`; todos los tests existentes siguen pasando |

Estrategias según ciclo encontrado:

**Si el ciclo es vía `__init__.py`:**
Limpiar el `__init__.py` — no reexportar aggregates ahí (evitar importación implícita del paquete):
```python
# aggregates/__init__.py — vaciar o solo dejar documentación
"""Aggregates del BC Competencia."""
```
Y actualizar todos los importadores para usar paths directos:
```python
# antes: from competencia.domain.aggregates import Competencia
# después: from competencia.domain.aggregates.competencia import Competencia
```

**Si el ciclo es entre `performance.py` y `performance_state.py`:**
Convertir la importación de módulo en importación explícita de funciones con `TYPE_CHECKING`:
```python
# performance.py — reemplazar:
from competencia.domain.aggregates import performance_state
# por:
if TYPE_CHECKING:
    from competencia.domain.aggregates import performance_state
```
Y mover las llamadas a `performance_state.*` a métodos con importación local.

**Si el ciclo es entre `competencia.py` y `performance.py` vía entidades compartidas:**
Extraer el tipo compartido (`GrillaDeSalida`, `GrillaEntry`) a `competencia/domain/value_objects/` o `competencia/domain/entities/` sin dependencia hacia arriba.

### Tarea 3 — Verificar

| | |
|---|---|
| **Precondición** | Cambios aplicados en Tarea 2 |
| **Postcondición** | `architectanalyst` reporta `DependencyCycle=0` en `competencia/domain/aggregates` |
| **Invariante** | Suite completa sigue pasando: `pytest tests/` |

```bash
pytest tests/unit/competencia/ tests/integration/competencia/ tests/features/ -q
architectanalyst src/ --sprint-id BL-006 --format json
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.1 — Ciclo ADP eliminado en competencia/domain/aggregates

  Scenario: ArchitectAnalyst reporta 0 ciclos en el módulo
    Given los cambios de esta US aplicados
    When se ejecuta architectanalyst sobre src/
    Then el reporte indica DependencyCycle=0 en competencia/domain/aggregates
    And should_block=false

  Scenario: Suite de tests no regresiona
    Given los cambios de esta US aplicados
    When se ejecutan todos los tests
    Then todos los tests pasan (sin nuevas fallas)

  Scenario: Imports directos de aggregates siguen funcionando
    Given la API pública de Competencia y Performance
    When otro módulo hace `from competencia.domain.aggregates.competencia import Competencia`
    Then la importación funciona sin error
```

---

## Notas de implementación

- Prioridad: alta — único hallazgo CRITICAL en `competencia` BC
- Impacto de riesgo: bajo si se usa el enfoque de `TYPE_CHECKING` — es un cambio de importaciones, no de lógica
- El `__init__.py` vacío puede requerir actualizar tests o fixtures que importan `from competencia.domain.aggregates import Competencia` — buscar con `grep -rn "from competencia.domain.aggregates import" tests/`
- Si el ciclo no es reproducible con el ArchitectAnalyst local, documentar el hallazgo como falso positivo y registrar en el BL-006 con justificación

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — AA-01
- BL-004/BL-005: `docs/contexto/BL-004-architectanalyst.md` · `docs/contexto/BL-005-architectanalyst.md`
- Código: `src/competencia/domain/aggregates/`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
