# Hipótesis de Ensayo: IA, Ingeniería de Software y Human-in-the-Loop

## 1. Propósito

Este documento formula una hipótesis conceptual del ensayo que subyace al
experimento AtaraxiaDive y resume qué parte de esa hipótesis cuenta ya con
evidencia empírica inicial.

La tesis no es que la IA "resuelve" la Ingeniería de Software, sino que
reconfigura dónde está el trabajo de mayor valor y vuelve más visible la
necesidad de rigor en especificación, arquitectura, calidad constructiva y
capitalización del aprendizaje.

---

## 2. Hipótesis central

**Hipótesis del ensayo**

> La IA potencia a la Ingeniería de Software en múltiples dimensiones, pero no
> sustituye al ingeniero ni vuelve prescindible el juicio humano. Cuanto mayor
> es la capacidad de automatización de la implementación, mayor es la necesidad
> de intervención humana en la comprensión del dominio, la especificación del
> comportamiento, la evaluación de trade-offs, el control de calidad
> constructiva y la transformación del trabajo realizado en conocimiento
> reusable.

En esta formulación:

- la IA aumenta productividad en artefactos micro;
- la ingeniería aporta estructura, criterio y validación;
- el `human-in-the-loop` sigue siendo esencial;
- el valor diferencial no está solo en producir código, sino en producir
  sistemas más correctos, mantenibles, útiles y enseñables.

---

## 3. Desarrollo conceptual de la hipótesis

### 3.1 La IA desplaza el cuello de botella

Si parte de la implementación puede derivarse desde especificaciones, entonces
la dificultad principal deja de estar en "escribir código" y se concentra aún
más en:

- entender el dominio;
- modelar correctamente sus conceptos y fronteras;
- explicitar invariantes, precondiciones y postcondiciones;
- verificar que la arquitectura y el código preserven esas decisiones.

La IA no elimina estos problemas. Los vuelve más determinantes.

### 3.2 La calidad relevante cambia de centro

En un contexto con IA, la calidad de uso sigue siendo importante, pero cobra
mayor centralidad la **calidad constructiva**, porque:

- una mala especificación puede amplificarse rápidamente en muchos artefactos;
- una mala decisión arquitectónica puede replicarse a gran escala;
- una inconsistencia documental puede contaminar código, tests y reportes;
- una deuda técnica no explicitada puede crecer silenciosamente detrás de una
  apariencia de productividad.

### 3.3 La automatización sin memoria no alcanza

La productividad local no equivale a capacidad de ingeniería. Para que la IA
produzca valor sostenible, el proceso debe dejar memoria explícita:

- decisiones;
- trazabilidad;
- criterios de calidad;
- retrospección;
- aprendizajes formalizados.

Sin esa memoria, la IA acelera producción; con esa memoria, puede acelerar
aprendizaje.

### 3.4 El human-in-the-loop no es un parche

En esta visión, el `human-in-the-loop` no aparece solo para corregir errores del
modelo, sino como componente estructural del sistema de trabajo. Su papel es
irreductible, al menos por ahora, en funciones como:

- reformular el problema;
- arbitrar ambigüedades semánticas;
- decidir entre alternativas con trade-offs no locales;
- detectar inconsistencias entre artefactos;
- interpretar el valor real de una métrica;
- convertir experiencia de proyecto en conocimiento transferible.

---

## 4. Diseño experimental implícito

AtaraxiaDive funciona como laboratorio para contrastar esta hipótesis mediante
un entorno compuesto por cuatro piezas coordinadas:

- **IEDD** como marco para la cadena dominio → modelo → especificación →
  arquitectura → implementación.
- **Claude Dev Kit** como mecanismo de implementación táctica por historia.
- **Software Limpio** como sistema de verificación programática.
- **CM / gestión de configuración** como memoria viva de la evolución del
  proyecto y del experimento.

La hipótesis no se evalúa preguntando si la IA "genera buen código", sino si el
conjunto metodología + herramientas + intervención humana permite:

- sostener coherencia entre artefactos;
- controlar la deuda técnica;
- producir aprendizaje acumulable;
- mejorar la calidad de las decisiones de ingeniería;
- mantener al humano como agente de gobierno del proceso.

---

## 5. Qué se ha demostrado hasta el momento

La evidencia disponible en AtaraxiaDive no cierra todavía toda la hipótesis,
pero sí permite afirmar varios resultados parciales.

### 5.1 Se confirmó que la automatización requiere calibración humana

Los documentos de contexto y las baselines muestran que el ecosistema no fue
usable de manera directa con un perfil genérico. Fue necesario:

- adaptar supuestos del Dev Kit a una arquitectura hexagonal BC-first;
- corregir paths, artefactos, quality gates y criterios del flujo;
- revisar consistencia documental luego de ADRs significativos;
- definir documentos de contexto específicos del proyecto.

Esto es evidencia a favor de que la IA y sus herramientas no operan solas en un
proyecto real: requieren diseño y gobierno humano del entorno.

### 5.2 Se confirmó que la productividad no elimina la necesidad de ingeniería

Los HITOs de SP1 y SP2 muestran que el pipeline `/implement-us` se volvió
operativo y que su overhead converge. Sin embargo, también muestran que:

- aparecieron tensiones entre BDD, Event Sourcing e invariantes DDD;
- hubo artefactos faltantes por compresión de contexto;
- algunas decisiones arquitectónicas emergieron recién al observar métricas y
  revisar la implementación;
- fue necesario crear una etapa formal de ajuste técnico post-subproyecto.

La productividad táctica aumentó, pero siguió siendo necesaria una capa de
ingeniería para interpretar, corregir y consolidar.

### 5.3 Se confirmó que la calidad constructiva necesita instrumentación explícita

La experiencia acumulada en SP1 y SP2 sugiere que los quality gates no son un
adorno operativo. Funcionan como dispositivos de gobierno del proceso:

- detectan violaciones arquitectónicas reales;
- catalizan decisiones de diseño no anticipadas;
- hacen visible deuda técnica que de otro modo quedaría distribuida;
- permiten transformar percepción subjetiva en evidencia discutible.

Esto apoya la hipótesis de que, en entornos con IA, la calidad constructiva debe
ser tratada como dimensión central y no como control posterior.

### 5.4 Se confirmó que el experimento produce conocimiento formalizable

Los `HITOs`, las `baselines`, los `ADRs`, la matriz de trazabilidad y los
reportes por US muestran que el proyecto ya está generando conocimiento con un
grado de formalización reutilizable. No se trata solo de bitácora narrativa:

- hay hipótesis explícitas;
- hay observaciones y lecciones;
- hay relaciones entre decisiones, fricciones y resultados;
- hay material potencialmente reusable para paper, libro o docencia.

Esto respalda la idea de que el proceso puede capitalizar aprendizaje y no solo
producir software.

### 5.5 Se confirmó, de manera parcial, la necesidad estructural del human-in-the-loop

Hasta ahora la evidencia apunta a que la intervención humana fue indispensable
para:

- encuadrar el problema y el valor del experimento;
- corregir desalineaciones entre herramientas y proyecto;
- reinterpretar resultados de métricas;
- decidir ajustes metodológicos;
- formalizar los aprendizajes emergentes.

No aparece todavía evidencia de que el entorno pueda sostener la misma calidad
sin esa intervención. Por el contrario, los HITOs sugieren que, sin ella, el
proceso tendería a degradarse silenciosamente.

---

## 6. Qué todavía no está demostrado

La hipótesis general sigue abierta en varios puntos:

- no está demostrado aún que este enfoque reduzca el costo total del ciclo de
  vida frente a alternativas más convencionales;
- no está demostrado todavía que la calidad final del producto sea superior de
  forma consistente;
- no está demostrado en un entorno con usuarios reales y operación sostenida;
- no está cuantificado todavía cuánto del conocimiento producido puede
  reutilizarse sin retrabajo significativo;
- no está aislado empíricamente qué parte del resultado se debe a IEDD, cuál a
  las herramientas y cuál al rol del humano experto.

Por lo tanto, lo alcanzado hasta ahora es una **validación inicial de
factibilidad y coherencia**, no una demostración final.

---

## 7. Tesis provisional del experimento

Con la evidencia reunida hasta SP2, la tesis provisional puede formularse así:

> La IA no reemplaza la Ingeniería de Software; la desplaza hacia actividades de
> mayor nivel y vuelve más valiosas la especificación rigurosa, la verificación
> arquitectónica, la memoria del proceso y la producción deliberada de
> aprendizaje. En ese contexto, el `human-in-the-loop` no es una concesión
> transitoria, sino la condición actual para que la automatización sea útil,
> controlable y epistemológicamente fértil.

---

## 8. Próxima contrastación empírica

Las próximas etapas del proyecto deberían aportar evidencia sobre:

- sostenibilidad del enfoque cuando aumenta la complejidad inter-BC;
- comportamiento del proceso con más integración full-stack y offline-first;
- costo real de mantener consistencia entre artefactos en horizontes más largos;
- capacidad del entorno para producir conocimiento reusable con menor
  reescritura;
- persistencia o reducción de la dependencia humana a medida que el entorno se
  especializa.

---

## 9. Conclusión

La hipótesis del ensayo no sostiene que la IA haga innecesaria la ingeniería,
sino lo contrario: cuanto más capaz es la IA de producir implementación, más
importante se vuelve la disciplina que define qué construir, cómo verificarlo,
cómo mantener coherencia entre decisiones y cómo convertir experiencia en
conocimiento acumulable.

AtaraxiaDive ya ofrece evidencia inicial a favor de esta visión. La parte aún
abierta del experimento es medir cuánto de esa promesa se sostiene cuando el
producto y el entorno sigan creciendo.
