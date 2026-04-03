# HITO-17 — Los datos reales actúan como oráculo empírico del dominio

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-17 — Hallazgo metodológico entre SP3 y SP4 |
| **Fecha** | 2026-04-03 |
| **Sprint** | Post-SP3 — preparación UAT / cierre BL-003 |
| **Relacionado** | `data/datasets/buenos_aires_2025/` · `.work/analisis-discrepancias-dataset-reales.md` |

---

## Contexto

Al preparar el UAT de SP3, surgió la pregunta: ¿podemos usar datos de una competencia
real como datos de prueba? El dataset disponible corresponde a "Apnea Indoor Buenos Aires
2025" —30 atletas, 5 disciplinas, 145 entries— extraído de los PDFs oficiales de la
federación. El desarrollador del proyecto compitió en ese torneo.

La pregunta era logística. Lo que produjo fue metodológico.

---

## El hallazgo

Lo que pasó no fue simplemente "encontramos bugs". Fue algo cualitativamente distinto.

Tenemos un proyecto donde el desarrollador es también un atleta del dominio. Está en el
dataset. Compitió en Buenos Aires 2025 en DBF, DNF y STA. Si hay alguien en el mundo que
debería conocer las reglas de ordenamiento de una grilla STA, es él.

Y sin embargo, la grilla STA estaba modelada al revés.

Eso no es un descuido. Es una señal sobre los **límites del conocimiento declarativo
del dominio**. Cuando un experto especifica reglas, lo hace desde su memoria semántica
—"en STA los mejores atletas van primero porque tienen más tiempo"— sin necesidad de
verificar contra datos reales. El Event Storming de este proyecto fue riguroso. Las
US-IEDD tienen precondiciones e invariantes formales. Y aun así, una regla de ordenamiento
básica quedó invertida porque nadie la contrastó contra una competencia real.

Lo que el dataset hizo fue actuar como un **oráculo empírico del dominio**: no interpretó,
no razonó, solo mostró cómo fue la grilla real de un torneo argentino con 30 atletas.
Esa evidencia fría expuso discrepancias que ninguna especificación, ningún Event Storming,
ningún test pudo haber encontrado —porque todos esos artefactos fueron construidos sobre
el mismo conocimiento declarativo que contenía el error.

El otro hallazgo notable es el del ranking. DISC-01 no es solo una feature faltante.
Es una **incomprensión estructural del modelo**. BC Resultados produce un ranking que
nunca existió en ningún torneo de apnea real: uno que mezcla a una atleta JUNIOR con
un atleta MASTER en la misma tabla ordenada. Eso no es un ranking de apnea —es una lista.
El modelo capturó el mecanismo de ordenamiento pero perdió la semántica de para qué
sirve ese ordenamiento en el dominio.

Lo que conecta DISC-01, DISC-02, DISC-03, DISC-04 y DISC-07 es un patrón común:
**todos son errores de lenguaje ubicuo que sobrevivieron al proceso IEDD porque el
proceso no tuvo contacto con datos reales**. Los acrónimos (`DBF`, `SPE`, `JUNIOR`)
son errores de lenguaje. El ordenamiento STA es un error de semántica. El ranking flat
es un error de modelo conceptual. Ninguno genera una excepción en runtime. Ninguno falla
un test. Todos son invisibles hasta que alguien pone una planilla real de la federación
en la mesa.

---

## El aprendizaje central

> Los datos reales de una competencia anterior son una forma de validación del dominio
> cualitativamente distinta a la especificación, el Event Storming y los tests.
> No son redundantes con esas capas —las complementan. Detectan la categoría de error
> que emerge cuando el conocimiento del experto de dominio tiene huecos o sutilezas
> que no afloran en el razonamiento abstracto, pero sí cuando el modelo tiene que
> "procesar" lo que realmente ocurrió.

Más precisamente: la especificación, el Event Storming y los tests validan el modelo
contra el **conocimiento declarado** del dominio. Los datos reales validan el modelo
contra el **comportamiento observado** del dominio. Son fuentes distintas de verdad,
y sus intersecciones no están garantizadas.

---

## Discrepancias encontradas

El análisis completo está en `.work/analisis-discrepancias-dataset-reales.md`.
A continuación el resumen con clasificación:

### CRÍTICOS — funcionalidad incorrecta

| ID | Descripción | BC afectado |
|----|-------------|-------------|
| **DISC-01** | Ranking flat vs. ranking por (disciplina, categoría, sexo). BC Resultados produce rankings que no existen en ningún torneo real. | Resultados |
| **DISC-02** | `DYNB` ≠ `DBF`. El acrónimo estándar AIDA es `DBF`. La app usa un nombre incorrecto para Dynamic Bi-Fins. | Shared / Torneo / Competencia |
| **DISC-03** | `SPE2X50` ≠ `SPE`. El nombre real usado en competencias argentinas es `SPE`. | Shared / Torneo / Competencia |
| **DISC-04** | Orden de grilla STA invertido. La app genera descendente (mayor AP primero). La realidad es ascendente en **todas** las disciplinas, incluyendo STA (30s → 330s en el dataset real). | Competencia (DisciplinaDescriptor) |

### MEDIOS — datos faltantes en el modelo

| ID | Descripción | BC afectado |
|----|-------------|-------------|
| **DISC-05** | `Atleta` no tiene campo `club`. Todos los documentos oficiales del torneo requieren el club como dato de identidad del atleta. | Registro |
| **DISC-06** | APs de STA y SPE se expresan en formato `MM:SS` en los documentos de la federación. La app espera un `Decimal` en segundos. No hay conversión en el dominio. | Competencia |
| **DISC-07** | `JUVENIL` ≠ `JUNIOR`. El estándar AIDA usa `JUNIOR`. La app usa `JUVENIL`, generando fricción con cualquier dato real. | Registro |

### BAJOS — observaciones del dominio

| ID | Descripción |
|----|-------------|
| **DISC-08** | `RP > AP` es la norma en distancia (100% de los atletas con tarjeta blanca en el dataset). La app ya lo permite correctamente, pero no está documentado como invariante explícito. |
| **DISC-09** | Los PDFs de la federación usan coma decimal (`104,27`). Cualquier script de ingesta debe normalizar. |
| **DISC-10** | Intervalo OT real: DBF=7min, STA=8min. Difiere de los 9min usados en los tests de SP2. No es un bug —es configurable— pero los tests deberían usar valores del dominio real. |

---

## Implicancia para IEDD como metodología

Este hallazgo revela un **gap en la cadena de 5 capas de IEDD**. La cadena actual es:

```
Capa 1 — Dominio (conocimiento declarado del experto)
    ↓
Capa 2 — Modelo DDD (Event Storming sobre el conocimiento declarado)
    ↓
Capa 3 — Especificación US-IEDD
    ↓
Capa 4 — Arquitectura
    ↓
Capa 5 — Implementación
```

Lo que falta es un paso entre Capa 1 y Capa 2:

```
Capa 1 — Dominio
    ↓
[ Validación empírica: contrastar el modelo emergente contra datasets reales ]
    ↓
Capa 2 — Modelo DDD
```

Sin ese paso, el Event Storming trabaja sobre el conocimiento declarado del experto,
que puede tener huecos silenciosos. Con ese paso, el modelo se confronta contra el
comportamiento observado antes de formalizarse en especificaciones.

En AtaraxiaDive, este paso ocurrió tarde —entre SP3 y SP4, casi por casualidad—.
La pregunta "¿podemos usar datos reales como datos de prueba?" generó más valor
metodológico que cualquier revisión de diseño formal previa.

---

## Regla práctica identificada

> Si el dominio tiene competencias o eventos pasados documentados en datos estructurados
> (PDFs, planillas, bases de datos de la federación), esos datos deben usarse como
> validación del modelo DDD antes de escribir la primera US-IEDD.
>
> El test mínimo: ¿puede el modelo procesar un evento real de principio a fin
> y producir los mismos resultados que la documentación oficial?

---

## Acción pendiente

- [x] Incorporar DISC-01 a DISC-07 como issues formales del backlog (`SP-ADJ-04`)
- [ ] Priorizar DISC-04 (orden STA) y DISC-01 (ranking por categoría) como bloqueantes
      de cualquier UAT con datos reales
- [ ] Evaluar si la plantilla IEDD debería incluir un paso formal de "validación empírica"
      entre Capa 1 y Capa 2, con criterio de aceptación: el modelo procesa datos reales
      y produce output verificable contra documentación oficial

---

*Registrado durante la preparación del UAT de SP3 — la pregunta logística que se volvió hallazgo metodológico*
