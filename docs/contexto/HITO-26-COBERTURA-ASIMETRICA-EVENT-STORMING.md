# HITO-26 — Cobertura asimétrica del Event Storming y su impacto en la calidad de la especificación

| Campo | Valor |
|-------|-------|
| **Número** | HITO-26 |
| **Fecha** | 2026-04-22 |
| **Contexto** | Post-UAT INC-5.1 — Panel del Organizador (SP5) |
| **Artefactos relacionados** | `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` · `docs/design/event-storming-big-picture.md` · `docs/design/event-storming-competencia.md` · `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md` |

---

## Qué ocurrió

Al completar INC-5.1 (Panel del Organizador, SP5) y ejecutar la UAT funcional, se identificaron
cinco hallazgos de severidad Alta que impedían el flujo operativo real del torneo.
Todos afectaban la interfaz del organizador: política de tabs por fase, visibilidad de
disciplinas en "Ver competencias", precondición de grilla para asignar jueces, y acciones de
fase incorrectas en `AccionesPanel`.

Los hallazgos se resolvieron en INC-5.1-ADJ (US-5.1.7..5.1.10). Pero su aparición plantea
una pregunta metodológica relevante para el experimento: **¿por qué aparecieron? ¿Qué no
fue capturado en la especificación?**

---

## Análisis del origen — Capa de especificación

### Las specs especificaron componentes, no condiciones de activación

US-5.1.1..5.1.6 fueron escritas como historias del tipo "agregar este componente" o
"implementar esta acción". Cada US capturó correctamente sus comandos, queries y actores.
Lo que no se especificó fue la política cross-cutting: **cuándo cada componente está
habilitado en función del estado del torneo**.

La política de tabs (qué pestañas son accesibles en cada fase del torneo) era una restricción
que atravesaba todas las US de INC-5.1 sin pertenecer a ninguna en particular. Nadie era
dueño de ella, y por lo tanto nunca fue escrita.

Este patrón se manifiesta en dos tipos de hallazgos:

- **Tabs habilitadas en fase incorrecta** (UAT-5.1-03, 05): DetalleTorneoPage renderizaba
  todas las tabs sin una política de estado. Las specs describieron qué agregar, no cuándo
  mostrarlo.

- **Precondición de datos ausente** (UAT-5.1-02): US-5.1.5 especificó la precondición de
  estado (`torneo en Preparacion`) pero omitió la precondición de datos (`disciplina tiene
  grilla generada`). La regla operacional existía en el dominio pero no fue elicitada durante
  la especificación de la US.

### El ciclo de vida de dos BCs no estaba modelado en la UI

`TorneoCompetenciasPage` asumía que `competencia.db` y `torneo.db` estaban en sincronía.
No lo están: las disciplinas configuradas en `torneo.db` existen desde `INSCRIPCION_ABIERTA`;
las competencias materializadas en `competencia.db` solo existen a partir de que se genera la
grilla. La spec nunca hizo explícita esa brecha de ciclo de vida cruzada entre BCs (UAT-5.1-01).

Esto no fue una falla de elicitación del dominio en sí — la frontera entre BC Torneo y BC
Competencia estaba modelada correctamente. Fue una falla al no traducir esa frontera a un Read
Model explícito para el organizador.

---

## Análisis del origen — Capa de modelado

### La asimetría estructural del Event Storming

Al revisar los artefactos de Event Storming, la causa de fondo se vuelve visible:

| BC | Nivel 1 — Big Picture | Nivel 2 — Process Modeling |
|---|---|---|
| **Competencia** | ✅ | ✅ — aggregates, state machines, invariantes, Read Models por actor |
| **Torneo** | ✅ | ✗ — nunca se realizó |

Todos los hallazgos UAT de INC-5.1 son del territorio del BC Torneo y del flujo del organizador.
Donde se realizó Process Modeling (BC Competencia), la UAT no encontró ningún problema de
dominio. Donde solo hubo Big Picture (BC Torneo), encontró cinco.

### Lo que el Process Modeling hubiera preguntado

El ES de BC Competencia definió Read Models explícitos para el juez durante la ejecución:

- `PerformanceActual` → Juez
- `ProximosAtletas` → Juez
- `ProgresoCompetencia` → Juez

El equivalente para el organizador — **¿qué ve el organizador en cada estado del torneo?** —
nunca fue formulado. Sin esa pregunta, no se modelaron las condiciones de activación de la UI
por fase, ni el Read Model que cruza la frontera entre BC Torneo y BC Competencia.

### El caso más claro: `AsignarJuez` nunca pasó por ES

La acción `AsignarJuez` no aparece en ninguno de los dos niveles del Event Storming. Fue
agregada en SP3 como CRUD del BC Torneo sin pasar por ninguna sesión de modelado. Sin ese
proceso, nunca se preguntó: *"¿cuándo puede el organizador asignar un juez? ¿Qué tiene
que existir para que esa acción tenga sentido?"*

La precondición operacional `grilla confirmada → juez asignable` era una regla del dominio
que existía implícitamente en la práctica del torneo real, pero que nunca fue formalizada
porque no hubo una sesión que la buscara. El UAT la descubrió tarde.

### El estado terminal `CANCELADO` y los Read Models omitidos

El ES Big Picture modeló `TorneoCancelado` como evento (HS-23: "se puede cancelar en cualquier
fase, datos preservados"). Pero nunca se preguntó: *"¿qué ve el organizador después de
`TorneoCancelado`?"*. No hay Read Model para ese estado en ningún artefacto de diseño.

La ausencia de esa pregunta es estructural: el Big Picture modela *qué ocurre*, no *quién
necesita ver qué como consecuencia de lo ocurrido*. Esa segunda pregunta es la que responde
el Process Modeling.

---

## Diferencia entre los dos hallazgos UAT-5.1-04

El hallazgo UAT-5.1-04 (`AccionesPanel` mostrando `Iniciar Ejecución` en un torneo en
`EJECUCION`) tiene una naturaleza diferente a los anteriores. El Event Storming modeló
correctamente el estado `EJECUCION` y la transición hacia `PREMIACION`. El código también
tenía el mapa correcto. El bug era un mismatch de normalización del campo `estado` entre
backend y frontend — un problema de contrato de integración, no de modelado de dominio.

Es importante distinguirlo: **no todo hallazgo de UAT es una brecha de especificación o
de Event Storming**. Algunos son bugs de implementación que solo la validación integrada
puede detectar.

---

## Evidencia empírica para el experimento

Este hallazgo produce evidencia directa sobre la hipótesis del experimento AtaraxiaDive:

> **La cobertura del Event Storming no es uniforme — cubre bien los flujos del actor que
> fue el foco del Process Modeling, y deja en punto ciego los flujos de actores que no
> protagonizaron ningún nivel de Process Modeling.**

En este proyecto, el foco fue siempre el juez (Core Domain = BC Competencia, actor principal
del Process Modeling). El organizador aparece en el Big Picture como disparador de eventos,
pero su experiencia operativa —qué ve, qué puede hacer, en qué condiciones— nunca fue el
objeto de una sesión dedicada.

El resultado: las specs de INC-5.1 para el organizador eran individualmente correctas pero
colectivamente incompletas. Capturaban el "qué" (componentes, comandos) sin capturar el
"cuándo" (condiciones de activación por estado) ni el "cómo se compone la información
entre BCs" (Read Models cross-BC).

### Lo que valida respecto a IEDD

IEDD funcionó bien donde el modelado fue profundo (BC Competencia): las US-IEDD derivadas del
Process Modeling tenían precondiciones completas y no generaron hallazgos de dominio en UAT.

IEDD mostró su límite donde el modelado fue superficial (BC Torneo): las US-IEDD derivadas
solo del Big Picture tenían precondiciones de estado pero no de datos, y omitían las políticas
cross-cutting de navegación.

La conclusión operativa para IEDD: **la calidad de las precondiciones en una US-IEDD es
proporcional a la profundidad del modelado previo**. Una US derivada de un Process Modeling
completo (con Read Models y máquinas de estado explícitas) tiene precondiciones más completas
que una US derivada solo de un Big Picture.

---

## Qué implicaría corregirlo metodológicamente

Dos opciones con diferente costo:

**Opción 1 — Process Modeling para el flujo del organizador**
Antes de especificar un incremento que toque el BC Torneo desde la perspectiva del
organizador, realizar una sesión de Process Modeling equivalente a la de BC Competencia:
definir Read Models por actor, estado de activación de cada acción, y dependencias de datos
entre BCs. Costo alto, beneficio proporcional a la complejidad del flujo.

**Opción 2 — US de política de navegación**
Al inicio de un incremento con múltiples paneles, agregar una US explícita cuyo propósito es
definir la política cross-cutting: qué componentes están activos en cada estado del aggregate.
Es la US más aburrida de escribir pero previene la mayoría de estos hallazgos. Costo bajo,
cobertura parcial.

**Opción 3 — Ampliar las precondiciones de las US-IEDD de frontend**
Incluir explícitamente en las precondiciones no solo el estado del aggregate sino también el
estado de los BCs relacionados. En lugar de `"precondición: torneo en Preparacion"`, escribir
`"precondición: torneo en Preparacion Y disciplina tiene Competencia con GrillaGenerada"`.
Requiere que quien especifica conozca el ciclo de vida de los BCs relacionados.

Las opciones no son excluyentes. La combinación más pragmática para un proyecto con recursos
limitados es: Opción 2 por defecto + Opción 3 cuando haya dependencias cross-BC conocidas.

---

## Conexión con HITOs anteriores

- **HITO-20** (invariantes de dominio que no cubren todas las variantes del deporte): la
  misma raíz — invariantes omitidas porque el foco del modelado fue el juez, no todos los
  actores y variantes del dominio.
- **HITO-17** (dataset real como oráculo empírico del dominio): el UAT con datos reales es
  el mecanismo que hace visible lo que el modelado dejó en punto ciego.

---

*Creado: 2026-04-22 — análisis post-UAT INC-5.1 (SP5)*
*Autores: Victor Valotto + Claude Code*
