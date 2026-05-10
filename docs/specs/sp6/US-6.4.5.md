# US-6.4.5: Refactoring `DeclararAPInscripcionHandler` + `SQLiteInscripcionRepository`

**Estado**: `Done`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgos**: DR-06 · DR-07
**Bounded Context**: `registro`
**Capas afectadas**:
- `registro/application/commands/declarar_ap_inscripcion.py`
- `registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- `registro/domain/aggregates/inscripcion.py` (posiblemente)

---

## Descripción

Como **desarrollador manteniendo el BC Registro**,
quiero **que `DeclararAPInscripcionHandler` y `SQLiteInscripcionRepository` no reporten FeatureEnvy ni FanOut elevado en DesignReviewer**
para **que la separación de responsabilidades sea más clara y el repositorio no acumule lógica de reconstrucción que pertenece al aggregate**.

---

## Contexto de los Hallazgos

### DR-06 — `DeclararAPInscripcionHandler` FeatureEnvy 4/2

DesignReviewer detecta que el handler accede 4 veces a datos de objetos externos (umbral = 2). El código actual:

```python
async def handle(self, cmd: DeclararAPInscripcionCommand) -> None:
    inscripcion = await self._repo.find_by_id(cmd.inscripcion_id)  # acceso 1
    if inscripcion is None:
        raise InscripcionNoEncontrada(...)
    inscripcion.declarar_ap(cmd.disciplina, cmd.valor_ap)           # acceso 2
    await self._repo.save(inscripcion)                              # acceso 3
```

Este patrón (load → mutate → save) es la aplicación layer estándar en hexagonal. El hallazgo puede ser un falso positivo del analizador estático. **Tarea 1 de esta US es investigar antes de refactorizar.**

### DR-07 — `SQLiteInscripcionRepository` FeatureEnvy 7/2 + FanOut 9/7

El método `_row_to_inscripcion` reconstruye el aggregate `Inscripcion` desde una fila SQLite, parseando JSON y construyendo value objects (`APDeclarado`, `Disciplina`, `UnidadMedida`). El repositorio accede a 7 objetos ajenos (umbral = 2) para hacer esta reconstrucción.

La raíz es que la lógica de "cómo construir Inscripcion desde un dict de datos planos" está en el repositorio en lugar de en el aggregate.

```python
def _row_to_inscripcion(self, row: aiosqlite.Row) -> Inscripcion:
    return Inscripcion(
        inscripcion_id=UUID(row["inscripcion_id"]),
        ...
        ap_por_disciplina={
            Disciplina(disciplina): APDeclarado(
                valor=Decimal(payload["valor"]),
                unidad=UnidadMedida(payload["unidad"]),
            )
            for disciplina, payload in json.loads(row["ap_por_disciplina"] or "{}").items()
        },
        ...
    )
```

---

## Especificación

### Tarea 1 — Investigar DR-06: ¿falso positivo o refactoring necesario?

| | |
|---|---|
| **Precondición** | DR-06 reporta FeatureEnvy en `DeclararAPInscripcionHandler` |
| **Postcondición** | Se determina si el hallazgo es un falso positivo estructural o hay lógica de dominio en el handler que debería estar en el aggregate |
| **Invariante** | No modificar código en esta tarea |

Criterios para falso positivo:
- El handler solo coordina (load → domain method → save) sin lógica de negocio propia
- La lógica de validación ya está en `inscripcion.declarar_ap()`

Si es falso positivo: documentar en BL-006 y marcar DR-06 como "no aplicable — patrón de coordination handler". No refactorizar.

Si hay lógica de negocio en el handler (condiciones, cálculos): moverla al aggregate.

### Tarea 2 — Extraer factory method en `Inscripcion` (DR-07)

| | |
|---|---|
| **Precondición** | `_row_to_inscripcion` en el repositorio construye el aggregate con conocimiento del esquema de datos planos |
| **Postcondición** | `Inscripcion` expone un `@classmethod` `from_row(data: dict) -> Inscripcion` que encapsula la reconstrucción; el repositorio lo llama con el dict de la fila |
| **Invariante** | El comportamiento de reconstrucción es idéntico; todos los tests de `registro` pasan |

```python
# registro/domain/aggregates/inscripcion.py — agregar:
import json
from decimal import Decimal
from uuid import UUID

@classmethod
def from_row(cls, data: dict[str, Any]) -> "Inscripcion":
    """Factory de reconstitución desde datos planos (ej: fila SQLite)."""
    return cls(
        inscripcion_id=UUID(data["inscripcion_id"]),
        atleta_id=UUID(data["atleta_id"]),
        torneo_id=UUID(data["torneo_id"]),
        disciplinas=frozenset(Disciplina(d) for d in json.loads(data["disciplinas"])),
        estado=EstadoInscripcion(data["estado"]),
        fecha_inscripcion=datetime.fromisoformat(data["fecha_inscripcion"]),
        ap_por_disciplina={
            Disciplina(disciplina): APDeclarado(
                valor=Decimal(payload["valor"]),
                unidad=UnidadMedida(payload["unidad"]),
            )
            for disciplina, payload in json.loads(data.get("ap_por_disciplina") or "{}").items()
        },
        apto_medico_path=data.get("apto_medico_path"),
        constancia_pago_path=data.get("constancia_pago_path"),
    )
```

```python
# sqlite_inscripcion_repository.py — simplificar:
def _row_to_inscripcion(self, row: aiosqlite.Row) -> Inscripcion:
    return Inscripcion.from_row(dict(row))
```

Esto reduce el FanOut del repositorio porque ya no importa `APDeclarado`, `UnidadMedida` ni parsea JSON directamente.

### Tarea 3 — Verificar métricas tras cambios

| | |
|---|---|
| **Precondición** | Cambios de Tarea 2 aplicados |
| **Postcondición** | DesignReviewer no reporta DR-07 (FeatureEnvy/FanOut) en `SQLiteInscripcionRepository` |
| **Invariante** | D de `registro` no sube respecto a BL-005 |

```bash
pytest tests/unit/registro/ tests/integration/registro/ -q
designreviewer src/ --config pyproject.toml 2>&1 | grep "registro"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.5 — DesignReviewer sin DR-06/DR-07 en registro

  Scenario: DR-06 investigado y resuelto
    Given la investigación de DeclararAPInscripcionHandler
    When se determina que es falso positivo
    Then se registra en BL-006 como no aplicable
    And el código del handler NO cambia

  Scenario: DR-06 tiene lógica movible
    Given la investigación de DeclararAPInscripcionHandler
    When se detecta lógica de negocio en el handler
    Then esa lógica se mueve al aggregate Inscripcion
    And DesignReviewer no reporta DR-06

  Scenario: SQLiteInscripcionRepository usa Inscripcion.from_row
    Given la Tarea 2 aplicada
    When el repositorio reconstruye una inscripción desde la DB
    Then llama a Inscripcion.from_row(dict(row)) con el dict de la fila
    And no importa APDeclarado, UnidadMedida, Disciplina directamente

  Scenario: Reconstrucción de inscripción con adjuntos es correcta
    Given una inscripción con apto_medico_path y constancia_pago_path en DB
    When se llama find_by_id
    Then el aggregate retornado tiene ambos paths correctos

  Scenario: Suite de tests de registro pasa sin cambios
    Given los cambios de esta US aplicados
    When se ejecutan tests de registro
    Then todos los tests pasan
```

---

## Notas de implementación

- `from_row` implica que `Inscripcion` importa `json`, `Decimal`, `UnidadMedida`, etc. — evaluar si esto eleva D del aggregate. Si lo hace, usar un `@dataclass` con campos ya tipados y dejar el parsing en el repositorio (el current approach)
- Alternativa más conservadora: extraer solo `_parse_ap_por_disciplina(raw: str) -> dict[Disciplina, APDeclarado]` como función de módulo privada en el repositorio — reduce FeatureEnvy sin tocar el aggregate
- Si el repositorio usa `aiosqlite.Row` directamente y `dict(row)` no funciona limpiamente, usar `{k: row[k] for k in row.keys()}`
- Importar `Any` de `typing` en `inscripcion.py` si se añade `from_row`

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — DR-06 · DR-07
- Handler: `src/registro/application/commands/declarar_ap_inscripcion.py`
- Repositorio: `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- Aggregate: `src/registro/domain/aggregates/inscripcion.py`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
