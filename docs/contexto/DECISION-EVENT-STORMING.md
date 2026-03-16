# Decisión: Incorporación de Event Storming al Proceso IEDD

| Campo | Valor |
|-------|-------|
| **Documento** | DECISION-EVENT-STORMING.md |
| **Categoría** | Decisión metodológica del experimento |
| **Fecha** | 2026-03-16 |
| **Autor** | Victor Valotto + Claude Cowork |
| **Estado** | Aceptada |

---

## 1. Contexto: el problema que motivó la decisión

El marco IEDD define una cadena de 5 capas donde Capa 1 (Dominio) alimenta
Capa 2 (Modelo DDD). Sin embargo, el proceso concreto de transición entre
ambas capas no estaba especificado: ¿cómo se pasa de documentos de dominio
en lenguaje natural a un modelo formal de aggregates, BCs e invariantes?

La respuesta implícita hasta ahora era "análisis directo de los RFs". Eso
tiene un problema conocido: el analista extrae lo que puede ver, pero las
reglas de negocio más importantes suelen ser las implícitas — las que los
expertos del dominio dan por sentadas y no mencionan espontáneamente.

Event Storming fue propuesto como técnica candidata para cubrir esa brecha.

---

## 2. Por qué Event Storming encaja en este proyecto

AtaraxiaDive tiene dos características que hacen a ES especialmente valioso:

**El dominio es rico en comportamiento temporal.** Un torneo de apnea no es
un sistema CRUD — es una secuencia de eventos con causas, efectos, reglas
automáticas y puntos de fallo. La narrativa temporal es exactamente lo que
ES modela con su línea de eventos de izquierda a derecha.

**El contexto Competencia usa Event Sourcing.** No es coincidencia: Event
Sourcing persiste eventos de dominio, y Event Storming los identifica. Los
domain events que emergen de la sesión de ES son literalmente los mismos
que el Event Store va a persistir. La sinergia es directa y reduce el riesgo
de que el modelo técnico diverja del modelo conceptual.

**La técnica produce lo que IEDD necesita en Capa 2.** Los outputs del ES
(domain events, comandos, actores, políticas, hot spots, candidatos a
aggregates) son exactamente los insumos que `context-map.md` y
`domain-model.md` necesitan para ser escritos con evidencia empírica en
lugar de intuición.

---

## 3. Beneficios esperados

**Invariantes más completos.** Las políticas (rosa) que emergen en ES son
reglas de negocio automáticas: "Cuando X entonces Y". Muchas de estas no
aparecen en los cuestionarios de RFs porque los expertos las consideran
obvias. En IEDD, esas políticas se convierten directamente en invariantes
de los aggregates en las US-IEDD.

**Hot spots explícitos.** Los puntos rojos documentan incertidumbres,
conflictos y ambigüedades antes de que lleguen al código. En el contexto
del experimento, un hot spot en el ES que luego genera un RFC de cambio es
evidencia directa del valor de la técnica.

**Boundaries naturales de BCs.** En ES, un BC emerge cuando el lenguaje
cambia en la línea de eventos — cuando los mismos participantes usan
palabras distintas para referirse a la misma cosa. Esas fronteras lingüísticas
son más confiables que las fronteras trazadas desde el análisis funcional.

**Candidatos a US-IEDD listos para especificar.** Cada par Comando → Evento
en el ES es un candidato natural a historia de usuario. La precondición de
la US es el estado del sistema antes del comando; la postcondición es el
estado después del evento. El mapeo es casi mecánico.

**Dato experimental valioso.** Esta sesión de ES es solo-asincrónica (un
experto del dominio, sin equipo, asistido por IA). Documentar qué se gana
y qué se pierde respecto a un ES colaborativo presencial es una contribución
original al conocimiento sobre ES mediado por IA — directamente útil para
el libro DDD y el paper IEDD.

---

## 4. Limitación identificada y cómo se resuelve

**Limitación principal:** Event Storming nació como técnica colaborativa.
Su "magia" es la emergencia de conocimiento distribuido entre múltiples
participantes. En un contexto solo-desarrollador esa dinámica no existe.

**Cómo se compensa:** La profundidad del dominio ya documentado en
`docs/dominio/` (5 archivos, cuestionario detallado con respuestas) actúa
como sustituto parcial de la sala llena de expertos. No es equivalente, pero
es significativamente mejor que nada. La hipótesis experimental es que un ES
bien preparado con documentación sólida produce resultados comparables a un
ES presencial de pocas horas con un equipo pequeño.

---

## 5. Decisión: la estrategia final de ES en AtaraxiaDive

Tras analizar la secuencia metodológica correcta, se identificó un error de
orden en la propuesta inicial: hacer ES sobre el BC Competencia *antes* de
tener un Context Map formalizado asumía que los límites del BC ya eran
conocidos, lo que invalidaba uno de los principales beneficios de la técnica.

La secuencia correcta, adoptada como decisión, es la siguiente:

```
Fase 0 — Diseño Estratégico

  vision.md
      ↓
  [ES Nivel 1 — Big Picture]
  event-storming-big-picture.md
  Alcance: dominio completo (todas las fases del torneo)
  Objetivo: descubrir candidatos a BC desde los eventos del dominio
  Produce: mapa de eventos, hot spots globales, candidatos a BCs
      ↓
  context-map.md
  (Los BCs emergen del ES, no se imponen desde análisis funcional)
      ↓
  [ES Nivel 2 — Process Modeling]
  event-storming-competencia.md
  Alcance: BC Competencia únicamente
  Objetivo: profundizar el Core Domain con comandos, políticas, agregados
  Produce: insumos directos para domain-model.md y US-IEDD de SP1
      ↓
  domain-model.md
      ↓
  architecture.md
```

**Justificación de la secuencia:** Las decisiones estratégicas (qué son los
BCs, dónde están sus fronteras) deben preceder al modelado táctico del
comportamiento dentro de un BC. El Big Picture ES opera sobre el dominio
completo y produce evidencia para las decisiones estratégicas. Solo después
de formalizar esas fronteras en el Context Map tiene sentido hacer un Process
Modeling ES enfocado en un BC específico.

---

## 6. Relación con el marco IEDD

Event Storming no es una capa nueva de IEDD. Opera como técnica de elicitación
y modelado entre Capa 1 (Dominio) y Capa 2 (Modelo DDD):

```
Capa 1 — DOMINIO
    ↓
    [ ES Big Picture → descubre BCs ]
    [ ES Process Modeling → profundiza Core Domain ]
    ↓
Capa 2 — MODELO (DDD)
```

La hipótesis central del experimento, en este punto, es:

> **Un ES bien preparado con documentación de dominio sólida produce un
> modelo DDD de mayor calidad (más invariantes, menos ambigüedad, BCs más
> coherentes) que el análisis directo de los requerimientos funcionales.**

Esta hipótesis se evalúa en la retrospectiva de BL-000.

---

## 7. Artefactos que produce esta decisión

| Artefacto | Tipo de ES | Ubicación | Estado |
|-----------|-----------|-----------|--------|
| `event-storming-big-picture.md` | Big Picture | `docs/design/` | ⏳ pendiente |
| `event-storming-competencia.md` | Process Modeling | `docs/design/` | ⏳ pendiente |

**Insumos para el Big Picture ES:**
- `docs/dominio/01-dominio_torneos_apnea.md`
- `docs/dominio/05-requerimientos_funcionales.md`
- `docs/requirements/vision.md` (debe existir antes)

**Insumos para el Process Modeling ES:**
- Todo lo anterior, más:
- `docs/design/context-map.md` (debe existir antes)

---

*Documento creado: 2026-03-16 — Semana 0*
*Mantenido por: Claude Cowork*
