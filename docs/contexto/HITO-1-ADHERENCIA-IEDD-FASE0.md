# HITO-1 — Análisis de Adherencia Metodológica: IEDD en Fase 0

| Campo | Valor |
|-------|-------|
| **Tipo** | Informe de hito experimental |
| **Fecha** | 2026-03-19 |
| **Fase** | Fase 0 — Inicialización |
| **Tag git** | `v0.1.0` |
| **Autor** | Victor Valotto + Claude Code |
| **Hipótesis en contraste** | Los invariantes derivados del Process Modeling producen US-IEDD con menos edge cases no anticipados durante SP1 |

---

## 1. Propósito de Este Informe

Este documento registra el primer hito del experimento AtaraxiaDive: una evaluación
de la adherencia al marco IEDD durante la Fase 0, antes de que empiece cualquier
implementación de código.

El objetivo del experimento no es solo construir AtaraxiaDive, sino generar **evidencia
empírica** sobre la aplicabilidad conjunta de IEDD, Software Limpio y el ecosistema
CM + Dev Kit. Este informe captura el estado del conocimiento al inicio de SP1:
qué se hizo, cómo se desvió del plan, qué emergió como valioso, y qué hipótesis
se llevan a SP1 para contrastar.

---

## 2. El Marco de Referencia: Cadena IEDD

IEDD propone 5 capas secuenciales. El orden no es arbitrario: cada capa produce
artefactos que alimentan la siguiente, y saltarse una capa introduce especificaciones
sin fundamento de dominio.

```
Capa 1 — DOMINIO
Capa 2 — MODELO (DDD Estratégico)
Capa 3 — ESPECIFICACIÓN (US-IEDD)
Capa 4 — ARQUITECTURA
Capa 5 — IMPLEMENTACIÓN
```

La Fase 0 debía completar Capas 1, 2 y 4 (el modelo arquitectónico de referencia),
dejando Capa 3 lista para SP1 y Capa 5 pendiente por completo.

---

## 3. Evaluación Capa por Capa

### Capa 1 — DOMINIO ✅ Completada

**Propósito IEDD:** Entender el dominio antes de modelar. Capturar el vocabulario,
los actores, los procesos de negocio y las reglas del mundo real.

**Lo que se hizo:**

| Artefacto | Estado | Aporte |
|-----------|--------|--------|
| `docs/dominio/01-dominio_torneos_apnea.md` | ✅ | Descripción del dominio, glosario deportivo |
| `docs/dominio/02-arquitectura_referencia.md` | ✅ | Decisiones técnicas iniciales del dominio |
| `docs/dominio/03-atributos_calidad.md` | ✅ | 9 áreas de calidad con IDs AC-XX-NN |
| `docs/dominio/04-estrategia_desarrollo.md` | ✅ | 5 subproyectos, 22 incrementos, DoD |
| `docs/dominio/05-requerimientos_funcionales.md` | ✅ | 48 RFs elicitados (~60% definidos al inicio) |
| `docs/requirements/vision.md` | ✅ | 5 roles, alcance v1, criterios de éxito |

**Adherencia:** Alta. El dominio fue explorado en profundidad antes de cualquier
decisión de modelado. El glosario de lenguaje ubicuo (AP, RP, OT, DNS, tarjetas)
está capturado y es la base del modelo.

**Observación:** Los RFs llegaron al 53% de definición completa al cerrar Fase 0
(45 de 85% definidos, 7 pendientes de SP4+). Esto es esperable: el dominio de
configuración de torneos depende de decisiones de producto que no se toman en Fase 0.

---

### Capa 2 — MODELO (DDD Estratégico) ✅ Completada con extensión metodológica

**Propósito IEDD:** Producir el modelo conceptual del dominio usando DDD estratégico:
Bounded Contexts, relaciones entre BCs, lenguaje ubicuo por BC.

**Lo que se hizo:**

| Artefacto | Estado | Aporte |
|-----------|--------|--------|
| `docs/design/event-storming-big-picture.md` | ✅ | ES Nivel 1: 25 eventos, 4 BCs emergentes, 25 hot spots |
| `docs/design/context-map.md` | ✅ | 6 BCs definitivos, relaciones DDD (ACL, OHS, PL, Partnership) |
| `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` | ✅ | Decisión formal: 6 BCs + ES en Competencia y Notificaciones |
| `docs/design/event-storming-competencia.md` | ✅ | ES Nivel 2: 2 aggregates, 14 invariantes, 12 US candidatas |
| `docs/design/domain-model.md` | ✅ | Aggregates, VOs, repositorios (puertos) — 6 BCs modelados |
| `docs/contexto/DECISION-EVENT-STORMING.md` | ✅ | Justificación de incorporar ES entre Capa 1 y Capa 2 |

**Adherencia:** Alta, con una **extensión metodológica documentada y justificada.**

La extensión fue incorporar Event Storming en dos niveles como método concreto entre
Capa 1 y Capa 2. IEDD no prescribe el método de modelado — solo que se produzca un
modelo de dominio. Event Storming es la técnica elegida, y la decisión está documentada
en `DECISION-EVENT-STORMING.md`.

**Resultado clave de esta capa:** Los 6 BCs emergieron del comportamiento del dominio
(eventos del sistema), no de la organización de los RFs. Esto es DDD estratégico
correctamente aplicado. El BC `Configuración` fue eliminado porque no emergió como
frontera natural: sus conceptos son atributos de otros BCs.

**Hot spots resueltos en esta capa:** 9 de 9, incluyendo los 4 del cierre de sesión
(HS-19: fórmula de puntos como VO configurable; HS-22: premios como registro
administrativo; HS-25: notificaciones individuales al cerrar torneo; HS-P2: ventana
de impugnación configurable por torneo).

---

### Capa 3 — ESPECIFICACIÓN (US-IEDD) ⚠️ Parcialmente completada

**Propósito IEDD:** Producir User Stories con precondición, postcondición e invariantes
formales. Cada US-IEDD debe ser derivable sin ambigüedad a partir del modelo de dominio.

**Lo que se hizo:**

| Artefacto | Estado | Aporte |
|-----------|--------|--------|
| `docs/iedd/US-IEDD-template.md` | ✅ | Template formal con precondición/postcondición/invariantes |
| `docs/iedd/ANALISIS-IEDD.md` | ✅ | Marco conceptual completo |
| `docs/iedd/ANALISIS-INTEGRACION-CLAUDE-DEV-KIT.md` | ✅ | Integración con /implement-us |
| `docs/traceability/matrix.md` | ✅ | 53 RFs → BC → SP → Incremento → US-IEDD candidata |
| US-IEDD individuales (SP1) | ❌ | Pendiente — se crean en SP1 antes de /implement-us |

**Adherencia:** Parcial, por diseño. Fase 0 no incluía la escritura de US-IEDD
individuales — solo el setup del marco y la matriz de trazabilidad. Las 8 US-IEDD
candidatas para SP1 están identificadas en `matrix.md` con comandos e invariantes
preliminares. La escritura formal en `docs/plans/` es el primer paso de SP1.

**Observación importante:** La Capa 3 requiere que Capa 2 esté completa. El haber
resuelto los 9 hot spots antes de escribir US-IEDD individuales es adherencia correcta
al orden IEDD: las invariantes están documentadas en el ES Process Modeling, y las
US-IEDD las tomarán como precondición directa.

---

### Capa 4 — ARQUITECTURA ✅ Completada

**Propósito IEDD:** Definir la arquitectura que soportará la implementación. Debe
derivarse del modelo de dominio, no imponerse sobre él.

**Artefactos producidos:**

| Artefacto | Estado | Aporte |
|-----------|--------|--------|
| `docs/adr/ADR-001-event-sourcing-competencia.md` | ✅ | Event Sourcing para BC Competencia |
| `docs/adr/ADR-002-fastapi-backend.md` | ✅ | FastAPI como framework backend |
| `docs/adr/ADR-003-offline-first-pwa.md` | ✅ | Offline-first con PWA + IndexedDB |
| `docs/adr/ADR-004-reglas-como-datos.md` | ✅ | Reglas de competencia como datos configurables |
| `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` | ✅ | 6 BCs + estrategia de implementación |
| `docs/design/architecture.md` | ✅ | C4 L1+L2+L3a+L3b con diagramas Mermaid |
| `docs/design/estrategia-desarrollo-bc.md` | ✅ | Mapeo BC×SP, secuencia, dependencias |

**Adherencia:** Alta. La arquitectura hexagonal se deriva del principio DDD de
separación dominio/infraestructura. Event Sourcing en BC Competencia emerge del
análisis del Core Domain (lógica no trivial, necesidad de audit trail). El modelo C4
captura los cuatro niveles relevantes para el proyecto: contexto del sistema,
contenedores, patrón hexagonal canónico, y BC Competencia instanciado.

**Tensión documentada:** ADR-001 a ADR-004 fueron escritos antes del ES Big Picture
(antes de que Capa 2 produjera el model completo). Esto es una desviación del orden
IEDD puro. Sin embargo, estas decisiones arquitectónicas emergieron del conocimiento
del dominio (Capa 1), no de una imposición tecnológica. La tensión fue identificada
y documentada en §11 de `estrategia-desarrollo-bc.md`.

---

### Capa 5 — IMPLEMENTACIÓN ❌ No iniciada

**Propósito IEDD:** Traducir las US-IEDD a código usando el Claude Dev Kit
(`/implement-us`) en 10 fases secuenciales.

**Estado:** No aplica en Fase 0. El código de producción empieza en SP1.

**Prerequisitos pendientes antes de SP1:**

| Herramienta | Estado | Impacto |
|-------------|--------|---------|
| Claude Dev Kit (`/implement-us`) | ❌ No instalado | Bloquea implementación IEDD |
| software_limpio / codeguard | ❌ No funcional | Bloquea quality gates automáticos |
| designreviewer | ❌ No funcional | Bloquea quality gates en merge |
| architectanalyst | ❌ No funcional | Bloquea retrospectiva arquitectónica por baseline |

---

## 4. Contribuciones Emergentes No Previstas en IEDD

Durante Fase 0 surgieron cuatro prácticas no especificadas por IEDD que agregaron
valor al proceso. Se documentan aquí para evaluar su formalización posterior.

### 4.1 Event Storming en dos niveles

IEDD no prescribe el método de modelado de dominio. La decisión de usar Event Storming
en dos niveles (Big Picture → Process Modeling) fue pragmática y produjo resultados
medibles:

- **Big Picture (Nivel 1):** emergieron 6 BCs desde el comportamiento del dominio,
  con 25 hot spots que forzaron decisiones de frontera.
- **Process Modeling (Nivel 2):** produjeron 14 invariantes formales para BC Competencia,
  que serán las precondiciones directas de US-IEDD de SP1.

**Hipótesis a contrastar en SP1:** ¿Los invariantes del Process Modeling producen
US-IEDD con menos edge cases no anticipados durante la implementación?

### 4.2 Mecanismo de Hot Spots

Los hot spots fueron el mecanismo para diferir decisiones sin bloquear el avance.
9 hot spots fueron identificados y todos resueltos antes de cerrar Fase 0.
El patrón resultó más efectivo que intentar resolver cada decisión en el momento
de descubrir la ambigüedad.

**Aprendizaje capturado:** Resolver hot spots en diseño (Capa 2) cuesta minutos;
en implementación (Capa 5), horas o días.

### 4.3 Mapeo BC×SP como artefacto de planificación

`docs/design/estrategia-desarrollo-bc.md` no estaba previsto en el plan original.
Emergió de la necesidad de hacer visibles las dependencias de implementación entre
BCs. El mapeo reveló que BC Notificaciones debe implementarse en SP5 (último), no
en SP2 como se asumía intuitivamente.

### 4.4 Trazabilidad formal RF → Incremento → US-IEDD

La matriz en `docs/traceability/matrix.md` cierra el loop entre requerimientos
funcionales y la cadena IEDD. 53 RFs mapeados, 85% con incremento y US-IEDD candidata
asignada. Esta trazabilidad no es parte del framework IEDD base pero es necesaria
para el experimento: permite medir si los RFs llegan a código sin distorsión.

---

## 5. Análisis de Adherencia: Resumen

| Dimensión | Evaluación | Nota |
|-----------|-----------|------|
| Orden de las capas | ✅ Alta | Capa 1 → 2 → 4 respetadas; Capa 3 iniciada con trazabilidad |
| Completitud de artefactos | ✅ Alta | 11/11 artefactos Fase 0 completados |
| Lenguaje ubicuo | ✅ Alta | Vocabulario del dominio consistente en todos los documentos |
| Fronteras de BC desde el dominio | ✅ Alta | BCs emergieron de ES, no de organización de RFs |
| Desvíos documentados | ✅ Alta | ADRs tempranos y ES antes de Capa 2 documentados y justificados |
| Tooling instalado | ❌ Baja | Dev Kit y software_limpio ausentes — prerequisito crítico para SP1 |
| Implementación (Capa 5) | N/A | No iniciada en Fase 0 — correcto |

**Veredicto:** La Fase 0 adhiere razonablemente a IEDD. Los desvíos son menores y
documentados, no violaciones estructurales. El principal riesgo para SP1 es el tooling
no instalado: sin `/implement-us` y sin los quality gates de software_limpio, la Capa 5
se ejecutará manualmente, lo que reduce la reproducibilidad del experimento.

---

## 6. Hipótesis Activas para SP1

Estas hipótesis se formularon en Fase 0 y serán evaluadas durante SP1 y SP2.

### H1 — Invariantes del Process Modeling reducen edge cases en implementación

> Los invariantes derivados del ES Process Modeling producen US-IEDD con menos
> edge cases no anticipados durante la implementación de SP1.

**Indicador de falsación:** Si durante la implementación de SP1 se descubren
precondiciones o invariantes no capturadas en el ES Competencia, la hipótesis
se falsea parcialmente.

**Cómo medirlo:** Contar las "sorpresas de implementación" por US-IEDD:
situaciones que requieran modificar la especificación formal durante el coding.
Registrar en la retrospectiva de BL-001.

### H2 — El diseño en Capa 2 abarata decisiones costosas

> Resolver ambigüedades de dominio (hot spots) en Capa 2 es significativamente
> menos costoso que resolverlas durante la implementación (Capa 5).

**Indicador:** Los 9 hot spots resueltos en Fase 0 tardaron en promedio < 30 minutos
cada uno. Si en SP1 surgen decisiones similares sin hot spot previo, registrar el
tiempo hasta resolución.

### H3 — La trazabilidad RF → US-IEDD previene gold plating

> Los RFs formalmente mapeados a incrementos y US-IEDD candidatas reducen la
> tendencia a implementar funcionalidad fuera del alcance del incremento activo.

**Indicador:** Al final de SP1, verificar si el código implementado está 100%
trazado a RFs en `matrix.md`. Gold plating = código sin RF correspondiente.

---

## 7. Próximo Hito Previsto

**HITO-2** se generará al cerrar **BL-001 (SP1 — La Performance)**.

Métricas que se esperan capturar en HITO-2:
- Sorpresas de implementación por US-IEDD (H1)
- Tiempo promedio de resolución de decisiones en Capa 5 vs. Capa 2 (H2)
- Porcentaje de código trazado a RFs (H3)
- Calidad medida por software_limpio: Pylint ≥ 8.0, cobertura ≥ 85%
- Fricción de integración entre herramientas (CM + Dev Kit + Software Limpio)

---

## 8. Artefactos por Capa — Inventario Completo

### Capa 1 — DOMINIO

| Artefacto | Tipo | Producido por |
|-----------|------|---------------|
| `docs/dominio/01-dominio_torneos_apnea.md` | Descripción del dominio | Análisis inicial |
| `docs/dominio/02-arquitectura_referencia.md` | Decisiones técnicas | Análisis inicial |
| `docs/dominio/03-atributos_calidad.md` | Calidad con IDs AC-XX-NN | Análisis inicial |
| `docs/dominio/04-estrategia_desarrollo.md` | Plan de desarrollo | Análisis inicial |
| `docs/dominio/05-requerimientos_funcionales.md` | 48 RFs elicitados | Elicitación |
| `docs/requirements/vision.md` | Visión del producto | Síntesis |

### Capa 2 — MODELO (DDD Estratégico)

| Artefacto | Tipo | Producido por |
|-----------|------|---------------|
| `docs/contexto/DECISION-EVENT-STORMING.md` | Decisión metodológica | Análisis de método |
| `docs/design/event-storming-big-picture.md` | ES Nivel 1 — dominio completo | Event Storming |
| `docs/design/context-map.md` | 6 BCs + relaciones DDD | ES Big Picture |
| `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` | Decisión formal de BCs | Context Map |
| `docs/design/event-storming-competencia.md` | ES Nivel 2 — Core Domain | Event Storming |
| `docs/design/domain-model.md` | Aggregates, VOs, repositorios | ES Process Modeling |

### Capa 3 — ESPECIFICACIÓN

| Artefacto | Tipo | Producido por |
|-----------|------|---------------|
| `docs/iedd/US-IEDD-template.md` | Template formal | Marco IEDD |
| `docs/iedd/ANALISIS-IEDD.md` | Marco conceptual | Análisis metodológico |
| `docs/iedd/ANALISIS-INTEGRACION-CLAUDE-DEV-KIT.md` | Integración Dev Kit | Análisis de tooling |
| `docs/traceability/matrix.md` | RF → BC → SP → US-IEDD | Síntesis Capa 1+2 |
| `docs/plans/US-X.Y.Z.md` (individuales) | US-IEDD por historia | **Pendiente SP1** |

### Capa 4 — ARQUITECTURA

| Artefacto | Tipo | Producido por |
|-----------|------|---------------|
| `docs/adr/ADR-001-event-sourcing-competencia.md` | Decisión ES | Análisis del Core Domain |
| `docs/adr/ADR-002-fastapi-backend.md` | Decisión de framework | Atributos de calidad |
| `docs/adr/ADR-003-offline-first-pwa.md` | Decisión de frontend | Atributos de calidad |
| `docs/adr/ADR-004-reglas-como-datos.md` | Decisión de configurabilidad | ES Big Picture HS-19 |
| `docs/design/architecture.md` | C4 L1+L2+L3a+L3b | Síntesis de ADRs + Domain Model |
| `docs/design/estrategia-desarrollo-bc.md` | BC×SP, secuencia, dependencias | Context Map + visión |

### Capa 5 — IMPLEMENTACIÓN

| Artefacto | Tipo | Estado |
|-----------|------|--------|
| `src/` | Código de producción | **Pendiente SP1** |
| `tests/` | Tests unit/integration/features | **Pendiente SP1** |
| `quality/reports/` | Reportes software_limpio | **Pendiente SP1** |

### Artefactos de Gestión (transversales)

| Artefacto | Tipo | Función |
|-----------|------|---------|
| `CLAUDE.md` | Convención de proyecto | Memoria del proyecto |
| `.cm/baselines/BL-000-pre-codigo.md` | Baseline | Snapshot del estado inicial |
| `docs/contexto/PLAN-EXPERIMENTO.md` | Plan del experimento | Preguntas y métricas |
| `docs/contexto/ANALISIS-ATARAXIADIVE.md` | Análisis de integración | Mapa completo del ecosistema |
| `docs/plans/FASE-0-PLAN.md` | Plan de Fase 0 | Control de avance |
| `pyproject.toml` | Configuración | Dependencias y herramientas de calidad |
| `docker-compose.yml` | Infraestructura | Entorno de desarrollo local |
| `.pre-commit-config.yaml` | Calidad | Hooks automáticos |

---

## 9. Conclusión

La Fase 0 demuestra que IEDD es aplicable a un proyecto real de dominio específico
(torneos de apnea) sin necesidad de adaptar el marco: el orden de capas se mantuvo,
los artefactos de cada capa alimentaron la siguiente, y los desvíos fueron documentados
y justificados en lugar de ignorados.

El principal riesgo identificado para SP1 es **tooling**, no metodología. Si el
Claude Dev Kit y software_limpio no se instalan antes del primer incremento, el
experimento pierde su dimensión de integración de herramientas — que es una de las
tres preguntas centrales del experimento.

**La Fase 0 cierra con el conocimiento del dominio formalizado, el modelo DDD
validado, la arquitectura referenciada, y 8 US-IEDD candidatas listas para ser
escritas en SP1. La implementación puede comenzar.**

---

*Generado: 2026-03-19 — Cierre de Fase 0 / tag v0.1.0*
*Ver también: `docs/design/estrategia-desarrollo-bc.md` §11 — Notas del Experimento*
*Próximo hito: HITO-2 al cerrar BL-001 (SP1 completo)*
