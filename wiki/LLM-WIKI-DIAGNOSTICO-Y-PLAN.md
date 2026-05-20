# LLM Wiki para AtaraxiaDive
## Diagnóstico, Vistas y Plan de Implementación

> **Fecha:** Mayo 2026
> **Contexto:** Prueba de concepto para implementar el patrón LLM Wiki (Karpathy, abril 2026)
> como gestor de conocimiento de un proyecto de software, con foco en trazabilidad
> y análisis de impacto para mantenimiento.

---

## Parte I — Diagnóstico

### 1. El patrón y su aplicación al software

El patrón LLM Wiki propone una alternativa al RAG clásico: en lugar de que el LLM
*recupere* conocimiento de documentos raw en cada consulta, el LLM *construye y mantiene*
un wiki persistente sintetizado a partir de las fuentes. El conocimiento se compila una
vez y se acumula; las conexiones, contradicciones y síntesis ya están pre-construidas
cuando se necesitan.

Aplicado a un proyecto de software, las fuentes son el código, los tests, los documentos
de arquitectura, diseño, requerimientos, planificación y calidad. El valor diferencial
respecto al RAG clásico es que la trazabilidad y el análisis de impacto dejan de ser
una consulta costosa que se recalcula cada vez, y se convierten en una *lectura* de
páginas del wiki ya sintetizadas.

El rol del LLM en este sistema es el de **experto que propone, no que implementa**:
analiza, advierte, conecta y sugiere, pero la decisión y la ejecución quedan en el humano.

### 2. Riqueza de activos de AtaraxiaDive

AtaraxiaDive presenta una densidad documental excepcional para un proyecto individual.
Los activos relevantes para el wiki se distribuyen en las siguientes capas:

| Capa | Ubicación | Contenido |
|------|-----------|-----------|
| Decisiones | `docs/adr/` | ADR-001 a ADR-013+: contexto, opciones, decisión y consecuencias |
| Arquitectura | `docs/architecture/` | 14 documentos: sistema, contenedores, 6 BCs, mapa de contexto, runtime, cross-cutting, offline |
| Dominio | `docs/dominio/` | Descripción del dominio, atributos de calidad, RFs, estrategia de desarrollo |
| Metodología | `docs/iedd/` | Marco IEDD, templates de especificación |
| Trazabilidad | `docs/traceability/matrix.md` | RF → BC → SP → US → tests → estado de cobertura |
| Planes | `docs/plans/spN/` | Plan de implementación por US |
| Reportes | `docs/reports/` | Reporte de cierre por US con evidencia de calidad |
| Calidad | `quality/reports/` | Quality gate reports (CodeGuard, DesignReviewer, ArchitectAnalyst) |
| Estado | `.cm/baselines/` | Snapshots de estado del proyecto (BL-000, BL-001, BL-002...) |
| Contexto metodológico | `docs/contexto/` | 14+ HITOs con aprendizajes del proceso experimental |
| Memoria operativa | `CLAUDE.md` | Estado y convenciones del proyecto |
| Código | `src/` | BC-first: competencia/, torneo/, registro/, resultados/, identidad/, notificaciones/ |
| Tests | `tests/` | unit/, integration/, features/ (BDD), uat/ |

**Hallazgo clave:** el repositorio ya tiene `llms.txt` — un índice estructurado de toda
la documentación pensado para consumo por LLMs. Es el equivalente exacto al `index.md`
que Karpathy describe como núcleo del wiki. El proyecto ya tiene la semilla.

### 3. El dolor principal que el wiki resuelve

El análisis metodológico HITO-14 ya identificó el problema central del proyecto:

> **D-02 — Demasiadas fuentes de verdad para el estado del proyecto.**
> El estado aparece en README, CLAUDE.md, docs/plans, docs/reports, .cm/baselines,
> docs/traceability, y a veces en specs individuales. Impacto: onboarding confuso,
> análisis incorrecto por parte de agentes o humanos, pérdida de confianza en la
> documentación superficial.

> **D-03 — Documentación fundacional desalineada con la arquitectura vigente.**
> Partes del proyecto siguen hablando de PostgreSQL mientras el stack real ya
> consolidó SQLite por BC.

El LLM Wiki es la solución directa a ambos problemas. La wiki sintetiza las múltiples
fuentes en páginas coherentes y unificadas. La operación de *lint* detecta y expone
inconsistencias como D-03 de forma sistemática y continua.

### 4. Dimensión adicional: AtaraxiaDive como laboratorio

El proyecto tiene una segunda naturaleza documentada en `docs/contexto/PLAN-EXPERIMENTO.md`:
es un experimento de investigación cuyos aprendizajes alimentan productos intelectuales
de largo plazo (libro DDD, curso IS, material de gestión, paper IEDD). Existe una
"matriz de conocimiento" que mapea cada aprendizaje del proyecto a capítulos y sesiones
específicas de esos productos.

El LLM Wiki puede cumplir un doble rol: gestor de conocimiento del software *y*
gestor de conocimiento de investigación, actuando como el eslabón que conecta
los hallazgos del proyecto con los productos intelectuales.

---

## Parte II — Vistas del Segundo Cerebro

### El concepto: un grafo, múltiples mapas de lectura

En Arquitectura de Software, el modelo de vistas (Kruchten 4+1, C4, Rozanski & Woods)
establece que el mismo sistema puede y debe describirse desde múltiples perspectivas.
Cada vista no es un sistema diferente — son los mismos componentes vistos con un lente
distinto, respondiendo a las preguntas de un stakeholder específico.

Aplicado al LLM Wiki, la misma idea se vuelve estructural: **las páginas del wiki no
cambian según quién consulta, pero los puntos de entrada y los recorridos sí**. No es
un wiki diferente por cada vista — son los mismos nodos del grafo de conocimiento
navegados con un mapa distinto.

En la práctica, cada vista es una página `wiki/vistas/<nombre>.md` que el LLM mantiene
como un recorrido sugerido con sus preguntas características. Cuando llega una consulta,
el LLM identifica qué vista es la más relevante y entra al grafo desde ese ángulo.

```
wiki/
└── vistas/
    ├── dominio.md           ← ¿Qué hace el sistema? ¿Cuál es su lenguaje?
    ├── decisiones.md        ← ¿Por qué se construyó así?
    ├── trazabilidad.md      ← ¿Qué implementa cada requerimiento?
    ├── impacto.md           ← ¿Qué se rompe si cambio X?
    ├── salud.md             ← ¿Qué tan bien está el proyecto?
    └── investigacion.md     ← ¿Qué aprendimos y para qué sirve?
```

### Vista de Dominio

**Propósito:** El sistema visto desde el negocio y el lenguaje ubicuo.

**Stakeholder:** Domain expert, nuevo integrante del equipo, product owner.

**Punto de entrada:** Los seis Bounded Contexts como unidades de responsabilidad
de negocio, los conceptos del lenguaje ubicuo, las reglas del deporte de apnea.

**Preguntas características:**
- ¿Qué hace el sistema?
- ¿Qué significa Performance en el contexto de AtaraxiaDive?
- ¿Qué diferencia hay entre Torneo y Competencia?
- ¿Qué es una Grilla y cómo se relaciona con una Disciplina?
- ¿Quiénes son los actores y qué puede hacer cada uno?

**Recorrido típico:**
`conceptos/performance.md` → `bounded-contexts/competencia.md` →
`conceptos/grilla.md` → `bounded-contexts/torneo.md`

**Relación con activos existentes:** Se construye principalmente a partir de
`docs/dominio/`, `docs/architecture/03-bounded-contexts.md` y el lenguaje ubicuo
implícito en los nombres del código fuente.

---

### Vista de Decisiones

**Propósito:** El sistema visto desde su historia de razonamiento técnico.

**Stakeholder:** Arquitecto, desarrollador senior, quien va a tomar la próxima
decisión técnica.

**Punto de entrada:** Los ADRs agrupados por área de impacto (persistencia,
frontend, arquitectura interna, calidad, despliegue), con sus relaciones entre sí
y el estado vigente de cada decisión.

**Preguntas características:**
- ¿Por qué SQLite y no PostgreSQL?
- ¿Qué alternativas se descartaron para el frontend y por qué?
- ¿Cuál es la justificación del Event Sourcing solo en dos BCs?
- ¿Qué ADRs impactan al BC Competencia?
- ¿Hay decisiones que se contradicen entre sí?

**Recorrido típico:**
`decisiones/ADR-007-sqlite.md` → `decisiones/ADR-008-event-store.md` →
`bounded-contexts/competencia.md` → `decisiones/ADR-001-event-sourcing.md`

**Valor específico para AtaraxiaDive:** Los ADRs del proyecto documentan decisiones
no triviales (Event Sourcing, Offline-first PWA, reglas como datos). Esta vista evita
que ese razonamiento se pierda y que futuras sesiones de trabajo rehagan el análisis
desde cero.

---

### Vista de Trazabilidad

**Propósito:** El sistema visto desde los requerimientos hacia la implementación.

**Stakeholder:** QA, auditor, desarrollador implementando un cambio.

**Punto de entrada:** Los Requerimientos Funcionales (RF), con un recorrido descendente
hacia la US que los implementa, el código que los materializa, los tests que los
verifican y el reporte que los cierra.

**Preguntas características:**
- ¿Qué US implementa el requerimiento RF-CO-03?
- ¿Qué tests cubren la historia US-3.3.1?
- ¿Hay requerimientos sin tests asociados?
- ¿Qué archivos de código implementan el registro de performance?
- ¿Está cerrada y verificada la US-3.5.1?

**Recorrido típico:**
`trazabilidad/RF-CO-03.md` → `trazabilidad/US-3.3.1.md` →
`bounded-contexts/competencia.md` → tests asociados en matrix

**Valor específico para AtaraxiaDive:** La `docs/traceability/matrix.md` ya existe
pero es tabular y estática. Esta vista la convierte en navegable y viva, con los
reportes de cierre accesibles desde cada US.

---

### Vista de Impacto

**Propósito:** El sistema visto desde las dependencias y el riesgo de cambio.

**Stakeholder:** Desarrollador planificando una modificación, tech lead evaluando
el alcance de una tarea.

**Punto de entrada:** Un componente, una interfaz, un evento de dominio, o un ADR,
y desde ahí hacia quién lo consume, quién lo publica, qué tests lo cubren, qué
cambios en cascada generaría su modificación.

**Preguntas características:**
- Si cambio la interfaz de `EventStorePort`, ¿qué módulos se ven afectados?
- ¿Qué BCs dependen del BC Identidad para funcionar?
- ¿Qué tests fallarían si modifico el aggregate Performance?
- ¿Qué documentos habría que actualizar si cambia el esquema del Event Store?
- ¿Cuál es el componente de mayor acoplamiento en el sistema?

**Recorrido típico:**
`impacto/EventStorePort.md` → `bounded-contexts/competencia.md` →
`bounded-contexts/notificaciones.md` → `decisiones/ADR-008-event-store.md`

**Valor específico para AtaraxiaDive:** Esta vista **no existe** en la documentación
actual del proyecto. Es la de mayor valor para mantenimiento y la que el wiki crearía
desde cero al sintetizar las relaciones entre páginas de BC, ADRs y código.

---

### Vista de Salud

**Propósito:** El sistema visto desde la deuda técnica, la calidad y la consistencia
entre lo que el proyecto dice ser y lo que realmente es.

**Stakeholder:** Tech lead, responsable de calidad, Victor evaluando el experimento.

**Punto de entrada:** Resultados del último lint del wiki, quality gate reports,
métricas de cobertura por BC, inconsistencias detectadas entre fuentes.

**Preguntas características:**
- ¿Qué requerimientos no tienen tests asociados?
- ¿Qué documentos están desalineados con la arquitectura vigente?
- ¿Qué BCs tienen deuda técnica acumulada según los quality gates?
- ¿Hay conceptos usados en el código sin página propia en el wiki?
- ¿Cuál es la tendencia de calidad entre BL-001 y BL-002?

**Recorrido típico:**
`salud/lint-actual.md` → `bounded-contexts/competencia.md` →
`trazabilidad/US-pendientes.md` → `decisiones/ADRs-desalineados.md`

**Valor específico para AtaraxiaDive:** Resuelve directamente D-02 y D-03 de
HITO-14. La salud del proyecto deja de ser una percepción distribuida en múltiples
documentos y se convierte en una página actualizada por cada lint.

---

### Vista de Investigación *(única en este proyecto)*

**Propósito:** El sistema visto como fuente de conocimiento para productos
intelectuales de largo plazo.

**Stakeholder:** Victor como investigador y autor.

**Punto de entrada:** Las hipótesis del PLAN-EXPERIMENTO, los HITOs metodológicos,
los aprendizajes por subproyecto, y desde ahí hacia cómo cada hallazgo alimenta
el libro DDD, el curso de IS, el paper IEDD o el material de gestión.

**Preguntas características:**
- ¿Qué aprendimos sobre Event Sourcing en AtaraxiaDive que pueda ir al libro DDD?
- ¿Qué evidencia empírica tiene la metodología IEDD para el paper?
- ¿Qué casos prácticos del proyecto sirven para el curso de IS semana 4?
- ¿Qué dice el experimento sobre la fricción de consistencia documental?
- ¿Qué aprendizajes del SP3 son generalizables a otros proyectos DDD?

**Recorrido típico:**
`investigacion/aprendizajes-event-sourcing.md` →
`investigacion/matriz-conocimiento.md` →
`investigacion/hipotesis-iedd.md` → `contexto/HITOs`

**Valor específico para AtaraxiaDive:** No tiene equivalente en la literatura de
arquitectura. Es la vista que transforma el wiki de herramienta de desarrollo
en herramienta de producción intelectual, materializando la "matriz de conocimiento"
del PLAN-EXPERIMENTO de forma navegable y actualizada.

---

### Tabla resumen de vistas

| Vista | Stakeholder principal | Pregunta central | Activos clave que la alimentan |
|-------|----------------------|-----------------|-------------------------------|
| Dominio | Domain expert, nuevo integrante | ¿Qué hace el sistema? | docs/dominio/, docs/architecture/ |
| Decisiones | Arquitecto, dev senior | ¿Por qué se construyó así? | docs/adr/ |
| Trazabilidad | QA, auditor, desarrollador | ¿Qué implementa cada RF? | matrix.md, plans/, reports/ |
| Impacto | Dev planificando cambios | ¿Qué se rompe si cambio X? | src/, tests/, docs/adr/ (inferido) |
| Salud | Tech lead, investigador | ¿Qué tan bien está el proyecto? | quality/reports/, lint del wiki |
| Investigación | Victor como autor | ¿Qué aprendimos? | docs/contexto/, HITO-*, PLAN-EXPERIMENTO |

---

## Parte III — Plan de Implementación

### Estructura objetivo del repositorio

```
ataraxiadive/
├── sources/                      ← Fuentes brutas (inmutables para el wiki)
│   ├── dominio/                  → docs/dominio/
│   ├── iedd/                     → docs/iedd/
│   ├── adr/                      → docs/adr/
│   ├── architecture/             → docs/architecture/
│   └── contexto/                 → docs/contexto/
├── sources-live/                 ← Fuentes que evolucionan con el código
│   ├── plans/                    → docs/plans/
│   ├── reports/                  → docs/reports/
│   ├── baselines/                → .cm/baselines/
│   ├── traceability/             → docs/traceability/
│   └── quality/                  → quality/reports/
├── wiki/                         ← Generado y mantenido por el LLM (no editar)
│   ├── index.md                  → Catálogo de todas las páginas
│   ├── log.md                    → Registro cronológico append-only
│   ├── bounded-contexts/         → Una página por BC
│   ├── decisiones/               → Una página por ADR (síntesis vigente)
│   ├── trazabilidad/             → Una página por US (ciclo completo)
│   ├── conceptos/                → Lenguaje ubicuo del dominio
│   ├── impacto/                  → Páginas de análisis de dependencias
│   ├── estado/                   → Estado actual del proyecto (única fuente)
│   ├── salud/                    → Resultados de lint
│   ├── investigacion/            → Aprendizajes y matriz de conocimiento
│   └── vistas/                   → Puntos de entrada por perspectiva (6 archivos)
└── WIKI.md                       ← Schema: convenciones y vistas para el LLM
```

### Categorías de páginas del wiki

**Páginas de Bounded Context** (6 páginas)
Sintetizan: responsabilidades, modelo de dominio, persistencia, eventos
publicados/consumidos, ADRs que lo gobiernan, US implementadas y pendientes,
tests y cobertura. Son el nodo hub del grafo — todas las vistas pasan por ellas.

**Páginas de decisión** (una por ADR)
Reescriben cada ADR en clave de "consecuencias vigentes", no solo de "decisión
tomada". El wiki actualiza la página si decisiones posteriores modificaron el
estado de la anterior (ej: ADR-002 menciona PostgreSQL pero ADR-007 lo reemplazó).

**Páginas de trazabilidad por US** (una por US cerrada)
Ciclo completo: requerimiento origen → criterios BDD → implementación (archivos
clave) → tests → quality gates → reporte de cierre.

**Páginas de conceptos del dominio**
Performance, Torneo, Atleta, Grilla, Tarjeta, Disciplina y demás términos del
lenguaje ubicuo, con invariantes, eventos y BC responsable.

**Páginas de impacto** (generadas por inferencia del LLM)
Documentan los puntos de acoplamiento del sistema: qué interfaces son críticas,
qué cambios tienen efecto en cascada, cuáles son los nodos de mayor riesgo.

**Página de estado del proyecto** (única fuente de verdad)
SP activo, US cerradas, US en progreso, baseline vigente, próximas entregas.
Solución directa a D-02.

**Páginas de investigación**
Aprendizajes por subproyecto mapeados a productos intelectuales, hipótesis del
experimento con su estado de verificación.

**Páginas de vistas** (6 páginas — una por perspectiva)
Puntos de entrada al grafo de conocimiento según el ángulo de consulta.
No duplican contenido: organizan recorridos sobre las páginas existentes.

**Páginas de salud** (resultado del lint periódico)
Inconsistencias detectadas, documentos desalineados, gaps de trazabilidad,
sugerencias de fuentes a ingestar.

---

### Fase 0 — Preparación (prerequisito) ✅ Completada

Resolver los gaps que degradarían la calidad del wiki antes del primer ingest.

**G-01 — Archivar documentos pre-ADR desalineados**

Agregar encabezado explícito en documentos de `docs/dominio/` que mencionan
PostgreSQL o decisiones ya superadas:

```markdown
> ⚠️ **Documento histórico.** Refleja el estado del proyecto anterior a ADR-007.
> Para arquitectura vigente, ver `docs/architecture/`.
```

**G-02 — Declarar jerarquía de verdad en CLAUDE.md**

```markdown
## Jerarquía de fuentes de verdad

Ante conflicto entre documentos, prevalece en este orden:
1. `.cm/baselines/` y `docs/reports/` — evidencia empírica de cierre de US
2. `docs/architecture/` y `docs/adr/` — arquitectura y decisiones vigentes
3. `CLAUDE.md` — memoria operativa
4. `README.md` — orientación general (no mantiene estado fino)

Documentos marcados como "históricos" no representan el estado actual.
```

**G-03 — Crear WIKI.md con schema inicial**

Definir tipos de páginas, convenciones de naming, wikilinks, comportamiento
ante contradicciones, y las seis vistas disponibles con sus preguntas
características. Ver Apéndice A para el contenido completo.

---

### Fase 1 — Ingest fundacional 🔄 En progreso (5/7 fuentes)

**Objetivo:** Construir el grafo base de conocimiento a partir de fuentes inmutables.

**Fuentes a ingestar (en orden):**

| Orden | Fuente | Páginas wiki generadas | Estado |
|-------|--------|------------------------|--------|
| 1 | `docs/dominio/01-dominio_torneos_apnea.md` | 8 conceptos de dominio (torneo, performance, disciplina, grilla, atleta, anuncio, tarjeta, roles) | ✅ |
| 2 | `docs/dominio/03-atributos_calidad.md` | 1 página (atributos-calidad); enriquece mapa ADR→BC | ✅ |
| 3 | `docs/dominio/05-requerimientos_funcionales.md` | 8 semillas de trazabilidad por área RF; enriquece 3 conceptos | ✅ |
| 4 | `docs/iedd/` | Marco metodológico (referencia para vista de investigación) | ✅ |
| 5 | `docs/adr/ADR-001..022` | 22 páginas de decisión (una por ADR) | ✅ |
| 6 | `docs/architecture/` (todos) | Páginas de BC (una por BC), mapa de contexto | ⏳ |
| 7 | `docs/contexto/ANALISIS-*.md` | Enriquecimiento de BCs y vista de investigación | ⏳ |

Al final del ingest de cada fuente, el LLM actualiza `wiki/index.md` y agrega
una entrada en `wiki/log.md`.

**Progreso actual:** 42 páginas creadas (9 conceptos, 8 semillas RF, 3 investigación, 22 decisiones).

**Resultado esperado:** ~35-45 páginas wiki, BCs documentados con ADRs vinculados,
lenguaje ubicuo del dominio capturado, `index.md` navegable.

---

### Fase 2 — Construcción de vistas

**Objetivo:** Crear los seis puntos de entrada una vez que hay suficientes páginas base.

Esta fase es nueva respecto al plan original y es la que habilita el acceso
multi-perspectiva al wiki.

**Instrucción al LLM por cada vista:**

```
Leé wiki/index.md completo. Creá wiki/vistas/<nombre-vista>.md con:
- Propósito de la vista (una oración)
- Stakeholder al que sirve
- Las 5 preguntas características que responde
- Un recorrido sugerido de 4-6 páginas del wiki para cada pregunta tipo
- Lista de páginas hub que esta vista usa con más frecuencia
```

**Orden sugerido:** Dominio → Decisiones → Trazabilidad → Salud → Impacto → Investigación.

La Vista de Impacto se genera al final porque requiere inferir relaciones entre
páginas, no solo catalogarlas.

**Resultado esperado:** 6 páginas de vistas operativas, cada una usable como
instrucción de contexto al inicio de una sesión de consulta especializada.

---

### Fase 3 — Ingest de estado

**Objetivo:** Poblar el wiki con el estado real de implementación del proyecto.

| Fuente | Páginas wiki generadas / actualizadas |
|--------|---------------------------------------|
| `docs/traceability/matrix.md` | Páginas de trazabilidad por US, actualización de BCs |
| `docs/reports/US-*.md` | Enriquecimiento de páginas US con evidencia de cierre |
| `.cm/baselines/BL-*.md` | Página de estado del proyecto |
| `quality/reports/` | Métricas de salud por BC en páginas de BC |
| `docs/contexto/HITO-*.md` | Páginas de investigación: aprendizajes por subproyecto |

**Resultado esperado:** Página de estado unificada (solución a D-02), trazabilidad
RF → código → tests navegable, vista de investigación poblada con hallazgos reales.

---

### Fase 4 — Primer lint

**Objetivo:** Detectar inconsistencias heredadas y generar la primera página de salud.

**Instrucción al LLM:**

```
Auditá el wiki completo. Generá wiki/salud/lint-001.md con:
1. Páginas que mencionan PostgreSQL como tecnología vigente
2. ADRs con estado contradictorio entre sí o con la arquitectura actual
3. Requerimientos en la matriz de trazabilidad sin página US en el wiki
4. BCs sin cobertura de tests registrada
5. Páginas de impacto con dependencias inferidas que requieren validación
6. Conceptos del dominio usados en el código sin página propia en wiki/conceptos/
7. Páginas huérfanas (sin ningún enlace entrante desde otras páginas)
8. Sugerencias de nuevas fuentes a ingestar para llenar los gaps detectados
```

**Resultado esperado:** Primera radiografía honesta del estado real del conocimiento
del proyecto. Esta página es la que le presenta al experto qué investigar y qué
proponer como acciones de mejora.

---

### Fase 5 — Operación continua

El sistema opera con tres comandos regulares más el uso de vistas como contexto:

**`/wiki-ingest [fuente]`**
Ingestar una nueva fuente. El LLM lee el documento o diff, determina qué páginas
impacta y las actualiza. Actualiza `index.md` y `log.md`. Una fuente puede tocar
5-15 páginas.

**`/wiki-query [pregunta]`**
Consultar el wiki. El LLM identifica la vista más relevante, entra al grafo desde
ese ángulo, lee las páginas pertinentes y sintetiza una respuesta con citas.
Si la respuesta es valiosa, la archiva como nueva página (las consultas componen).

*Ejemplos de consultas de valor para mantenimiento:*
- "¿Qué componentes se ven afectados si cambio la interfaz del EventStore?" → Vista de Impacto
- "¿Qué ADRs son relevantes para implementar notificaciones push?" → Vista de Decisiones
- "¿Qué tests cubren el flujo de registro de performance con tarjeta roja?" → Vista de Trazabilidad
- "¿Qué aprendimos sobre Event Sourcing para el libro DDD?" → Vista de Investigación

**`/wiki-lint`**
Auditoría periódica de salud. Actualiza `wiki/salud/`. Sugiere nuevas fuentes a
ingestar para llenar vacíos detectados.

**Uso de vistas como contexto de sesión:**
Al iniciar una sesión de trabajo especializada, se puede precargar la vista
correspondiente como contexto inicial del LLM:

```
Leé wiki/vistas/impacto.md. A partir de ahora respondé consultas desde
esa perspectiva usando el wiki como base de conocimiento.
```

---

### Triggers de sincronización (post-POC)

Una vez validado el POC manualmente, automatizar el ingest ante eventos semánticos:

| Evento | Acción wiki |
|--------|-------------|
| Merge a main con cambios en `docs/adr/` | Reingestar ADR → actualizar página de decisión y BCs afectados |
| Merge a main con cambios en `src/` o `tests/` | Actualizar páginas de BC y de impacto afectadas |
| Nuevo reporte en `docs/reports/` | Ingestar report → crear/actualizar página de trazabilidad US |
| Nuevo baseline en `.cm/baselines/` | Actualizar página de estado del proyecto |
| Nuevo ADR | Crear página de decisión → lint de páginas que podrían verse afectadas |
| Cierre de SP | Ingestar HITOs del SP → actualizar vista de investigación |

---

### Hitos del POC

| Hito | Entregable | Criterio de éxito | Estado |
|------|------------|-------------------|--------|
| H-0 | Gaps G-01/02/03 resueltos | CLAUDE.md con jerarquía de verdad, WIKI.md creado | ✅ |
| H-1 | Ingest fundacional completo | 35+ páginas wiki, BCs documentados, index.md navegable | 🔄 42/35+ páginas, 5/7 fuentes |
| H-2 | Vistas construidas | 6 páginas de vistas operativas, recorridos validados | ⏳ |
| H-3 | Ingest de estado completo | Página de estado unificada, trazabilidad por US visible | ⏳ |
| H-4 | Primer lint ejecutado | Página de salud con inconsistencias identificadas | ⏳ |
| H-5 | Primera consulta de impacto | Respuesta fundamentada archivada como página del wiki | ⏳ |
| H-6 | Evaluación del POC | ¿El wiki reduce la fricción de análisis de impacto? ¿Son útiles las vistas? | ⏳ |

---

## Apéndice A — Schema inicial para WIKI.md

```markdown
# WIKI.md — Convenciones del LLM Wiki de AtaraxiaDive

## Rol del LLM
Sos el mantenedor del wiki y el experto del proyecto. Tu trabajo es construir
y mantener páginas markdown que sintetizan el conocimiento de AtaraxiaDive.
No implementás código. Analizás, proponés y documentás.

## Jerarquía de fuentes
Ante conflicto entre fuentes, prevalece:
baselines/reports > architecture/adr > CLAUDE.md > README
Los documentos marcados como "históricos" no representan el estado vigente.

## Tipos de páginas y ubicaciones
- wiki/bounded-contexts/<nombre-bc>.md
- wiki/decisiones/ADR-NNN-<slug>.md
- wiki/trazabilidad/US-<id>.md
- wiki/conceptos/<concepto>.md
- wiki/impacto/<componente-o-interfaz>.md
- wiki/estado/proyecto.md
- wiki/investigacion/<aprendizaje-o-hipotesis>.md
- wiki/salud/lint-<NNN>.md
- wiki/vistas/<nombre-vista>.md

## Frontmatter obligatorio por tipo
Todas las páginas incluyen:
  title, type, last_updated, sources[]

BCs además incluyen:
  bc_name, persistence_style, adrs[], us_count, test_coverage

US además incluyen:
  us_id, bc, sp, estado, tests_count, report_path

## Wikilinks
Siempre usar [[nombre-de-pagina]] para referencias entre páginas.
Nunca usar rutas relativas directas a docs/ desde el wiki.

## Vistas disponibles
Al recibir una consulta, identificá la vista más relevante y navegá el grafo
desde ese ángulo:

| Vista | Cuándo usarla |
|-------|--------------|
| dominio | Preguntas sobre qué hace el sistema, conceptos, actores |
| decisiones | Preguntas sobre por qué se construyó algo de cierta manera |
| trazabilidad | Preguntas sobre qué implementa un requerimiento o qué tests cubren algo |
| impacto | Preguntas sobre consecuencias de un cambio o dependencias |
| salud | Preguntas sobre calidad, deuda técnica, inconsistencias |
| investigacion | Preguntas sobre aprendizajes, experimento, productos intelectuales |

## Operación de ingest
1. Leer la fuente completa.
2. Identificar entidades, conceptos, decisiones y relaciones nuevas o modificadas.
3. Crear o actualizar páginas afectadas (5-15 páginas por fuente típicamente).
4. Actualizar wiki/index.md.
5. Agregar en wiki/log.md: ## [YYYY-MM-DD] ingest | <nombre-fuente>

## Operación de lint
1. Leer wiki/index.md completo.
2. Verificar consistencia entre páginas.
3. Identificar gaps: requerimientos sin tests, BCs sin cobertura, páginas huérfanas.
4. Generar wiki/salud/lint-NNN.md con hallazgos y acciones sugeridas.
5. Nunca modificar sources/ ni sources-live/. Solo modificar wiki/.
```

---

*Documento generado con Claude Cowork — Mayo 2026*
*Basado en exploración directa del repositorio vvalotto/ataraxiadive*
*Versión 2 — incorpora modelo de vistas arquitectónicas*
