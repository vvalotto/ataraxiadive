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

## 1. Protocolo de Superficie — validación post-performance (§1.2.2)

### Qué dice el reglamento

Cuando el atleta termina su performance y sale a la superficie, no basta con que haya
completado la distancia o el tiempo. El resultado solo es válido si el atleta completa el
**Protocolo de Superficie** dentro de los 20 segundos posteriores a la emersión. Este
protocolo consiste en:

1. Mantener la cabeza fuera del agua (vías respiratorias y nivel de las orejas sobre la
   superficie, de forma continua).
2. Realizar el **signo OK** convencional de buceo (dos dedos formando un círculo) en
   dirección al Juez Principal, ubicado en el borde de la pileta.
3. No recibir ningún tipo de ayuda externa, no apoyarse en la línea del carril ni en ninguna
   parte del cuerpo de otra persona.

Si el atleta no puede completar este protocolo en 20 segundos, o necesita ayuda durante
ese período, es descalificado — incluso si la performance en sí fue perfecta. El juez
tiene hasta 3 minutos para deliberar y mostrar la tarjeta correspondiente.

### Qué hace la aplicación hoy

El flujo del juez va directamente de "Finalizar Performance" a "Registrar RP" y luego
a "Asignar Tarjeta". No existe ningún paso entre la finalización de la performance y la
asignación de la tarjeta que represente la observación y validación del protocolo de
superficie.

### La diferencia

Hoy el juez asigna la tarjeta basándose solo en lo que ocurrió bajo el agua. El
reglamento requiere que la tarjeta refleje también lo que ocurrió en superficie durante
los 20 segundos post-emersión. Una performance correcta bajo el agua puede resultar
en tarjeta roja si el protocolo de superficie falla. Esta brecha afecta directamente al
flujo principal del juez.

---

## 2. Dos tipos de Black-out con consecuencias distintas (§1.1.10)

### Qué dice el reglamento

El reglamento distingue explícitamente dos situaciones de pérdida de consciencia:

**Black-out en superficie (§1.1.10.2):** el atleta pierde la consciencia después de
emerger, durante o después del protocolo de superficie. Consecuencias:
- Descalificado del evento.
- Debe ser examinado por un médico.
- El médico **puede autorizar** que compita al día siguiente.

**Black-out bajo el agua (§1.1.10.3):** el atleta pierde la consciencia durante la
performance, antes de emerger. Consecuencias:
- Descalificado del evento.
- **No puede competir al día siguiente** bajo ninguna circunstancia.
- Solo puede volver a competir el día subsiguiente, y únicamente con aprobación médica.

### Qué hace la aplicación hoy

La aplicación modela un único evento de Black-out (BKO) que siempre resulta en
tarjeta roja automática. No distingue dónde ocurrió ni registra ningún tipo de
inhabilitación temporal del atleta para competir en días sucesivos.

### La diferencia

Hay dos diferencias funcionales. La primera es informativa: el registro del BKO debería
indicar si ocurrió en superficie o bajo el agua, ya que esto cambia la gravedad del
evento y tiene implicancias médicas. La segunda es operativa: el organizador necesita
saber si un atleta que sufrió un BKO puede o no inscribirse en las disciplinas del día
siguiente, lo que hoy no es posible determinar desde la aplicación.

---

## 3. Penalizaciones técnicas generales — más allá de la tarjeta amarilla (§1.1.13)

### Qué dice el reglamento

Una "penalización general" es una sanción que se aplica cuando el atleta comete una
infracción técnica específica durante la performance, pero que no invalida el intento
completo. Para las disciplinas dinámicas, la penalización general consiste en restar
3 metros a la distancia realizada.

Las situaciones que generan penalización general son:
- **Sin contacto con la pared al iniciar (§2.2.1.4):** el atleta inicia la fase de apnea
  sin estar tocando la pared de la piscina.
- **Cuerpo completo fuera del carril (§2.2.2.2):** si todo el cuerpo del atleta sale
  del carril de competencia (las desviaciones parciales están permitidas).
- **Asistente no retira a 3 minutos del OT (§2.1.6.2):** si el asistente personal del
  atleta permanece en la zona de competencia después de la llamada de 3 minutos.
- **Patada de delfín en evento de bialetas (§1.1.3.3):** en disciplinas con bialetas
  (DBF), se aplica una penalización general por cada ciclo de patada de delfín
  realizado fuera de las zonas permitidas (los 3 metros al inicio y en los giros).

Las penalizaciones generales pueden acumularse.

### Qué hace la aplicación hoy

La aplicación conoce la penalización de −3 metros únicamente en el contexto de la
tarjeta amarilla resuelta como blanca (donde la penalización puede aplicarse como
parte de la deliberación). No existe una forma de registrar una penalización técnica
separada de la asignación de tarjeta.

### La diferencia

Hoy la única forma de reflejar una penalización es a través de la tarjeta amarilla,
que requiere deliberación y puede resultar en blanca o roja. Pero las penalizaciones
técnicas del reglamento son independientes de la tarjeta: el atleta puede recibir
tarjeta blanca y aun así tener −3 metros en su distancia final por haber salido del
carril. Son dos mecanismos distintos que hoy la app trata como uno solo.

---

## 4. Categorías de competencia — sistema completo con Masters (§1.1.7)

### Qué dice el reglamento

Las competencias oficiales organizan a los atletas en categorías por edad y género.
El sistema de categorías es:

| Categoría | Rango de edad |
|-----------|--------------|
| Junior | 15–17 años |
| Senior | 18–49 años |
| Masters 50-54 | 50–54 años |
| Masters 55-59 | 55–59 años |
| Masters 60-64 | 60–64 años |
| Masters 65-70 | 65–70 años |
| Masters 70+ | 70 años o más |

Reglas adicionales:
- La edad se calcula como: `año de la temporada - año de nacimiento` (no la edad exacta
  al día de la competencia).
- Un atleta de categoría Masters puede optar por competir en la categoría Senior.
  Si en ese contexto bate un récord Masters, el récord se homologa igualmente.

### Qué hace la aplicación hoy

La aplicación registra el género del atleta, pero no implementa el sistema de
categorías. Los rankings actuales agrupan por disciplina y género, sin distinción de
categoría etaria.

### La diferencia

En un torneo oficial, los rankings y podios se determinan dentro de cada categoría
por separado. Un atleta Senior y un atleta Masters 50-54 pueden competir juntos en
la misma grilla de salida pero se clasifican en tablas distintas. La aplicación hoy
produce un único ranking por disciplina y género sin esta subdivisión. Tampoco
gestiona la opción de un atleta Masters de competir en la categoría Senior.

---

## 5. Subdisciplinas de velocidad-resistencia — SPE no es una sola disciplina (§1.1.8.7)

### Qué dice el reglamento

Las disciplinas de velocidad-resistencia no son una sola prueba sino cuatro variantes
definidas por la distancia total:

| Nombre | Distancia | Tipo |
|--------|-----------|------|
| Velocidad 2×50m | 100 m (2 largos de 50m) | Velocidad |
| Velocidad 4×50m | 200 m (4 largos de 50m) | Velocidad |
| Resistencia 8×50m | 400 m (8 largos de 50m) | Resistencia |
| Resistencia 16×50m | 800 m (16 largos de 50m) | Resistencia |

En todas ellas el atleta alterna apnea activa con recuperación pasiva en los extremos
de la pileta. Los récords se homologan por variante separadamente.

### Qué hace la aplicación hoy

La disciplina `SPE` (velocidad/resistencia) está definida como una sola disciplina,
sin distinción de variante ni distancia total.

### La diferencia

Un torneo puede incluir, por ejemplo, `2×50m` y `8×50m` como dos eventos distintos,
cada uno con su propia grilla de salida y su propio ranking. Hoy la aplicación no puede
representar esto: solo puede tener una instancia de SPE por torneo, y esa instancia no
especifica cuántos largos son.

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

La grilla de salida se genera y puede ordenarse, pero no implementa esta regla de
ordenamiento automático basado en el tipo de disciplina y el AP declarado.

### La diferencia

En un torneo oficial, la grilla de salida no es arbitraria: tiene un orden definido por
el reglamento. El organizador puede ajustar el orden, pero el punto de partida debe
ser el orden reglamentario. Hoy la aplicación no genera ese orden automáticamente.

---

## 7. Protocolo del juez durante la apnea estática — señales táctiles (§3.2.1)

### Qué dice el reglamento

Durante una performance de apnea estática (STA), el atleta permanece inmóvil bajo
el agua y no hay forma visual de saber si está bien. El reglamento establece un
protocolo de control de seguridad obligatorio: el juez de superficie debe comunicarse
con el atleta mediante **contacto táctil** a intervalos específicos calculados desde el
AP declarado:

- A `AP − 1 minuto`
- A `AP − 30 segundos`
- A `AP − 15 segundos`
- En el momento del `AP`
- A partir de ahí, cada **15 segundos** si el atleta continúa

El atleta y el juez acuerdan antes del intento la señal y la respuesta esperada. Si el
atleta no responde a la señal del juez, el juez repite el toque. Si persiste la no
respuesta, el juez interrumpe el intento y extrae al atleta (BKO).

### Qué hace la aplicación hoy

El flujo del juez para STA es el mismo que para las disciplinas dinámicas: cronómetro
activo, botón de finalizar, posibilidad de registrar BKO. No existe ninguna guía o
registro de las señales táctiles obligatorias.

### La diferencia

El protocolo de señales táctiles es una responsabilidad del juez con consecuencias
de seguridad. La aplicación podría asistir al juez mostrando los momentos en que debe
contactar al atleta, calculados automáticamente desde el AP declarado. Hoy esa
información no está disponible en la interfaz durante la performance.

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

### La diferencia

En la práctica el flujo puede ser el mismo si el juez presiona el botón en el momento
exacto de la inmersión de las vías respiratorias. Pero el reglamento es preciso: el
resultado de STA se mide desde las vías respiratorias, y el botón actual dice "ATLETA
INICIA" (que en dinámica significa el inicio del movimiento, no necesariamente de la
apnea). La distinción es sutil pero relevante para la exactitud del registro.

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

### La diferencia

Es principalmente una diferencia de nomenclatura y registro. El reglamento reconoce
la "Salida en falso" como un resultado específico de SPE. Para el audit log y para
estadísticas, sería importante distinguir entre "no inició en ventana" (llegó tarde) y
"inició antes del OT" (salida en falso), ya que son infracciones distintas con causas
distintas.

---

## 10. Conducta antideportiva — sanciones que trascienden el evento (Anexo FAAS)

### Qué dice el reglamento

El Anexo FAAS establece que la comisión de apnea tiene potestad para sancionar la
conducta antideportiva con medidas que van más allá de la descalificación del evento.
Las sanciones pueden incluir:

- Prohibición de competir en fechas futuras del mismo torneo.
- Prohibición de participar en competencias internacionales.

La sanción puede aplicarse al deportista, al entrenador, o a toda la escuela/club.
La conducta antideportiva no necesita estar explícitamente detallada en el reglamento
para ser sancionada.

### Qué hace la aplicación hoy

Las únicas consecuencias que la aplicación puede registrar son las que ocurren dentro
de una performance: tarjeta blanca, amarilla, roja, DNS, o DQ. No existe ningún
mecanismo para registrar sanciones que afecten la participación futura del atleta.

### La diferencia

Una sanción por conducta antideportiva afecta al atleta en múltiples torneos y en el
tiempo. Hoy no hay manera de que el organizador registre este tipo de sanción en la
plataforma, ni de que el sistema impida la inscripción de un atleta sancionado. Esta
brecha es principalmente administrativa y de gestión de federación, no de gestión
de performance individual.

---

## Tabla resumen

| # | Brecha | Artículo | Prioridad funcional |
|---|--------|----------|-------------------|
| 1 | Protocolo de superficie — 20s + signo OK post-performance | §1.2.2 | Alta |
| 2 | Dos tipos de BKO con consecuencias distintas | §1.1.10 | Alta |
| 3 | Penalizaciones técnicas independientes de la tarjeta | §1.1.13, §2.2.1.4, §2.2.2.2, §2.1.6.2 | Media |
| 4 | Sistema completo de categorías con Masters | §1.1.7 | Media |
| 5 | SPE tiene 4 variantes de distancia distintas | §1.1.8.7 | Media |
| 6 | Orden de grilla por tipo de disciplina (invertido en SPE) | §1.2.4.3 | Media |
| 7 | Señales táctiles del juez durante STA | §3.2.1.4 | Baja |
| 8 | Inicio de cronómetro STA — inmersión de vías respiratorias | §3.1.3.1 | Baja |
| 9 | "Salida en falso" como resultado específico de SPE | §4.2.1.3 | Baja |
| 10 | Conducta antideportiva — sanciones multi-torneo | Anexo FAAS | Baja |

---

*Análisis realizado sobre: Reglamento CMAS Apnea Indoor Versión 2022/01 — Traducción FAAS*
*Archivo fuente: `data/datos_prueba/REGLAS INTERNACIONALES APNEA INDOOR FAAS-CMAS Versión 2025.pdf`*
