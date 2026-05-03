# Análisis: Ingeniería de Especificación Dirigida por el Dominio (IEDD)

> Estado documental: histórico
> Análisis metodológico de IEDD realizado en Fase 0.
> Conservado como evidencia del fundamento teórico del experimento.
> Fuente vigente relacionada: `docs/contexto/PLAN-EXPERIMENTO.md`, `docs/iedd/`

**Fecha:** Marzo 2026
**Documentos analizados:** 3 archivos — tesis central, marco de 5 capas, diagrama conceptual

---

## 1. ¿Qué propone IEDD?

La iniciativa parte de una observación simple pero de consecuencias enormes:

> *La mayor dificultad del software está en especificar y diseñar el comportamiento
> del sistema — no en escribir código. La IA hace visible esta realidad al automatizar
> parcialmente la implementación.*

IEDD propone reinterpretar la ingeniería de software como una **cadena de
transformación conceptual** en 5 capas:

```
┌─────────────────────────────────┐
│           DOMINIO               │  Realidad del problema
│  actores, procesos, reglas      │  (ninguna decisión tecnológica)
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│           MODELO                │  Domain-Driven Design
│  entidades, agregados, eventos  │  (representación conceptual)
│  contextos, lenguaje ubicuo     │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│        ESPECIFICACIÓN           │  Comportamiento formal
│  invariantes, pre/postcondiciones│  (QUÉ debe hacer, no CÓMO)
│  operaciones, estados           │
└──────────────┬──────────────────┘
               │
         ┌─────┴─────┐
         │    IA     │  Traductor conceptual
         └─────┬─────┘
               ↓
┌─────────────────────────────────┐
│        ARQUITECTURA             │  Organización del sistema
│  componentes, contextos,        │  (cómo implementar la especificación)
│  persistencia, eventos          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│       IMPLEMENTACIÓN            │  Tecnología concreta
│  código, APIs, bases de datos   │  (lenguajes = herramientas, no fin)
│  frameworks, infraestructura    │
└─────────────────────────────────┘
```

La tesis central: **la IA actúa como compilador conceptual entre Especificación
e Implementación**. La calidad del output depende de la claridad del modelo
y la precisión de la especificación — no de quién escribe el código.

---

## 2. La inversión pedagógica propuesta

| | Enfoque tradicional | Enfoque IEDD |
|---|---|---|
| Punto de partida | Lenguaje de programación | Dominio del problema |
| Eje central | Código | Especificación del comportamiento |
| Rol de la IA | Herramienta de código | Traductor de especificaciones |
| Formación centrada en | Sintaxis, frameworks | Modelado, especificación, ambigüedad |
| Implementación es | El trabajo principal | La parte derivable |

Esta inversión no es cosmética. Define un profesional diferente: alguien que
comprende dominios complejos, construye modelos conceptuales precisos y
especifica comportamientos sin ambigüedad — y usa la IA para derivar el código.

---

## 3. La coherencia con el ecosistema completo

IEDD no es un proyecto aislado. Es el **marco teórico que unifica todo lo demás**.
Al leerlo junto con los otros proyectos analizados, emerge una arquitectura
intelectual de gran coherencia:

```
        IEDD
(el proceso: cómo se transforma dominio en sistema)
        │
        ├──── La Trilogía Limpia / software_limpio
        │     (la calidad: cómo se mide en cada capa)
        │
        ├──── Claude Dev Kit
        │     (la automatización: cómo se implementa US a US)
        │
        └──── Entorno-ia-dev (CM)
              (la memoria: cómo se gestiona la evolución)
```

Las cuatro son vistas ortogonales del mismo fenómeno. Cada una responde
una pregunta diferente sobre cómo construir software con IA.

### La correspondencia directa entre capas IEDD y artefactos CM

| Capa IEDD | Artefacto en entorno-ia-dev |
|-----------|----------------------------|
| Dominio | `docs/requirements/vision.md` + conversaciones con Cowork |
| Modelo | `docs/design/domain-model.md` (DDD) |
| Especificación | `docs/requirements/user-stories.md` (con pre/post/invariantes) |
| Arquitectura | `docs/design/architecture.md` + ADRs |
| Implementación | `src/` construido por Claude Dev Kit |

El CM framework no es solo gestión de documentos — es la **memoria de la cadena
IEDD completa**.

### La US como especificación parcial

Hay un encaje muy fino entre IEDD y claude-dev-kitc que vale la pena nombrar:

- Una **User Story bien escrita** (con criterios de aceptación claros) es una
  especificación parcial en términos IEDD: describe comportamiento esperado sin
  tecnología específica.
- Los **escenarios BDD** (Gherkin, Fase 1 del kit) son la formalización de esa
  especificación en términos `Given-When-Then` — equivalentes a
  `precondición-operación-postcondición`.
- **Claude Code implementando la US** es la IA actuando como traductor conceptual
  — exactamente el rol que IEDD le asigna.

El flujo `US → BDD → código` que automatiza el kit **es** el flujo
`especificación → traducción IA → implementación` de IEDD.

### software_limpio como verificador de cada capa

| Capa IEDD | Agente verificador | Qué verifica |
|-----------|--------------------|--------------|
| Modelo | DesignReviewer | LCOM (cohesión), CBO (acoplamiento) — el modelo respeta los 6 principios del Diseño Limpio |
| Especificación | DesignReviewer | God Object, Feature Envy — señalan cuando la especificación asignó responsabilidades mal |
| Arquitectura | ArchitectAnalyst | Violaciones de capas, ciclos de dependencias — el código respeta la arquitectura definida |
| Implementación | CodeGuard | PEP8, complejidad, seguridad — el código implementado tiene calidad básica |

`software_limpio` no solo mide el código — mide **cuánto fidelidad tiene la
implementación respecto al modelo y la especificación original**.

---

## 4. Posibilidad de experimentar con el proyecto sandbox

La pregunta concreta: ¿puede el sandbox servir para probar IEDD junto con
todo el ecosistema?

**Sí, y de manera muy directa.** El sandbox es el laboratorio ideal porque:

1. Es un dominio simple controlado (no distrae con complejidad de negocio)
2. Permite recorrer las 5 capas IEDD de forma deliberada
3. Genera evidencia empírica de cuándo la cadena funciona y cuándo se rompe

### Experimento propuesto: el ciclo completo IEDD-sandbox

**Capa 1 — Dominio** (Cowork como facilitador):
```
Cowork: "Describí el dominio del sandbox en lenguaje natural.
         ¿Quiénes son los actores? ¿Qué procesos existen?
         ¿Cuáles son las reglas del negocio que no pueden violarse?"
→ Output: vision.md enriquecido con dominio explícito
```

**Capa 2 — Modelo** (Cowork construye el modelo DDD):
```
Cowork: construye domain-model.md con:
  - Entidades identificadas
  - Objetos de valor
  - Agregados y sus invariantes
  - Eventos de dominio
  - Bounded context (si aplica)
  - Lenguaje ubicuo (glosario)
→ Output: docs/design/domain-model.md (DDD completo)
```

**Capa 3 — Especificación** (US enriquecidas):
```
Cowork: toma cada US del backlog y la enriquece con:
  - Invariantes del agregado afectado
  - Precondición formal
  - Postcondición formal
  - Eventos que dispara
→ Output: user-stories.md con especificaciones formales
→ ADRs que documentan decisiones de comportamiento
```

**Traducción IA → implementación** (Claude Code + Dev Kit):
```
Code: /implement-us US-001
  → Fase 1: BDD generado desde la especificación formal
           (¿los escenarios Gherkin capturan las pre/post condiciones?)
  → Fase 2: Plan respeta el modelo DDD
  → Fase 3: Código implementa los invariantes
  → Fases 4-6: Tests verifican el comportamiento especificado
  → Fase 7: Quality gates (DesignReviewer verifica coherencia modelo-código)
```

**Verificación de la arquitectura** (software_limpio):
```
Code: architectanalyst src/ --sprint-id BL-001
  → ¿Se respetan las capas DDD definidas en el ADR de arquitectura?
  → ¿El acoplamiento entre módulos refleja el modelo de dominio?
  → ¿Hay ciclos que indican problemas en el modelo conceptual?
```

### Lo que este experimento podría demostrar

1. **¿Mejora la calidad del BDD generado** cuando la US tiene precondiciones y
   postcondiciones explícitas? (comparar US "tradicional" vs US-IEDD)

2. **¿Reduce el número de iteraciones de corrección** tener un modelo de dominio
   explícito antes de implementar? (medir varianza del tracking de tiempo)

3. **¿Los quality gates de DesignReviewer correlacionan** con violaciones al
   modelo conceptual? (¿un God Object es siempre una US mal especificada?)

4. **¿La cadena es sostenible** — es decir, mantener el modelo actualizado
   ante cambios tiene menor costo que el beneficio en claridad de la implementación?

---

## 5. Lo que falta para cerrar el marco

IEDD está conceptualmente maduro pero todavía no tiene:

**Un formato estándar de especificación** que sea:
- Suficientemente formal para que la IA lo interprete bien
- Suficientemente legible para que el humano lo valide
- Compatible con el template de US del claude-dev-kit

**Una propuesta concreta sería** extender el template de User Story del kit
con secciones IEDD:

```markdown
# US-NNN: [título]

## Descripción
Como [actor], quiero [acción] para [beneficio].

## Contexto del dominio
- Agregado afectado: [nombre]
- Invariante del agregado: [regla que nunca puede violarse]

## Especificación del comportamiento
- **Precondición:** [estado que debe existir antes de la operación]
- **Postcondición:** [estado garantizado al finalizar]
- **Eventos generados:** [eventos de dominio que se disparan]

## Criterios de aceptación (BDD)
- Scenario: [descripción]
  Given [precondición en lenguaje de negocio]
  When [acción del actor]
  Then [resultado esperado]
```

Este template es la bisagra entre las capas Modelo/Especificación de IEDD
y el input que consume `/implement-us` del kit.

---

## 6. Conexión con "La Trilogía Limpia"

IEDD y La Trilogía Limpia comparten la misma tesis filosófica central desde
ángulos distintos:

| | La Trilogía Limpia | IEDD |
|---|---|---|
| Pregunta central | ¿Cómo saber si el código es bueno? | ¿Cómo construir el sistema desde el problema? |
| Mecanismo | Métricas objetivas por nivel | Capas de transformación conceptual |
| El rol de la IA | Herramienta dirigida por el juicio profesional | Traductor entre especificación e implementación |
| El profesional | Director de calidad | Especificador y modelador |
| La implementación | Verificable con métricas | Derivable desde la especificación |

Son la misma filosofía expresada en dos registros: uno operacional
(cómo medir), uno metodológico (cómo construir).

---

## 7. Síntesis: el ecosistema unificado

Con IEDD, el ecosistema completo tiene una coherencia que ninguna pieza
tiene por sí sola:

```
"La Trilogía Limpia" (libro / marco filosófico)
    → fundamenta un nuevo rol profesional: director de calidad
    → operacionalizado por software_limpio (métricas por capa)

IEDD (marco metodológico)
    → propone el proceso: dominio → modelo → especificación → impl.
    → operacionalizado por:
        entorno-ia-dev: gestiona la memoria de cada capa (CM)
        claude-dev-kitc: automatiza la transición spec → impl (US a US)
        software_limpio: verifica que el código respeta el modelo
```

El sandbox no es solo un proyecto de prueba técnica.
Es la **demostración empírica de que este ecosistema funciona en conjunto**.
Si funciona, se convierte en el caso de estudio del libro, del curso y de
la propuesta académica de FIUNER simultáneamente.

---

## 8. Próximos pasos concretos

**Para el sandbox (laboratorio):**
1. Elegir un dominio simple con reglas de negocio reales (sugerencia: sistema
   de préstamos de biblioteca — tiene invariantes claros, estados, eventos)
2. Recorrer las 5 capas IEDD con Cowork como facilitador antes de escribir
   una sola línea de código
3. Enriquecer el template de US del kit con las secciones IEDD propuestas
4. Ejecutar `/implement-us` con una US-IEDD y comparar la calidad del BDD
   generado versus una US tradicional

**Para el marco conceptual:**
1. Formalizar el template de US-IEDD como artefacto del entorno-ia-dev
2. Actualizar el CLAUDE.md del entorno para incorporar las 5 capas IEDD
   como guía de qué documentos crear en cada etapa del proyecto
3. Vincular explícitamente las métricas de software_limpio con los principios
   del Diseño Limpio que verifican en cada capa IEDD

---

*Análisis generado con Claude Cowork — Marzo 2026*
