# US-ADJ-1.5: Router SRP — Separar schemas.py + dependencies.py

**Estado**: `Done`
**Sprint**: SP-ADJ-01 — Ajuste Técnico Post-SP2
**Issues**: ADJ-07
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/api/`

---

## Descripción

Como **desarrollador del BC Competencia**,
quiero **separar `router.py` en tres archivos con responsabilidad única**
para **que cada archivo tenga una razón de cambio y sea navegable independientemente**.

---

## Contexto de la deuda

`competencia/api/router.py` tiene 552 líneas mezclando cuatro responsabilidades:

| Responsabilidad | Líneas aprox. | Razón de cambio |
|---|---|---|
| Schemas Pydantic (request/response) | ~30 | Cambia cuando la API contract cambia |
| Providers de DI (`get_*` + `Annotated`) | ~120 | Cambia cuando cambia la infraestructura |
| Endpoints HTTP | ~250 | Cambia cuando cambia la interfaz del juez |
| Cableado cross-BC (P-08) | ~30 | Cambia cuando cambia la integración entre BCs |

El punto 4 ya se resuelve en US-ADJ-1.4. Esta US separa los primeros tres.

---

## Especificación

### Estructura objetivo

```
competencia/api/
  __init__.py
  router.py        ← solo endpoints; ~250 líneas
  schemas.py       ← Pydantic models de request/response; ~30 líneas
  dependencies.py  ← providers get_* y tipos Annotated; ~120 líneas
```

| | |
|---|---|
| **Precondición** | `router.py` de 552 líneas con 4 responsabilidades |
| **Postcondición** | 3 archivos con responsabilidad única; `router.py` ≤ 280 líneas |
| **Invariante** | Todos los endpoints responden igual; todos los tests pasan |

### Contenido de cada archivo

**`schemas.py`** — solo modelos Pydantic:
```python
# CambioGrillaSchema, AjustarGrillaBody, ConfirmarGrillaBody, IniciarCompetenciaBody
```

**`dependencies.py`** — solo providers de DI:
```python
# get_event_store, get_disciplina_descriptor, get_andariveles_activos_adapter,
# get_performances_estado_adapter, get_on_finalizada_callback (si no fue a app.py),
# todos los get_*_handler, todos los Annotated types (EventStoreDep, etc.)
```

**`router.py`** — solo endpoints:
```python
from competencia.api.schemas import AjustarGrillaBody, ConfirmarGrillaBody, IniciarCompetenciaBody
from competencia.api.dependencies import AjustarGrillaHandlerDep, ConfirmarGrillaHandlerDep, ...

router = APIRouter(...)

@router.get(...)
async def get_eventos(...): ...

@router.post(...)
async def post_ajustar_grilla(...): ...
# etc.
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-ADJ-1.5 — Router SRP

  Scenario: router.py contiene solo endpoints
    Given el archivo competencia/api/router.py refactorizado
    Then no contiene clases Pydantic (BaseModel)
    And no contiene funciones get_* de DI
    And contiene solo funciones decoradas con @router.get o @router.post

  Scenario: schemas.py contiene solo modelos Pydantic
    Given el archivo competencia/api/schemas.py
    Then contiene CambioGrillaSchema, AjustarGrillaBody, ConfirmarGrillaBody, IniciarCompetenciaBody
    And no contiene imports de FastAPI Depends

  Scenario: dependencies.py contiene solo providers de DI
    Given el archivo competencia/api/dependencies.py
    Then contiene todas las funciones get_* y los tipos Annotated
    And no contiene funciones decoradas con @router.get o @router.post

  Scenario: todos los endpoints responden igual tras la separación
    Given la suite de tests de integración existente
    When se ejecutan todos los tests HTTP
    Then 481+ tests pasan sin regresiones

  Scenario: router.py tiene ≤ 280 líneas tras el refactor
    Given el archivo competencia/api/router.py refactorizado
    Then tiene como máximo 280 líneas
```

---

## Notas de implementación

- Esta US **debe ejecutarse después de US-ADJ-1.4** — el cableado cross-BC ya estará
  fuera del router, lo que simplifica la separación.
- Los imports en `router.py` cambian de importar desde `competencia.infrastructure.*`
  a importar desde `competencia.api.dependencies`.
- Verificar que `__init__.py` de `competencia/api/` exporte correctamente el `router`
  para que `app.py` pueda importarlo sin cambios.
- Los tests que parchean (`monkeypatch`, `dependency_overrides`) providers de DI pueden
  necesitar actualizar el path de import del provider.

---

## Referencias

- Análisis: `.work/revision-sp2/05-revision-solid.md` (H-O, SRP)
- Plan: `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`
- Dependencia: US-ADJ-1.4 debe estar completa antes de implementar esta US

---

*Redactado: 2026-03-28 — SP-ADJ-01*
