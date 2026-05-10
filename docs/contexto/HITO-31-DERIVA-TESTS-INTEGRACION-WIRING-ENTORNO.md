# HITO-31 — Deriva de tests de integración: wiring de dependencias, invariantes incorrectos y entorno

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-31 — Hallazgo de calidad en SP6 |
| **Fecha** | 2026-05-08 |
| **Sprint** | SP6 — Validación, Ajustes y Despliegue |
| **Relacionado** | HITO-30 · `PerformancesAPAdapter` · `AtletaNombreAdapter` · `RegistrarAPHandler` |

---

## Contexto

Continuando la revisión de la suite de tests en SP6 (iniciada en HITO-30 para tests unitarios), la ejecución de los tests de integración desde PyCharm reveló 31 fallos adicionales. Los fallos se agrupan en tres familias:

**Familia A — Ruptura de contrato de adaptador en tests de integración** (25 tests):
- Archivos: `test_generar_grilla_integration.py`, `test_ajustar_grilla_integration.py`, `test_confirmar_grilla_integration.py`, `test_disciplina_descriptor_integration.py`, `test_flujo_e2e_inc21.py`, `test_generar_grilla_api.py`, `test_grilla_tarjeta_asignada_api.py`
- `PerformancesAPAdapter.__init__()` recibía 1 argumento (`event_store`) en todos los tests. El mismo refactor de SP5 que afectó los tests unitarios (HITO-30, Familia A) había dejado los tests de integración igualmente desactualizados.

**Familia B — Invariante incorrecto especificado en un test** (1 test):
- `test_registrar_ap_integration.py::test_segunda_llamada_misma_combinacion_lanza_error`
- El test esperaba `APYaRegistrado` en la segunda llamada con la misma combinación (competencia, participante, disciplina). Sin embargo, la regla del dominio es otra: el atleta puede actualizar su AP mientras la grilla no haya sido generada (US-5.5.1). El test estaba especificando un comportamiento incorrecto.

**Familia C — Adaptadores de infraestructura con paths relativos en API tests** (5 tests, ERRORs en runtime):
- Archivos: `test_api_interfaz_juez.py` (2 tests), `test_generar_grilla_api.py`, `test_grilla_tarjeta_asignada_api.py`, `test_audit_log_api.py`
- Los fixtures de los tests de API solo sobreescribían `get_event_store`. Los endpoints que usan `AtletaNombreAdapter()` —`/proximas`, `/grilla`, `/audit-log`— construyen el adaptador con `data/registro.db` como path relativo al CWD. Desde PyCharm, el CWD no es la raíz del proyecto y el archivo no se encuentra.

---

## Análisis de causa raíz

### Familia A

La misma dinámica que HITO-30 Familia A, pero a nivel de integración:

```
PerformancesAPAdapter(event_store)           ← 1 argumento, todos los tests de integración
  → PerformancesAPAdapter(                   ← refactorizado en SP5
        event_store,
        competencias_por_torneo,
        inscripcion_repo
    )

TypeError al ejecutar el test, no en el setup:
  el error aparece en la línea exacta donde se instancia el adaptador.
```

Los tests de integración no tenían por qué usar el adaptador real: estaban testeando handlers, no el adaptador de infraestructura. Usaban `PerformancesAPAdapter(store)` porque era la forma conveniente de alimentar APs al handler, pero esto crea una dependencia de infraestructura innecesaria en el nivel de integración.

### Familia B

Este caso es cualitativamente distinto: no es un test desactualizado sino un test que nunca fue correcto. El nombre (`lanza_error`) y el assertion (`pytest.raises(APYaRegistrado)`) especificaban comportamiento equivocado frente a la regla real del dominio.

```
Regla real (US-5.5.1):
  segunda llamada antes de generar grilla  → actualiza el AP (mismo performance_id, nuevo evento)
  segunda llamada después de confirmar grilla → GrillaYaConfirmadaError

Test incorrecto:
  segunda llamada → APYaRegistrado   ← no ocurre, ni debería ocurrir
```

El test fallaba porque el handler no lanzaba `APYaRegistrado` —que era el comportamiento correcto— y el test estaba verificando el comportamiento incorrecto.

### Familia C

Los tests de API (TestClient + FastAPI) ejercen el grafo completo de inyección de dependencias. Sobreescribir `get_event_store` es necesario pero no suficiente: los handlers que no dependen directamente de `event_store` como argumento en el fixture —como `get_obtener_proximas_performances_handler`, que crea `AtletaNombreAdapter()` internamente— no reciben la sobreescritura.

```
test sobreescribe:  get_event_store → store temporal
endpoint llama:     ObtenerProximasPerformancesHandler(event_store, AtletaNombreAdapter())
AtletaNombreAdapter() construye con:  data/registro.db (path relativo al CWD)

Desde CLI (raíz):    CWD = /proyecto/ → data/registro.db existe ✅
Desde PyCharm:       CWD = /proyecto/tests/... → data/registro.db no existe ❌
                     OperationalError: unable to open database file
```

La causa es idéntica a HITO-30 Familia C, pero manifestada en tests de API en lugar de fixtures de migración. El patrón es el mismo: supuesto implícito sobre el CWD en paths relativos.

---

## Por qué los tests de integración exponen problemas distintos a los unitarios

| Dimensión | Tests unitarios | Tests de integración |
|-----------|----------------|---------------------|
| Alcance del fallo | Componente aislado | Colaboración entre componentes |
| Detectabilidad del fallo A | TypeError inmediato en el test | TypeError en línea específica de seed o setup |
| Wiring de dependencias | No aplica (mocks/stubs explícitos) | El grafo de DI de FastAPI se ejecuta real |
| Fallo por CWD | Solo en fixtures de migración | En cualquier adaptador con path relativo invocado por endpoint |
| Fallo por invariante incorrecto | El handler lanza o no lanza | El handler lanza o no lanza (igual), pero más costoso de diagnosticar porque el contexto es más amplio |

El nivel de integración agrega una capa de complejidad: la inyección de dependencias de FastAPI puede instanciar adaptadores con configuración de producción (paths de DB reales) dentro de una sesión de test, sin que el test lo haya solicitado explícitamente.

---

## El patrón del Familia C ampliado: sobreescritura parcial de dependencias

```
Problema:
  test fixture sobreescribe → dependency_A
  endpoint depende de     → dependency_A, dependency_B
  dependency_B usa        → adaptador con path relativo → falla en PyCharm

Síntoma:
  test pasa en CLI, falla en PyCharm
  el error no señala el test, señala el adaptador de infraestructura

Diagnóstico:
  buscar qué handlers del router usan AtletaNombreAdapter(), SQLiteInscripcionRepository(), etc.
  verificar que todos estén sobreescritos en el fixture o usen stubs
```

Este patrón es especialmente difícil de detectar porque:
1. El test pasa en CLI (donde `data/registro.db` existe)
2. El error apunta a código de infraestructura, no al test
3. La solución requiere entender el grafo de inyección de dependencias del router

---

## Resolución aplicada

**Familia A:**
- Se creó `tests/integration/competencia/_stubs.py` con `StubPerformancesAPPort` que lee eventos `APRegistrado` directamente del `SQLiteEventStore` usando `load_all_streams_with_prefix`.
- Se reemplazó `PerformancesAPAdapter(store)` por `StubPerformancesAPPort(store)` en todos los tests afectados.
- Para el test de API (`test_generar_grilla_api.py`) se sobreescribió además `get_generar_grilla_handler` en el fixture.

**Familia B:**
- Se reemplazó `test_segunda_llamada_misma_combinacion_lanza_error` por `test_segunda_llamada_misma_combinacion_actualiza_ap`.
- El nuevo test verifica: misma `performance_id` en ambas llamadas, 2 eventos `APRegistrado` en el stream, valor actualizado en el último evento.

**Familia C:**
- Se agregó `StubAtletaNombrePort` a `_stubs.py` (devuelve `f"Atleta-{str(atleta_id)[:8]}"`, igual al fallback del adapter real).
- Se sobreescribieron `get_obtener_proximas_performances_handler`, `get_obtener_grilla_handler` y `get_obtener_audit_log_handler` en los fixtures de los 4 archivos afectados.

**Resultado:** 207/207 tests de integración pasando. 871/871 tests totales (unitarios + integración) pasando.

---

## Qué lo habría prevenido

| Mecanismo | Familia que previene |
|-----------|---------------------|
| `pytest tests/integration/` en el pipeline PR | A, B y C, en el commit que introdujo el cambio |
| Override explícito de **todas** las dependencias que usan paths en tests de API | C — el fixture que sobreescribe parcialmente es el anti-patrón |
| Review formal de tests al cerrar una US que refactoriza un adaptador | A — buscar `grep -r "PerformancesAPAdapter"` al cambiar la firma |
| Nomenclatura del test que refleje el invariante exacto | B — `lanza_error` oculta qué error y en qué condición |

---

## Diferencia con HITO-30: ¿qué agrega el nivel de integración?

HITO-30 documentó la deriva en tests unitarios. HITO-31 agrega:

1. **El wiring de infraestructura es un vector de falla propio del nivel de integración.** Los tests unitarios usan stubs explícitos; los de integración confían en el DI del framework, y ese DI puede instanciar adaptadores con config de producción.

2. **Un test incorrecto es más costoso de diagnosticar que un test desactualizado.** La Familia B no es un test viejo: es un test que especificaba el comportamiento equivocado desde el principio. La corrección requirió entender el dominio (US-5.5.1), no solo actualizar la firma.

3. **El entorno de ejecución sigue siendo el vector de falla más silencioso.** Tanto en unitarios (Familia C de HITO-30) como en integración (Familia C de este HITO), el test pasa en CI y falla en el IDE del desarrollador. Esto invierte el contrato esperado: normalmente el IDE es el entorno controlado.

---

## Pregunta para el experimento

HITO-30 preguntó: *¿qué porcentaje de la deuda de test silenciosa se origina en cambios de invariantes no propagados, versus en funcionalidades no cubiertas?*

HITO-31 agrega una tercera categoría: **tests que especifican comportamiento incorrecto**. La Familia B no es deuda por omisión ni por deriva — es deuda por especificación errónea. En un proyecto IEDD+LLM, esta categoría puede tener una causa específica: el LLM puede escribir el assertion de un test basándose en el nombre de la excepción disponible, sin verificar si esa excepción aplica en la condición exacta del test.

**¿Con qué frecuencia los tests escritos por el LLM verifican el comportamiento correcto frente a los escritos por el equipo humano? ¿La especificación formal IEDD reduce esta clase de error?**

---

*Registrado: 2026-05-08 — SP6 validación de suite de tests*
