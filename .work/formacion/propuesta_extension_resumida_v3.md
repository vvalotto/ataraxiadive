# Ingeniería de Software con IA: del uso ad-hoc al proceso propio
## Propuesta de extensión técnica para equipos de desarrollo

*Víctor Valotto — Abril 2026*

---

## El enfoque

Cuando un equipo incorpora IA al desarrollo, aparece rápido un primer techo: los resultados son inconsistentes, cada interacción empieza desde cero y el conocimiento acumulado no se transfiere. El problema rara vez es la herramienta. Es que el equipo todavía no tiene colaboradores propios — templates que ya saben cómo especificar, procesos que se repiten sin la fricción habitual, skills que codifican el conocimiento del equipo y trabajan con consistencia.

Construir esos colaboradores requiere un marco conceptual sólido, no horas de trabajo adicional. Esta capacitación trabaja ese marco y lo convierte en artefactos concretos que el equipo puede usar desde el primer módulo.

La diferencia entre el uso ad-hoc y el uso sistemático de la IA no es de esfuerzo: es de estructura. Un colaborador bien diseñado produce resultados coherentes sin que nadie tenga que recordar el contexto cada vez. Esta capacitación enseña a diseñar esa estructura.

---

## Contenido por módulo

### Módulo 1 — Cuando la implementación se automatiza, ¿qué queda para el ingeniero? (2 hs)

El primer módulo no presenta herramientas. Establece el problema que hace que valga la pena construir colaboradores.

Cuando la implementación puede asistirse con IA, el cuello de botella no desaparece: se desplaza. Deja de estar en escribir código y se concentra en especificar el comportamiento con precisión, construir el modelo conceptual correcto y verificar que el resultado lo preserve. Una mala especificación amplificada por IA genera más deuda técnica que una mala especificación sin IA — y la genera más rápido.

**Contenidos:**
- La cadena de transformación: Dominio → Modelo → Especificación → Arquitectura → Implementación. En qué capas puede intervenir la IA y en cuáles el juicio humano es irreemplazable.
- El nuevo rol profesional: cuatro competencias que la IA no sustituye sino que vuelve más necesarias — Dirigir (dar contexto y restricciones), Evaluar (medir con criterios objetivos), Refinar (iterar hasta cumplir principios de diseño), Decidir (asumir responsabilidad de las elecciones arquitectónicas).
- Por qué el uso ad-hoc no escala: deuda de especificación, resultados inconsistentes, pérdida de coherencia entre artefactos.
- La hipótesis que orienta el programa: cuanto más automatizable es la implementación, más crítica se vuelve la especificación — y más valioso es tener colaboradores que ya sepan cómo especificar.

**Demostración en vivo:** la misma tarea enviada dos veces al mismo modelo — una como prompt libre, otra con contexto, restricciones y criterios explícitos. La diferencia en consistencia y utilidad del resultado es visible sin necesidad de explicación adicional.

---

### Módulo 2 — El modelo del dominio: lo que un buen colaborador necesita saber (2 hs)

Para que un colaborador produzca resultados coherentes, necesita entender el problema. Ese entendimiento vive en el modelo del dominio: la representación conceptual de los objetos, comportamientos y reglas del negocio que el sistema debe implementar. Sin ese modelo, cualquier template o proceso trabaja en el vacío.

Este módulo introduce Domain-Driven Design como herramienta de especificación — no como metodología completa, sino como el conjunto de conceptos que tienen impacto directo en la calidad de lo que se le pide a la IA.

**Contenidos:**
- Qué es un modelo del dominio y por qué construirlo antes de interactuar con la IA.
- Conceptos fundamentales de DDD aplicados a la especificación: entidades, objetos de valor, agregados, eventos del dominio, contextos delimitados, lenguaje ubicuo.
- Invariantes: condiciones que el sistema debe preservar siempre, independientemente de cómo esté implementado. Son el núcleo de la especificación formal y el conocimiento más valioso que un colaborador puede codificar.
- Cómo el lenguaje ubicuo reduce la ambigüedad en la comunicación con la IA y entre los miembros del equipo.

**Ejercicio práctico:** modelar un dominio simple del sector, identificar sus invariantes y construir el lenguaje ubicuo del área. Sin código todavía.

---

### Módulo 3 — El spec-kit: un colaborador que ya sabe cómo especificar (2 hs)

Un spec-kit es un formato estructurado de especificación. Es el primer colaborador concreto: una vez diseñado para el contexto del equipo, produce especificaciones coherentes sin que nadie tenga que recordar qué información incluir o en qué orden presentarla.

Lo que separa un spec-kit de un prompt detallado es que el spec-kit codifica el modelo del dominio — y eso lo hace verificable. Se puede evaluar si una especificación es suficientemente precisa antes de enviarla a la IA.

**Contenidos:**
- Qué es SDD (Spec-Driven Development) y en qué se diferencia de escribir prompts elaborados.
- Anatomía de un spec-kit: precondiciones, postcondiciones, invariantes del dominio, escenarios de comportamiento en lenguaje ejecutable (BDD), contexto arquitectónico relevante.
- Por qué los escenarios BDD son la traducción ejecutable de la especificación y no tests independientes: la especificación y la verificación son el mismo artefacto.
- Criterios para diseñar el spec-kit propio: qué campos son universales, cuáles dependen del stack, cuáles dependen del dominio.

**Ejercicio práctico:** escribir un spec-kit completo para la historia de usuario modelada en el módulo anterior. Revisión en pares con criterio explícito de evaluación.

**Artefacto transferible:** plantilla de spec-kit disponible para uso y adaptación inmediata en proyectos propios.

---

### Módulo 4 — El flujo agentic: un colaborador que ya sabe cómo implementar (2 hs)

Un flujo agentic es un proceso estructurado donde la IA participa en fases definidas, produce artefactos concretos por fase y requiere aprobación humana en puntos específicos. Es el segundo colaborador clave: una vez diseñado, el equipo no tiene que redescubrir en cada historia qué pasos seguir, dónde revisar o qué artefactos generar.

El módulo presenta una implementación de referencia de ese diseño — no para que los equipos la adopten tal cual, sino para analizar con qué criterios fue construida y derivar la propia.

**Contenidos:**
- Qué hace cada fase de un flujo agentic bien diseñado: validación del spec-kit, escenarios BDD, plan de implementación, código, tests unitarios, tests de integración, validación de escenarios, quality gates, documentación, reporte final.
- Criterios de diseño: qué fases tiene sentido separar, dónde colocar los puntos de aprobación bloqueantes, qué artefactos generan valor y cuáles son burocracia.
- El rol del tracking por fase: medir el overhead real del proceso como dato de diseño, no como control administrativo.
- Ejercicio de diseño: dado el stack y contexto del equipo, ¿cuántas fases tendría su flujo? ¿Dónde estarían los puntos de aprobación? ¿Qué artefactos generaría cada fase?

**Demostración en vivo:** ejecución completa del flujo sobre una historia de usuario real, desde el spec-kit hasta el reporte final. Foco en los artefactos generados y en las decisiones de diseño que los explican.

---

### Módulo 5 — Los quality gates: colaboradores que ya saben qué verificar (2 hs)

Cuando la IA genera código, puede replicar una mala decisión de diseño a escala industrial antes de que nadie la detecte. Los quality gates son el tercer colaborador: verifican automáticamente que el resultado cumpla los principios de diseño que el equipo considera no negociables.

Lo que distingue un quality gate bien diseñado de un linter genérico es que mide principios — cohesión, acoplamiento, separación de responsabilidades — no solo convenciones de estilo.

**Contenidos:**
- El triángulo de gobernanza: principios sin métricas son dogma, métricas sin principios son números vacíos, IA sin ambos es caos productivo.
- Por qué los quality gates se diseñan en niveles con acciones deliberadamente distintas: advertir (pre-commit), bloquear (revisión de PR), informar tendencias (cierre de sprint). Confundir los niveles produce gobernanza defectuosa.
- Una implementación de referencia analizada en sus tres niveles: verificaciones de estilo, seguridad y complejidad; analizadores de principios SOLID y métricas de acoplamiento/cohesión; métricas de Martin y ciclos de dependencias.
- Cómo calibrar umbrales al contexto del equipo: no hay umbrales universales, hay umbrales apropiados para un tipo de arquitectura y un tamaño de equipo.
- Criterios para diseñar el esquema propio: qué principios son no negociables, cuáles dependen del contexto, qué herramientas del ecosistema del equipo pueden implementarlos.

**Demostración en vivo:** ejecución de los tres niveles sobre código real. Interpretación de un reporte: qué principio de diseño está siendo violado, no solo qué número está fuera de umbral.

---

### Módulo 6 — El equipo propio: integrar los colaboradores en el proceso real (2 hs)

Los módulos anteriores construyen tres colaboradores: el spec-kit, el flujo agentic y los quality gates. Este módulo trabaja la integración y la adopción: cómo estos colaboradores funcionan juntos, qué evidencia existe sobre su comportamiento en un ciclo completo y cómo introducirlos en un equipo que ya tiene su propia forma de trabajar.

**Contenidos:**
- Qué confirma la evidencia disponible de un ciclo completo de desarrollo con este método: la especificación formal reduce la inconsistencia entre lo especificado y lo implementado; el flujo agentic es gobernable con puntos de aprobación bien posicionados; los quality gates funcionan como dispositivos de reflexión de diseño, no solo como detectores de violaciones.
- Hallazgos que la evidencia no anticipó: los quality gates generan valor indirecto al crear checkpoints donde emerge conocimiento de diseño no automatizable; los datos reales del dominio detectan errores que sobreviven a toda la especificación formal; la IA no es un ejecutor confiable en los pasos de coordinación humana y requiere verificación activa.
- Qué sigue abierto: validación en equipos, comparación sistemática con alternativas convencionales, sostenibilidad en proyectos de mayor escala.
- Métricas que vale la pena medir en un equipo real: overhead por fase, tendencias de acoplamiento y cohesión entre sprints, cobertura de tests, tasa de violaciones por ciclo.
- Trabajo de diseño: los participantes aplican los criterios del programa a su propio contexto. ¿Cómo sería su spec-kit? ¿Cuántas fases tendría su flujo? ¿Qué tres quality gates considerarían no negociables? ¿Por dónde empezarían la adopción?

---

## La base de evidencia

Todo lo que se presenta está respaldado por un ciclo completo de desarrollo diseñado como experimento controlado, con el objetivo explícito de generar evidencia empírica sobre este método. El experimento produce artefactos accesibles: especificaciones, reportes de calidad, decisiones de diseño documentadas y métricas por sprint. Los participantes pueden revisar ese material durante todo el programa.

Las dos implementaciones de referencia son proyectos de código abierto:
- **Claude Dev Kit**: framework de implementación agentic en 10 fases, con 5 perfiles de stack documentados · [github.com/vvalotto/claude-dev-kit](https://github.com/vvalotto/claude-dev-kit)
- **Software Limpio**: framework de quality gates en tres niveles con 12 analizadores AST · [github.com/vvalotto/software_limpio](https://github.com/vvalotto/software_limpio)

El instructor no describe lo que otros hicieron. Está ejecutando el experimento.

---

## Estructura

- **16 horas:** 4 hs de startup y adaptación al cliente + 12 hs de contenido (6 módulos de 2 hs)
- **Modalidad:** virtual, semanal, con acceso al repositorio de referencia desde el primer módulo
- **Formato:** marco conceptual + implementaciones de referencia analizadas + ejercicio de diseño propio

El startup incluye relevamiento del stack, flujos actuales y nivel de adopción de IA del equipo, para ajustar los ejercicios al contexto real de los participantes.

---

## Audiencia

Equipos de desarrollo (5–15 personas), tech leads y arquitectos que ya usan IA de forma ad-hoc y quieren construir un proceso propio. Requiere experiencia activa en desarrollo de software. No requiere conocimiento previo de DDD ni de las herramientas presentadas.

---

## Lo que no cubre

| Tema | Razón |
|------|-------|
| Sistemas multi-agente (LangGraph, AutoGen) | Sin evidencia empírica propia en ese dominio. |
| Construcción de productos de IA (RAG, fine-tuning) | El foco es ingeniería de software *con* IA, no construir IA. |
| Stacks distintos a Python | Las implementaciones de referencia cubren Python; los principios son transferibles. |
| Validación del método en equipos | La evidencia disponible proviene de un proyecto individual. La extrapolación a equipos requiere calibración propia. |

---

*Propuesta preparada por Víctor Valotto · Abril 2026 · Versión 3.0*
