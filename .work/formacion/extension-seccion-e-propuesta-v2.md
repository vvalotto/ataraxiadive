
A- VISIÓN DE LA CAPACITACIÓN

La presente propuesta tiene como objetivo brindar una capacitación especializada en el uso profesional de la Inteligencia Artificial en equipos de desarrollo de software, orientada a técnicos, desarrolladores y tech leads que ya utilizan herramientas de IA de forma cotidiana y buscan sistematizar esa práctica con rigor metodológico.
La capacitación parte de una premisa concreta: la IA no elimina la necesidad de ingeniería de software, la desplaza. Cuando la implementación puede derivarse parcialmente desde especificaciones, el cuello de botella deja de estar en escribir código y se concentra en especificar el comportamiento con precisión, construir modelos conceptuales correctos y verificar que el sistema los preserve. Esta capacitación convierte esa premisa en método.
El programa se estructura en 16 horas de capacitación, organizadas de manera progresiva desde el fundamento conceptual hasta la aplicación práctica con herramientas de código abierto. Todo lo que se enseña está respaldado por un proyecto real en ejecución, con métricas, artefactos y evidencia disponibles para los participantes desde el primer módulo.

B- TEMARIO DE LA CAPACITACIÓN
START UP DE LA CAPACITACIÓN: (4 horas)
•	Confirmación/adaptación de las temáticas con el cliente final.
•	Relevamiento del stack tecnológico y flujos de trabajo actuales del equipo.
•	Envío de formulario para evaluar el nivel de adopción de IA y prácticas de ingeniería existentes.
•	Ajuste de contenidos y ejercicios prácticos en base al contexto real del equipo participante.

Modulo 1: (2 horas)
Por qué la IA reconfigura el trabajo del ingeniero de software
•	La cadena de transformación conceptual: Dominio → Modelo → Especificación → Arquitectura → Implementación. En qué capas puede intervenir la IA y en cuáles no puede reemplazar el juicio humano.
El nuevo rol profesional: de programador a evaluador de calidad
•	Las cuatro competencias del profesional en la era de la IA: Dirigir (dar contexto y restricciones), Evaluar (medir con criterios objetivos), Refinar (iterar hasta cumplir principios), Decidir (asumir responsabilidad de diseño). La antifragilidad como postura profesional: el valor construido sobre principios universales se fortalece con la disrupción; el valor construido sobre herramientas específicas, no.
•	Demostración en vivo: la misma tarea enviada dos veces al mismo modelo, una como prompt libre y otra con contexto y restricciones explícitas. Se observa en vivo la diferencia en consistencia y utilidad del resultado, sin herramientas adicionales.

Modulo 2: (2 horas)
El modelo del dominio como base para trabajar con IA
•	Qué es un modelo del dominio y por qué debe construirse antes de interactuar con la IA. Conceptos fundamentales de Domain-Driven Design aplicados al trabajo con modelos de lenguaje: entidades, objetos de valor, agregados, eventos, contextos delimitados, lenguaje ubicuo.
Invariantes y comportamiento esperado
•	Cómo el modelo conceptual actúa como especificación de comportamiento. Qué son los invariantes y por qué una mala especificación amplificada por IA genera más deuda técnica que una mala especificación sin IA.
•	Ejercicio práctico: modelar un dominio simple del sector, identificar sus invariantes y construir el lenguaje ubicuo del área. Sin código todavía.

Modulo 3: (2 horas)
Spec-Driven Development: el spec-kit como contrato con la IA
•	Qué es SDD (Spec-Driven Development) y en qué se diferencia de escribir un prompt. Estructura del spec-kit: precondiciones, postcondiciones, invariantes, escenarios de comportamiento, contexto de dominio e impacto arquitectónico.
Construcción de una especificación formal paso a paso
•	Cómo escribir una historia de usuario con especificación formal (US-IEDD): del lenguaje de negocio a los criterios verificables. Por qué los escenarios BDD son la traducción ejecutable de la especificación y no tests independientes.
•	Ejercicio práctico: especificar la historia de usuario del módulo anterior. Revisión en pares: ¿la especificación es suficientemente precisa para que alguien sin contexto la implemente correctamente?
•	Artefacto transferible: plantilla US-IEDD disponible para uso inmediato en proyectos propios.

Modulo 4: (2 horas)
El flujo agentic de implementación
•	Qué es un flujo agentic de desarrollo y en qué se diferencia del uso ad-hoc de IA. Las 10 fases del Claude Dev Kit: validación, escenarios BDD, plan, implementación, tests unitarios, tests de integración, validación BDD, quality gates, documentación y reporte final. Cómo estructurar los puntos de aprobación humana para no perder el control del proceso.
Tracking, perfiles y compatibilidad
•	El sistema de tracking por fase: por qué medir el tiempo es parte del método, no burocracia. Perfiles de stack disponibles (FastAPI, Flask, PyQt, Python genérico). Compatibilidad con Claude Code y Codex.
•	Demostración en vivo: ejecución completa de /implement-us sobre la historia de usuario especificada en el módulo anterior. Observación de los artefactos generados por fase.

Modulo 5: (2 horas)
Por qué medir es parte del ciclo agentic
•	El triángulo Principios + Métricas + IA: principios sin métricas son dogma, métricas sin principios son números vacíos, IA sin ambos es caos productivo. Cómo los principios de diseño (cohesión, acoplamiento, separación de concerns) se traducen en métricas medibles y cómo esas métricas cierran el ciclo de refinamiento.
Quality gates en tres niveles: Software Limpio
•	CodeGuard (pre-commit, advierte): 6 verificaciones sobre cada archivo modificado. DesignReviewer (PR review, bloquea si crítico): 12 analizadores de diseño orientados a principios SOLID y métricas de acoplamiento y cohesión. ArchitectAnalyst (cierre de sprint, informa tendencias): métricas de Martin, ciclos de dependencias, evolución entre sprints.
•	Cómo calibrar umbrales por tipo de arquitectura. Integración con CI/CD y hooks de git.
•	Demostración en vivo: ejecución de los tres agentes sobre código real del experimento. Interpretación de un reporte: qué principio está siendo violado, no solo qué número está fuera de umbral.

Modulo 6: (2 horas)
Evidencia, límites del método y adaptación al equipo
•	Qué se ha confirmado experimentalmente en el proyecto AtaraxiaDive (SP1 a SP3, 481 tests, quality reports por incremento): la automatización requiere calibración humana, la productividad táctica no elimina la necesidad de ingeniería, los quality gates funcionan como dispositivos de gobierno del proceso.
Qué sigue abierto y cómo adoptar el método
•	Qué no está demostrado todavía: costo total frente a alternativas convencionales, validación en equipos, sostenibilidad en proyectos más largos. Métricas que vale la pena medir en un equipo real. Cómo introducir el método en un equipo que ya usa IA de forma ad-hoc: por dónde empezar, qué resistencias esperar, cómo demostrar valor sin requerir adopción total.
•	Discusión abierta: casos del equipo, adaptaciones al stack y contexto propio.

TOTAL DE HORAS DE CAPACITACIÓN 2 = 16 horas

C- ESTRUCTURA GENERAL DE LA CAPACITACIÓN VIRTUAL:
•	Start up (4 horas) y Contenidos (12 horas)
•	Cada clase se desarrolla en un módulo de 2 horas
•	Las clases serán semanales, preferentemente en el mismo día y horario
•	La capacitación se desarrolla en módulos teórico-prácticos, combinando:
o	Exposición conceptual con fundamento teórico explícito.
o	Demostraciones en vivo sobre código y artefactos reales de un proyecto en ejecución.
o	Ejercicios aplicados con artefactos transferibles al trabajo propio.
o	Espacios de discusión sobre límites del método, evidencia disponible y adaptación al contexto del equipo.
El enfoque está orientado a que los participantes comprendan el "por qué" antes del "cómo", adquiriendo criterios de ingeniería transferibles que no dependen de herramientas específicas. Los repositorios de las herramientas utilizadas son públicos y accesibles desde el primer módulo.

D- OBJETIVOS DE APRENDIZAJE
•	Comprender por qué la IA desplaza el trabajo del ingeniero hacia las capas de mayor valor y qué implica eso en la práctica diaria del equipo.
•	Construir modelos de dominio y especificar comportamiento con el nivel de precisión necesario para trabajar con IA de forma predecible y consistente.
•	Dominar el formato de especificación formal (spec-kit) como artefacto transferible a proyectos propios, independientemente del stack tecnológico.
•	Ejecutar un flujo agentic de implementación completo, con puntos de control humano en cada fase.
•	Instrumentar quality gates en tres niveles, interpretar sus resultados en términos de principios de diseño y calibrarlos al contexto del equipo.
•	Evaluar con criterio propio qué parte del método es aplicable en su organización y por dónde iniciar la adopción.

E- AUDIENCIA Y PRERREQUISITOS
Esta capacitación está dirigida a equipos de desarrollo (5 a 15 personas), tech leads y arquitectos de software que ya utilizan herramientas de IA en su trabajo diario y buscan sistematizar esa práctica.
•	Requiere experiencia activa en desarrollo de software.
•	No requiere conocimiento previo de IA, DDD ni metodologías ágiles formales.
•	No es adecuada para perfiles no técnicos o equipos sin práctica de desarrollo activa.
Las herramientas utilizadas durante la capacitación cubren proyectos Python. Para otros stacks, los conceptos metodológicos son transferibles; las herramientas de quality gates requieren adaptación.
