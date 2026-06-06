# Aprendizajes de la Propuesta Metodológica IEDD
## Síntesis extraída del experimento AtaraxiaDive

> **Estado documental:** activo — síntesis acumulativa de aprendizajes metodológicos
> **Fuentes principales:** ANALISIS-IEDD.md · HITO-1 · HITO-13 · HITO-14 · PLAN-EXPERIMENTO.md
> **Fecha de síntesis:** Mayo 2026

---

## La tesis central que lo explica todo

Hay una observación de partida que parece simple pero tiene consecuencias de largo alcance:

> *La mayor dificultad del software está en especificar y diseñar el comportamiento del sistema — no en escribir código. La IA hace visible esta realidad al automatizar parcialmente la implementación.*

IEDD (Ingeniería de Especificación Dirigida por el Dominio) no es un método más de desarrollo. Es una **reinterpretación del oficio**: si la IA puede escribir código con calidad aceptable a partir de una especificación precisa, entonces el valor del ingeniero se desplaza hacia arriba en la cadena — hacia la comprensión del dominio, la construcción del modelo y la especificación del comportamiento.

La implementación se vuelve *derivable*. La especificación, no.

---

## La cadena de transformación conceptual

IEDD propone cinco capas de transformación, cada una con un propósito distinto:

```
DOMINIO          →  Realidad del problema (actores, procesos, reglas)
     ↓
MODELO           →  Representación conceptual (DDD: entidades, agregados,
     ↓               eventos, invariantes, lenguaje ubicuo)
ESPECIFICACIÓN   →  Comportamiento formal (precondiciones, postcondiciones,
     ↓               invariantes, operaciones, estados)
     ↓ [IA como traductor conceptual]
ARQUITECTURA     →  Organización del sistema (componentes, capas, comunicación)
     ↓
IMPLEMENTACIÓN   →  Tecnología concreta (código, APIs, bases de datos)
```

**El punto crítico está entre Especificación y Arquitectura.** La IA actúa ahí como compilador conceptual: toma una especificación formal y deriva código. La calidad del output depende directamente de la claridad del modelo y la precisión de la especificación — no de quién escribe el código.

---

## La inversión pedagógica propuesta

| | Enfoque tradicional | Enfoque IEDD |
|---|---|---|
| Punto de partida | Lenguaje de programación | Dominio del problema |
| Eje central | Código | Especificación del comportamiento |
| Rol de la IA | Herramienta de código | Traductor de especificaciones |
| Formación centrada en | Sintaxis, frameworks | Modelado, especificación, ambigüedad |
| La implementación es | El trabajo principal | La parte derivable |

Esta inversión no es cosmética. Define un profesional diferente: alguien que comprende dominios complejos, construye modelos conceptuales precisos y especifica comportamientos sin ambigüedad — y usa la IA para derivar el código.

---

## El ecosistema integrado

IEDD no es un proyecto aislado. Es el **marco teórico que unifica todo el ecosistema**:

```
        IEDD
(el proceso: cómo se transforma dominio en sistema)
        │
        ├──── software_limpio
        │     (la calidad: cómo se mide en cada capa)
        │
        ├──── Claude Dev Kit / implement-us
        │     (la automatización: cómo se implementa US a US)
        │
        └──── CM Framework (entorno-ia-dev)
              (la memoria: cómo se gestiona la evolución del modelo)
```

Cada uno responde una pregunta diferente sobre el mismo fenómeno. La correspondencia es directa:

| Capa IEDD | Artefacto CM | Agente verificador |
|-----------|--------------|-------------------|
| Dominio | vision.md + diálogos Cowork | — |
| Modelo | domain-model.md (DDD) | — |
| Especificación | user-stories.md (US-IEDD) | DesignReviewer (LCOM, CBO) |
| Arquitectura | architecture.md + ADRs | ArchitectAnalyst (ciclos, capas) |
| Implementación | src/ | CodeGuard (complejidad, PEP8) |

El CM framework no es solo gestión de documentos. Es la **memoria de la cadena IEDD completa**.

---

## La US-IEDD como bisagra metodológica

El artefacto más concreto que produce IEDD es la User Story enriquecida con especificación formal:

```markdown
## Contexto del dominio
- Agregado afectado: [nombre]
- Invariante del agregado: [regla que nunca puede violarse]

## Especificación del comportamiento
- Precondición: [estado que debe existir antes de la operación]
- Postcondición: [estado garantizado al finalizar]
- Eventos generados: [eventos de dominio que se disparan]

## Criterios de aceptación (BDD)
- Scenario: [descripción]
  Given [precondición en lenguaje de negocio]
  When [acción del actor]
  Then [resultado esperado]
```

Este template es la bisagra entre las capas Modelo/Especificación de IEDD y el input que consume `/implement-us`. El flujo `US-IEDD → BDD → código` **es** el flujo `especificación → traducción IA → implementación` de IEDD materializado como proceso concreto.

---

## Aprendizajes de la Fase 0 (adherencia metodológica)

La Fase 0 de AtaraxiaDive fue el primer banco de pruebas real de IEDD. Los hallazgos principales:

**Lo que funcionó:**

- Las 5 capas produjeron artefactos concretos y no solo intención metodológica
- Event Storming encajó naturalmente entre Capa 1 y Capa 2 como técnica de elicitación y modelado
- La arquitectura hexagonal emergió del modelo de dominio, no se impuso sobre él (ADR-001 a ADR-005)
- La trazabilidad RF → BC → SP → US-IEDD fue posible y útil

**La desviación documentada:**

Los ADRs de arquitectura (Capa 4) se escribieron antes de que el Event Storming completara la Capa 2. La secuencia IEDD pura no se respetó. Sin embargo, las decisiones emergieron del conocimiento del dominio (Capa 1), no de capricho tecnológico. La tensión fue identificada y documentada — lo cual es en sí mismo un aprendizaje: **la secuencia ideal es un objetivo, no una garantía**. El movimiento entre capas es iterativo en la práctica.

---

## Hallazgo experimental 1: el Sprint de Ajuste Técnico (HITO-13)

**El problema:** IEDD fue diseñado para modelar features. Pero al cerrar SP2, la revisión con DesignReviewer y ArchitectAnalyst produjo 8 issues de refactoring concretos. Ninguno bloqueante, todos degradantes a largo plazo. ¿Dónde vive ese trabajo dentro del marco?

**El hallazgo:** IEDD necesita un segundo modo de US — la **US de refactoring técnico**:

| Campo | US de feature | US de refactoring |
|-------|--------------|-------------------|
| Precondición | Estado del negocio requerido | Smell o deuda detectada (métrica, patrón) |
| Postcondición | Comportamiento garantizado | Métrica mejorada o patrón corregido |
| Invariante | Regla de negocio | Tests no regresionan · DesignReviewer no empeora |

**La extensión:** Se instituye el **Sprint de Ajuste Técnico (SP-ADJ)** como etapa formal del ciclo:

```
SP-N (features)
  └── BL-N (baseline + retrospectiva)
        └── Revisión de calidad
              └── SP-ADJ-N (si hay deuda significativa)
                    └── BL-ADJ-N
                          └── SP-N+1 (features)
```

Este ciclo no estaba en el diseño original de IEDD. Emergió del contacto con un proyecto real. La evidencia empírica lo justifica: mezclar features con refactoring dentro del mismo SP complica el Definition of Done y genera ruido en la evidencia del experimento.

**Implicancia para el paper IEDD:** el SP-ADJ es una extensión documentable del marco para proyectos que usan quality gates automatizados.

---

## Fortalezas identificadas del sistema metodológico (HITO-14)

**1. La metodología tiene una tesis fuerte y verificable**
La cadena IEDD no es retórica vaga. Es una transformación explícita `dominio → modelo → especificación → arquitectura → implementación` con hipótesis observables: obliga a pensar antes de implementar, hace visible dónde aparece la ambigüedad, permite evaluar no solo el software sino el proceso que lo produce.

**2. El dominio elegido amplifica el valor del experimento**
AtaraxiaDive no es un CRUD trivial. Tiene estados, eventos, reglas del deporte, restricciones temporales, requisitos de calidad offline y trazabilidad fuerte. Eso da material real para DDD, justifica invariantes y permite poner a prueba si IEDD mejora la precisión conceptual.

**3. La jerarquía de trabajo es ejecutable**
Subproyecto → Incremento → US-IEDD → fases del kit → baseline → UAT → quality gates. Cada nivel tiene lugar explícito en el sistema. Baja la ambigüedad operativa y mejora la trazabilidad entre planificación, implementación y cierre.

**4. El proceso produce evidencia, no solo intención**
Reportes de baselines, tests unitarios, BDD, UAT, tracking de USs. El marco no quedó solo en documentos. Hay evidencia empírica utilizable para retrospectiva o paper.

**5. El control de calidad opera en tres niveles**
CodeGuard (código) + DesignReviewer (diseño OO) + ArchitectAnalyst (arquitectura) forman un esquema de control por capas. Hace visible deuda que un proyecto solitario normalmente dejaría pasar.

---

## Debilidades identificadas y acciones (HITO-14)

### Las más críticas (prioridad alta)

**D-02 — Múltiples fuentes de verdad para el estado del proyecto**
El estado aparece en README, CLAUDE.md, docs/plans, .cm/baselines y reportes individuales. Genera onboarding confuso y pérdida de confianza en la documentación superficial.
→ *Acción:* declarar jerarquía formal: `baselines/reportes > CLAUDE.md > README`. El README no mantiene estado fino.

**D-03 — Documentación fundacional desalineada con la arquitectura vigente**
Partes del proyecto hablan de PostgreSQL y Docker cuando la arquitectura vigente ya consolidó SQLite por BC sin Docker.
→ *Acción:* marcar vigencia explícita en cada documento: `fundacional` / `vigente` / `histórico`.

**D-04 — /implement-us no ajustado a la arquitectura real**
La herramienta trabaja con un perfil `fastapi-rest` orientado a layered architecture, mientras el proyecto declara BC-first + hexagonal + DDD. Esto genera paths incorrectos y fricción en la herramienta que debería reducirla.
→ *Acción:* crear perfil `ataraxiadive-fastapi-hexagonal` con estructura `src/<bc>/domain|application|infrastructure|api`.

**D-05 — La regla hexagonal declarada como absoluta no se cumple estrictamente**
Varios routers importan directamente desde `domain/` e `infrastructure/`, violando la arquitectura declarada en CLAUDE.md.
→ *Acción:* decidir si la regla sigue siendo absoluta o si se flexibiliza para BCs CRUD simples — y documentarlo explícitamente.

### Las que afectan la sostenibilidad

**D-01 — Sobrecarga metodológica**
El sistema combina IEDD, CM, Dev Kit, quality agents, tracking, reportes, baselines, HITOs, specs y UATs. El riesgo no es conceptual sino operacional: el costo de sostener el marco puede terminar compitiendo con el avance del producto.
→ *Acción:* clasificar artefactos en obligatorios / opcionales / derivados. Reducir actualización manual.

**D-06 — Imports directos entre BCs**
Algunos adaptadores consumen tipos concretos de otro BC, violando el principio de comunicación por puertos y ACLs.
→ *Acción:* auditar imports cross-BC. Crear contratos de lectura delgados para consumo entre contextos.

**D-10 — Hallazgos sin traducción sistemática a acciones**
El proyecto documenta muchas observaciones valiosas, pero no siempre las transforma en acciones priorizadas con criterio de cierre.
→ *Acción:* cada HITO debe producir una tabla `hallazgo → acción → prioridad → cuándo`.

---

## La conclusión experimental central (HITO-14)

> *"AtaraxiaDive tiene una metodología fuerte y una estructura con fundamento real,
> pero necesita ahora una fase de consolidación para que el marco no se vuelva más
> complejo que el sistema que intenta guiar."*

La pregunta del experimento ya no es si la metodología puede arrancar — puede. La pregunta ahora es si puede **sostenerse sin degradar claridad, velocidad ni coherencia a medida que el proyecto crece**.

Esa es la hipótesis que los próximos subproyectos deben responder.

---

## La matriz de conocimiento: lo que el experimento produce

Cada incremento de AtaraxiaDive genera materia prima directa para productos intelectuales de largo plazo. La regla es **no reescribir**: los ADRs, retrospectivas y reportes son el libro, el curso y el paper en estado bruto.

| Qué se aprende en AtaraxiaDive | → Libro DDD | → Curso IS | → Paper IEDD |
|-------------------------------|-------------|------------|--------------|
| Performance aggregate + invariantes | "Aggregates con invariantes reales" | Caso práctico semana 4 | Ejemplo RF→invariante→BDD |
| Event Sourcing para auditoría | "Domain Events como memoria" | Caso práctico semana 8 | — |
| Máquina de estados del Torneo | "State machines como ubiquitous language" | Caso práctico semana 6 | — |
| Reglas como datos (disciplinas) | "Bounded Context Configuración" | Caso práctico semana 10 | — |
| Métricas BL-001 a BL-N | — | Lab: medir deuda técnica | Evidencia empírica IEDD |
| Retrospectivas del entorno | — | — | Friction analysis en entornos IA |
| SP-ADJ como etapa formal | — | — | Extensión del marco IEDD |

---

## Hallazgo experimental 2: deriva silenciosa de tests en proyectos IEDD+LLM (HITO-30/31/32)

Al abrir SP6, la ejecución completa de la suite de tests reveló 115 tests silenciosamente fallando — distribuidos en 3 niveles (21 unitarios, 31 de integración, 63 BDD). Los tests no habían fallado en CI porque no se ejecutaban en cada PR; el LLM los escribió correctamente al crear cada US, pero no los actualizó cuando USs posteriores cambiaron las reglas de dominio.

**Tres patrones de deriva documentados:**

| Nivel | Patrón dominante | Ejemplo |
|---|---|---|
| Unitarios (HITO-30) | Refactor de puertos no propagado a stubs de test | `PerformancesAPAdapter` con nueva firma no reflejada |
| Integración (HITO-31) | Wiring incorrecto entre handlers e infraestructura real | Path relativo a DB que solo falla fuera de raíz |
| BDD (HITO-32) | Scenarios correctos al escribirse, inválidos tras refactor posterior | Algoritmo FAAS reemplazado, scenario con semántica del algoritmo anterior |

**Implicación metodológica para IEDD:** al cerrar una US que modifica una regla de dominio existente, el checklist debe incluir explícitamente: `grep` sobre tests existentes buscando el símbolo/regla modificada, verificación de validez semántica de scenarios encontrados, y ejecución completa de la suite antes del commit. Este es el principio de "regresión de invariantes" — no solo de funcionalidad.

---

## Hallazgo experimental 3: límites de los quality gates automatizados (HITO-33)

Durante INC-6.4 (SP6), DesignReviewer reportó LCOM=2 en `RankingCompetencia`. El análisis reveló que el flag no era un defecto sino una consecuencia estructural del patrón Aggregate+Event Sourcing: todo aggregate con Event Sourcing tendrá inevitablemente dos grupos de métodos (comando y reconstitución) que LCOM interpreta como falta de cohesión.

**El hallazgo:** las métricas OO clásicas producen falsos positivos sistemáticos en patrones DDD+ES. LCOM=2 en un aggregate ES no indica deuda — indica que el patrón está implementado correctamente.

**Extensión necesaria del marco:** IEDD necesita una categoría de "falso positivo documentado" en los reportes de quality gate, análoga a un `noqa` semántico con justificación explícita. El registro en BL-006 (DR-01) es el primer ejemplo de este mecanismo operando. Sin esta categoría, los quality gates producen ruido que degrada la confianza en el sistema de control de calidad.

---

## Hallazgo experimental 4: incrementos de dominio técnico (HITO-34/35)

SP7 introdujo dos incrementos sin lógica de negocio: INC-7.1 (despliegue a Fly.io) e INC-7.2 (manual de usuario). El experimento los trató como incrementos IEDD de primera clase con DoD verificable.

**INC-7.1 — Despliegue:** el entorno de producción es un oráculo distinto al entorno de desarrollo. Variables implícitas (PYTHONPATH, SQLite en filesystem efímero, volumes persistentes) solo se revelan al desplegar. Tratar el despliegue como tarea implícita de cierre habría producido trabajo sin trazabilidad.

**INC-7.2 — Manual de usuario:** documentar el sistema desde afuera fuerza un recorrido exhaustivo de cada pantalla que el UAT no garantiza. El manual escrito contra el sistema real (no contra especificaciones) es un oráculo de consistencia UX.

**Implicación:** IEDD debería reconocer explícitamente los **incrementos de dominio técnico** (infraestructura, despliegue, documentación) como ciudadanos de primera clase del ciclo, con su propio template de US y DoD adaptado.

---

## Hallazgo experimental 5: la cadena de validación completa (HITO-36)

Puerto Madryn 2026 fue el primer uso del sistema en una competencia real. Resultado: 0 defectos de dominio, 4 defectos de usabilidad (nav móvil, texto ambiguo).

**La observación clave:** los invariantes de dominio especificados con IEDD, validados con BDD y verificados en UAT, se mantuvieron bajo presión real. Los únicos defectos encontrados eran de interfaz — una categoría que IEDD no especifica con el mismo nivel de formalidad que el dominio.

**La cadena de validación completa observada en el experimento:**

```
Tests formales (unit/integración/BDD)  → detecta invariantes, contratos, regresiones
       ↓
UAT con dataset real                   → detecta flujos completos y variantes de dominio
       ↓
UAT exploratorio                       → detecta inconsistencias no especificadas
       ↓
Manual de usuario                      → detecta inconsistencias UX desde afuera
       ↓
Producción real                        → detecta presión real, usuarios nuevos, interfaz móvil
```

Cada capa detecta una categoría que la anterior no puede ver. Ninguna es redundante.

**Implicación para IEDD:** el método protege el dominio; la producción real protege la interfaz. La extensión metodológica para especificación de comportamiento de interfaz móvil queda como pregunta abierta para trabajos futuros.

---

## Estado de las preguntas del experimento (cierre)

| Pregunta | Estado | Evidencia |
|---|---|---|
| ¿Las US-IEDD producen menos defectos de dominio que US clásicas? | ✅ Evidencia positiva | 0 defectos de dominio en producción real (HITO-36) |
| ¿Los BDD scenarios cubren casos que la especificación informal omite? | ✅ Confirmada | HITO-6, HITO-20 — variantes de dominio no anticipadas |
| ¿IEDD reveló ambigüedades en RFs que habrían llegado al código? | ✅ Confirmada | HITO-1, HITO-17 — oráculo de dominio |
| ¿Los quality gates correlacionan con violaciones al modelo conceptual? | 🔄 Parcial | HITO-11 (sí), HITO-33 (falsos positivos estructurales) |
| ¿La cadena es sostenible a lo largo del proyecto? | ✅ Confirmada | 7 SPs + 13 ADJs completados con el marco intacto |
| ¿IEDD especifica interfaces con el mismo rigor que el dominio? | ❌ Brecha identificada | HITO-36 — defectos de interfaz no capturados por el método |

---

*Síntesis generada con Claude Cowork — Mayo 2026*
*Actualizado: Junio 2026 — HITO-30..36 incorporados · estado de preguntas del experimento al cierre*
*Fuentes: docs/contexto/ANALISIS-IEDD.md · HITO-1 · HITO-13 · HITO-14 · HITO-30 · HITO-31 · HITO-32 · HITO-33 · HITO-34 · HITO-35 · HITO-36 · PLAN-EXPERIMENTO.md · BL-006 · BL-007*
