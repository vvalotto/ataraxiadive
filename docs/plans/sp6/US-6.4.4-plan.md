# Plan de Implementacion: US-6.4.4 - Refactor FAAS + CodeGuard

**Patron:** Hexagonal DDD BC-first  
**Producto:** resultados  
**Incremento:** INC-6.4 - Deuda Tecnica Sistema  
**Estimacion total:** 2h 20min  
**Estado:** Completado

## Contexto Validado

- La US existe en `docs/specs/sp6/US-6.4.4.md`.
- El BC afectado es `resultados`.
- El componente principal existe en `src/resultados/domain/services/algoritmo_faas.py`.
- Tests unitarios existentes cubren distancia, tiempo, DNS, tarjeta roja, bordes y precision:
  `tests/unit/resultados/domain/test_algoritmo_faas.py`.
- DesignReviewer reproduce el hallazgo DR-02:
  - `LCOMAnalyzer` en `AlgoritmoPuntajeFAAS`: `2/1`.
- La implementacion actual tiene dos paths sin estado compartido:
  - `_calcular_distancia()`
  - `_calcular_tiempo()`

## Decisiones de Diseno

- Usar la opcion de extraccion a funciones de modulo, no dispatch via `getattr`.
- `AlgoritmoPuntajeFAAS` quedara como thin dispatcher que implementa el port
  `AlgoritmoPuntaje`.
- Mover `_calcular_distancia`, `_calcular_tiempo` y `_es_valido` a funciones de modulo.
- Mantener `_redondear` como funcion de modulo.
- No cambiar la firma publica de `calcular()`.
- No tocar reglas de negocio ni redondeo.

## Componentes a Modificar

### 1. Servicio de dominio FAAS

- [x] `src/resultados/domain/services/algoritmo_faas.py` (35 min)
  - Extraer `_calcular_distancia(resultados)` a funcion de modulo.
  - Extraer `_calcular_tiempo(resultados)` a funcion de modulo.
  - Convertir `_es_valido(resultado)` en funcion de modulo.
  - Dejar `AlgoritmoPuntajeFAAS.calcular()` como dispatch explicito:
    - `Disciplina.es_tiempo()` -> `_calcular_tiempo`
    - caso contrario -> `_calcular_distancia`

### 2. Tests unitarios

- [x] `tests/unit/resultados/domain/test_algoritmo_faas.py` (20 min)
  - Mantener tests existentes como regresion de comportamiento.
  - Agregar casos parametrizados si hace falta para dejar explicita equivalencia DYN/STA.
  - Evitar asserts fragiles sobre detalles internos.

### 3. BDD

- [x] `tests/features/US-6.4.4-refactor-faas-codeguard.feature` (10 min)
  - Escenarios creados en Fase 1.
- [x] Validacion BDD documental/automatizable (15 min)
  - Registrar correspondencia entre escenarios y gates ejecutados.
  - Crear steps solo si hay patron existente para esta clase de arquitectura; si no,
    documentar validacion por comandos en reporte.

### 4. Correcciones CodeGuard / formato

- [x] Identificar hallazgos CG-01/03/04/05 (20 min)
  - Ejecutar CodeGuard acotado sobre componentes modificados.
  - Ejecutar ruff/black/isort checks para detectar E501/imports huerfanos.
- [x] Corregir E501/imports huerfanos si aparecen en el alcance (20 min)
  - Limitar cambios a archivos reportados por los gates.
  - No hacer reformateos masivos fuera del scope.

### 5. Quality Gates

- [x] Unitarios resultados domain/application (10 min)
  - `.venv/bin/python -m pytest tests/unit/resultados/domain/test_algoritmo_faas.py -q`
  - `.venv/bin/python -m pytest tests/unit/resultados tests/integration/resultados -q`
- [x] DesignReviewer acotado (10 min)
  - `.venv/bin/designreviewer src/resultados/domain/services/algoritmo_faas.py --config pyproject.toml`
  - Criterio: no reporta LCOM en `AlgoritmoPuntajeFAAS`.
- [x] CodeGuard (10 min)
  - `.venv/bin/codeguard src/resultados/domain/services/algoritmo_faas.py`
  - Si se corrigen otros archivos, incluirlos en la corrida.
- [x] Formato (10 min)
  - `.venv/bin/black --check src/ tests/`
  - `.venv/bin/isort --check src/ tests/`
  - `.venv/bin/ruff check <archivos tocados>`
- [x] Regresion ampliada (15 min)
  - `.venv/bin/python -m pytest tests/unit/resultados tests/integration/resultados -q`

### 6. Documentacion y Cierre

- [x] Actualizar `CHANGELOG.md` (5 min).
- [x] Actualizar `docs/traceability/matrix.md` para marcar US-6.4.4 done si los gates pasan (5 min).
- [x] Actualizar `docs/specs/sp6/US-6.4.4.md` a `Done` (5 min).
- [x] Generar `docs/reports/US-6.4.4-report.md` (15 min).
- [x] Actualizar este plan con resultados de validacion (5 min).

## Resultados de Validacion

- `.venv/bin/python -m pytest tests/unit/resultados/domain/test_algoritmo_faas.py -q`
  - `15 passed`
- `.venv/bin/python -m pytest tests/unit/resultados -q`
  - `74 passed`
- `.venv/bin/python -m pytest tests/integration/resultados -q`
  - `13 passed`
- `.venv/bin/python -m pytest tests/unit/resultados tests/integration/resultados -q`
  - `87 passed`
- `.venv/bin/designreviewer src/resultados/domain/services/algoritmo_faas.py --config pyproject.toml`
  - `Sin violaciones de diseno detectadas`
- `.venv/bin/codeguard src/resultados/domain/services/algoritmo_faas.py`
  - `0 errores`, `0 advertencias`, `3 informativos`
- `.venv/bin/ruff check src/resultados/domain/services/algoritmo_faas.py`
  - `All checks passed`
- `.venv/bin/black --check src/resultados/domain/services/algoritmo_faas.py tests/unit/resultados/domain/test_algoritmo_faas.py`
  - `2 files would be left unchanged`
- `.venv/bin/isort --check-only src/resultados/domain/services/algoritmo_faas.py tests/unit/resultados/domain/test_algoritmo_faas.py`
  - OK
- `.venv/bin/pycodestyle src/resultados --select=E501 --max-line-length=100`
  - OK
- `.venv/bin/codeguard src/resultados`
  - `0 errores`, `1 advertencia` preexistente por complejidad en `_rankear_categoria`,
    `101 informativos`

## Nota de alcance

- La corrida exploratoria `ruff` sobre archivos `.feature`/`.md` no aplica: ruff los parsea como
  Python y reporta `invalid-syntax`. El gate valido se ejecuto sobre archivos Python tocados.

## Riesgos

- DesignReviewer puede seguir reportando LCOM si interpreta la clase thin dispatcher como
  contenedor de paths externos. Si ocurre, se documentara evidencia y se evaluara mover
  calculadores a estrategias concretas solo si el beneficio compensa.
- `black --check src/ tests/` puede fallar por formato preexistente fuera de esta US. En ese caso
  se documentara el hallazgo y se correra formato acotado sobre archivos tocados.
- `codeguard src/` puede ser lento; se priorizara CodeGuard acotado y luego una corrida amplia si
  el tiempo lo permite.

## STOP de Fase 2

No se modifica codigo de `src/` ni tests existentes hasta recibir aprobacion explicita de este plan.
