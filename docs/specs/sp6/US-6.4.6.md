# US-6.4.6: Decisión ARCH-03 + SRP `RankingCompetencia` + monitoreo `identidad`/`shared`

**Estado**: `Pending`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgos**: ARCH-03 · DR-01 · AA-02 · AA-04
**Bounded Contexts**: `resultados` · `identidad` · `shared`
**Capas afectadas**:
- `resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- `resultados/domain/aggregates/ranking_competencia.py`
- Documentación BL-006

---

## Descripción

Como **desarrollador y arquitecto del sistema**,
quiero **resolver la decisión pendiente sobre `ResultadosCompetenciaAdapter`, aplicar SRP en `RankingCompetencia` si corresponde, y registrar el estado de `identidad`/`shared` en BL-006**
para **cerrar todos los hallazgos pendientes de INC-6.4 y preparar el informe arquitectural final del SP6**.

---

## Contexto de los Hallazgos

### ARCH-03 — `ResultadosCompetenciaAdapter`: ¿ACL aceptable o violación?

**Decisión pendiente desde PLAN-SP6.** La nota dice "import cross-BC directo — decisión pendiente".

Al revisar el código actual (`resultados/infrastructure/repositories/resultados_competencia_adapter.py`):

```python
# Imports del adaptador:
from shared.domain.ports.event_store_port import EventStorePort       # shared — OK
from shared.domain.value_objects.disciplina import Disciplina         # shared — OK
from resultados.domain.ports.resultados_competencia_port import (      # propio BC — OK
    ResultadoFinal, ResultadosCompetenciaPort,
)
```

**El adaptador NO importa nada de `competencia.*` directamente.** Lee el event store de competencia (pasado como `EventStorePort` — shared abstraction) e interpreta los eventos por nombre de tipo (`"APRegistrado"`, `"ResultadoRegistrado"`, etc.) sin importar las clases de evento del BC Competencia.

**Diagnóstico**: ARCH-03 no es una violación de import cross-BC. Es un ACL legítimo en la capa de infraestructura de `resultados`. El acoplamiento temporal (nombres de event types como strings) es el mínimo viable para este patrón.

**Riesgo residual**: Si BC Competencia renombra un event type, el ACL silencia el cambio sin error de importación. Mitigación: test de integración que verifique el flujo completo.

### DR-01 — `RankingCompetencia` LCOM 2/1

DesignReviewer detecta LCOM=2 en `RankingCompetencia`. La clase tiene dos grupos de métodos:
1. **Cálculo**: `calcular()` → emite eventos, actualiza `_entries` y `_calculado`
2. **Reconstitución**: `reconstitute()`, `_apply_stored()`, `_rehidratar_resultados_calculados()` → reconstruye desde events

Este patrón (command + reconstitution) es inherente a Event Sourcing. La alternativa (separar en dos clases) violaría el patrón aggregate y haría que `reconstitute` no tenga acceso al estado mutable del aggregate.

**Diagnóstico preliminar**: probable falso positivo de LCOM en aggregates ES. **Tarea 1 investiga antes de refactorizar.**

### AA-02 — `identidad` D=0.67 CRITICAL (mejorando desde 0.87)

Tendencia positiva pero aún en zona de pain. No hay US de identidad en SP6 — el D no cambiará sin intervención. **Documentar tendencia en BL-006 sin cambio de código.**

### AA-04 — `shared` D=0.63 CRITICAL (estable)

`shared` es un módulo de soporte que todos los BCs importan. Reducir D requeriría reestructurar el módulo, lo que impactaría todos los BCs. **Fuera de scope SP6 — documentar en BL-006.**

---

## Especificación

### Tarea 1 — Formalizar decisión ARCH-03

| | |
|---|---|
| **Precondición** | ARCH-03 marcado como "decisión pendiente" en PLAN-SP6 |
| **Postcondición** | ARCH-03 cerrado formalmente como "ACL aceptable" con justificación documentada |
| **Invariante** | No se modifica `ResultadosCompetenciaAdapter` |

Verificar que el adaptador no tiene imports de `competencia.*`:

```bash
grep -n "from competencia\." src/resultados/infrastructure/repositories/resultados_competencia_adapter.py
# Resultado esperado: sin coincidencias
```

Registrar la decisión en BL-006 y en `docs/design/adr/` si se considera necesario un ADR formal.

### Tarea 2 — Investigar y aplicar (o descartar) SRP en `RankingCompetencia`

| | |
|---|---|
| **Precondición** | DR-01 reporta LCOM 2/1 en `RankingCompetencia` |
| **Postcondición** | Se determina si el LCOM es un falso positivo de ES o si hay lógica movible; si hay, se extrae |
| **Invariante** | El comportamiento del aggregate (calcular, reconstituir, emitir eventos) no cambia |

Criterios para falso positivo de ES:
- Los dos "grupos" de métodos son inevitables: uno para el comando de dominio, otro para la reconstitución desde eventos
- Separar en dos clases haría que `reconstitute()` no pueda mutar el estado interno del aggregate

Si es falso positivo: documentar en BL-006 como "LCOM=2 inherente al patrón ES — no aplicable".

Si hay lógica movible (ej: los helpers de módulo `_calcular_entries`, `_agrupar_por_categoria`, etc. ya están fuera de la clase — verificar si alguno tiene state):
- Los helpers de módulo YA están extraídos fuera de la clase — esto es correcto
- Verificar si hay algún método de instancia que no use `self.*` (candidato para función de módulo)

### Tarea 3 — Registrar monitoreo AA-02 y AA-04 en BL-006

| | |
|---|---|
| **Precondición** | `identidad` D=0.67 y `shared` D=0.63 sin cambios de código en SP6 |
| **Postcondición** | BL-006 registra los valores de D con decisión explícita de no intervención en v1.0 |
| **Invariante** | No se modifica código de `identidad` ni `shared` |

Contenido a registrar en BL-006:
- `identidad` D=0.67: tendencia ↓ desde 0.87 (BL-004) → 0.67 (BL-005). Candidato a refactoring en SP7 si sigue en zona de pain. Acción en SP6: ninguna.
- `shared` D=0.63: estable entre BL-004 y BL-005. Reducirlo requiere reestructurar módulo compartido — impacto sistémico alto para v1.0. Diferir a post-despliegue.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.6 — Decisiones arquitecturales cerradas y registradas

  Scenario: ARCH-03 cerrado como ACL aceptable
    Given el análisis de ResultadosCompetenciaAdapter
    When se verifica que no hay imports de competencia.*
    Then ARCH-03 se cierra como "ACL aceptable — sin import cross-BC"
    And la decisión queda registrada en BL-006

  Scenario: DR-01 investigado y resuelto
    Given el análisis de RankingCompetencia
    When se determina si LCOM=2 es falso positivo de ES
    Then el resultado queda documentado en BL-006
    And si es falso positivo: el código NO cambia
    And si hay lógica movible: se extrae y DesignReviewer no reporta DR-01

  Scenario: AA-02 y AA-04 registrados en BL-006
    Given los valores D de identidad=0.67 y shared=0.63
    When se cierra INC-6.4
    Then BL-006 registra ambos módulos con decisión explícita de no intervención
    And queda indicado el criterio para intervención futura (D > umbral en SP7)

  Scenario: DesignReviewer 0 CRITICAL al cierre de INC-6.4
    Given todos los hallazgos de INC-6.4 procesados
    When se ejecuta designreviewer sobre src/
    Then el reporte indica 0 CRITICAL
    And should_block=false
```

---

## Notas de implementación

- ARCH-03: si `grep "from competencia\." resultados_competencia_adapter.py` devuelve coincidencias, hay un import real y sí hay que refactorizar. De lo contrario, la decisión es cierre-como-válido.
- Para la decisión ARCH-03, crear ADR solo si el equipo prevé reutilizar este patrón ACL en el futuro — para v1.0 basta con un comentario en BL-006
- Los helpers de módulo en `ranking_competencia.py` (funciones con `_` prefix fuera de la clase) ya representan buena separación — verificar con `grep "^def _" ranking_competencia.py` cuántas hay fuera de la clase
- Si DR-01 resulta ser un falso positivo y hay capacidad, evaluar añadir `# noqa: DR-01` o configurar excepción en DesignReviewer para aggregates ES (consultar PLAN-SP6 §QG-01)

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — ARCH-03 · DR-01 · AA-02 · AA-04
- Adaptador: `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- Aggregate: `src/resultados/domain/aggregates/ranking_competencia.py`
- BL-005: `docs/contexto/BL-005-architectanalyst.md`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
