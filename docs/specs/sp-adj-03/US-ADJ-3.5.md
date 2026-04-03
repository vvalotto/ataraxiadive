# US-ADJ-3.5: Limpiar imports en ports de Competencia → `shared.domain`

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: ADJ-06
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/ports/disciplina_descriptor_port.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **actualizar `disciplina_descriptor_port.py` para importar desde `shared.domain.value_objects`**
para **que el port de dominio de Competencia use la fuente canónica de `Disciplina` y `DisciplinaDescriptor`**.

---

## Contexto de la deuda

### ADJ-06 — Port de Competencia importa sus propios value objects en lugar de `shared`

`competencia/domain/ports/disciplina_descriptor_port.py`:

```python
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
```

`Disciplina` y `DisciplinaDescriptor` fueron movidos a `shared/domain/value_objects/`
en SP-ADJ-02 (US-ADJ-2.6). Los archivos en `competencia/domain/value_objects/` son
re-exports. El port debería apuntar directamente a `shared`, no al re-export.

Es un issue cosmético — el comportamiento es idéntico — pero mantiene una dependencia
innecesaria sobre el re-export de Competencia.

---

## Especificación

### Precondición

```python
# competencia/domain/ports/disciplina_descriptor_port.py
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
```

### Postcondición

```python
# competencia/domain/ports/disciplina_descriptor_port.py
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
```

### Invariantes

- `INV-ADJ-3.5-1`: el contrato del port no cambia — misma firma, mismos tipos
- `INV-ADJ-3.5-2`: todos los tests pasan sin modificación
- `INV-ADJ-3.5-3`: no se crean nuevas dependencias — solo se actualiza el import path

---

## Criterios de aceptación

```gherkin
Scenario: disciplina_descriptor_port.py importa desde shared.domain
  Given el archivo competencia/domain/ports/disciplina_descriptor_port.py
  Then no contiene imports desde competencia.domain.value_objects
  And importa Disciplina desde shared.domain.value_objects.disciplina
  And importa DisciplinaDescriptor desde shared.domain.value_objects.disciplina_descriptor

Scenario: todos los tests pasan tras el cambio
  Given el cambio de import aplicado
  When se ejecuta pytest tests/
  Then 100% de los tests pasan
```

---

## Notas de implementación

- Cambio de una o dos líneas. Riesgo prácticamente nulo.
- Verificar que no haya otros archivos en `competencia/domain/ports/` con el mismo patrón.
- Puede hacerse en el mismo PR que US-ADJ-3.1 si se quiere agrupar los cambios de `competencia/domain/`.

---

## Referencias

- US-ADJ-2.6: movió `Disciplina` y `DisciplinaDescriptor` a `shared/domain/`
- Issues consolidados: `.work/revision-sp3/07-issues-consolidados.md` (ADJ-06)
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
