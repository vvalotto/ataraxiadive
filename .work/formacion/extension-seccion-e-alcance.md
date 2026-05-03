# Extensión Sección E — Alcance de la Propuesta

> Documento de alcance previo a la redacción de la propuesta completa.
> Define qué está dentro y qué queda fuera, con justificación basada en evidencia disponible.

---

## Propósito de la extensión

Responder los tres requerimientos de la Sección E de la propuesta original:

1. Evolución hacia enfoques **agentic**: del uso de chat a flujos estructurados y autónomos.
2. **Metodologías de ingeniería**: SDD (Spec-Driven Development) y uso de spec-kits.
3. **Ciclo de vida integral**: testing, documentación y codificación desde una lógica de orquestación de procesos.

La extensión no reemplaza los módulos 1–6 de la propuesta original. Se posiciona como un
**track técnico complementario** orientado a equipos de desarrollo.

---

## Dentro del alcance

### 1. Marco conceptual: IEDD y la reconfiguración del rol del ingeniero

**Qué es:** Un marco teórico que reformula la ingeniería de software en cinco capas
(Dominio → Modelo → Especificación → Arquitectura → Implementación) y sostiene que la IA
desplaza el cuello de botella desde la implementación hacia la especificación.

**Por qué está incluido:** Provee el fundamento conceptual sin el cual las herramientas
son solo herramientas. Responde el "por qué ahora" de la sección E.

**Evidencia de soporte:**
- `docs/iedd/01-Ingenieria_Especificaciones_DDD_IA.md`
- `docs/iedd/02-Marco_Conceptual_5_Capas.md`

**Límite honesto:** Es un marco en construcción con validación empírica inicial, no
una teoría cerrada ni publicada académicamente.

---

### 2. SDD + spec-kits: la US-IEDD como artefacto de especificación

**Qué es:** Un formato concreto de historia de usuario con precondiciones, postcondiciones,
invariantes, escenarios BDD y contexto de dominio. Es el spec-kit operativo del marco IEDD.

**Por qué está incluido:** Es exactamente lo que la sección E pide bajo "SDD y uso de
spec-kits". Es transferible, instalable y tiene uso documentado en un proyecto real.

**Evidencia de soporte:**
- `docs/iedd/US-IEDD-template.md` — plantilla completa
- AtaraxiaDive SP1→SP3 — más de 30 US-IEDD implementadas con este formato

**Límite honesto:** El formato fue diseñado para proyectos Python con arquitectura hexagonal.
Requiere adaptación para otros stacks o arquitecturas.

---

### 3. Flujo agentic de implementación: Claude Dev Kit

**Qué es:** Un framework instalable (v1.3.0) que automatiza el ciclo completo de
implementación de una historia de usuario en 10 fases estructuradas, con tracking de
tiempo y quality gates integrados.

**Por qué está incluido:** Es la respuesta concreta al requerimiento de "enfoques agentic
y flujos autónomos". No es teoría: es un framework en producción con 107 tests, 99% de
cobertura y 5 perfiles de stack documentados (PyQt, FastAPI, Flask REST, Flask WebApp,
Python genérico).

**Evidencia de soporte:**
- `github.com/vvalotto/claude-dev-kit` — v1.3.0, MIT
- 5 proyectos de ejemplo con métricas reales
- AtaraxiaDive: overhead del flujo convergió a ~18 min por US (medido desde SP1 a SP2).
  Proyecto con propósito de producto real: atributos de calidad no funcionales acotados,
  arquitectura formal, quality gates en cada incremento.

**Límite honesto:** Solo soporta proyectos Python. Node.js/TypeScript está en roadmap
pero no disponible. Requiere un agente de codificación compatible (Claude Code o Codex);
el framework es agnóstico al modelo subyacente.

---

### 4. Quality gates automatizados: Software Limpio

**Qué es:** Framework de control de calidad en tres niveles: CodeGuard (pre-commit,
advierte), DesignReviewer (PR review, bloquea si CRITICAL), ArchitectAnalyst (fin de
sprint, informa tendencias).

**Por qué está incluido:** Es la respuesta al requerimiento de "ciclo de vida integral"
con quality gates verificables. Cubre métricas de diseño (12 analyzers AST), métricas
arquitectónicas (métricas de Martin, ciclos de Tarjan) e integración con CI/CD.

**Evidencia de soporte:**
- `github.com/vvalotto/software_limpio` — v0.3.0, MIT
- AtaraxiaDive: DesignReviewer ejecutado en cada PR desde SP1; ArchitectAnalyst en cada
  cierre de baseline; 0 CRITICAL sostenido desde SP2

**Límite honesto:** Solo analiza código Python. La configuración de umbrales requiere
calibración por equipo y tipo de arquitectura.

---

### 5. Human-in-the-loop como componente estructural

**Qué es:** La hipótesis central del experimento: la IA no reemplaza al ingeniero, sino
que desplaza su trabajo hacia las capas de mayor valor. El rol humano es irreductible en
especificación, evaluación de trade-offs, gobierno del proceso y capitalización del
aprendizaje.

**Por qué está incluido:** Responde directamente a la preocupación implícita en la sección
E sobre "control del proceso". Es el argumento que da sentido a todos los demás módulos.

**Evidencia de soporte:**
- `docs/iedd/04-Hipotesis_Ensayo_IA_Ingenieria_Human_In_The_Loop.md`
- HITOs SP1→SP3: calibración humana necesaria en múltiples puntos del experimento

**Límite honesto:** La hipótesis tiene validación parcial en un proyecto diseñado con
rigor de producto real (atributos de calidad no funcionales acotados, arquitectura
hexagonal, quality gates formales), conducido por un desarrollador experto. No está
validada en equipos ni en contextos de menor expertise previo.

---

## Fuera del alcance

| Tema | Razón de exclusión |
|------|-------------------|
| Sistemas multi-agente (LangGraph, AutoGen, CrewAI) | Sin evidencia empírica propia. Se puede combinar con módulos de la propuesta original. |
| Construcción de productos de IA (RAG, fine-tuning, modelo propio) | Fuera del foco: el problema es ingeniería de software con IA, no construir IA. |
| Stacks no-Python (Node.js, Java, .NET, Go) | Las herramientas (Dev Kit + Software Limpio) solo cubren Python hoy. |
| Plataformas no-code / low-code | No hay evidencia ni posición metodológica sobre ellas. |
| Modelos generativos de imagen, audio y video | Cubierto en módulos 4–6 de la propuesta original si se requiere. |
| Validación en equipos grandes o entornos enterprise | La evidencia proviene de un proyecto unipersonal de complejidad media. |
| Garantías de reducción de costo total o calidad superior medida | La hipótesis está abierta. No se puede afirmar como resultado probado. |

---

## Lo que diferencia esta propuesta

La mayoría de las capacitaciones de IA para desarrollo de software enseñan herramientas.
Esta propuesta enseña un **marco con fundamento teórico, herramientas que lo implementan,
y evidencia real de hasta dónde funciona y dónde todavía está en evaluación**.

Esa honestidad es parte de la diferenciación, no un debilitamiento.

---

## Audiencia objetivo de la extensión

Equipos de desarrollo (5–15 personas), tech leads y arquitectos que ya usan IA de forma
ad-hoc y quieren sistematizarlo. Requieren experiencia en desarrollo de software; no
requieren conocimiento previo de IA.

No es adecuada para audiencias no técnicas o equipos sin práctica de desarrollo activa.

---

*Versión 0.1 — Abril 2026*
*Base: docs/iedd/, github.com/vvalotto/claude-dev-kit, github.com/vvalotto/software_limpio, AtaraxiaDive SP1→SP3*
