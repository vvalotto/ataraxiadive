# Brechas entre el Reglamento CMAS/FAAS y la aplicación actual

> **Fuente:** Reglamento CMAS Apnea Indoor v2022/01 — Traducción FAAS (versión en uso 2025)
> **Fecha de análisis:** 2026-04-05
> **Propósito:** Registro de funcionalidad definida en el reglamento oficial que no está
> contemplada actualmente en AtaraxiaDive. Cada brecha incluye la descripción de la regla
> y la diferencia funcional respecto al estado actual. No implica decisión de implementar.

---

## Cómo leer este documento

Cada brecha describe:
- **Qué dice el reglamento** — la regla oficial con referencia al artículo
- **Qué hace la aplicación hoy** — el comportamiento actual
- **La diferencia** — qué funcionalidad faltaría para cumplir el reglamento

Las brechas están agrupadas por tema y ordenadas por impacto funcional.

---

## 1. Motivo de la tarjeta roja — CRUD de causas (§1.2.2, §1.1.10, §1.1.14)

### Qué dice el reglamento

Una tarjeta roja puede emitirse por múltiples causas distintas: Black-out, no seguir el
protocolo de superficie (signo OK, mantener cabeza fuera del agua, no apoyarse en el
carril), o infracciones técnicas que implican descalificación directa. El reglamento
trata cada causa como un evento diferente con sus propias consecuencias (por ejemplo,
el BKO tiene implicancias para los días siguientes del torneo; el fallo de protocolo de
superficie no).

### Qué hace la aplicación hoy

Cuando el juez asigna tarjeta roja, la aplicación solo registra el resultado final
(tarjeta roja) sin capturar el motivo. La excepción es el BKO, que tiene su propia
pantalla dedicada. Las demás causas de descalificación no se distinguen entre sí.

### La diferencia — decisión de diseño

El flujo del juez **no cambia**: se registra la performance, se asigna la tarjeta.
Lo que se agrega es que al seleccionar tarjeta roja se abre una selección de motivo
obligatoria con las causas posibles. Las causas son configurables (CRUD) dado que
el reglamento puede evolucionar o variar según la federación. Causas iniciales:

- Black-out (BKO) — ya existe como flujo separado, se integra aquí
- No siguió protocolo de superficie
- Penalización / infracción técnica

Esto convierte el BKO en un motivo de tarjeta roja dentro de un mecanismo unificado,
en lugar de un flujo paralelo. El registro queda más completo y permite estadísticas
por causa de descalificación.

---

## 2. Dos tipos de Black-out con consecuencias distintas (§1.1.10)

> **Decisión:** esta brecha queda resuelta por la brecha #1. Los dos tipos de BKO
> (superficie y bajo el agua) son motivos de tarjeta roja dentro del CRUD de causas.
> BKO superficie y BKO subacuático son entradas distintas en esa lista, con sus
> respectivas descripciones de consecuencias para el organizador.
> No requiere tratamiento separado.

---

## 3. Penalizaciones técnicas — concepto de "Tarjeta Blanca con penalizaciones" (§1.1.13)

### Qué dice el reglamento

Una "penalización general" se aplica cuando el atleta comete una infracción técnica
durante la performance que no invalida el intento pero sí reduce el resultado. Para
disciplinas dinámicas: −3 metros por infracción. Las penalizaciones se acumulan
(dos infracciones = −6 metros). Las situaciones que las generan:

- Sin contacto con la pared al iniciar (§2.2.1.4)
- Cuerpo completo fuera del carril (§2.2.2.2)
- Asistente no retira de la zona a 3 min del OT (§2.1.6.2)
- Patada de delfín en evento de bialetas — por cada ciclo (§1.1.3.3)

### Qué hace la aplicación hoy

El modelo actual tiene tres resultados posibles: Blanca, Amarilla (en revisión) y Roja.
La penalización de −3m existe solo como parte de la resolución de una tarjeta amarilla.
No existe el concepto de una performance válida con penalizaciones aplicadas
directamente por el juez, sin pasar por el proceso de deliberación de la amarilla.

### La diferencia — decisión de diseño

Se necesita un nuevo resultado: **Tarjeta Blanca con penalizaciones**. Su lógica:

- La performance es válida (el atleta completó el intento y el protocolo de superficie).
- El juez registra una o más infracciones técnicas al momento de asignar la tarjeta.
- Cada infracción aplica −3m (dinámica) o el equivalente según la disciplina.
- El RP final para el ranking = distancia medida − suma de penalizaciones.
- La tarjeta mostrada al atleta es **Blanca**, pero el registro interno incluye
  las infracciones y el RP penalizado.

Esto es distinto de la tarjeta amarilla: no hay deliberación, no hay resolución
posterior. El juez constata la infracción en el momento y la aplica directamente.
La tarjeta amarilla queda reservada para los casos donde hay duda sobre si el
resultado es válido o no (requiere revisión por los jueces antes de decidir).

---

## 4. Categorías de competencia — sistema completo con Masters (§1.1.7)

> **Decisión:** fuera de alcance. No se distinguirán subcategorías Masters por ahora.
> La aplicación manejará Junior, Senior y Masters como categoría única sin subdivisión
> etaria. Si en el futuro se necesita, se incorpora como extensión del BC Registro.

---

## 5. Subdisciplinas de velocidad-resistencia — SPE no es una sola disciplina (§1.1.8.7)

### Qué dice el reglamento

Las disciplinas de velocidad-resistencia no son una sola prueba sino cuatro variantes
definidas por la distancia total:

| Nombre | Largos | Distancia total | Tipo |
|--------|--------|-----------------|------|
| SPE 2×50m | 2 | 100 m | Velocidad |
| SPE 4×50m | 4 | 200 m | Velocidad |
| SPE 8×50m | 8 | 400 m | Resistencia |
| SPE 16×50m | 16 | 800 m | Resistencia |

En todas el atleta alterna apnea activa con recuperación pasiva en cada extremo.
El resultado es un tiempo (menor es mejor). Los récords se homologan por variante.

### Qué hace la aplicación hoy

La disciplina `SPE` está definida como una sola disciplina sin distinción de variante.
Un torneo solo puede tener una instancia de SPE, sin especificar cuántos largos son.

### La diferencia — decisión de incorporar

Se incorporan las cuatro variantes como subdisciplinas de SPE. Cada variante es un
evento independiente dentro del torneo: tiene su propia grilla de salida, su propio
ranking y su propio conjunto de performances. Un torneo puede incluir `SPE 2×50m` y
`SPE 8×50m` simultáneamente como dos eventos distintos.

El modelo de disciplina pasa de `tipo = SPE` a `tipo = SPE, variante = 2x50 | 4x50 | 8x50 | 16x50`.
El resultado de SPE siempre es un tiempo, no una distancia.

---

## 6. Orden de la grilla de salida — regla invertida para velocidad-resistencia (§1.2.4.3)

### Qué dice el reglamento

El orden de salida en competencias de apnea sigue esta regla:

- **DNF, DYN, DBF, STA:** los atletas con menor performance declarada (AP/PB)
  compiten primero, los de mayor performance al final. Esto es para que los atletas
  más fuertes compitan al final, cuando el ambiente es más cargado de expectativa.
- **SPE (velocidad-resistencia):** el orden es **inverso**: primero los de mayor tiempo
  declarado (más lentos), al final los más rápidos.

La razón de la inversión para SPE es que en esta disciplina el resultado es un tiempo
(menor es mejor), por lo que la lógica se aplica al revés.

### Qué hace la aplicación hoy

La grilla de salida se genera y puede ordenarse, pero no implementa la regla de
ordenamiento automático basada en el tipo de disciplina y el AP declarado.

### La diferencia — decisión de incorporar

La generación de la grilla debe aplicar el orden reglamentario como punto de partida:

- **DNF, DYN, DBF, STA:** orden ascendente por AP — menor performance declarada
  primero, mayor al final.
- **SPE (todas las variantes):** orden descendente por AP — mayor tiempo declarado
  primero (los más lentos), menor tiempo al final (los más rápidos).

El organizador puede ajustar el orden manualmente después de la generación, pero
el orden inicial que produce el sistema debe cumplir el reglamento.

---

## 7. Protocolo del juez durante la apnea estática — señales táctiles (§3.2.1)

> **Decisión:** fuera de alcance. Las señales táctiles son responsabilidad operativa
> del juez y no se registran en la aplicación.

---

## 8. Inicio del cronómetro en apnea estática — momento diferente (§3.1.3.1)

### Qué dice el reglamento

En la disciplina estática (STA), el cronómetro **no arranca en el Tiempo Oficial**.
Arranca en el momento exacto en que el atleta **sumerge sus vías respiratorias** por
debajo de la superficie del agua, lo que puede ocurrir en cualquier momento dentro
de la ventana OT hasta OT+30s.

El resultado (tiempo realizado, RT) es el tiempo efectivo de apnea desde la inmersión
de vías respiratorias hasta la emersión.

### Qué hace la aplicación hoy

El flujo del juez activa el cronómetro cuando el juez presiona el botón "ATLETA INICIA"
en el Paso 3, lo que conceptualmente ocurre cuando el atleta se sumerge. Para las
disciplinas dinámicas esto es equivalente. Para STA, sin embargo, el cronómetro que
mide el resultado es el de la inmersión de vías respiratorias, no el inicio del movimiento.

### La diferencia — decisión de incorporar

El flujo del Paso 3 en STA debe diferenciarse del flujo dinámico. En dinámica,
"ATLETA INICIA" marca el momento en que el atleta se desplaza. En STA, el botón
equivalente debe llamarse **"VÍAS RESPIRATORIAS EN AGUA"** y el cronómetro
que arranca en ese momento es el que determina el RT oficial.

El Paso 3 detecta la disciplina y muestra la etiqueta correcta. El resultado registrado
es el tiempo entre ese toque y el momento en que el juez presiona "FINALIZAR"
(cuando las vías respiratorias emergen). La ventana OT+30s aplica igual que en
dinámica para determinar si el inicio es válido.

---

## 9. "Salida en falso" en velocidad-resistencia — nombre y tratamiento específico (§4.2.1.3)

### Qué dice el reglamento

En las disciplinas de velocidad-resistencia (SPE), si un atleta comienza a nadar antes
de su Tiempo Oficial, el evento se denomina específicamente **"Salida en falso"**
(False Start). El atleta es descalificado del intento.

En las disciplinas dinámicas, la misma situación se llama simplemente DQ por inicio
anticipado (§1.2.1.9), sin nombre específico.

### Qué hace la aplicación hoy

La aplicación registra DQ para el caso en que el atleta no inicia dentro de la ventana
OT+30s. No hay un tipo específico de DQ para el inicio anticipado, ni una etiqueta
diferenciada para SPE.

### La diferencia — decisión de incorporar

"Salida en falso" es un motivo de tarjeta roja dentro del CRUD de causas definido
en la brecha #1. Se incorpora como motivo específico de descalificación, disponible
para todas las disciplinas (aunque en SPE tiene nombre propio reglamentario).
Junto con "No inició en ventana OT+30s", cubren los dos tipos de DQ por problema
en el inicio.

---

## 10. Conducta antideportiva — sanciones que trascienden el evento (Anexo FAAS)

> **Decisión:** fuera de alcance por ahora. Es gestión de federación, no de torneo.

---

## Tabla resumen

| # | Brecha | Artículo | Prioridad funcional |
|---|--------|----------|-------------------|
| 1 | Motivo de tarjeta roja — CRUD de causas (BKO, protocolo, infracción) | §1.2.2, §1.1.10 | Alta |
| 2 | Dos tipos de BKO — resuelto por brecha #1 (motivos de tarjeta roja) | §1.1.10 | — |
| 3 | Tarjeta Blanca con penalizaciones — nuevo resultado con RP reducido | §1.1.13, §2.2.1.4, §2.2.2.2 | Alta |
| 4 | Categorías Masters — fuera de alcance por ahora | §1.1.7 | — |
| 5 | Subdisciplinas SPE — 4 variantes (2×50, 4×50, 8×50, 16×50) — incorporar | §1.1.8.7 | Media |
| 6 | Orden de grilla reglamentario por tipo de disciplina — incorporar | §1.2.4.3 | Media |
| 7 | Señales táctiles STA — fuera de alcance | §3.2.1.4 | — |
| 8 | Inicio cronómetro STA — botón "Vías respiratorias en agua" — incorporar | §3.1.3.1 | Baja |
| 9 | Salida en falso — motivo de tarjeta roja, resuelto por brecha #1 | §4.2.1.3 | — |
| 10 | Conducta antideportiva — fuera de alcance | Anexo FAAS | — |

---

*Análisis realizado sobre: Reglamento CMAS Apnea Indoor Versión 2022/01 — Traducción FAAS*
*Archivo fuente: `data/datos_prueba/REGLAS INTERNACIONALES APNEA INDOOR FAAS-CMAS Versión 2025.pdf`*
