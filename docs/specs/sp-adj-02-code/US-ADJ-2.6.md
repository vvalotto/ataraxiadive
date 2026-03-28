# US-ADJ-2.6: Mover `Disciplina`, `DisciplinaDescriptor`, `UnidadMedida` a `shared/domain/`

**Estado**: `Done`
**Sprint**: SP-ADJ-02-code — Ajuste Técnico Post-BL-002
**Issues**: B-01 · B-02
**Bounded Context**: `shared` · `competencia` · `resultados`
**Capas afectadas**: `shared/domain/value_objects/` · `competencia/domain/value_objects/` · todos los imports en `resultados/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **mover `Disciplina`, `DisciplinaDescriptor` y `UnidadMedida` al paquete `shared/domain/value_objects/`**
para **eliminar las violaciones cross-BC donde `resultados/domain/` importa tipos del dominio de `competencia`**.

---

## Contexto de la deuda

### B-01 — `resultados/domain/` importa tipos de `competencia.domain`

```python
# resultados/domain/aggregates/ranking_competencia.py
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor

# resultados/domain/ports/resultados_competencia_port.py
from competencia.domain.value_objects.disciplina import Disciplina
```

Violación de la Regla de Oro (§6 CLAUDE.md): el dominio de un BC no puede importar
del dominio de otro BC. `Disciplina` es un tipo transversal del deporte — no pertenece
al Core Domain de Competencia, sino al vocabulario compartido de todos los BCs.

### B-02 — `resultados/application/` importa de `competencia.infrastructure`

```python
# resultados/application/commands/calcular_ranking.py
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
```

El adapter de DisciplinaDescriptor vive en `competencia.infrastructure` pero es consumido
por la application layer de `resultados`. Doble violación: cross-BC + hexagonal.

### Archivos violadores (6 en total)

| Archivo | Viola |
|---------|-------|
| `resultados/domain/aggregates/ranking_competencia.py` | B-01 |
| `resultados/domain/ports/resultados_competencia_port.py` | B-01 |
| `resultados/application/commands/calcular_ranking.py` | B-01 + B-02 |
| `resultados/application/queries/obtener_ranking.py` | B-01 |
| `resultados/api/router.py` | B-01 |
| `resultados/infrastructure/repositories/resultados_competencia_adapter.py` | B-01 |

---

## Especificación

### Precondición

| Tipo | Definición actual |
|------|------------------|
| `Disciplina` | `src/competencia/domain/value_objects/disciplina.py` |
| `DisciplinaDescriptor` | `src/competencia/domain/value_objects/disciplina_descriptor.py` |
| `UnidadMedida` | `src/competencia/domain/value_objects/unidad_medida.py` |
| Imports resultados | 6 archivos importan desde `competencia.domain` o `competencia.infrastructure` |

### Postcondición

| Tipo | Nueva ubicación canónica |
|------|--------------------------|
| `Disciplina` | `src/shared/domain/value_objects/disciplina.py` |
| `DisciplinaDescriptor` | `src/shared/domain/value_objects/disciplina_descriptor.py` |
| `UnidadMedida` | `src/shared/domain/value_objects/unidad_medida.py` |
| `competencia/domain/value_objects/disciplina.py` | Re-exporta desde `shared.domain.value_objects` |
| `competencia/domain/value_objects/disciplina_descriptor.py` | Re-exporta desde `shared.domain.value_objects` |
| `competencia/domain/value_objects/unidad_medida.py` | Re-exporta desde `shared.domain.value_objects` |
| Imports resultados | Los 6 archivos importan desde `shared.domain.value_objects` |

### Invariantes

- `INV-ADJ-2.6-1`: El comportamiento de `Disciplina`, `DisciplinaDescriptor` y `UnidadMedida` es idéntico
- `INV-ADJ-2.6-2`: Los ~35 imports internos de `competencia/` no se rompen (via re-export)
- `INV-ADJ-2.6-3`: `pytest tests/` — 100% pass sin modificar tests
- `INV-ADJ-2.6-4`: `shared/domain/` no importa nada de `competencia/` ni de `resultados/`

---

## Plan de implementación

### Paso 1 — Crear los tres archivos en `shared/domain/value_objects/`

Copiar el contenido real (no referencia) de cada archivo:

```
shared/domain/value_objects/disciplina.py         ← contenido de competencia/domain/value_objects/disciplina.py
shared/domain/value_objects/unidad_medida.py      ← contenido de competencia/domain/value_objects/unidad_medida.py
shared/domain/value_objects/disciplina_descriptor.py  ← contenido, actualizar import de UnidadMedida
```

`DisciplinaDescriptor` importa `UnidadMedida` y `Disciplina` — actualizar esos imports
para que apunten a `shared.domain.value_objects`.

### Paso 2 — Re-exportar desde los archivos originales en `competencia/`

```python
# competencia/domain/value_objects/disciplina.py — reemplazar contenido por:
"""Re-export de Disciplina desde shared.domain (fuente canónica)."""
from shared.domain.value_objects.disciplina import Disciplina

__all__ = ["Disciplina"]
```

Idem para `unidad_medida.py` y `disciplina_descriptor.py`.

### Paso 3 — Actualizar los 6 archivos de `resultados/`

Cambiar todos los imports desde `competencia.domain` o `competencia.infrastructure`
por imports desde `shared.domain.value_objects`.

### Paso 4 — Actualizar `__init__.py` de shared

```python
# shared/domain/value_objects/__init__.py
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from shared.domain.value_objects.unidad_medida import UnidadMedida

__all__ = ["Disciplina", "DisciplinaDescriptor", "UnidadMedida"]
```

### Paso 5 — Actualizar `__init__.py` de competencia value_objects

El `__init__.py` de `competencia/domain/value_objects/` ya exporta estos tres tipos.
Verificar que sigue funcionando vía re-export (no requiere cambio si los archivos
originales hacen el re-export correctamente).

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-2.6 — Disciplina en shared/domain/

  Scenario: Disciplina tiene su fuente canónica en shared/domain/
    Given el archivo shared/domain/value_objects/disciplina.py
    Then define la clase Disciplina con los 9 valores (STA, DNF, DYN, DYNB, SPE2X50, CNF, CWT, FIM, VWT)
    And tiene los métodos es_tiempo() y es_distancia()

  Scenario: competencia re-exporta Disciplina para backward compat
    Given el archivo competencia/domain/value_objects/disciplina.py
    Then contiene solo un re-export hacia shared.domain.value_objects
    And from competencia.domain.value_objects.disciplina import Disciplina funciona correctamente

  Scenario: resultados no importa nada de competencia.domain
    Given los 6 archivos de resultados/ que usaban imports cross-BC
    Then ninguno contiene imports desde competencia.domain
    And ninguno contiene imports desde competencia.infrastructure

  Scenario: todos los tests pasan tras la refactorización
    Given el repositorio con los imports actualizados
    When se ejecuta pytest tests/
    Then 100% de los tests pasan sin modificar ningún test

  Scenario: shared/domain/ es puro (no importa de otros BCs)
    Given el paquete shared/domain/value_objects/
    Then ningún archivo importa desde competencia, resultados, torneo, registro, identidad o notificaciones
```

---

## Notas de implementación

- `DisciplinaDescriptor` tiene un `@classmethod para(disciplina: Disciplina)` — verificar
  que el import interno se actualiza correctamente al moverlo a `shared/`.
- El re-export en `competencia/` puede mantenerse en SP-ADJ-02-code y eliminarse en SP3
  cuando se migren los ~35 imports internos. No es deuda nueva — es decisión consciente.
- Si `DisciplinaDescriptorAdapter` (en `competencia/infrastructure/`) también importa
  `DisciplinaDescriptor`, actualizar ese import también.

---

## Referencias

- Regla de Oro: `CLAUDE.md §6`
- ADR-006: `docs/adr/ADR-006-estructura-bc-first.md`
- Revisión: `.work/revision-consistencia.md` (gaps B-01, B-02)
- Plan: `docs/plans/sp-adj-02-code/PLAN-SP-ADJ-02-code.md`

---

*Redactado: 2026-03-28 — SP-ADJ-02-code*
