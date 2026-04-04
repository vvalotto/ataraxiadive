# Plan de Implementacion — US-ADJ-3.4

## Resumen

Eliminar el acoplamiento directo de los routers de `competencia`, `registro` y
`torneo` con `identidad.api.dependencies`, moviendo el punto de importacion
transversal a `shared/api/dependencies.py`.

## Objetivo observable

- existe `src/shared/api/dependencies.py`
- `OrganizadorDep`, `AtletaDep` y `JuezDep` se re-exportan desde `shared/api/`
- los routers de `competencia`, `registro` y `torneo` importan desde
  `shared.api.dependencies`
- el comportamiento de autorizacion permanece igual

## Alcance

- `src/shared/api/__init__.py`
- `src/shared/api/dependencies.py`
- `src/competencia/api/router.py`
- `src/registro/api/router.py`
- `src/torneo/api/router.py`
- tests de autorizacion/API impactados si hace falta ajustar imports

No incluye:

- cambios en la implementacion de JWT o auth
- cambios en `identidad/api/dependencies.py`
- cambios en `src/app.py`
- BDD nueva

## Decisiones de diseño

1. `shared/api/dependencies.py` sera un modulo de re-export; no implementa auth.
2. La implementacion concreta sigue viviendo en `identidad/api/dependencies.py`.
3. `shared/api/` pasa a ser la frontera transversal para dependencias FastAPI
   compartidas entre BCs.
4. `app.py` puede seguir importando configuracion concreta de `identidad`, ya
   que actua como composition root y no como BC consumidor.

## Implementacion por area

### Shared

- crear `src/shared/api/__init__.py`
- crear `src/shared/api/dependencies.py`
- re-exportar:
  - `AtletaDep`
  - `JuezDep`
  - `OrganizadorDep`

### Routers

- cambiar imports en:
  - `competencia/api/router.py`
  - `registro/api/router.py`
  - `torneo/api/router.py`

### Validacion

- comprobar con grep que no queden imports desde `identidad.api.dependencies`
  en BCs distintos de `identidad`
- correr tests existentes de auth/router

## Riesgos a controlar

1. romper imports por crear un paquete `shared/api/` incompleto
2. que algun test o router dependa del path anterior y falle por import
3. confundir el alcance y mover tambien wiring que no corresponde a esta US

## Validacion prevista

- `pytest tests/unit/identidad/api/test_dependencies.py -q`
- `pytest tests/integration/torneo/test_disciplinas_torneo_api.py -q`
- `py_compile` sobre archivos impactados
- `grep -R "from identidad.api.dependencies" src/competencia src/registro src/torneo`
- `codeguard` sobre `shared/api/dependencies.py` y routers impactados
- `git diff --check`

## Artefactos esperados al cierre

- nuevo modulo `shared/api/dependencies.py`
- routers desacoplados de `identidad.api`
- evidencia de quality gates
- `docs/reports/US-ADJ-3.4-report.md`
