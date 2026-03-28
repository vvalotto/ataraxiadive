# Plan US-ADJ-1.5 — Router SRP: schemas.py + dependencies.py

**Sprint:** SP-ADJ-01 | **Estimación:** 30 min | **BDD:** omitido (refactor técnico)

## Contexto

`router.py` mezcla tres responsabilidades en 524 líneas:
- Schemas Pydantic (4 modelos: ~30 líneas)
- Dependency providers (14 funciones + 10 tipos Annotated: ~140 líneas)
- Endpoints HTTP (10 endpoints: ~280 líneas)

SRP exige un módulo por responsabilidad.

## Estructura objetivo

```
src/competencia/api/
├── schemas.py       ← Pydantic models (NEW ~30 líneas)
├── dependencies.py  ← get_* functions + *Dep types (NEW ~140 líneas)
└── router.py        ← solo endpoints (REWRITE ~280 líneas)
```

## Tareas

| # | Tarea | Estimación |
|---|-------|-----------|
| T1 | Crear `schemas.py` con los 4 modelos Pydantic | 5 min |
| T2 | Crear `dependencies.py` con todos los providers y tipos Dep | 10 min |
| T3 | Reescribir `router.py` solo con endpoints + imports necesarios | 10 min |
| T4 | Ejecutar `pytest tests/ -x -q` — 481/481 deben pasar | 5 min |

## Constraint clave

6 archivos de tests importan `get_event_store` desde `competencia.api.router`:
- `tests/integration/competencia/test_flujo_e2e.py`
- `tests/integration/competencia/test_api_interfaz_juez.py`
- `tests/features/steps/api_disciplina_aware_steps.py`
- `tests/features/steps/flujo_e2e_steps.py`
- `tests/features/steps/ejecucion_multi_andarivel_steps.py`
- `tests/features/steps/interfaz_juez_steps.py`

**Solución:** `router.py` importa `get_event_store` desde `dependencies.py`.
Cuando los tests hacen `from competencia.api.router import get_event_store`,
obtienen el mismo objeto función — `dependency_overrides[get_event_store]` sigue funcionando.

## Quality Gates

| Gate | Target |
|------|--------|
| Tests (pytest) | 481/481 ✅ |
| `router.py` líneas | ≤ 280 |
| `schemas.py` sin imports de `application/` | 0 violaciones |
| `dependencies.py` sin endpoints | 0 `@router.` en el archivo |
