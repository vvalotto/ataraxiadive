# Ingeniería de Software con IA: del uso ad-hoc al proceso propio
## Propuesta de extensión técnica para equipos de desarrollo

*Víctor Valotto — Abril 2026*

---

## El enfoque

Esta capacitación no enseña herramientas específicas. Enseña a construir un proceso propio.

Cuando un equipo de desarrollo incorpora IA, aparecen tres preguntas que ninguna herramienta responde sola: ¿cómo especificamos el comportamiento con suficiente precisión para que la IA produzca resultados coherentes? ¿Cómo estructuramos el flujo de implementación para no perder el control del proceso? ¿Cómo medimos si lo que produce la IA cumple los criterios de calidad que el equipo considera no negociables?

El programa trabaja esas tres preguntas con un marco conceptual (IEDD, basado en Spec-Driven Development), con dos implementaciones de referencia construidas específicamente para responderlas, y con la evidencia empírica de un proyecto real que las pone a prueba. El objetivo no es que los participantes adopten esas implementaciones: es que entiendan los principios que las hacen funcionar y puedan construir las suyas.

---

## Contenido por módulo

### Módulo 1 — El ingeniero en la era de la IA (2 hs)

El primer módulo no presenta herramientas. Establece el problema que hace necesario el método.

Cuando la implementación puede asistirse con IA, el cuello de botella no desaparece: se desplaza. Deja de estar en escribir código y se concentra en especificar el comportamiento con precisión, construir el modelo conceptual correcto y verificar que el resultado lo preserve. Una mala especificación amplificada por IA genera más deuda técnica que una mala especificación sin IA —y la genera más rápido.

**Contenidos:**
- La cadena de transformación: Dominio → Modelo → Especificación → Arquitectura → Implementación. En qué capas puede intervenir la IA y en cuáles el juicio humano es irreemplazable.
- El nuevo rol profesional: cuatro competencias que la IA no sustituye sino que vuelve más necesarias — Dirigir (dar contexto y restricciones), Evaluar (medir con criterios objetivos), Refinar (iterar hasta cumplir principios de diseño), Decidir (asumir responsabilidad de las elecciones arquitectónicas).
- Por qué el uso ad-hoc de IA no escala: deuda de especificación, resultados inconsistentes, pérdida de coherencia entre artefactos.
- Introducción al marco IEDD: la hipótesis experimental, las cinco capas y su relación con SDD.

**Demostración en vivo:** la misma tarea de desarrollo enviada dos veces al mismo modelo —una como prompt libre, otra con contexto, restricciones y criterios explícitos. La diferencia en consistencia y utilidad del resultado es visible sin necesidad de explicación adicional.

---

### Módulo 2 — El modelo del dominio como base de la especificación (2 hs)

Antes de pedirle algo a la IA, el equipo necesita saber con precisión qué quiere. Ese conocimiento vive en el modelo del dominio: la representación conceptual de los objetos, comportamientos y reglas del negocio que el sistema debe implementar.

Este módulo introduce Domain-Driven Design como herramienta de especificación, no como metodología completa. El foco está en los conceptos que tienen impacto directo en la calidad de lo que se le pide a la IA.

**Contenidos:**
- Qué es un modelo del dominio y por qué construirlo antes de interactuar con la IA.
- Conceptos fundamentales de DDD aplicados a la especificación: entidades, objetos de valor, agregados, eventos del dominio, contextos delimitados, lenguaje ubicuo.
- Invariantes: condiciones que el sistema debe preservar siempre, independientemente de cómo esté implementado. Son el núcleo de la especificación formal.
- Cómo el lenguaje ubicuo del dominio reduce la ambigüedad en la comunicación con la IA y entre los miembros del equipo.

**Ejercicio práctico:** modelar un dominio simple del sector, identificar sus invariantes y construir el lenguaje ubicuo del área. Sin código todavía.

---

### Módulo 3 — Spec-Driven Development: el spec-kit como contrato (2 hs)

Un spec-kit es un formato estructurado de especificación que le da a la IA la información necesaria para producir un resultado coherente, verificable y trazable. Es el artefacto que separa el uso profesional del uso ad-hoc —y el que cada equipo necesita diseñar para su propio contexto.

**Contenidos:**
- Qué es SDD y en qué se diferencia de escribir un prompt detallado.
- Anatomía de un spec-kit: precondiciones, postcondiciones, invariantes del dominio, escenarios de comportamiento en lenguaje ejecutable (BDD), contexto arquitectónico relevante.
- Por qué los escenarios BDD son la traducción ejecutable de la especificación y no tests independientes: la especificación y la verificación son el mismo artefacto.
- Cómo evaluar la calidad de un spec-kit: ¿puede alguien sin contexto implementar correctamente lo que está escrito?
- Criterios para diseñar el formato de spec-kit propio: qué campos son universales, cuáles dependen del stack, cuáles dependen del dominio.

**Ejercicio práctico:** escribir un spec-kit completo para la historia de usuario modelada en el módulo anterior. Revisión en pares con criterio explícito de evaluación.

**Artefacto transferible:** plantilla de spec-kit disponible para uso y adaptación inmediata en proyectos propios.

---

### Módulo 4 — Cómo diseñar un flujo agentic de implementación (2 hs)

Un flujo agentic es un proceso estructurado donde la IA participa en fases definidas, produce artefactos concretos por fase y requiere aprobación humana en puntos específicos. No es pedirle a la IA que "haga todo": es diseñar un proceso donde el control humano y la asistencia de la IA tienen roles distintos y complementarios.

El módulo presenta **Claude Dev Kit** como implementación de referencia de ese diseño. No para que los equipos lo adopten, sino para analizar con qué criterios fue construido y derivar los propios.

**Contenidos:**
- Qué hace cada una de las diez fases del Dev Kit: validación del spec-kit, escenarios BDD, plan de implementación, código, tests unitarios, tests de integración, validación de escenarios, quality gates, documentación, reporte final.
- Criterios de diseño: qué fases tiene sentido separar, dónde colocar los puntos de aprobación bloqueantes, qué artefactos generan valor y cuáles son burocracia.
- El rol del tracking por fase: medir el overhead real del proceso como dato de diseño, no como control administrativo.
- Cómo adaptar el diseño al stack del equipo: los principios son independientes de la herramienta de IA subyacente.
- Ejercicio de diseño: dado el stack y contexto del equipo participante, ¿cuántas fases tendría su flujo? ¿Dónde estarían los puntos de aprobación? ¿Qué artefactos generaría cada fase?

**Demostración en vivo:** ejecución completa del Dev Kit sobre una historia de usuario real, desde el spec-kit hasta el reporte final. Foco en los artefactos generados y en las decisiones de diseño que los explican.

**Evidencia:** el overhead del flujo convergió a ~18 minutos por historia de usuario en el experimento AtaraxiaDive, sobre una arquitectura hexagonal de complejidad media.

---

### Módulo 5 — Cómo diseñar quality gates para un proceso agentic (2 hs)

Cuando la IA genera código, puede replicar una mala decisión de diseño a escala industrial antes de que nadie la detecte. Los quality gates son el mecanismo que convierte principios de diseño —cohesión, acoplamiento, separación de responsabilidades— en criterios verificables que el proceso puede evaluar automáticamente.

El módulo presenta **Software Limpio** como implementación de referencia. El objetivo no es que los equipos lo instalen: es que entiendan los principios de diseño detrás de sus tres niveles y puedan construir el esquema propio.

**Contenidos:**
- El triángulo de gobernanza: principios sin métricas son dogma, métricas sin principios son números vacíos, IA sin ambos es caos productivo.
- Por qué los quality gates se diseñan en niveles con acciones deliberadamente distintas: advertir (pre-commit), bloquear (revisión de PR), informar tendencias (cierre de sprint). Confundir los niveles produce gobernanza defectuosa.
- Qué mide Software Limpio en cada nivel y por qué: 6 verificaciones de estilo, seguridad y complejidad (CodeGuard), 12 analizadores de principios SOLID y métricas de acoplamiento/cohesión (DesignReviewer), métricas de Martin y ciclos de dependencias (ArchitectAnalyst).
- Cómo traducir principios de diseño en métricas medibles para un stack específico.
- Cómo calibrar umbrales: no hay umbrales universales, hay umbrales apropiados para un tipo de arquitectura y un tamaño de equipo.
- Criterios para diseñar el esquema propio: qué principios son no negociables, cuáles dependen del contexto, qué herramientas del ecosistema del equipo pueden implementarlos.

**Demostración en vivo:** ejecución de los tres agentes sobre código real del experimento. Interpretación de un reporte: qué principio de diseño está siendo violado, no solo qué número está fuera de umbral.

---

### Módulo 6 — Evidencia, límites y diseño del proceso propio (2 hs)

Enseñar un método sin mostrar sus datos es vender teoría. Este módulo cierra el programa presentando la evidencia real del experimento —incluyendo lo que todavía no está demostrado— y trabaja con el equipo en el diseño concreto de su propio proceso.

**Contenidos:**
- Qué confirma el experimento AtaraxiaDive hasta SP3: la especificación formal reduce la inconsistencia, el flujo agentic es gobernable con puntos de aprobación bien colocados, los quality gates funcionan como dispositivos de diseño y no solo de control.
- Qué sigue abierto: validación en equipos, comparación sistemática con alternativas convencionales, sostenibilidad en proyectos de mayor escala y complejidad.
- Métricas que vale la pena medir en un equipo real: overhead por fase, tendencias de acoplamiento y cohesión entre sprints, cobertura de tests, tasa de violaciones por ciclo.
- Trabajo de diseño: los participantes aplican los criterios del programa a su propio contexto. ¿Cómo sería su spec-kit? ¿Cuántas fases tendría su flujo? ¿Qué tres quality gates considerarían no negociables? ¿Por dónde empezarían la adopción?
- Discusión sobre resistencias esperadas y cómo demostrar valor sin requerir adopción total desde el inicio.

---

## La base de evidencia

Todo lo que se enseña está respaldado por **AtaraxiaDive**, un proyecto real en ejecución diseñado explícitamente como experimento controlado para generar evidencia empírica sobre este método.

Estado actual: tres subproyectos completados, 481 tests pasando, 98% de cobertura en el módulo central, cero violaciones críticas de diseño desde el segundo sprint, overhead del flujo agentic convergido a ~18 minutos por historia de usuario. Los artefactos del experimento —código, reportes de calidad, decisiones de diseño documentadas, métricas por sprint— son accesibles para los participantes durante todo el programa.

Las dos implementaciones de referencia son proyectos de código abierto con métricas propias:
- **Claude Dev Kit v1.3.0**: 107 tests, 99% de cobertura, 5 perfiles de stack documentados · [github.com/vvalotto/claude-dev-kit](https://github.com/vvalotto/claude-dev-kit)
- **Software Limpio v0.3.0**: 12 analizadores AST, métricas de Martin, integración CI/CD · [github.com/vvalotto/software_limpio](https://github.com/vvalotto/software_limpio)

El instructor no describe lo que otros hicieron. Está ejecutando el experimento.

---

## Estructura

- **16 horas:** 4 hs de startup y adaptación al cliente + 12 hs de contenido (6 módulos de 2 hs)
- **Modalidad:** virtual, semanal, con acceso al repositorio del experimento desde el primer módulo
- **Formato:** fundamento conceptual + implementación de referencia analizada + ejercicio de diseño propio

El startup incluye relevamiento del stack, flujos actuales y nivel de adopción de IA del equipo, para ajustar los ejercicios al contexto real de los participantes.

---

## Audiencia

Equipos de desarrollo (5–15 personas), tech leads y arquitectos que ya usan IA de forma ad-hoc y quieren construir un proceso sistemático. Requiere experiencia activa en desarrollo de software. No requiere conocimiento previo de DDD ni de las herramientas presentadas.

---

## Lo que no cubre

| Tema | Razón |
|------|-------|
| Sistemas multi-agente (LangGraph, AutoGen) | Sin evidencia empírica propia en ese dominio. |
| Construcción de productos de IA (RAG, fine-tuning) | El foco es ingeniería de software *con* IA, no construir IA. |
| Stacks distintos a Python | Las implementaciones de referencia cubren Python; los principios son transferibles. |
| Validación en equipos o proyectos enterprise | La evidencia proviene de un proyecto unipersonal de complejidad media. |

---

*Propuesta preparada por Víctor Valotto · Abril 2026 · Versión 1.0*
