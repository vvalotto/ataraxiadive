# HITO-32 — Deriva de tests BDD: contratos de adaptadores, passwords y semántica de dominio

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-32 — Hallazgo de calidad en SP6 |
| **Fecha** | 2026-05-08 |
| **Sprint** | SP6 — Validación, Ajustes y Despliegue |
| **Relacionado** | HITO-30 · HITO-31 · `PerformancesAPAdapter` · `RankingOverall` · Identidad |

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

## Análisis de causa raíz transversal

| Familia | Tests afectados | Causa raíz |
|---------|:--------------:|------------|
| A — `PerformancesAPAdapter` | 36 | Refactor de SP5 no propagado a BDD |
| B1 — Passwords + campos missing | 5 | Dos cambios de contrato de API no reflejados en BDD |
| B2 — APYaRegistrado | 1 | Refactor de dominio (upsert) no reflejado en BDD |
| B3 — CANCELADA en listado | 1 | Invariante de repositorio incorrecto en test |
| C — RankingOverall posicional → FAAS | 4 | Refactor de dominio de SP5.6.4 no reflejado en BDD |
| **Total** | **47** | |

---

## Pregunta experimental

Las Familias B2, B3 y C son casos de **tests con invariantes incorrectos** escritos por LLM (asistidos por Claude). La proporción es significativa: 6/47 (13%) de los fallos BDD son tests que especifican el comportamiento incorrecto, no el correcto.

Hipótesis de HITO-31 confirmada con mayor evidencia: el LLM tiende a especificar el comportamiento que describe el enunciado original de la US, sin actualizar cuando el comportamiento cambia en USs posteriores. Los tests de integración y BDD tienen mayor riesgo porque suelen escribirse contra el comportamiento descrito, y el dominio puede evolucionar sin que los tests sean actualizados.

**Implicación metodológica para IEDD:** Al cerrar un sprint, la revisión de tests debería incluir explícitamente la verificación de que los tests BDD de USs anteriores sigan siendo válidos frente a los cambios de USs posteriores. Este es el principio de "regresión de invariantes" — no solo de funcionalidad.

---

## Mecanismo de detección

Los 47 fallos solo eran visibles al ejecutar desde PyCharm (CWD distinto a raíz). La ejecución desde CLI en la raíz del proyecto también fallaría en estas familias (las razones no son de CWD, sino de contratos), pero el CI no detectó los fallos porque los tests BDD probablemente no se ejecutaban en el pipeline de PR o fallaban silenciosamente.

**Recomendación:** Ejecutar `pytest tests/features/` como parte del CI pipeline con la misma prioridad que unit e integration tests.

---

## Resultado

- Suite BDD: **269/269 pasando** (antes: 222/269)
- Suite total: **1140/1140 pasando** (664 unit + 207 integración + 269 BDD)
- HITO-30: 21 tests unitarios · HITO-31: 31 tests de integración · HITO-32: 47 tests BDD
- Total corregido en SP6 pre-baseline: **99 tests** que estaban silenciosamente fallando
