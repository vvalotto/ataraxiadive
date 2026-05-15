# HITO-32 — Deriva de tests BDD: contratos de adaptadores, passwords y semántica de dominio

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-32 — Hallazgo de calidad en SP6 |
| **Fecha** | 2026-05-08 |
| **Sprint** | SP6 — Validación, Ajustes y Despliegue |
| **Relacionado** | HITO-30 · HITO-31 · `PerformancesAPAdapter` · `AtletaNombreAdapter` · `RankingOverall` · Identidad |

---

## Contexto

Completando la revisión de la suite de tests en SP6 (iniciada en HITO-30 para unit y HITO-31 para integración), la ejecución de los tests BDD (pytest-bdd) desde PyCharm reveló 47 fallos. Los fallos se agrupan en tres familias con causas raíz distintas.

---

## Familia A — Ruptura de contrato de adaptador en steps BDD (36 tests)

**Afectados:** `ajustar_grilla_steps.py`, `api_disciplina_aware_steps.py`, `confirmar_grilla_steps.py`, `disciplina_descriptor_steps.py`, `ejecucion_multi_andarivel_steps.py`, `generar_grilla_steps.py`, `test_US_4_1_4_steps.py`

**Causa:** `PerformancesAPAdapter.__init__()` recibía 1 argumento en todos los steps BDD. Misma raíz que HITO-30 Familia A y HITO-31 Familia A: el refactor de SP5 que agregó `competencias_por_torneo` e `inscripcion_repo` al adaptador no fue reflejado en los tests BDD.

**Solución:** `StubPerformancesAPPort` en `tests/features/steps/_stubs.py` (tercer módulo compartido en la codebase de tests, análogo al de integración). Reemplaza todas las instancias de `PerformancesAPAdapter(store)` en los 7 archivos afectados.

**Patrón recurrente confirmado:** Tres suites (unit, integración, BDD) afectadas por el mismo refactor. Los tests BDD son los últimos en ejecutarse habitualmente y por eso la deriva persistió más tiempo.

---

## Familia B — Tests con invariantes y contratos incorrectos (6 tests)

Esta familia agrupa tres sub-causas distintas:

### B1 — Passwords desfasadas en identidad JWT (5 tests)

**Archivos:** `identidad_jwt_steps.py`, `US-3.2.1-bc-identidad-jwt.feature`

**Causa:** Las passwords en el feature file (`clave1234`, `secreto99`, `admin1234`) y en el step hardcodeado (`password1`) cumplían la regla original (≥8 chars) pero no la regla actual (≥10 + mayúscula + dígito, introducida en SP4/5). El endpoint retornaba 422 en lugar de 201.

**Sub-causa adicional:** El `RegistroRequest` de Pydantic requiere `nombre` y `apellido` (agregados en SP5 para completar el perfil del atleta), pero los steps solo enviaban `email`, `password`, `rol`. Esto generaba un 422 independiente de la password.

**Sub-causa adicional:** El scenario "JWT válido es verificable" usaba `rol: ADMIN`. El handler rechaza ADMIN con 403 (`RolNoPermitido`). El scenario fue rediseñado con `rol: ORGANIZADOR`.

**Solución:** Actualizar passwords a `Clave1234A`, `Secreto99A`, etc.; agregar `nombre`/`apellido` en todos los POSTs de registro; cambiar ADMIN → ORGANIZADOR.

### B2 — Test con invariante incorrecto en registrar AP (1 test)

**Archivo:** `US-1.2.1-registrar-ap.feature`

**Causa:** El scenario "Rechazo por AP ya registrado" esperaba que la segunda declaración lanzara `APYaRegistrado`. En US-5.5.1 (SP5) el dominio fue refactorizado para permitir actualización de AP (upsert) mientras la grilla no esté generada. El scenario especificaba el comportamiento antiguo.

**Solución:** Renombrar scenario a "Segunda declaración de AP actualiza el valor (upsert)" y cambiar el `then` a `el AP queda registrado exitosamente`.

### B3 — Test esperaba CANCELADA en listado de inscripciones (1 test)

**Archivo:** `test_US_3_2_3_steps.py`

**Causa:** El test buscaba la inscripción cancelada en el resultado de `GET /registro/torneos/{id}/inscriptos` esperando encontrarla con `estado: CANCELADA`. Sin embargo, `find_by_torneo()` excluye explícitamente inscripciones CANCELADAS (`WHERE estado != 'CANCELADA'`). El test tenía una expectativa incorrecta sobre el contrato del endpoint.

**Solución:** Invertir la aserción: verificar que la inscripción cancelada NO aparece en el listado (que es el comportamiento correcto y documentado del repositorio).

---

## Familia C — Fórmula de overall refactorizada (4 tests)

**Archivos:** `calcular_overall_steps.py`, `US-3.5.1-ranking-overall.feature`

**Causa:** En SP5.6.4 (US-5.6.4) el `RankingOverall` fue refactorizado de una fórmula posicional (suma de posiciones, menor = mejor) a puntos FAAS acumulados (suma de puntos, mayor = mejor). La `EntradaOverall` cambió de tener `puntaje: int` a `puntos_overall: Decimal`. Los seeds de los tests no incluían `puntos` ni `categoria` en las entradas (defaulteaban a 0.00), y el dominio introdujo `DisciplinasNoFinalizadas` cuando rankings están vacíos (en lugar de retornar empty overall).

**Tres efectos:**
1. `entry.puntaje` → `AttributeError` (campo eliminado)
2. `atleta_a.detalle["DNF"] == 2` → `KeyError` (la "penalización" ya no es un contador sino ausencia del key)
3. `DisciplinasNoFinalizadas` en escenarios donde el ranking estaba vacío → steps que esperaban comportamiento gracioso fallaban

**Solución:** Reescribir feature file con semántica FAAS (puntos en lugar de posiciones), agregar `puntos` y `categoria` a todos los seeds, actualizar aserciones a `puntos_overall`, agregar `when` step "solo con STA", capturar `DisciplinasNoFinalizadas` en el `when` step para aserciones explícitas.

---

## Familia D — `AtletaNombreAdapter` con path relativo desde PyCharm (9 tests)

**Afectados:** `api_disciplina_aware_steps.py`, `ejecucion_multi_andarivel_steps.py`, `interfaz_juez_steps.py`

**Causa:** `AtletaNombreAdapter` abre `data/registro.db` con un path relativo al CWD. Cuando los tests se ejecutan desde PyCharm (CWD = directorio del archivo), el archivo no existe y se lanza `sqlite3.OperationalError: unable to open database file`. Desde CLI en la raíz del proyecto, el path resuelve correctamente y los tests pasan — de ahí que esta familia solo sea visible desde PyCharm.

**Misma raíz que HITO-31 Familia C** (integración), pero en la capa BDD. Los handlers `ObtenerProximasPerformancesHandler` y `ObtenerGrillaHandler` inyectan `AtletaNombreAdapter` vía el contenedor de dependencias de FastAPI; los steps BDD creaban la app sin sobrescribir esas dependencias.

**Solución:** `dependency_overrides` en los fixtures de los 3 archivos afectados:
- `get_obtener_proximas_performances_handler` → `ObtenerProximasPerformancesHandler(store, StubAtletaNombrePort())`
- `get_obtener_grilla_handler` → `ObtenerGrillaHandler(store, StubAtletaNombrePort())`

`StubAtletaNombrePort` ya estaba disponible en `tests/features/steps/_stubs.py` (creado en Familia A).

---

## Familia E — Scenarios BDD de una US no actualizados al refactorizar la regla de dominio (2026-05-15)

**Archivos:** `tests/features/US-5.6.1-algoritmo-puntaje-faas.feature`, `tests/features/US-5.6.3-ranking-puntos-faas.feature` y sus steps (2 tests)

**Causa raíz:** Distinta a todas las familias anteriores. Los scenarios fueron **correctos cuando se escribieron** — pasaban contra la implementación de su US. El problema apareció cuando una US posterior cambió la regla de dominio que los scenarios cubrían, y nadie buscó ni revisó los scenarios afectados.

**Caso 1 — US-5.6.1 vs US-6.4.4 (algoritmo STA):**
- US-5.6.1 implementa `AlgoritmoPuntajeFAAS` con una única fórmula para disciplinas de tiempo: `t_min → 100 pts` (menos tiempo = mejor). El scenario "tiempo — el mas rapido recibe 100 puntos" usa `STA` y espera que Luis (190s) reciba 100 pts y Ana (270s) reciba 0.
- US-6.4.4 refactoriza el algoritmo para distinguir STA (más tiempo = mejor) vs SPE (menos tiempo = mejor).
- El scenario de US-5.6.1 queda con disciplina `STA` pero expectativas de SPE. El test pasa la validación visual ("el scenario dice lo que debería hacer") pero falla en runtime porque la regla de dominio cambió.
- **Corrección:** disciplina cambiada a `SPE_2X50` — semánticamente correcta para "el más rápido gana".

**Caso 2 — US-5.6.3 vs segmentación por categoría (algoritmo FAAS):**
- US-5.6.3 escribe el scenario con Ana (SENIOR_FEMENINO, 70m) y Luis (SENIOR_MASCULINO, 56m) esperando Luis = 80.00 pts = (56/70)×100. Esto asume que todos los atletas compiten en un pool único.
- En algún punto posterior el algoritmo FAAS incorpora segmentación por categoría: cada categoría tiene su propio `d_max`. Luis, único en SENIOR_MASCULINO, obtiene 100.00 pts.
- El scenario especificaba el comportamiento correcto para el algoritmo original, pero incorrecto para el algoritmo con segmentación.
- **Corrección:** Luis puesto en la misma categoría que Ana (SENIOR_FEMENINO) para que la proporción sea válida.

**Por qué no se detectó al leer/revisar el scenario:**
Leer el scenario en el momento de su creación no habría revelado nada — era correcto. La validación que faltó fue **al cerrar la US que cambió la regla**: al implementar US-6.4.4 (distinción STA/SPE) y al agregar segmentación por categoría, el paso obligatorio habría sido `grep -r "AlgoritmoPuntajeFAAS\|STA\|calcular_tiempo" tests/features/` y verificar que todos los scenarios afectados siguieran siendo válidos. Ese grep nunca se ejecutó.

**Diferencia con Familia C (RankingOverall posicional → FAAS):**
La Familia C también es un refactor de dominio no propagado a BDD, pero el cambio era tan profundo (fórmula posicional → fórmula FAAS) que afectaba semántica, campos y estructura. La Familia E es más sutil: el scenario parece correcto a simple vista, el nombre del scenario es consistente con las expectativas, y el error solo aparece al entender en detalle qué hace la nueva implementación con ese input específico.

**Implicación metodológica:**
Al cerrar una US que modifica una regla de dominio existente (no solo agrega funcionalidad), el checklist debe incluir:
1. `grep` sobre `tests/features/` buscando el nombre del servicio/método/regla modificada
2. Verificar que los scenarios encontrados sigan siendo semánticamente válidos con la nueva implementación
3. Ejecutar `pytest tests/features/` completo antes del commit

---

## Familia F — Globals de módulo contaminados entre tests por estado de app.py (2026-05-15)

**Archivos:** `tests/features/steps/pagina_publica_torneo_detalle_steps.py`, `tests/features/steps/torneos_publicos_steps.py` (5 tests)

**Causa raíz:** `torneo/api/router.py` expone tres variables de módulo mutables que son seteadas por `app.py` al arrancar la aplicación:

```python
_cierre_inscripcion_precondition: CierreInscripcionPrecondition | None = None
_ejecucion_precondition: EjecucionPrecondition | None = None
_ejecucion_post_action: EjecucionPostAction | None = None
```

En producción esto es correcto: `app.py` las setea una vez al inicializar. En tests, los módulos Python son **singletons en `sys.modules`**: cuando un test anterior importa `app.py` y setea los tres globals, ese estado persiste para todos los tests posteriores del mismo proceso. Los step files que montan una `FastAPI()` fresca con `torneo_router` no resetean estos globals, por lo que los endpoints `cerrar-inscripcion` e `iniciar-ejecucion` invocan precondiciones y post-actions que acceden a `data/registro.db` con path relativo → `sqlite3.OperationalError: unable to open database file`.

**Síntoma característico:** el test pasa al ejecutarse en aislamiento (`pytest tests/features/steps/pagina_publica_torneo_detalle_steps.py` solo), falla en la suite completa. La causa es el orden de ejecución: algún test anterior en el proceso importa `app.py`, y el estado global queda contaminado.

**Complicación adicional:** `torneo/api/__init__.py` re-exporta `router` (el `APIRouter`):
```python
from torneo.api.router import router
__all__ = ["router"]
```
Esto hace que `import torneo.api.router as m` resuelva el `APIRouter`, no el módulo. La forma correcta de obtener el módulo es vía `sys.modules["torneo.api.router"]` después de cualquier import que lo cargue como side-effect.

**Fix aplicado en ambos step files:**
```python
import sys
from torneo.api.router import router  # side-effect: carga el módulo en sys.modules
_torneo_router_mod = sys.modules["torneo.api.router"]

@pytest.fixture
def context(tmp_path, monkeypatch):
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    monkeypatch.setattr(_torneo_router_mod, "_cierre_inscripcion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_post_action", None)
    return {}
```

`monkeypatch.setattr` restaura el valor original automáticamente al finalizar cada test.

**Por qué se diseñó con globals mutables:** la precondición de `cerrar-inscripcion` cruza bounded contexts (torneo llama a registro). Los globals son el composition root pragmático para este cross-BC wiring en producción. Son correctos en runtime; frágiles en tests que comparten proceso.

**Diferencia con Familia D (path relativo):** en la Familia D el adaptador de infraestructura usa un path relativo al CWD. En la Familia F el path relativo lo usa una precondición inyectada via global de módulo — el test no puede sobreescribir la dependency de FastAPI porque el problema está antes del DI, en el closure que captura `_inscripcion_repo()`.

---

## Análisis de causa raíz transversal

| Familia | Tests afectados | Causa raíz |
|---------|:--------------:|------------|
| A — `PerformancesAPAdapter` | 36 | Refactor de SP5 no propagado a BDD |
| B1 — Passwords + campos missing | 5 | Dos cambios de contrato de API no reflejados en BDD |
| B2 — APYaRegistrado | 1 | Refactor de dominio (upsert) no reflejado en BDD |
| B3 — CANCELADA en listado | 1 | Invariante de repositorio incorrecto en test |
| C — RankingOverall posicional → FAAS | 4 | Refactor de dominio de SP5.6.4 no reflejado en BDD |
| D — `AtletaNombreAdapter` path relativo | 9 | Dependencia con path relativo no sobreescrita en fixtures BDD |
| E — Scenarios correctos al escribirlos, inválidos tras refactor posterior | 2 | Regla de dominio evolucionó sin revisión de scenarios afectados |
| F — Globals de módulo contaminados entre tests por `app.py` | 5 | Estado mutable de módulo seteado en un test persiste en los siguientes |
| **Total** | **63** | |

---

## Pregunta experimental

Las Familias B2, B3, C y E son casos de **tests con invariantes incorrectos** escritos por LLM (asistidos por Claude). La proporción es significativa: 8/58 (14%) de los fallos BDD son tests que especifican el comportamiento incorrecto, no el correcto.

Hipótesis de HITO-31 confirmada con mayor evidencia: el LLM tiende a especificar el comportamiento que describe el enunciado original de la US, sin actualizar cuando el comportamiento cambia en USs posteriores. Los tests de integración y BDD tienen mayor riesgo porque suelen escribirse contra el comportamiento descrito, y el dominio puede evolucionar sin que los tests sean actualizados.

La Familia E agrega un matiz: **el error no es de escritura sino de omisión de búsqueda**. El scenario era correcto; lo que faltó fue el paso activo de buscarlo y revisarlo al momento del cambio posterior. Esta distinción es relevante para IEDD porque sugiere que la corrección no está en cómo se escriben los tests, sino en cuándo y cómo se buscan los tests existentes al implementar cada US.

**Implicación metodológica para IEDD:** Al cerrar un sprint, la revisión de tests debería incluir explícitamente la verificación de que los tests BDD de USs anteriores sigan siendo válidos frente a los cambios de USs posteriores. Este es el principio de "regresión de invariantes" — no solo de funcionalidad.

---

## Mecanismo de detección

**Familias A/B/C (47 tests):** Los fallos son independientes del CWD — ocurren tanto desde CLI como desde PyCharm. No fueron detectados por CI porque los tests BDD probablemente no se ejecutaban en el pipeline de PR o fallaban silenciosamente.

**Familia D (9 tests):** Los fallos son específicos de PyCharm (CWD ≠ raíz del proyecto). Desde CLI en la raíz el path `data/registro.db` resuelve correctamente, por lo que la suite mostraba 269/269 desde terminal mientras desde PyCharm 9 tests fallaban con `sqlite3.OperationalError`. Misma dinámica que HITO-31 Familia C pero en la capa BDD.

**Implicación:** Ejecutar `pytest tests/features/` solo desde CLI en raíz es insuficiente para detectar deriva de CWD. La cobertura completa requiere ejecutar desde múltiples entornos o usar `dependency_overrides` sistemáticamente para aislar paths absolutos del filesystem.

**Recomendación:** Ejecutar `pytest tests/features/` como parte del CI pipeline con la misma prioridad que unit e integration tests.

---

## Resultado

- Suite BDD: **282/282 pasando** (Familias A/B/C/D resueltas en SP6 + Familias E/F resueltas en SP6 continuación)
- Suite total: **1170/1170 pasando** (676 unit + 212 integración + 282 BDD) — 4 skipped (validación visual UI)
- HITO-30: 21 tests unitarios · HITO-31: 31 tests de integración · HITO-32: **63 tests BDD** (Familias A–F)
- Total corregido acumulado SP6: **115 tests** que estaban silenciosamente fallando
