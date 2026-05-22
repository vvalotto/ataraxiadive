---
title: "IEDD — Marco Conceptual"
type: investigacion
last_updated: "2026-05-20"
sources:
  - docs/iedd/01-Ingenieria_Especificaciones_DDD_IA.md
  - docs/iedd/02-Marco_Conceptual_5_Capas.md
  - docs/iedd/03-Diagrama_Conceptual.md
---

# IEDD — Marco Conceptual

**IEDD:** Ingeniería de Especificaciones Basada en Dominio. Marco metodológico experimental que integra DDD, ingeniería de especificaciones e IA como traductor de comportamiento.

---

## El modelo de 5 capas

```
┌───────────────────────┐
│       DOMINIO         │  Realidad del problema: actores, procesos, reglas, lenguaje
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│        MODELO         │  Domain-Driven Design: entidades, agregados, eventos,
│       (DDD)           │  contextos delimitados, lenguaje ubicuo
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│    ESPECIFICACIÓN     │  Comportamiento del sistema: invariantes, reglas,
│                       │  precondiciones, postcondiciones, estados, eventos
└──────────┬────────────┘
           │  ←── IA actúa como traductor conceptual en esta transición
           ▼
┌───────────────────────┐
│     ARQUITECTURA      │  Organización del sistema: componentes, contextos,
│                       │  persistencia, comunicación, manejo de eventos
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│   IMPLEMENTACIÓN      │  Tecnología concreta: código, APIs, bases de datos,
│                       │  frameworks, infraestructura
└───────────────────────┘
```

**Principio:** la IA puede intervenir principalmente en las capas inferiores, **sin reemplazar las superiores**.

---

## La tesis central

> La ingeniería de software puede definirse como la disciplina que **modela dominios complejos y especifica sistemas** capaces de representar y ejecutar ese modelo.
> Los lenguajes de programación pasan a ser medios de materialización.

### Cambio de foco que produce la IA generativa

| Antes | Ahora |
|-------|-------|
| Programar sistemas | Especificar sistemas |
| La implementación era el cuello de botella | La especificación es el cuello de botella |
| Lenguajes → programación → diseño | Dominio → modelo → especificación → arquitectura → implementación |

### La IA como compilador conceptual

La calidad del resultado depende de:
- **Claridad del modelo** de dominio
- **Precisión de la especificación** del comportamiento
- **Ausencia de ambigüedad** en invariantes y reglas

---

## El aporte de DDD en este marco

DDD proporciona la construcción del modelo conceptual a partir del dominio:

- **Entidades y objetos de valor** — capturan conceptos del dominio
- **Agregados** — fronteras de consistencia
- **Eventos de dominio** — qué ocurrió con significado de negocio
- **Contextos delimitados** — fronteras semánticas del modelo
- **Lenguaje ubicuo** — vocabulario compartido entre dominio e implementación

El modelo DDD se interpreta como una **especificación conceptual** del sistema.

---

## Implicaciones para la práctica de ingeniería

La actividad principal del ingeniero pasa a ser:
1. Comprender el dominio
2. Construir el modelo conceptual
3. Definir el comportamiento esperado con precisión
4. Eliminar ambigüedades en invariantes y reglas

La implementación resulta **derivable** a partir de esa especificación.

---

## Relaciones

- Ver [[iedd-hipotesis-experimento]] para la hipótesis central del ensayo y la evidencia acumulada.
- Ver [[uat-metodologia]] para la política de validación funcional E2E.
- AtaraxiaDive es el laboratorio experimental de este marco — ver [[investigacion/hipotesis-experimento]].
- Los BCs del proyecto materializan el modelo: [[competencia]], [[bc-torneo]], [[registro]], [[resultados]], [[identidad]], [[notificaciones]].
