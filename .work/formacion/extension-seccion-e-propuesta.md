# Extensión Sección E — Propuesta de Capacitación
## Ingeniería de Software con IA: Del Chat a la Práctica Profesional

---

## A — VISIÓN

La IA generativa no elimina la necesidad de ingeniería de software. La desplaza.

Cuando la implementación puede derivarse parcialmente desde especificaciones, el cuello de
botella deja de estar en escribir código y se concentra en algo que la IA no puede hacer
sola: comprender el dominio, construir el modelo conceptual, especificar el comportamiento
con precisión, y verificar que el sistema lo preserve.

Esta capacitación parte de esa premisa y la convierte en método.

Los participantes aprenden un marco conceptual para entender por qué el uso ad-hoc de IA
no escala, y un conjunto de herramientas concretas, de código abierto, para sistematizarlo.
Todo lo que se enseña está respaldado por un proyecto real en ejecución: AtaraxiaDive,
una plataforma de gestión de torneos de apnea desarrollada como experimento controlado
para generar evidencia empírica sobre esta hipótesis.

**Lo que diferencia esta propuesta:** el instructor no describe casos de otros.
Está ejecutando el experimento.

---

## B — TEMARIO

### Módulo 1 — Por qué la IA reconfigura el trabajo del ingeniero (2 hs)

**El problema que la IA hace visible**

Durante décadas la enseñanza del software se organizó alrededor de los lenguajes de
programación: lenguaje → programación → sistema. La IA generativa expone la limitación
de ese orden: la implementación puede automatizarse parcialmente; la especificación, no.

**Contenidos:**
- La cadena de transformación conceptual: Dominio → Modelo → Especificación →
  Arquitectura → Implementación
- En qué capas puede intervenir la IA y en cuáles no puede reemplazar el juicio humano
- Por qué el uso de chat para desarrollar software no escala: deuda de especificación,
  resultados inconsistentes, pérdida de coherencia entre artefactos
- La hipótesis central: cuanto mayor es la automatización de la implementación, mayor
  es la necesidad de rigor en especificación, calidad constructiva y memoria del proceso
- El human-in-the-loop como componente estructural, no como parche
- El nuevo rol profesional: de programador a evaluador de calidad — cuatro competencias
  cíclicas: Dirigir (dar contexto y restricciones a la IA), Evaluar (medir con criterios
  objetivos), Refinar (iterar hasta cumplir principios), Decidir (asumir responsabilidad
  de diseño). La IA no reemplaza ninguna de estas competencias; las vuelve más necesarias.
- Antifragilidad profesional: el profesional cuyo valor está en principios universales
  se fortalece con la disrupción de la IA; el que compite en velocidad de escritura, no.

**Demostración en vivo:** la misma tarea de desarrollo enviada dos veces al mismo
modelo — una como prompt libre, otra con contexto, restricciones y criterios explícitos.
Se observa en vivo cómo cambia la consistencia, completitud y utilidad del resultado.
Sin herramientas todavía: solo el problema visible antes de presentar cualquier solución.

---

### Módulo 2 — El modelo del dominio como especificación conceptual (2 hs)

**Domain-Driven Design como base para trabajar con IA**

Si la calidad del resultado que produce la IA depende de la claridad del modelo y la
precisión de la especificación, entonces construir ese modelo correctamente es la
habilidad central del ingeniero en este nuevo contexto.

**Contenidos:**
- Qué es un modelo del dominio y por qué importa antes de hablar con la IA
- Conceptos fundamentales de DDD aplicados al trabajo con IA: entidades, objetos de
  valor, agregados, eventos, contextos delimitados, lenguaje ubicuo
- Cómo el modelo conceptual actúa como especificación de comportamiento
- Invariantes: condiciones que el sistema debe preservar siempre, independientemente
  de la tecnología
- Por qué una mala especificación amplificada por IA genera más deuda técnica que
  una mala especificación sin IA

**Ejercicio práctico:** modelar un dominio simple, identificar sus invariantes y
construir el lenguaje ubicuo del área. Sin código todavía.

---

### Módulo 3 — Spec-Driven Development: el spec-kit como contrato con la IA (2 hs)

**Cómo especificar comportamiento de forma que la IA pueda implementarlo bien**

Un spec-kit es un formato estructurado de especificación que le da a la IA la
información necesaria para producir un resultado coherente, verificable y trazable.
Es el artefacto que separa el uso profesional del uso ad-hoc.

**Contenidos:**
- Qué es SDD (Spec-Driven Development) y en qué se diferencia de escribir un prompt
- Estructura del spec-kit: precondiciones, postcondiciones, invariantes, escenarios
  BDD, contexto de dominio, impacto arquitectónico
- Cómo construir una US-IEDD (User Story con especificación formal) paso a paso
- Por qué los escenarios BDD son la traducción ejecutable de la especificación, no
  tests independientes
- Cómo el spec-kit reduce la ambigüedad y hace el resultado predecible

**Ejercicio práctico:** tomar el dominio modelado en el módulo anterior y escribir
una US-IEDD completa. Revisión en pares: ¿la especificación es suficientemente
precisa para que alguien sin contexto la implemente correctamente?

**Artefacto transferible:** plantilla US-IEDD disponible para uso inmediato en
proyectos propios.

---

### Módulo 4 — El flujo agentic de implementación (2 hs)

**Claude Dev Kit: de la especificación al artefacto entregable en 10 fases**

Un flujo agentic no es pedirle a la IA que "haga todo". Es un proceso estructurado
con fases definidas, artefactos por fase, puntos de aprobación humana y quality gates
automáticos. Claude Dev Kit es un framework de código abierto que implementa ese flujo.

**Contenidos:**
- Qué hace cada una de las 10 fases: validación, BDD, planning, implementación, tests
  unitarios, tests de integración, validación BDD, quality gates, documentación,
  reporte final
- Cómo estructurar los puntos de aprobación para no perder el control del proceso
- Qué decide la IA y qué decide el ingeniero: la línea que define el rol humano
- El sistema de tracking: por qué medir el tiempo por fase es parte del método,
  no un adorno burocrático
- Perfiles de stack disponibles: PyQt, FastAPI, Flask REST, Flask WebApp, Python
  genérico. Compatibilidad con Claude Code y Codex.

**Demostración en vivo:** ejecución completa de `/implement-us` sobre una historia
de usuario real, desde el spec-kit hasta el reporte final. Observación de artefactos
generados por fase.

**Evidencia:** overhead del flujo convergió a ~18 minutos por US en el experimento
AtaraxiaDive (medido de SP1 a SP2, sobre una arquitectura hexagonal de complejidad media).

---

### Módulo 5 — Quality gates: medir para gobernar el ciclo agentic (2 hs)

**El triángulo Principios + Métricas + IA — y Software Limpio como implementación**

> *"Principios sin métricas son dogma. Métricas sin principios son números vacíos.
> IA sin ambos es caos productivo."*

En un ciclo agentic, la IA puede replicar una mala decisión de diseño a escala
industrial antes de que nadie la detecte. Las métricas no son un control posterior:
son el mecanismo que convierte principios abstractos en criterios verificables y
cierra el ciclo Dirigir → Evaluar → Refinar → Decidir con evidencia objetiva.

**Contenidos:**

*El fundamento: el triángulo de competencias*
- Por qué la IA sola no garantiza calidad: amplifica el criterio del ingeniero,
  no lo reemplaza
- Cómo los principios de diseño (cohesión, acoplamiento, separación de concerns)
  se traducen en métricas medibles
- El ciclo integrado: principio → restricción en el spec-kit → código generado →
  métrica → identificación del principio violado → refinamiento
- Por qué sin métricas el proceso agentic produce deuda técnica a escala industrial
  antes de que sea visible

*La implementación: Software Limpio en tres niveles*

| Nivel | Herramienta | Momento | Acción |
|-------|-------------|---------|--------|
| 1 | CodeGuard | Pre-commit | Advierte, no bloquea — 6 checks (PEP8, seguridad, complejidad, Pylint, tipos, imports) |
| 2 | DesignReviewer | PR review | Bloquea si CRITICAL — 12 analyzers AST (acoplamiento, cohesión, code smells, SOLID) |
| 3 | ArchitectAnalyst | Fin de sprint | Informa tendencias — métricas de Martin (Ca, Ce, I, A, D), ciclos de dependencias |

- Por qué cada nivel tiene una acción diferente (advertir / bloquear / informar)
  y qué consecuencias tiene confundirlos
- Cómo calibrar los umbrales por tipo de arquitectura y tamaño de equipo
- Cómo los quality gates catalizan decisiones de diseño que de otro modo quedarían
  implícitas
- Integración con CI/CD y hooks de git

**Demostración en vivo:** ejecución de los tres agentes sobre código real del
experimento. Interpretación de un reporte con violaciones CRITICAL y WARNING:
qué principio está siendo violado, no solo qué número está fuera de umbral.

**Evidencia:** DesignReviewer ejecutado en cada PR desde SP1 de AtaraxiaDive;
ArchitectAnalyst en cada cierre de baseline; 0 violaciones CRITICAL sostenidas
desde SP2 sobre una base de 481 tests.

---

### Módulo 6 — Evidencia, métricas y adaptación al equipo (2 hs)

**Qué dice el experimento y cómo aplicarlo en tu contexto**

Enseñar un método sin mostrar sus datos es vender teoría. Este módulo cierra
el programa mostrando la evidencia real del experimento —incluyendo lo que todavía
no está demostrado— y trabaja con los participantes en cómo adaptar el método a
su propio contexto.

**Contenidos:**
- Qué se ha confirmado experimentalmente hasta SP3: la automatización requiere
  calibración humana, la productividad táctica no elimina la necesidad de
  ingeniería, los quality gates funcionan como dispositivos de gobierno, el
  proceso produce conocimiento formalizable
- Qué sigue abierto: costo total del ciclo de vida frente a alternativas
  convencionales, validación en equipos, sostenibilidad en proyectos más largos
- Métricas que vale la pena medir en un equipo real: overhead por fase, tendencias
  de acoplamiento/cohesión, cobertura de tests, tasa de violaciones por sprint
- Cómo introducir el método en un equipo que ya usa IA de forma ad-hoc: qué cambiar
  primero, qué resistencias esperar, cómo demostrar valor sin requerir adopción total
- Discusión abierta: casos del equipo, adaptaciones, fricción esperada

---

## C — ESTRUCTURA

- **Total:** 16 horas (4 hs de startup + 12 hs de contenido)
- **Formato:** módulos de 2 horas, semanales, mismo día y horario
- **Modalidad:** virtual, con acceso a los repositorios de código durante el programa
- **Cada módulo combina:**
  - Exposición conceptual con base teórica explícita
  - Demostración en vivo sobre código y artefactos reales
  - Ejercicio aplicado con feedback

**Sin slides vacías:** cada concepto tiene un artefacto real como ejemplo.
Los repositorios de las herramientas son públicos y accesibles desde el primer módulo.

---

## D — OBJETIVOS DE APRENDIZAJE

- Comprender por qué la IA desplaza el trabajo del ingeniero hacia las capas de
  mayor valor y qué implica eso en la práctica diaria
- Construir un modelo de dominio y especificar comportamiento con el nivel de
  precisión necesario para trabajar con IA de forma predecible
- Dominar el formato US-IEDD como spec-kit transferible a proyectos propios
- Ejecutar un flujo agentic de implementación completo con Claude Dev Kit
- Instrumentar quality gates en tres niveles e interpretar sus resultados
- Evaluar críticamente qué parte del método es aplicable en su equipo y por dónde
  empezar la adopción

---

## E — FUERA DEL ALCANCE

Ser explícito es parte de la diferenciación:

- **Sistemas multi-agente** (LangGraph, AutoGen, CrewAI): no hay evidencia empírica
  propia. Puede combinarse con módulos de la propuesta base si se requiere.
- **Construcción de productos de IA** (RAG, fine-tuning, modelos propios): fuera del
  foco. El problema abordado es ingeniería de software con IA, no construir IA.
- **Stacks no-Python**: las herramientas cubren Python. Soporte para TypeScript/Node.js
  está en roadmap del Dev Kit pero no disponible.
- **Plataformas no-code / low-code**: sin posición metodológica ni evidencia.
- **Garantías de reducción de costo total o calidad superior medida**: la hipótesis
  tiene validación parcial. No se afirma como resultado probado.

---

## F — AUDIENCIA IDEAL

Equipos de desarrollo (5–15 personas), tech leads y arquitectos que ya usan IA de
forma ad-hoc y quieren sistematizarlo.

**Requiere:** experiencia activa en desarrollo de software.
**No requiere:** conocimiento previo de IA, DDD o metodologías ágiles.

No es adecuada para audiencias no técnicas.

---

## G — BASE DE EVIDENCIA

| Fuente | Descripción | Acceso |
|--------|-------------|--------|
| Claude Dev Kit v1.3.0 | Framework agentic: 10 fases, 5 perfiles, 107 tests, 99% cobertura | github.com/vvalotto/claude-dev-kit (MIT) |
| Software Limpio v0.3.0 | Quality gates: 3 agentes, 12 analyzers AST, métricas de Martin. Marco teórico: triángulo Principios + Métricas + IA, nuevo rol profesional, antifragilidad | github.com/vvalotto/software_limpio (MIT) |
| AtaraxiaDive SP1→SP3 | Proyecto real: 481 tests, quality reports por incremento, métricas de tracking, baselines formales | Accesible durante la capacitación |
| Marco IEDD | Fundamento conceptual: 5 capas, spec-kit, hipótesis experimental documentada | Incluido en los materiales del curso |

AtaraxiaDive es un experimento diseñado con propósito de producto real: atributos de
calidad no funcionales acotados, arquitectura hexagonal formal, quality gates en cada
incremento. No es un proyecto de juguete, pero tampoco es un sistema en producción
con usuarios reales todavía.

---

*Versión 0.1 — Abril 2026*
*Propuesta preparada por Víctor Valotto*
