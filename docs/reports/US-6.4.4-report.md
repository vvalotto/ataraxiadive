# Reporte Final: US-6.4.4 - Refactor FAAS + CodeGuard

**Fecha:** 2026-05-09  
**Incremento:** INC-6.4 - Deuda Tecnica Sistema  
**Producto / BC:** resultados  
**Estado:** Completada

## Resumen

Se refactorizo `AlgoritmoPuntajeFAAS` para dejar la clase como dispatcher explicito
del port `AlgoritmoPuntaje`, moviendo los calculos de distancia y tiempo a funciones
de modulo sin cambiar reglas de negocio, firma publica ni resultados numericos.

Ademas, se corrigieron hallazgos de linea larga dentro del alcance `resultados`
detectados durante la validacion CodeGuard.

## Cambios Implementados

- `src/resultados/domain/services/algoritmo_faas.py`
  - `AlgoritmoPuntajeFAAS.calcular()` despacha por `Disciplina.es_tiempo()`.
  - `_calcular_distancia`, `_calcular_tiempo`, `_puntaje_tiempo`, `_es_valido` y
    `_redondear` quedan como funciones puras de modulo.
  - No se modifica el contrato publico ni el algoritmo de puntaje.
- `src/resultados/domain/aggregates/ranking_overall.py`
  - Correccion de docstring largo.
- `src/resultados/domain/ports/resultados_competencia_port.py`
  - Correccion de docstring largo.
- `tests/features/US-6.4.4-refactor-faas-codeguard.feature`
  - Escenarios BDD de arquitectura, regresion numerica, CodeGuard y formato.
- Documentacion actualizada en `CHANGELOG.md`, `docs/specs/sp6/US-6.4.4.md`,
  `docs/traceability/matrix.md` y `docs/plans/sp6/US-6.4.4-plan.md`.

## Evidencia de Validacion

| Gate | Resultado |
| --- | --- |
| `pytest tests/unit/resultados/domain/test_algoritmo_faas.py -q` | `15 passed` |
| `pytest tests/unit/resultados -q` | `74 passed` |
| `pytest tests/integration/resultados -q` | `13 passed` |
| `pytest tests/unit/resultados tests/integration/resultados -q` | `87 passed` |
| `designreviewer src/resultados/domain/services/algoritmo_faas.py --config pyproject.toml` | Sin violaciones de diseno |
| `codeguard src/resultados/domain/services/algoritmo_faas.py` | `0 errores`, `0 advertencias`, `3 informativos` |
| `codeguard src/resultados` | `0 errores`, `1 advertencia`, `101 informativos` |
| `pycodestyle src/resultados --select=E501 --max-line-length=100` | OK |
| `ruff check src/resultados/domain/services/algoritmo_faas.py` | OK |
| `black --check src/resultados/domain/services/algoritmo_faas.py tests/unit/resultados/domain/test_algoritmo_faas.py` | OK |
| `isort --check-only src/resultados/domain/services/algoritmo_faas.py tests/unit/resultados/domain/test_algoritmo_faas.py` | OK |

## Criterios de Aceptacion

- DesignReviewer no reporta DR-02 / LCOM en `AlgoritmoPuntajeFAAS`.
- Los tests unitarios existentes de FAAS siguen pasando sin cambios de expectativa.
- La regresion de `resultados` pasa completa para unitarios e integracion.
- CodeGuard acotado al componente queda sin errores ni advertencias.
- Las correcciones E501 dentro de `src/resultados` quedan verificadas con
  `pycodestyle`.
- La trazabilidad, changelog y especificacion de la US quedan actualizados.

## Observaciones

- La corrida amplia `codeguard src/resultados` conserva una advertencia preexistente
  por complejidad ciclomatica en `_rankear_categoria` (`C=11`), fuera del alcance de
  esta US. No quedan advertencias en `AlgoritmoPuntajeFAAS`.
- La corrida amplia de `ruff` sobre archivos no Python no aplica porque parsea
  `.feature` y `.md` como Python. El gate valido se ejecuto sobre los archivos Python
  tocados.
- No se detectaron cambios funcionales esperados: el refactor es estructural.

## Siguiente Paso

Preparar commit y PR de `feature/US-6.4.4-refactor-faas` hacia `develop`.
