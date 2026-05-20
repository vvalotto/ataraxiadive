---
title: "Vista de Investigación"
type: vista
last_updated: "2026-05-20"
sources:
  - docs/contexto/PLAN-EXPERIMENTO.md
  - docs/contexto/HITO-*.md
  - docs/contexto/ANALISIS-IEDD.md
---

# Vista de Investigación

> El sistema visto como fuente de conocimiento para productos intelectuales
> de largo plazo.

## Propósito

Responder preguntas sobre qué aprendió el proyecto, cómo esos aprendizajes
se mapean a los productos intelectuales de Victor, y qué evidencia empírica
existe para las hipótesis del experimento IEDD.

Esta vista no tiene equivalente en la literatura de arquitectura de software.
Es específica de AtaraxiaDive como laboratorio de investigación.

## Stakeholder principal

Victor Valotto como investigador, autor y docente.

## Preguntas características

1. ¿Qué aprendimos sobre Event Sourcing en AtaraxiaDive que pueda ir al libro DDD?
2. ¿Qué evidencia empírica tiene la metodología IEDD para el paper?
3. ¿Qué casos prácticos del SP3 sirven para el curso de IS?
4. ¿Qué dice el experimento sobre la fricción de consistencia documental con IA?
5. ¿Qué hipótesis del PLAN-EXPERIMENTO fueron confirmadas o refutadas?
6. ¿Qué aprendizajes del SP1 son generalizables a otros proyectos DDD?
7. ¿Qué reflexiones del proyecto alimentan el material de gestión (PMBOK v7)?

## Matriz de conocimiento (esqueleto)

| Aprendizaje en AtaraxiaDive | Libro DDD | Curso IS | Material Gestión | Paper IEDD |
|-----------------------------|-----------|----------|-----------------|------------|
| Performance aggregate + invariantes | Cap. "Aggregates con invariantes reales" | Caso práctico semana 4 | — | Ejemplo RF→invariante→BDD |
| Event Sourcing para auditoría | Cap. "Domain Events como memoria del dominio" | Caso práctico semana 8 | — | — |
| Máquina de estados del Torneo | Cap. "State machines como ubiquitous language" | Caso práctico semana 6 | Ejemplo de WIP y flujos | — |
| Reglas como datos (disciplinas) | Cap. "Bounded Context Configuración" | Caso práctico semana 10 | — | — |
| Offline-first + sync | Cap. "Arquitectura como consecuencia del dominio" | — | Gestión de riesgos técnicos | — |
| Fricción documental con IA | — | — | Reflexiones iteración ágil | Friction analysis IEDD |

*Fuente: docs/contexto/PLAN-EXPERIMENTO.md — a enriquecer con cada HITO ingresado*

## Hipótesis del experimento (a poblar)

> *Vacío — pendiente ingest de PLAN-EXPERIMENTO.md y HITOs metodológicos*

## Recorridos sugeridos

**Para preparar contenido del libro DDD:**
`[[investigacion/aprendizajes-ddd]]` → páginas de BC relevantes
→ ADRs con razonamiento DDD → evidencia en tests BDD

**Para construir el caso de investigación IEDD:**
`[[investigacion/hipotesis-iedd]]` → HITOs como evidencia
→ métricas de calidad por baseline → análisis de fricción

**Para preparar material de clase:**
`[[investigacion/casos-practicos-is]]` → US concretas con BDD
→ código del dominio como ejemplo → reflexión metodológica

## Páginas hub de esta vista

- `wiki/investigacion/` — todas las páginas de aprendizaje (a crear en Fase 3)
- [[investigacion/matriz-conocimiento]] — la tabla completa mapeada
- [[investigacion/hipotesis-iedd]] — estado de verificación del experimento

---
*Vista pendiente de poblarse — requiere Fase 3 (ingest de HITOs y PLAN-EXPERIMENTO)*
*Es la vista más diferenciadora del proyecto — no existe en ningún otro framework de wiki*
