# Consideraciones de alcance
## Ingeniería de Software con IA: del uso ad-hoc al proceso propio

*Víctor Valotto — Abril 2026*

---

Toda propuesta tiene condiciones de aplicabilidad. Las tres consideraciones que siguen no son advertencias de último momento: son parte del diagnóstico honesto que permite decidir si esta capacitación es la respuesta correcta para un equipo en particular, o si requiere ajustes antes de presentarla.

---

## 1. Qué incluyen las 4 horas de startup

Las 4 horas de startup no forman parte de los módulos de contenido. Son trabajo previo que hace posible que los módulos sean útiles para ese equipo en particular y no para un equipo genérico.

Incluyen cuatro actividades concretas: una reunión con el cliente para confirmar qué temáticas son prioritarias y cuáles pueden ajustarse; un relevamiento del stack tecnológico y los flujos de trabajo actuales del equipo; un análisis para mapear su nivel real de adopción de IA; y el ajuste de los ejercicios prácticos en función de ese contexto.

El resultado esperado es que las demostraciones en vivo y los ejercicios de diseño usen el contexto del equipo — su dominio, su stack, sus prácticas actuales — y no un caso construido para la ocasión. Sin este trabajo previo, la capacitación puede darse, pero pierde buena parte de lo que la diferencia de un curso grabado.

Las 4 horas son el costo real de esa personalización. No es burocracia: es la inversión que transforma contenido genérico en contenido aplicable.

---

## 2. Qué pasa si el equipo no trabaja con Python

Es la limitación técnica más importante de la propuesta y conviene nombrarla antes de la conversación con el cliente, no después.

Las dos implementaciones de referencia — Claude Dev Kit y Software Limpio — solo cubren proyectos Python en su versión actual. Un equipo que trabaja con TypeScript, Java, Go o cualquier otro stack puede seguir todos los módulos, pero la transferencia directa de herramientas no está disponible: el participante puede diseñar su spec-kit y su flujo agentic, pero no se va con una herramienta instalable que funcione en su repositorio sin trabajo adicional.

Lo que sí es transferible con independencia del stack:

- El marco conceptual completo: DDD, invariantes, lenguaje ubicuo, cadena de transformación.
- El formato de spec-kit: es un documento estructurado, no código. Se adapta a cualquier contexto.
- El diseño del flujo agentic: los principios de separación de fases, puntos de aprobación y tracking aplican a cualquier agente de codificación.
- Los criterios para diseñar quality gates: aunque la implementación concreta requiere encontrar o construir equivalentes en el ecosistema del equipo.

La pregunta práctica antes de presentar la propuesta es directa: ¿el equipo trabaja principalmente con Python? Si la respuesta es no, el valor de la capacitación está en el método y los conceptos — que es valor real — pero la promesa de herramientas listas para usar no aplica. Mencionarlo explícitamente en la propuesta evita una conversación incómoda después de la primera sesión.

---

## 3. Qué pasa si el equipo trabaja sobre un producto en uso

Esta es quizás la consideración más frecuente y la que la evidencia disponible cubre menos.

El experimento que respalda esta propuesta fue diseñado desde cero: arquitectura limpia desde el primer commit, modelo del dominio construido antes de la primera línea de código, quality gates con baseline en cero. La mayoría de los equipos reales trabajan sobre un producto con historia — deuda técnica acumulada, convenciones no escritas, comportamiento heredado que nadie quiere romper.

**Lo que funciona igual.** El spec-kit y el marco conceptual de los módulos 1, 2 y 3 conservan su valor con independencia de si el producto existe. Especificar el comportamiento esperado antes de implementar tiene sentido — y en código legacy tiene sentido adicional: reduce el riesgo de romper comportamiento existente que no está documentado. El lenguaje ubicuo también gana relevancia en equipos con historia: es frecuente que el mismo concepto de negocio tenga tres nombres distintos en el código, en las reuniones y en los tickets.

**Lo que se complica.** El flujo agentic requiere que el agente tenga contexto del código existente para no generar soluciones que ignoren convenciones, dependencias o restricciones ya presentes. Eso implica estrategias adicionales — ventanas de contexto más cuidadas, documentación del sistema como parte del spec-kit, criterios explícitos sobre qué partes del código el agente puede modificar y cuáles no. La propuesta no cubre esas estrategias en profundidad porque la evidencia disponible no las incluye.

Los quality gates son el punto más delicado. Un producto en uso típicamente ya tiene violations: acoplamiento elevado en módulos viejos, cohesión baja en clases que crecieron sin diseño deliberado, complejidad heredada. Si los umbrales se calibran sobre ese baseline, los gates pierden sensibilidad para detectar degradación nueva. Si se calibran con valores ideales, bloquean trabajo válido con ruido de deuda existente. Calibrar bien en ese contexto es un problema no trivial que requiere un proceso propio — y la capacitación lo señala como problema de diseño, no lo resuelve.

**La conclusión práctica.** Para un equipo trabajando sobre un producto en uso, los módulos 1, 2 y 3 ofrecen valor transferible de forma directa. Los módulos 4 y 5 son útiles como referencia de diseño: el equipo entiende los principios y puede construir su propio esquema, pero la adopción requiere adaptación que va más allá de lo que la capacitación puede garantizar. El módulo 6, que trabaja el diseño del proceso propio, cobra especial relevancia en este contexto: es el espacio donde esa adaptación empieza a tomar forma.

---

## Síntesis para la conversación con el cliente

Estas tres consideraciones no invalidan la propuesta. La enmarcan. Un equipo que trabaja con Python en un proyecto nuevo o en uno relativamente joven, con disposición a construir proceso, es el contexto donde la propuesta entrega su valor completo. A medida que el contexto se aleja de ese punto — otro stack, producto con historia, deuda técnica significativa — la transferencia directa de herramientas disminuye, pero el valor conceptual se mantiene.

La conversación de diagnóstico con el cliente antes de presentar la propuesta debería responder tres preguntas:

1. ¿Cuál es el stack principal del equipo?
2. ¿Están construyendo algo nuevo o manteniendo un producto en uso?
3. ¿Qué buscan llevarse: herramientas instalables, o un método que puedan adaptar?

Las respuestas determinan qué parte de la propuesta es aplicable de forma directa y qué parte requiere encuadre honesto sobre el trabajo adicional que implicaría la adopción.

---

*Versión 1.0 — Abril 2026*
