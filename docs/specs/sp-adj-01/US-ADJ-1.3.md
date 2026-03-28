# US-ADJ-1.3: Consolidar _build_stream_id en módulo compartido

**Estado**: `Done`
**Sprint**: SP-ADJ-01 — Ajuste Técnico Post-SP2
**Issues**: ADJ-02
**Bounded Context**: `competencia`
**Capas afectadas**: `application/commands/`

---

## Descripción

Como **desarrollador del BC Competencia**,
quiero **consolidar las 11 copias de `_build_stream_id` en un módulo compartido `_stream_ids.py`**
para **garantizar que el formato del stream ID sea una fuente única de verdad**.

---

## Contexto de la deuda

La función `_build_stream_id` está duplicada en 11 archivos de `application/commands/`:

**Performance stream ID** (6 copias idénticas):
```python
# En: registrar_ap.py, llamar_atleta.py, registrar_resultado.py,
#     registrar_dns.py, corregir_resultado.py, asignar_tarjeta.py
def _build_stream_id(competencia_id, participante_id, disciplina) -> str:
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
```

**Competencia stream ID** (5 copias idénticas):
```python
# En: generar_grilla.py, ajustar_grilla.py, confirmar_grilla.py,
#     iniciar_competencia.py, configurar_intervalo_ot.py
def _build_stream_id(competencia_id) -> str:
    return f"competencia-{competencia_id}"
```

**Riesgo:** el stream ID es la llave primaria del Event Store. Un error de formato es silencioso
(load retorna lista vacía, se crea un nuevo stream) y puede corromper datos de producción.

---

## Especificación

### Nuevo módulo: `competencia/application/commands/_stream_ids.py`

| | |
|---|---|
| **Precondición** | 11 definiciones locales de `_build_stream_id` en 11 archivos distintos |
| **Postcondición** | 1 módulo con 2 funciones; todos los handlers importan desde allí |
| **Invariante** | Los stream IDs generados son byte-a-byte idénticos a los actuales |

```python
# competencia/application/commands/_stream_ids.py

from uuid import UUID
from competencia.domain.value_objects.disciplina import Disciplina


def performance_stream_id(
    competencia_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
) -> str:
    """Stream ID canónico para una Performance.

    Format: "performance-{competencia_id}-{participante_id}-{disciplina}"
    Es el natural key de una Performance en el Event Store.
    """
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"


def competencia_stream_id(competencia_id: UUID) -> str:
    """Stream ID canónico para una Competencia.

    Format: "competencia-{competencia_id}"
    """
    return f"competencia-{competencia_id}"
```

### Actualización en cada handler

Reemplazar cada definición local por import y llamada al módulo:

```python
# Antes (en cada handler):
def _build_stream_id(competencia_id, participante_id, disciplina) -> str:
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"

# Después:
from competencia.application.commands._stream_ids import performance_stream_id
# ...
stream_id = performance_stream_id(command.competencia_id, command.participante_id, command.disciplina)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-1.3 — Stream IDs consolidados

  Scenario: performance_stream_id produce el mismo formato que antes
    Given competencia_id = UUID("aaaa..."), participante_id = UUID("bbbb..."), disciplina = STA
    When se llama a performance_stream_id(competencia_id, participante_id, disciplina)
    Then retorna "performance-aaaa...-bbbb...-STA"
    And es idéntico al formato anterior

  Scenario: competencia_stream_id produce el mismo formato que antes
    Given competencia_id = UUID("aaaa...")
    When se llama a competencia_stream_id(competencia_id)
    Then retorna "competencia-aaaa..."

  Scenario: no existe _build_stream_id en ningún handler tras el refactor
    Given el directorio application/commands/ refactorizado
    Then ningún archivo contiene una definición de función "_build_stream_id"

  Scenario: todos los tests de integración pasan sin modificación
    Given los tests de integración existentes para RegistrarAP, LlamarAtleta, etc.
    When se ejecuta la suite completa
    Then 481+ tests pasan sin regresiones
```

---

## Notas de implementación

- Los tests existentes no necesitan cambios — solo verifican comportamiento, no la ubicación de la función.
- Verificar que `queries/` no tenga copias adicionales del stream ID.
- El módulo `_stream_ids.py` vive en `application/commands/` porque es donde se usa;
  si en el futuro las queries también lo necesitan, promoverlo a `application/`.

---

## Referencias

- Análisis: `.work/revision-sp2/03-analisis-handlers.md` (H-H, H-I)
- Plan: `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`

---

*Redactado: 2026-03-28 — SP-ADJ-01*
