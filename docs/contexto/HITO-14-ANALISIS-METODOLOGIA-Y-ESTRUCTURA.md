# HITO-14 — Análisis crítico de la metodología propuesta y de la estructura real del proyecto

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-14 — Fortalezas y debilidades del sistema metodológico y estructural |
| **Fecha** | 2026-03-31 |
| **Sprint** | SP3 en curso — revisión meta-metodológica |
| **Relacionado** | `docs/contexto/PLAN-EXPERIMENTO.md` · `docs/contexto/ANALISIS-IEDD.md` · `docs/plans/WORKFLOW-DESARROLLO.md` · `CLAUDE.md` |

---

## Propósito

Este hito registra una evaluación crítica de dos planos que en AtaraxiaDive no pueden
separarse:

1. La **metodología propuesta** para desarrollar el sistema con IA
2. La **estructura real del proyecto**, observada en documentación y código

El objetivo no es juzgar si el enfoque "sirve" o "no sirve", sino identificar:

- qué partes ya muestran valor claro
- qué partes generan fricción, deuda o contradicción
- qué acciones concretas conviene ejecutar para fortalecer el experimento

---

## Síntesis ejecutiva

La metodología tiene una fortaleza conceptual poco común: no es una lista de buenas
prácticas, sino un sistema explícito que conecta dominio, modelo, especificación,
arquitectura, implementación, quality gates y memoria del producto.

La estructura del repositorio acompaña bastante bien esa intención: hay bounded contexts
reales, trazabilidad documental, reportes por US, líneas base y una cantidad no menor
de código y tests.

La principal debilidad no está en la idea sino en su operación cotidiana:

- hay más de una fuente de verdad para el estado del proyecto
- la herramienta táctica principal (`/implement-us`) no modela naturalmente la arquitectura real
- algunas reglas metodológicas declaradas como absolutas no se cumplen estrictamente en el código
- parte de la documentación fundacional y operativa quedó desalineada respecto del estado actual

La consecuencia es clara: el proyecto es fuerte como laboratorio metodológico, pero
necesita reducir fricción y consolidar una fuente de verdad operativa si quiere sostener
esa fortaleza a medida que crece.

---

## Fortalezas

### 1. La metodología tiene una tesis fuerte y verificable

La cadena IEDD no aparece como retórica vaga, sino como una transformación explícita
`dominio → modelo → especificación → arquitectura → implementación`, con hipótesis
observables sobre calidad y fricción del proceso.

**Evidencia:**
- `docs/contexto/PLAN-EXPERIMENTO.md`
- `docs/contexto/ANALISIS-IEDD.md`

**Valor concreto:**
- obliga a pensar antes de implementar
- hace visible dónde aparece la ambigüedad
- permite evaluar no solo el software, sino el proceso que lo produce

---

### 2. El dominio elegido es especialmente bueno para el experimento

AtaraxiaDive no es un CRUD trivial. Tiene estados, eventos, reglas del deporte,
restricciones temporales, calidad offline y trazabilidad fuerte.

**Evidencia:**
- `docs/contexto/ANALISIS-ATARAXIADIVE.md`
- `docs/dominio/01-dominio_torneos_apnea.md`
- `docs/dominio/05-requerimientos_funcionales.md`

**Valor concreto:**
- da material real para DDD
- justifica invariantes y eventos de dominio
- permite poner a prueba si la metodología mejora la precisión conceptual

---

### 3. La jerarquía de trabajo está bien definida

Subproyecto, incremento, US-IEDD, fases del kit, baseline, UAT y quality gates tienen
lugar explícito en el sistema.

**Evidencia:**
- `docs/plans/WORKFLOW-DESARROLLO.md`
- `CLAUDE.md`

**Valor concreto:**
- baja ambigüedad operativa
- hace más fácil cerrar trabajo en unidades verificables
- mejora la trazabilidad entre planificación, implementación y cierre

---

### 4. El repositorio expresa bastante bien la idea BC-first

La estructura de `src/` ya materializa bounded contexts reales y separa capas con un
orden razonable.

**Evidencia estructural:**
- `src/competencia/`
- `src/torneo/`
- `src/registro/`
- `src/identidad/`
- `src/resultados/`
- `src/shared/`

**Valor concreto:**
- facilita razonamiento por contexto
- limita el tamaño conceptual de cada módulo
- hace más factible mantener coherencia DDD a medida que crece el sistema

---

### 5. El proceso ya produce artefactos útiles, no solo intención metodológica

Hay evidencia de ejecución real: reportes, baselines, tests unitarios, tests de
integración, BDD, UAT y tracking de USs.

**Evidencia:**
- `.cm/baselines/BL-001-sp1-la-performance.md`
- `.cm/baselines/BL-002.md`
- `docs/reports/`
- `tests/unit/`, `tests/integration/`, `tests/features/`, `tests/uat/`
- `.claude/tracking/`

**Valor concreto:**
- el marco no quedó solo en documentos
- existe evidencia empírica utilizable para retrospectiva o paper
- el proyecto ya puede auditar parte de su propia historia

---

### 6. Hay una intención seria de medir calidad en distintos niveles

La combinación CodeGuard + DesignReviewer + ArchitectAnalyst da un esquema de control
por capas temporalmente bien pensado.

**Evidencia:**
- `docs/contexto/ANALISIS-SOFTWARE-LIMPIO.md`
- `pyproject.toml`
- `quality/reports/`

**Valor concreto:**
- hace visible deuda que un proyecto solitario normalmente dejaría pasar
- introduce feedback objetivo en diseño y arquitectura
- fortalece el valor experimental del proyecto

---

## Debilidades y acciones recomendadas

### D-01. Exceso de carga metodológica y documental

El sistema completo combina IEDD, CM, Dev Kit, quality agents, tracking, reportes,
baselines, HITO, specs, plans y UAT. El riesgo no es conceptual sino operacional:
que el costo de sostener el marco termine compitiendo con el avance del producto.

**Evidencia:**
- la cantidad de artefactos por US e incremento es alta
- varias piezas del sistema requieren mantenimiento simultáneo
- ya hay señales de desalineación entre documentos de entrada y estado real

**Impacto:**
- fatiga de mantenimiento
- mayor probabilidad de documentos obsoletos
- más tiempo gastado en coordinación que en reducir incertidumbre real

**Acciones recomendadas:**
1. Definir un conjunto explícito de artefactos `obligatorios`, `opcionales` y `derivados`.
2. Reducir la necesidad de actualización manual en artefactos redundantes.
3. Designar una única fuente de verdad por tipo de información:
   estado del proyecto, arquitectura vigente, workflow, implementación cerrada.
4. Ejecutar una poda metodológica al cierre de SP3:
   qué artefactos aportaron valor real y cuáles solo agregaron costo.

---

### D-02. Hay demasiadas fuentes de verdad para el estado del proyecto

El estado aparece en `README`, `CLAUDE.md`, `docs/plans`, `docs/reports`,
`.cm/baselines`, `docs/traceability` y a veces en specs individuales.

**Evidencia:**
- `README.md` declara SPs pendientes
- `CLAUDE.md` describe un estado más avanzado
- reportes y código muestran implementación ya cerrada de varias US

**Impacto:**
- onboarding confuso
- análisis incorrecto por parte de agentes o humanos
- pérdida de confianza en la documentación superficial

**Acciones recomendadas:**
1. Declarar formalmente una jerarquía de verdad:
   `baseline/reportes > CLAUDE.md > README`.
2. Simplificar el `README` para que no mantenga estado fino del roadmap.
3. Mover el estado detallado del proyecto a un único documento operativo.
4. Revisar al cierre de cada SP qué documentos deben actualizarse sí o sí y cuáles no.

---

### D-03. La documentación fundacional y operativa quedó desalineada con la arquitectura vigente

Partes del proyecto siguen hablando de PostgreSQL y de flujos previos, mientras la
arquitectura vigente del código y de varios ADRs ya consolidó SQLite por BC.

**Evidencia:**
- `README.md`
- `docker-compose.yml`
- `docs/dominio/02-arquitectura_referencia.md`
- `docs/dominio/04-estrategia_desarrollo.md`

**Impacto:**
- falsa comprensión del stack real
- posibilidad de intentar correr el proyecto con instrucciones incorrectas
- ruido en la evidencia del experimento

**Acciones recomendadas:**
1. Ejecutar un `SP-ADJ-doc` focalizado en “consistencia documental operativa”.
2. Actualizar o archivar explícitamente los documentos pre-ADR que ya no son vigentes.
3. Agregar una convención visible:
   `documento fundacional`, `documento vigente`, `documento histórico`.
4. Corregir primero los puntos de mayor impacto:
   `README.md`, `docker-compose.yml`, documentos de estrategia y arquitectura de referencia.

---

### D-04. `/implement-us` no encaja naturalmente con la arquitectura real de AtaraxiaDive

La herramienta táctica principal trabaja con un perfil `fastapi-rest` orientado a
layered architecture, mientras el proyecto declara BC-first + hexagonal + DDD.

**Evidencia:**
- `docs/contexto/IMPLEMENT-US-DISCREPANCIAS.md`
- `./.claude/skills/implement-us/`

**Impacto:**
- paths y convenciones equivocadas
- generación de componentes conceptualmente incorrectos
- necesidad de adaptación manual frecuente
- fricción precisamente en la herramienta que debería bajar fricción

**Acciones recomendadas:**
1. Crear un perfil específico `ataraxiadive-fastapi-hexagonal` o equivalente.
2. Reescribir la Fase 0 para que lea contexto real del repo antes de planificar o generar.
3. Ajustar templates y paths del kit a:
   `src/<bc>/domain|application|infrastructure|api`
   y `tests/unit/<bc>/`, `tests/integration/<bc>/`.
4. Tratar esta adaptación como artefacto experimental central del proyecto, no como parche local.

---

### D-05. La regla hexagonal declarada como absoluta no se cumple de forma estricta en el código

La documentación afirma que `api/` no debe importar `domain/` ni `infrastructure/`
directamente, pero hay varios routers que sí lo hacen.

**Evidencia:**
- `CLAUDE.md` §6
- `src/identidad/api/router.py`
- `src/registro/api/router.py`
- `src/torneo/api/router.py`

**Impacto:**
- erosiona la autoridad de la regla arquitectónica
- vuelve más difícil usar métricas o revisiones como evidencia dura
- deja una distancia entre “doctrina” y “práctica”

**Acciones recomendadas:**
1. Decidir si la regla sigue siendo absoluta o si se va a flexibilizar explícitamente.
2. Si sigue siendo absoluta:
   extraer DTOs y factories de infraestructura fuera de `api/` y usar dependencias/puertos.
3. Si se flexibiliza:
   documentar la excepción con precisión para BCs CRUD simples.
4. Hacer una revisión arquitectónica puntual de `api/` en los BCs CRUD y unificar criterio.

---

### D-06. Hay imports directos entre BCs pese a que la metodología los prohíbe

El proyecto declara que la comunicación entre BCs debe ocurrir solo vía puertos y ACLs,
pero algunos adaptadores consumen tipos concretos de otro BC.

**Evidencia:**
- `CLAUDE.md` §6
- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`

**Impacto:**
- acoplamiento semántico entre contextos
- riesgo de fuga del modelo del BC upstream
- menor capacidad de cambio independiente

**Acciones recomendadas:**
1. Definir con precisión qué se permite en un ACL:
   ¿puede leer aggregates del upstream o solo puertos/DTOs?
2. Crear contratos de lectura más delgados para consumo cross-BC.
3. Mover cualquier integración estructural pesada a `shared/` solo si realmente es lenguaje común.
4. Correr una auditoría de imports cross-BC y clasificarlos en:
   aceptables, tolerables temporales, corregir.

---

### D-07. El BC `Notificaciones` está consolidado en el modelo, pero no en la implementación

En la documentación estratégica aparece como bounded context definitivo, incluso con
Event Sourcing, pero en código todavía es casi solo scaffolding.

**Evidencia:**
- `docs/design/context-map.md`
- `CLAUDE.md`
- `src/notificaciones/`

**Impacto:**
- asimetría entre mapa conceptual y estado real
- riesgo de sobreafirmar madurez arquitectónica no implementada
- dificultad para interpretar cuánto del sistema está realmente consolidado

**Acciones recomendadas:**
1. Marcar explícitamente en la documentación qué BCs están `modelados`, `parcialmente implementados` o `operativos`.
2. Evitar describir `Notificaciones` como equivalente en madurez a `Competencia` o `Torneo`.
3. Definir un criterio mínimo para considerar implementado un BC:
   aggregate, puertos, persistencia, API o integración observable.
4. Reflejar esa semántica de madurez en `CLAUDE.md` y context map.

---

### D-08. Hay tooling interno útil en `./.claude/`, pero con deuda y referencias rotas

El repo incluye hooks, tracking, skill `implement-us` y comandos de sesión, pero no todo
está alineado con la realidad del proyecto ni documentado de forma consistente.

**Evidencia:**
- `./.claude/tracking/README.md` apunta a docs inexistentes
- `./.claude/memory/` está vacío
- hooks usan memoria global en `~/.claude/...`

**Impacto:**
- confusión entre tooling local del repo y tooling global del usuario
- menor reproducibilidad del proceso
- onboarding más difícil para un tercero o para una futura reinstalación limpia

**Acciones recomendadas:**
1. Separar claramente tooling de proyecto vs estado global del usuario.
2. Corregir o eliminar referencias a documentación inexistente.
3. Documentar qué parte de `./.claude/` es indispensable para el workflow y qué parte es auxiliar.
4. Decidir si `tracking` y `hooks` forman parte del experimento o son solo soporte técnico.

---

### D-09. Parte del experimento sigue apoyándose en supuestos que ya cambiaron

Algunos documentos del experimento siguen formulados desde preguntas ya resueltas
en el repo real, como la elección de backend o la base de datos.

**Evidencia:**
- `docs/contexto/PLAN-EXPERIMENTO.md` aún plantea decisiones iniciales ya cerradas
- documentos tempranos siguen redactados como si el stack no estuviera fijado

**Impacto:**
- contamina la lectura histórica con ambigüedad innecesaria
- vuelve más difícil distinguir “hipótesis inicial” de “decisión efectiva”

**Acciones recomendadas:**
1. Añadir una nota editorial en documentos históricos cuando una decisión ya fue cerrada.
2. No reescribir la historia, pero sí marcar explícitamente qué partes son previas al estado actual.
3. Crear un índice de vigencia documental:
   `histórico`, `activo`, `reemplazado`.

---

### D-10. Falta una matriz operativa que conecte hallazgo metodológico con acción concreta

El proyecto documenta muchas observaciones valiosas, pero no siempre las transforma en
acciones priorizadas, con responsable y criterio de cierre.

**Evidencia:**
- abundan análisis y HITO con buena lectura conceptual
- no siempre se convierten en acciones visibles de corrección o consolidación

**Impacto:**
- riesgo de acumular aprendizaje sin cierre operativo
- retrospección rica pero poco ejecutable

**Acciones recomendadas:**
1. Convertir este tipo de HITO en backlog concreto de mejora metodológica.
2. Crear una tabla simple:
   `hallazgo → acción → prioridad → cuándo ejecutarlo`.
3. Resolver primero debilidades que afectan verdad operativa:
   D-02, D-03, D-04 y D-05.

---

## Matriz resumida de priorización

| ID | Debilidad | Impacto | Prioridad sugerida |
|----|-----------|---------|--------------------|
| D-01 | Sobrecarga metodológica | Alto | Media |
| D-02 | Múltiples fuentes de verdad | Muy alto | Alta |
| D-03 | Documentación desalineada | Muy alto | Alta |
| D-04 | `/implement-us` no ajustado al proyecto | Muy alto | Alta |
| D-05 | Regla hexagonal no cumplida estrictamente | Alto | Alta |
| D-06 | Imports directos entre BCs | Alto | Media-Alta |
| D-07 | BCs modelados pero no implementados con misma claridad | Medio | Media |
| D-08 | Tooling `.claude/` con deuda | Medio | Media |
| D-09 | Documentos históricos redactados como si siguieran vigentes | Medio | Media |
| D-10 | Hallazgos sin traducción sistemática a acciones | Alto | Alta |

---

## Recomendación de ejecución por etapas

### Etapa 1 — Verdad operativa

Objetivo: que el proyecto vuelva a contar una sola historia consistente.

Ejecutar:
1. Consolidar fuente de verdad del estado del proyecto
2. Corregir `README`, `docker-compose` y documentos operativos desalineados
3. Marcar vigencia de documentos fundacionales vs históricos

### Etapa 2 — Coherencia táctica

Objetivo: que la herramienta principal del flujo deje de ir contra la arquitectura real.

Ejecutar:
1. Adaptar `/implement-us` a AtaraxiaDive
2. Revisar templates, paths y Fase 0
3. Alinear tracking, reportes y workflow con esa adaptación

### Etapa 3 — Coherencia arquitectónica

Objetivo: reducir la distancia entre arquitectura declarada y arquitectura aplicada.

Ejecutar:
1. Auditar imports `api → infrastructure/domain`
2. Auditar imports cross-BC
3. Decidir y documentar excepciones reales vs reglas absolutas

### Etapa 4 — Simplificación del experimento

Objetivo: bajar fricción sin perder capacidad de aprendizaje.

Ejecutar:
1. Clasificar artefactos obligatorios/opcionales
2. Eliminar o archivar tooling o documentos que no aportan valor observable
3. Medir overhead metodológico al cierre de SP3

---

## Cierre

La conclusión central de este análisis es positiva pero exigente:

**AtaraxiaDive tiene una metodología fuerte y una estructura con fundamento real,
pero necesita ahora una fase de consolidación para que el marco no se vuelva más
complejo que el sistema que intenta guiar.**

La oportunidad experimental es muy buena precisamente por eso: ya no se trata de
probar si la metodología puede arrancar, sino de probar si puede sostenerse sin
degradar claridad, velocidad ni coherencia a medida que el proyecto crece.
