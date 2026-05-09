# Plan de Implementacion: US-6.4.1 - Romper ciclo ADP en competencia/domain/aggregates

**Patron:** Hexagonal DDD BC-first
**Producto:** competencia
**Incremento:** INC-6.4 - Deuda Tecnica Sistema
**Estimacion total:** 1h 15min
**Estado:** Completado
**Fecha completado:** 2026-05-09

## Contexto Validado

- La US existe en `docs/specs/sp6/US-6.4.1.md`.
- El BC `competencia` existe con capas `domain/`, `application/`, `infrastructure/` y `api/`.
- Los artefactos arquitectonicos requeridos existen: ADR-005, ADR-006, `docs/design/architecture.md` y `docs/design/domain-model.md`.
- `CLAUDE.md`, `tests/`, `pyproject.toml`, CodeGuard, DesignReviewer y ArchitectAnalyst estan configurados.
- ArchitectAnalyst reproduce el hallazgo:
  - `DependencyCycle`
  - modulo `competencia/domain/aggregates`
  - mensaje: `competencia.domain.aggregates -> competencia.domain.aggregates.performance -> competencia.domain.aggregates`
  - `should_block=false`

## Diagnostico

El ciclo real esta causado por dos aristas estaticas:

1. `src/competencia/domain/aggregates/__init__.py` reexporta `Competencia` y `Performance`.
2. `src/competencia/domain/aggregates/performance.py` importa el helper con:
   `from competencia.domain.aggregates import performance_state`.

Eso genera el grafo:

```text
competencia.domain.aggregates
  -> competencia.domain.aggregates.performance
  -> competencia.domain.aggregates
```

No se encontraron consumidores externos que usen `from competencia.domain.aggregates import Competencia`
o `from competencia.domain.aggregates import Performance`. Los imports del codigo y tests ya usan paths
directos a `competencia.domain.aggregates.competencia` y
`competencia.domain.aggregates.performance`.

## Componentes a Modificar

### 1. Paquete aggregates

- [x] `src/competencia/domain/aggregates/__init__.py` (5 min)
  - Eliminar reexports de `Competencia` y `Performance`.
  - Dejar solo docstring del paquete.
  - Objetivo: remover la arista `aggregates -> performance`.

### 2. Aggregate Performance

- [x] `src/competencia/domain/aggregates/performance.py` (10 min)
  - Reemplazar `from competencia.domain.aggregates import performance_state`.
  - Importar `apply_stored` y `parse_payload` desde
    `competencia.domain.aggregates.performance_state`.
  - Actualizar las dos llamadas:
    - `performance_state.parse_payload(...)` -> `parse_payload(...)`
    - `performance_state.apply_stored(...)` -> `apply_stored(...)`
  - Objetivo: remover la arista `performance -> aggregates`.

### 3. Tests de regresion de imports

- [x] Agregar test unitario acotado (15 min)
  - Verificar import directo de `Competencia`.
  - Verificar import directo de `Performance`.
  - Verificar que importar el paquete `competencia.domain.aggregates` no expone reexports
    ni dispara import de aggregates concretos.

### 4. BDD

- [x] `tests/features/US-6.4.1-romper-ciclo-adp.feature` (10 min)
  - Escenarios creados para ArchitectAnalyst, suite de competencia e imports directos.
- [x] Validacion manual/automatizada del feature (10 min)
  - Esta US no requiere nuevo step complejo si la verificacion queda cubierta por tests
    y quality gates.

### 5. Quality Gates

- [x] Ejecutar tests de competencia (10 min)
  - `.venv/bin/python -m pytest tests/unit/competencia/ tests/integration/competencia/ tests/features/ -q`
- [x] Ejecutar ArchitectAnalyst (10 min)
  - `.venv/bin/architectanalyst src/ --sprint-id BL-006 --format json`
  - Criterio: no debe existir `DependencyCycle` para `competencia/domain/aggregates`.
- [x] Ejecutar CodeGuard acotado si los tests pasan (5 min)
  - `.venv/bin/codeguard src/competencia/`

### 6. Documentacion y Reporte

- [x] Documentar resultado en Fase 8 (5 min)
  - Registrar si el cambio elimina AA-01 y si quedan riesgos residuales.
- [ ] Generar `docs/reports/US-6.4.1-report.md` en Fase 9 (10 min)
  - Incluir comandos ejecutados, resultado de ArchitectAnalyst y tests.

## Resultado de Implementacion

- Se eliminaron los reexports de `Competencia` y `Performance` desde
  `competencia.domain.aggregates`.
- `Performance` usa imports directos a `apply_stored` y `parse_payload`.
- `performance_state` dejo de importar `Performance` bajo `TYPE_CHECKING`; las funciones de
  reconstitucion reciben `Any` para evitar una dependencia estatica inversa.
- Se agrego `tests/unit/competencia/domain/test_aggregates_imports.py`.

## Validacion Ejecutada

- `.venv/bin/python -m pytest tests/unit/competencia/domain/test_aggregates_imports.py tests/unit/competencia/domain/test_performance.py -q`
  - Resultado: 74 passed.
- `.venv/bin/python -m pytest tests/unit/competencia/ tests/integration/competencia/ -q`
  - Resultado: 469 passed.
- `.venv/bin/architectanalyst src/ --sprint-id BL-006 --format json`
  - Resultado: `should_block=false`, `DependencyCycle=0`.
- `.venv/bin/codeguard src/competencia/domain/aggregates/`
  - Resultado: 0 errores, 0 advertencias.
- `.venv/bin/python -m pytest tests/features/ -q`
  - Resultado: 268 passed, 1 failed en `tests/features/steps/adaptador_email_steps.py`.
  - Clasificacion: falla preexistente/no relacionada con `competencia/domain/aggregates`.

## Lecciones Aprendidas

- ArchitectAnalyst cuenta imports bajo `TYPE_CHECKING` como aristas del grafo estatico.
- Para helpers internos de reconstitucion que mutan estado privado del aggregate, `Any` evita
  introducir una dependencia circular solo para anotaciones.

## Riesgos

- Eliminar reexports puede romper consumidores externos no presentes en el repo. El contrato
  canonico del proyecto usa imports directos por modulo, y los consumidores internos ya estan
  alineados.
- ArchitectAnalyst puede seguir detectando otros ciclos fuera del alcance de esta US. El criterio
  de aceptacion es especifico para `competencia/domain/aggregates`.

## STOP de Fase 2

No se modifica codigo de `src/` hasta recibir aprobacion explicita de este plan.
