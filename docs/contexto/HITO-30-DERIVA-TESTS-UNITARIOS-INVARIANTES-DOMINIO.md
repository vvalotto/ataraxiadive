# HITO-30 — Deriva silenciosa de tests unitarios: invariantes, contratos y entorno

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-30 — Hallazgo de calidad en SP6 |
| **Fecha** | 2026-05-08 |
| **Sprint** | SP6 — Validación, Ajustes y Despliegue |
| **Relacionado** | HITO-12 · HITO-27 · `PerformancesAPAdapter` · `identidad/domain/exceptions.py` |

---

## Contexto

Al iniciar SP6, la ejecución del suite de tests unitarios desde PyCharm reveló 21 fallos que no habían sido detectados durante SP5. Los fallos agrupados en tres familias distintas:

**Familia A — Ruptura de contrato de adaptador** (1 test):
- `test_obtener_grilla_handler.py::test_obtener_grilla_expone_tarjeta_asignada`
- `PerformancesAPAdapter.__init__()` fue refactorizado en SP5 para recibir `competencias_por_torneo` y `inscripcion_repo` (antes solo recibía `event_store`). El test continuó llamando `PerformancesAPAdapter(store)`.

**Familia B — Desfase de reglas de dominio en tests** (16 tests):
- Tests en `identidad/` usaban passwords como `"apnea123"`, `"seguro12"`, `"12345678"` que satisfacían la regla antigua (≥8 chars).
- La regla del dominio había evolucionado a: ≥10 chars + mayúscula + dígito.
- Los tests fallaban con `PasswordDemasiadoCorto` antes de llegar al assertion real.
- Adicionalmente: `test_password_demasiado_corto_mensaje` afirmaba `"8" in str(exc)` pero el mensaje de la excepción decía `"10 caracteres"`.

**Familia C — Path relativo sensible al entorno de ejecución** (4 tests, ERRORs en setup):
- `test_sqlite_event_store_prefix.py` (4 tests) fallaban con `ERROR` en el fixture, antes de ejecutar cualquier assertion.
- `run_migrations` construía el `Config` de Alembic con `Config("alembic.ini")` — path relativo al CWD.
- Desde CLI en la raíz del proyecto: funciona. Desde PyCharm: el CWD es distinto y Alembic no encuentra `alembic.ini`, lanzando `CommandError: No 'script_location' key found`.

---

## Análisis de causa raíz

### Por qué ocurrieron

Las familias A y B comparten la misma dinámica: **un cambio en producción no propagó su contrato a los tests dependientes**. La familia C tiene una causa distinta: **un supuesto implícito sobre el entorno de ejecución**.

```
Familias A y B — producción evolucionó, tests congelados:

  PerformancesAPAdapter(store)
    → PerformancesAPAdapter(store, competencias_por_torneo, inscripcion_repo)

  _MIN_PASSWORD_LENGTH = 8
    → _MIN_PASSWORD_LENGTH = 10 + re.search(r"[A-Z]") + re.search(r"[0-9]")

  Test congelado: PerformancesAPAdapter(store)   ← TypeError en runtime
  Test congelado: password="apnea123"            ← falla regla de dominio

Familia C — supuesto implícito de entorno:

  Config("alembic.ini")   ← asume CWD == raíz del proyecto
  Desde CLI raíz: CWD = /proyecto/ → alembic.ini encontrado ✅
  Desde PyCharm:  CWD = /proyecto/tests/... → alembic.ini no encontrado ❌
```

El fallo de A y B es **latente por deriva**: el test existía y pasaba, dejó de pasar cuando el código cambió. El fallo de C es **latente por entorno**: el test pasaba en un contexto de ejecución y fallaba en otro, sin ningún cambio en el código.

### Por qué no se detectaron antes

1. **Los tests unitarios no estaban en el pipeline de PR.** Los commits de SP5 pasaron por DesignReviewer (que valida métricas arquitectónicas) pero no por `pytest tests/unit/` como gate obligatorio pre-merge.

2. **mypy en modo estricto habría capturado la Familia A.** `PerformancesAPAdapter(store)` es un `TypeError` detectable estáticamente. Si mypy hubiera corrido sobre los archivos de test, habría bloqueado el merge que introdujo el refactor del adaptador.

3. **Las constantes de dominio estaban hardcodeadas en los tests.** La regla `≥8` vivía como literal en los tests (`"apnea123"`, `"12345678"`) en lugar de referenciarse desde la constante `_MIN_PASSWORD_LENGTH` del handler. Cuando la constante cambió, los literales quedaron desfasados sin ningún mecanismo de alerta.

4. **Validación dividida y divergida en la API.** El router Pydantic seguía validando `len(v) < 8` mientras el handler aplicaba `len < 10 + uppercase + digit`. Las dos capas no compartían la lógica. Esto no rompió la API en producción (el handler es más estricto), pero creó una superficie de confusión para quien leyera el router esperando encontrar la regla vigente.

5. **El path relativo nunca fue testeado desde un CWD distinto.** `Config("alembic.ini")` funciona correctamente desde CLI pero es frágil frente a entornos que no arrancan desde la raíz. PyCharm es el caso más común, pero también afectaría a cualquier CI que no configure explícitamente el directorio de trabajo.

---

## El patrón de falla

```
Ciclo de vida de un test frágil:

  1. US implementada       → test verde ✅
  2. US posterior refactoriza dependencia o cambia invariante
  3. Test no actualizado   → test latente ⚠️ (verde porque no se ejecuta)
  4. Días o semanas después, alguien corre el suite completo
  5. Fallos inesperados    → diagnóstico costoso, confusión sobre alcance
```

La brecha entre el paso 2 y el paso 5 es el intervalo de **deuda de test silenciosa**. En este caso fue de aproximadamente un sprint completo (SP5 → SP6).

---

## Qué lo habría prevenido

### Prevención estructural (proceso)

| Mecanismo | Dónde actúa | Qué habría capturado |
|-----------|-------------|----------------------|
| `pytest tests/unit/` en el pipeline PR | Pre-merge | Familias A, B y C, en el commit que introdujo el cambio |
| `mypy --strict` sobre `tests/` | Pre-commit o CI | Familia A (TypeError en constructor) |
| Constantes de dominio importadas en los tests | En el test mismo | Familia B (falla en el momento de escribirlo con la constante nueva) |
| Paths absolutos via `Path(__file__)` en lugar de `Config("archivo.ini")` | En el test mismo | Familia C (independiente del CWD, funciona en cualquier entorno) |

### Prevención de diseño

**Para Familia A:** El test de `ObtenerGrillaHandler` no debería depender del adaptador de infraestructura concreto (`PerformancesAPAdapter`). Un test unitario debería testear el handler contra una implementación del *puerto* (`PerformancesAPPort`), no contra el adaptador. El adaptador es un detalle de infraestructura. La solución aplicada —`StubPerformancesAPPort`— es la estructura correcta para este nivel de test.

**Para Familia C:** Cualquier path a archivo de configuración en un test debe ser absoluto, calculado desde `Path(__file__)`. El CWD es una variable de entorno implícita que cambia entre CLI, PyCharm, y CI. `Path(__file__).parents[N]` es portable y explícito.

**Para Familia B:** La regla de validación de password debería vivir en un único lugar:
```
opción A: en el domain aggregate Usuario (invariante de dominio puro)
opción B: en un value object Password que centralice la regla
```
Si la regla vive en el dominio y los tests construyen objetos de dominio, la regla se aplica automáticamente. No hay literal que pueda quedar desfasado.

---

## Observación sobre el contexto LLM

Este tipo de falla tiene una dimensión particular en el contexto IEDD: el LLM que implementa una US conoce el estado del codebase en el momento de la sesión, pero **no tiene visibilidad automática de qué tests escritos en sesiones anteriores dependen del código que acaba de cambiar**.

La búsqueda de afectados (`grep -r "PerformancesAPAdapter"`, `grep -r "apnea123"`) es un paso que debe hacerse explícitamente. No es parte automática de `/implement-us` tal como está definido actualmente.

Esto sugiere una extensión posible del pipeline: al cerrar la Fase 7 (implementación), correr el suite completo de tests unitarios y reportar los fallidos como parte del output de la fase, antes de hacer el commit.

---

## Familia D — Fake con `*_args` que no captura kwargs del constructor (2026-05-15)

**Archivo:** `tests/unit/test_app_p09.py` (3 tests: `test_callback_dispara_overall_si_todas_finalizaron`, `test_callback_no_dispara_overall_si_falta_otra_disciplina`, `test_callback_standalone_no_activa_p09`)

**Causa:** `CalcularRankingHandler` recibió el argumento `algoritmo=AlgoritmoPuntajeFAAS()` como keyword argument en US-5.6.2 (commit `32be3c2`). Los tres `FakeRankingHandler` del test habían sido escritos en US-3.5.2 con `def __init__(self, *_args)`, que captura solo args posicionales. Al pasar `algoritmo=...`, Python lanza:

```
TypeError: FakeRankingHandler.__init__() got an unexpected keyword argument 'algoritmo'
```

**Diferencia con Familia A:** La Familia A es un cambio en la cantidad de argumentos posicionales — el fake falla porque recibe más args de los que declara. La Familia D es un cambio a keyword argument — el fake parece "seguro" por tener `*_args` pero ignora los kwargs. El mensaje de error es distinto y puede llevar a pensar que la causa es diferente.

```
Familia A:  def __init__(self, store)       → TypeError: takes 2 positional arguments but 4 given
Familia D:  def __init__(self, *_args)      → TypeError: got an unexpected keyword argument 'algoritmo'
                                               # *_args se ve como "acepta todo", pero no acepta kwargs
```

**Timeline:** fake escrito en US-3.5.2 (SP3), kwarg agregado en US-5.6.2 (SP5), fallo detectado en SP6.

**Fix:** `def __init__(self, *_args, **_kwargs)` — la signatura correcta para un fake que no tiene opinión sobre sus dependencias.

**Prevención:** Los fakes cuyo propósito es absorber la construcción sin importarle las dependencias deben declararla explícitamente con `*_args, **_kwargs`. Un fake con solo `*_args` hace un supuesto implícito: que el constructor real nunca usará keyword arguments.

---

## Resolución aplicada

- **Familia A:** Se introdujo `StubPerformancesAPPort` en el test, que lee `APRegistrado` events del event store in-memory. El test unitario ahora es independiente de la infraestructura.
- **Familia B:** Se actualizaron todas las passwords de test al nuevo estándar (≥10 chars, mayúscula, dígito). Se renombró `test_registrar_password_exactamente_8_es_valido` → `test_registrar_password_exactamente_10_es_valido`. Se corrigió la aserción del mensaje de excepción.
- **Familia C:** Se reemplazó `Config("alembic.ini")` por `Config(str(Path(__file__).parents[4] / "alembic.ini"))`. El fixture ahora es portable entre CLI, PyCharm y CI.
- **Split de validación API:** La validación Pydantic del router sigue en `len < 8` (no se cambió — eso es trabajo de una US, no un hotfix de test). Se registra como deuda técnica.

---

## Aprendizaje central

> Un test verde que no se ejecuta regularmente no aporta confianza — solo la ilusión de ella. La cobertura de tests es solo tan valiosa como la frecuencia con que se ejecutan en el contexto de los cambios reales del codebase.

La pregunta que este HITO propone para el experimento:

**¿Qué porcentaje de la deuda de test silenciosa en un proyecto IEDD + LLM se origina en cambios de invariantes de dominio no propagados, versus en nuevas funcionalidades no cubiertas?**

---

*Registrado: 2026-05-08 — SP6 apertura*
