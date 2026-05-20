---
title: "IEDD — Hipótesis del Experimento"
type: investigacion
last_updated: "2026-05-20"
sources:
  - docs/iedd/04-Hipotesis_Ensayo_IA_Ingenieria_Human_In_The_Loop.md
---

# IEDD — Hipótesis del Experimento

Estado del ensayo que subyace a AtaraxiaDive: qué se hipotetiza, qué está confirmado, qué sigue abierto.

---

## Hipótesis central

> La IA potencia a la Ingeniería de Software en múltiples dimensiones, pero **no sustituye al ingeniero** ni vuelve prescindible el juicio humano. Cuanto mayor es la capacidad de automatización de la implementación, mayor es la necesidad de intervención humana en la comprensión del dominio, la especificación del comportamiento, la evaluación de trade-offs, el control de calidad constructiva y la transformación del trabajo realizado en conocimiento reusable.

---

## Desarrollo conceptual

### La IA desplaza el cuello de botella

Si la implementación puede derivarse desde especificaciones, la dificultad se concentra aún más en:
- entender el dominio
- modelar correctamente sus conceptos y fronteras
- explicitar invariantes, precondiciones y postcondiciones
- verificar que arquitectura y código preserven esas decisiones

**La IA no elimina estos problemas — los vuelve más determinantes.**

### La calidad relevante cambia de centro

En un contexto con IA, cobra mayor centralidad la **calidad constructiva**:
- una mala especificación puede amplificarse rápidamente en muchos artefactos
- una mala decisión arquitectónica puede replicarse a gran escala
- una inconsistencia documental puede contaminar código, tests y reportes
- una deuda técnica no explicitada puede crecer silenciosamente

### La automatización sin memoria no alcanza

Para que la IA produzca valor sostenible, el proceso debe dejar memoria explícita:
- decisiones (ADRs)
- trazabilidad (matrix.md, US cerradas)
- criterios de calidad (quality gates)
- retrospección (HITOs)
- aprendizajes formalizados

> Sin esa memoria, la IA acelera producción. Con esa memoria, puede acelerar aprendizaje.

### El human-in-the-loop es estructural

El `human-in-the-loop` no aparece solo para corregir errores — es componente estructural. Su papel es irreductible en:
- reformular el problema
- arbitrar ambigüedades semánticas
- decidir entre alternativas con trade-offs no locales
- detectar inconsistencias entre artefactos
- interpretar el valor real de una métrica
- convertir experiencia de proyecto en conocimiento transferible

---

## Diseño experimental

AtaraxiaDive funciona como laboratorio con cuatro piezas coordinadas:

| Pieza | Rol en el experimento |
|-------|----------------------|
| **IEDD** | Marco para la cadena dominio → modelo → especificación → arquitectura → implementación |
| **Claude Dev Kit** | Mecanismo de implementación táctica por historia (`/implement-us`) |
| **Software Limpio** (DesignReviewer, ArchitectAnalyst) | Sistema de verificación programática de calidad constructiva |
| **CM / gestión de configuración** | Memoria viva de la evolución del proyecto y del experimento |

La hipótesis **no** se evalúa preguntando si la IA genera buen código, sino si el conjunto permite:
- sostener coherencia entre artefactos
- controlar la deuda técnica
- producir aprendizaje acumulable
- mejorar la calidad de las decisiones de ingeniería
- mantener al humano como agente de gobierno del proceso

---

## Estado de confirmación de la hipótesis

### ✅ Confirmado: la automatización requiere calibración humana

El ecosistema no fue usable directamente con perfil genérico. Fue necesario:
- adaptar supuestos del Dev Kit a arquitectura hexagonal BC-first
- corregir paths, artefactos, quality gates y criterios del flujo
- revisar consistencia documental luego de ADRs significativos

**Evidencia:** HITOs de configuración del entorno y documentos de contexto.

### ✅ Confirmado: la productividad no elimina la necesidad de ingeniería

Los HITOs de SP1 y SP2 muestran que el pipeline se volvió operativo, pero también que:
- aparecieron tensiones entre BDD, Event Sourcing e invariantes DDD
- hubo artefactos faltantes por compresión de contexto
- algunas decisiones arquitectónicas emergieron recién al observar métricas
- fue necesario crear una etapa formal de ajuste técnico post-subproyecto (SP-ADJ)

### ✅ Confirmado: la calidad constructiva necesita instrumentación explícita

Los quality gates funcionan como dispositivos de gobierno:
- detectan violaciones arquitectónicas reales
- catalizan decisiones de diseño no anticipadas
- hacen visible deuda técnica distribuida
- transforman percepción subjetiva en evidencia discutible

### ✅ Confirmado: el proceso produce conocimiento formalizable

HITOs, baselines, ADRs, matrix de trazabilidad y reportes por US muestran:
- hipótesis explícitas con observaciones y lecciones
- relaciones entre decisiones, fricciones y resultados
- material potencialmente reusable para paper, libro o docencia

### ✅ Confirmado (parcial): necesidad estructural del human-in-the-loop

La intervención humana fue indispensable para encuadrar el problema, corregir desalineaciones, reinterpretar métricas, decidir ajustes metodológicos y formalizar aprendizajes emergentes.

---

## Qué todavía no está demostrado

| Punto abierto | Por qué importa |
|---------------|----------------|
| Si este enfoque reduce el costo total del ciclo de vida frente a alternativas convencionales | Validez económica del método |
| Si la calidad final del producto es superior de forma consistente | Validez técnica del método |
| Si funciona en un entorno con usuarios reales y operación sostenida | Validez práctica |
| Cuánto del conocimiento producido puede reutilizarse sin retrabajo | Validez del modelo de capitalización |
| Qué parte del resultado se debe a IEDD, cuál a las herramientas, cuál al humano experto | Aislamiento de causas |

Lo alcanzado hasta ahora es una **validación inicial de factibilidad y coherencia**, no una demostración final.

---

## Tesis provisional del experimento

> La IA no reemplaza la Ingeniería de Software; la desplaza hacia actividades de mayor nivel y vuelve más valiosas la especificación rigurosa, la verificación arquitectónica, la memoria del proceso y la producción deliberada de aprendizaje. En ese contexto, el `human-in-the-loop` no es una concesión transitoria, sino la condición actual para que la automatización sea útil, controlable y epistemológicamente fértil.

---

## Próximas contrastaciones empíricas

- Sostenibilidad cuando aumenta la complejidad inter-BC
- Comportamiento con más integración full-stack y offline-first
- Costo real de mantener consistencia entre artefactos en horizontes largos
- Capacidad del entorno para producir conocimiento reusable con menor reescritura
- Persistencia o reducción de la dependencia humana a medida que el entorno se especializa

---

## Relaciones

- Ver [[iedd-marco-conceptual]] para el modelo de 5 capas que fundamenta la hipótesis.
- Los HITOs del proyecto son la evidencia empírica acumulada — ver `docs/contexto/INDICE-HITOS.md`.
- Ver [[uat-metodologia]] para la política de validación E2E que instrumenta el proceso.
