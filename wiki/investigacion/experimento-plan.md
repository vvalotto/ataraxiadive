---
title: "Plan del Experimento — AtaraxiaDive como laboratorio vivo"
type: investigacion
last_updated: "2026-05-20"
sources:
  - docs/contexto/PLAN-EXPERIMENTO.md
  - docs/contexto/ANALISIS-ATARAXIADIVE.md
  - docs/contexto/ANALISIS-IEDD.md
---

# Plan del Experimento — AtaraxiaDive como laboratorio vivo

## El objetivo real

No es "construir un gestor de torneos de apnea".

El objetivo es **demostrar, con evidencia empírica propia, que es posible desarrollar software con IA manteniendo la memoria del producto viva, la deuda técnica visible, y el conocimiento formalizable**. AtaraxiaDive es el vehículo. El conocimiento producido en el proceso es el producto de fondo.

## Las tres preguntas del experimento

1. ¿El entorno CM + Dev Kit + Software Limpio funciona como sistema integrado o cada herramienta exige fricción de coordinación?
2. ¿IEDD es una metodología que mejora la calidad de las especificaciones o es teoría que no sobrevive el contacto con un proyecto real?
3. ¿Cuánto del conocimiento producido durante el desarrollo se puede capitalizar directamente en material académico sin reescritura?

## Los tres horizontes

| Horizonte | SPs | Duración | Objetivo | Criterio de éxito |
|-----------|-----|----------|----------|-------------------|
| H1 — Validar | SP1 + SP2 | 2-3 meses | ¿El entorno funciona para un ciclo real? | BL-002 con métricas, 12-15 USs trazadas, primera retrospectiva |
| H2 — Construir | SP3 + SP4 | 4-6 meses | ¿El sistema es usable? ¿Escala bajo presión? | Torneo simulable de principio a fin; material suficiente para paper IEDD |
| H3 — Producir | SP5 + capitalización | 6-12 meses | ¿El conocimiento se capitaliza en productos intelectuales? | Torneo real; 3 caps. libro DDD; 1 caso de estudio IS; 1 artículo/ponencia |

**Estado actual (SP6 en curso):** H1 y H2 completados. H3 en progreso.

## Jerarquía de trabajo

```
Subproyecto (SP1–SP6+)
  └── Incremento (ej: INC-4.2)
        └── Historia de Usuario (ej: US-4.2.1)
              └── /implement-us → 10 fases por US
```

- **Subproyecto:** cierra cuando todos sus incrementos terminan → genera una Baseline.
- **Incremento:** cierra cuando todas sus USs pasan **y** la DoD de integración es observable.
- **US:** unidad del Dev Kit. Procesada con `/implement-us` en 10 fases.

## Capitalización de conocimiento

Cada incremento produce conocimiento que fluye hacia productos intelectuales sin reescritura:

| Aprendizaje en AtaraxiaDive | Libro DDD | Curso IS | Paper IEDD |
|-----------------------------|-----------|----------|------------|
| Performance aggregate + invariantes | "Aggregates con invariantes reales" | Caso práct. semana 4 | Ejemplo RF→invariante→BDD |
| Event Sourcing para auditoría | "Domain Events como memoria del dominio" | Caso práct. semana 8 | — |
| Máquina de estados del Torneo | "State machines como ubiquitous language" | Caso práct. semana 6 | — |
| Reglas como datos (disciplinas) | "Bounded Context Configuración" | Caso práct. semana 10 | — |

**La regla:** no reescribir. Los ADRs, retrospectivas y reportes de `/implement-us` son materia prima directa.

## Por qué AtaraxiaDive es un caso de estudio excepcionalmente bueno

- **Dominio de primera mano:** Victor practica apnea — el riesgo de ambigüedad de dominio está eliminado.
- **Lógica no trivial:** máquina de estados con 7 estados, reglas configurables como datos, invariantes de aggregate verificables, integridad criptográfica (SHA-256).
- **Atributos de calidad exigentes y medibles:** 500ms, 50 usuarios concurrentes, offline obligatorio, 6 acciones del juez.
- **Modelo de desarrollo alineado:** SP → Baseline, Incremento → DoD binaria, US → `/implement-us`.

## Subproyectos y Baselines

| SP | Nombre | BL generada | Foco |
|----|--------|-------------|------|
| SP1 | La Performance | BL-001 | Primer aggregate, ES, walking skeleton |
| SP2 | La Competencia | BL-002 | Core domain, quality gates, SP-ADJ |
| SP3 | El Torneo | BL-003 | Supporting domains, CQRS emergente |
| SP4 | La Plataforma | BL-004 | Offline, auditoría, notificaciones, datos reales |
| SP5 | La Puesta en Marcha | BL-005 | Multi-rol, usuarios, seguridad, despliegue |
| SP6 | Validación y Despliegue | BL-006 (en curso) | Deriva de tests, wiki, producción |

## Páginas relacionadas

- [[iedd-marco-conceptual]] — el marco teórico que este experimento valida
- [[iedd-hipotesis-experimento]] — hipótesis centrales y estado de confirmación
- [[hitos-catalog]] — los 32 HITOs: evidencia empírica del experimento
- [[uat-metodologia]] — metodología UAT que emergió del experimento
