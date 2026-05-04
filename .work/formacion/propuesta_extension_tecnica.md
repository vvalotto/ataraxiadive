# Extensión Técnica: Ingeniería de Software con IA
## Track especializado para equipos de desarrollo
### Complemento a la Propuesta de Capacitación en Inteligencia Artificial

*Víctor Valotto — Abril 2026*

---

## Posicionamiento

La propuesta de capacitación en IA cubre lo que cualquier profesional necesita entender sobre la tecnología: qué son los modelos de lenguaje, cómo funcionan, qué riesgos presentan y cómo impactan en los procesos y modelos de negocio. Es un programa de formación en profundidad para una audiencia amplia.

Esta extensión cubre algo diferente y complementario: **cómo trabaja un equipo de desarrollo de software cuando incorpora IA de forma sistemática**. No es sobre qué es la IA, sino sobre qué cambia en la práctica profesional de quien construye sistemas cuando la IA empieza a participar en ese proceso.

Son dos necesidades distintas. Esta extensión responde a la segunda.

---

## La premisa que la fundamenta

Cuando la implementación de código puede asistirse con IA, el cuello de botella no desaparece: se desplaza. Deja de estar en escribir código y se concentra en algo que la IA no puede hacer sola: comprender el dominio del problema, construir el modelo conceptual correcto, especificar el comportamiento del sistema con precisión, y verificar que el resultado lo preserve.

Dicho de otra manera: **cuanto más automatizable es la implementación, más crítica se vuelve la especificación**. Un equipo que usa IA sin método puede producir código que funciona pero que no corresponde al problema real, con una velocidad que hace el error más difícil de detectar.

Esta extensión parte de esa premisa y la convierte en un método de trabajo concreto, respaldado por evidencia empírica real.

---

## Qué propone el programa

El programa se organiza en seis módulos de dos horas, con la misma estructura semanal de la propuesta base.

---

### Módulo 1 — El ingeniero en la era de la IA (2 hs)

El primer módulo no presenta herramientas. Establece el problema.

Cuando la implementación puede delegarse parcialmente, el valor profesional se concentra en cuatro competencias: **dirigir** (dar contexto y restricciones a la IA), **evaluar** (medir el resultado con criterios objetivos), **refinar** (iterar hasta que el resultado cumpla los principios de diseño), y **decidir** (asumir la responsabilidad de las elecciones arquitectónicas). La IA no reemplaza ninguna de estas competencias; las hace más necesarias.

La sesión cierra con una demostración en vivo: la misma tarea de desarrollo enviada dos veces al mismo modelo, una como prompt libre y otra con contexto, restricciones y criterios explícitos. La diferencia en la consistencia y utilidad del resultado es visible sin necesidad de explicación adicional.

---

### Módulo 2 — El modelo del dominio como especificación (2 hs)

Antes de pedirle algo a la IA, el equipo necesita saber con precisión qué quiere. Ese conocimiento vive en el modelo del dominio: la representación conceptual de los objetos, comportamientos y reglas del negocio que el sistema debe implementar.

Este módulo introduce Domain-Driven Design —no como metodología completa, sino como herramienta de especificación— y trabaja el concepto de invariante: las condiciones que el sistema debe preservar siempre, independientemente de cómo esté implementado. Una mala especificación amplificada por IA genera más deuda técnica que una mala especificación sin IA. La velocidad no resuelve el problema de fondo; lo escala.

El módulo incluye un ejercicio práctico de modelado sobre un dominio del sector del equipo participante.

---

### Módulo 3 — Spec-Driven Development: el contrato con la IA (2 hs)

Un spec-kit es un formato estructurado de especificación que le da a la IA la información que necesita para producir un resultado coherente, verificable y trazable. Es el artefacto central del método y el que separa el uso profesional del uso ad-hoc.

El módulo presenta la estructura completa de un spec-kit: precondiciones, postcondiciones, invariantes del dominio, escenarios de comportamiento en lenguaje ejecutable (BDD), contexto de dominio y consideraciones arquitectónicas. El participante aprende a escribir uno paso a paso y verifica la calidad de su especificación con una prueba concreta: ¿puede alguien sin contexto implementar correctamente lo que está escrito?

Al finalizar el módulo, cada participante tiene una plantilla de especificación transferible a sus proyectos propios.

---

### Módulo 4 — El flujo agentic de implementación (2 hs)

Un flujo agentic no es pedirle a la IA que "haga todo". Es un proceso estructurado con fases definidas, artefactos por fase y puntos de aprobación humana. La diferencia entre un flujo agentic y el uso ad-hoc es la misma que entre un proceso de ingeniería y una improvisación documentada.

Este módulo presenta **Claude Dev Kit**, un framework de código abierto (v1.3.0, MIT) que implementa ese flujo en diez fases: validación de la especificación, generación de escenarios de comportamiento, plan de implementación, código, tests unitarios, tests de integración, validación de escenarios, quality gates automáticos, documentación y reporte final. Cada fase produce artefactos concretos. Dos fases requieren aprobación explícita del ingeniero antes de continuar.

La sesión incluye una demostración en vivo completa del flujo sobre una historia de usuario real, desde el spec-kit hasta el reporte final.

**Evidencia medida:** el overhead del flujo convergió a aproximadamente 18 minutos por historia de usuario en el experimento de referencia, sobre una arquitectura de complejidad media.

---

### Módulo 5 — Quality gates: gobernar el proceso agentic (2 hs)

La IA puede replicar una mala decisión de diseño a escala industrial antes de que nadie la detecte. Los quality gates no son un control posterior: son el mecanismo que convierte principios abstractos de diseño en criterios verificables y cierra el ciclo con evidencia objetiva.

El módulo presenta **Software Limpio**, un framework de código abierto (v0.3.0, MIT) que opera en tres niveles:

| Nivel | Herramienta | Momento | Acción |
|-------|-------------|---------|--------|
| 1 | CodeGuard | Pre-commit | Advierte: 6 verificaciones de estilo, seguridad y complejidad |
| 2 | DesignReviewer | Revisión de PR | Bloquea si es crítico: 12 analizadores de diseño orientados a principios SOLID |
| 3 | ArchitectAnalyst | Cierre de sprint | Informa tendencias: métricas de acoplamiento, cohesión y ciclos de dependencias |

Cada nivel tiene una acción deliberadamente diferente. Confundir el nivel que advierte con el que bloquea —o el que bloquea con el que informa— produce gobernanza defectuosa. El módulo trabaja sobre ese distinción y sobre cómo calibrar los umbrales al contexto del equipo.

La sesión incluye una demostración en vivo sobre código real del experimento, con interpretación de un reporte: no solo qué número está fuera de umbral, sino qué principio de diseño está siendo violado.

---

### Módulo 6 — Evidencia, límites y adopción (2 hs)

Enseñar un método sin mostrar sus datos es vender teoría. Este módulo cierra el programa con la evidencia real del experimento —incluyendo lo que todavía no está demostrado— y trabaja con el equipo en cómo adaptar el método a su propio contexto.

Se presentan los resultados concretos del experimento AtaraxiaDive (SP1 a SP3): 481 tests, quality gates en cada incremento, métricas de acoplamiento y cohesión por sprint, overhead medido por fase. Se identifican también los límites actuales del método: no está validado en equipos, no está comparado sistemáticamente contra alternativas convencionales, y la evidencia proviene de un proyecto conducido por un desarrollador experto con rigor de producto real pero sin usuarios en producción todavía.

El módulo cierra con trabajo práctico: qué cambiar primero en el flujo del equipo, qué resistencias esperar, cómo demostrar valor sin requerir adopción total desde el inicio.

---

## La base de evidencia

Lo que diferencia esta propuesta de otras capacitaciones sobre IA y desarrollo de software es concreto: el instructor no describe casos de otros. **Está ejecutando el experimento mientras enseña.**

### Proyecto AtaraxiaDive

Plataforma web para gestión de torneos de apnea, desarrollada como experimento controlado para generar evidencia empírica sobre el método IEDD (Ingeniería de Especificaciones Dirigida por el Dominio). No es un proyecto de demostración: tiene atributos de calidad no funcionales acotados, arquitectura hexagonal formal, quality gates en cada incremento y decisiones de diseño documentadas con justificación.

Estado actual: tres subproyectos completados (SP1 a SP3), 481 tests pasando, cobertura del 98% en el módulo central, cero violaciones críticas de diseño desde el segundo sprint. Los artefactos del experimento —código, reportes de calidad, decisiones arquitectónicas, métricas de tracking— son accesibles para los participantes desde el primer módulo.

### Claude Dev Kit — v1.3.0

Framework instalable de código abierto (MIT) que implementa el flujo agentic de 10 fases. 107 tests propios, 99% de cobertura. Cinco perfiles de stack documentados (FastAPI, Flask REST, Flask Web App, PyQt, Python genérico), cada uno con proyectos de ejemplo con métricas reales. Compatible con Claude Code y Codex.

Repositorio: [github.com/vvalotto/claude-dev-kit](https://github.com/vvalotto/claude-dev-kit)

### Software Limpio — v0.3.0

Framework de control de calidad en tres niveles (CodeGuard, DesignReviewer, ArchitectAnalyst). 12 analizadores AST orientados a principios de diseño. Métricas de Martin para análisis arquitectónico. Integración con hooks de git y pipelines CI/CD.

Repositorio: [github.com/vvalotto/software_limpio](https://github.com/vvalotto/software_limpio)

### Marco IEDD

Fundamento conceptual del método: cinco capas de transformación (Dominio → Modelo → Especificación → Arquitectura → Implementación), hipótesis experimental documentada y plantilla de especificación formal (US-IEDD). Más de 30 historias de usuario implementadas con este formato en el experimento.

---

## Cómo se integra con el programa original

Las dos propuestas responden a necesidades distintas y se complementan sin superponerse.

| | Programa base | Extensión técnica |
|---|---|---|
| **Audiencia** | Toda la organización | Equipos de desarrollo |
| **Foco** | IA: qué es, cómo funciona, qué impacta | Cómo trabajar con IA de forma sistemática |
| **Contenido** | Modelos de lenguaje, riesgos, plataformas, innovación | Especificación, flujo agentic, quality gates |
| **Resultado** | Criterios para evaluar y adoptar IA | Método de trabajo transferible a proyectos propios |

La extensión asume que los participantes han completado el programa base, o que tienen experiencia equivalente con herramientas de IA. No repite contenido; lo profundiza para un perfil específico.

---

## Estructura y formato

- **Total:** 16 horas (4 hs de startup y adaptación al cliente + 12 hs de contenido)
- **Formato:** módulos semanales de 2 horas, mismo día y horario
- **Modalidad:** virtual, con acceso a los repositorios de código durante todo el programa
- **Cada módulo combina:** exposición conceptual con fundamento teórico explícito · demostración en vivo sobre código y artefactos reales · ejercicio aplicado con artefacto transferible

Las cuatro horas de startup incluyen relevamiento del stack tecnológico y flujos de trabajo actuales del equipo, ajuste de ejercicios prácticos al contexto real, y evaluación del nivel de adopción de IA existente para calibrar el punto de partida.

---

## Audiencia y prerrequisitos

Equipos de desarrollo de 5 a 15 personas, tech leads y arquitectos de software que ya utilizan herramientas de IA en su trabajo diario y quieren sistematizar esa práctica.

**Requiere:** experiencia activa en desarrollo de software.  
**No requiere:** conocimiento previo de DDD, metodologías ágiles formales ni herramientas de IA específicas.  
**Nota de stack:** las herramientas de quality gates y el framework de implementación cubren proyectos Python. Para otros stacks, los conceptos metodológicos son completamente transferibles; las herramientas requieren adaptación.

---

## Lo que esta propuesta no cubre

La claridad sobre los límites es parte de la propuesta, no un debilitamiento.

| Tema | Razón |
|------|-------|
| Sistemas multi-agente (LangGraph, AutoGen, CrewAI) | Sin evidencia empírica propia. Puede combinarse con módulos del programa base si se requiere. |
| Construcción de productos de IA (RAG, fine-tuning) | El problema abordado es ingeniería de software *con* IA, no construir IA. |
| Stacks distintos a Python | Claude Dev Kit y Software Limpio cubren Python. El roadmap incluye TypeScript/Node.js pero no está disponible. |
| Validación en equipos grandes o enterprise | La evidencia proviene de un proyecto unipersonal de complejidad media. La extrapolación requiere calibración. |
| Garantías de reducción de costo o mejora de calidad medida | La hipótesis tiene validación parcial. No se afirma como resultado probado. |

---

## Por qué esta propuesta es diferente

La mayoría de las capacitaciones sobre IA para desarrollo de software enseñan herramientas. Esta propuesta enseña un método con fundamento conceptual, herramientas que lo implementan, y evidencia real de hasta dónde funciona y dónde todavía está en evaluación.

Esa honestidad no es una limitación. Es lo que le da valor duradero al aprendizaje: los participantes adquieren criterios de ingeniería transferibles, no dependencias de plataformas que pueden cambiar en seis meses.

El instructor no describe un experimento que alguien hizo en otro lugar. Lo está ejecutando.

---

*Propuesta preparada por Víctor Valotto · Abril 2026*  
*Versión 1.0*
