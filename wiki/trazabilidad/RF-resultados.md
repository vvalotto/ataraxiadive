---
title: "RF — Premiación y Resultados"
type: trazabilidad
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
---

# RF — Premiación y Resultados

Requerimientos funcionales del área de resultados. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-PM-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| RF-PM-01 | ¿Los resultados son por puntos o por marca absoluta? | **Pendiente.** Es una regla de negocio configurable. |
| RF-PM-02 | ¿Existe ranking general del torneo? | **Sí.** Se denomina **Overall**. |
| RF-PM-03 | ¿Cómo se resuelven los empates? | Mismo puesto y mismos puntos. |
| RF-PM-04 | ¿Los certificados requieren logos/firmas específicas? | No es importante en esta etapa. |
| RF-PM-05 | ¿Hay rankings separados por categoría y género? | **Sí.** Rankings por [[disciplina]], categoría y género. |
| RF-PM-06 | ¿Cómo se publican los resultados? | En la plataforma; descargables. |

## Reglas de negocio clave

- **Overall:** existe un ranking general que combina resultados de múltiples [[disciplina|disciplinas]].
- **Rankings:** separados por disciplina, categoría y género.
- **Empates:** mismo puesto y mismos puntos — no hay criterio de desempate definido.
- **Publicación:** en la plataforma y descargable (PDF).

## Pendientes en elicitación

| ID | Pendiente | Clasificación |
|----|-----------|---------------|
| RF-PM-01 | Sistema de puntos vs marca absoluta — regla de negocio configurable no definida | **Backlog activo** — la decisión de diseño es pendiente; el algoritmo FAAS existe |

## Estado de implementación (lint-001)

RF-PM-01 no tiene US asociada explícita como "sistema de puntos", pero hay implementación parcial:
- SP5 implementó `AlgoritmoPuntaje` (US-5.6.1..US-5.6.6) con método de puntaje FAAS
- El ranking actual usa **marca absoluta** como criterio primario
- El puntaje FAAS es opcional y no está integrado en el flujo principal de ranking

**Lo que falta:** decidir si el sistema de puntos reemplaza o complementa el ranking por marca. Candidato a US en SP8 una vez definida la regla de negocio con el dominio experto.

## BCs que implementan esta área

- [[resultados]] — cálculo de rankings, ranking general (Overall)
