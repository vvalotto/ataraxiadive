---
title: "Vista de Salud"
type: vista
last_updated: "2026-05-20"
sources:
  - quality/reports/
  - wiki/salud/
  - docs/contexto/HITO-14-ANALISIS-METODOLOGIA-Y-ESTRUCTURA.md
---

# Vista de Salud

> El sistema visto desde la deuda técnica, la calidad y la consistencia
> entre lo que el proyecto dice ser y lo que realmente es.

## Propósito

Responder preguntas sobre el estado de salud del proyecto: cobertura de tests,
deuda técnica, inconsistencias documentales, gaps de trazabilidad. Es la vista
que convierte el diagnóstico disperso en múltiples documentos en una narrativa
coherente y actualizada.

Resuelve directamente los problemas identificados en HITO-14:
- **D-02**: múltiples fuentes de verdad para el estado del proyecto
- **D-03**: documentación fundacional desalineada con la arquitectura vigente

## Stakeholder principal

Tech lead, responsable de calidad, Victor evaluando el experimento.

## Preguntas características

1. ¿Qué requerimientos no tienen tests asociados?
2. ¿Qué documentos están desalineados con la arquitectura vigente?
3. ¿Qué BCs tienen deuda técnica acumulada según los quality gates?
4. ¿Hay conceptos usados en el código sin página propia en el wiki?
5. ¿Cuál es la tendencia de calidad entre baselines?
6. ¿Qué páginas del wiki están huérfanas (sin enlaces entrantes)?
7. ¿Qué inconsistencias existen entre ADRs y el código actual?

## Problemas heredados conocidos (pre-wiki)

Identificados en HITO-14 — a verificar y resolver con el lint:

| ID | Problema | Impacto |
|----|----------|---------|
| D-02 | Múltiples fuentes de verdad para estado del proyecto | Muy alto |
| D-03 | Docs fundacionales mencionan PostgreSQL (ya reemplazado por SQLite) | Muy alto |
| D-05 | Regla hexagonal no cumplida estrictamente en todo el código | Alto |
| D-06 | Imports directos entre BCs en algunos módulos | Alto |
| D-09 | Documentos históricos redactados como si siguieran vigentes | Medio |

## Recorridos sugeridos

**Para una revisión de salud general:**
`[[salud/lint-actual]]` → sección por sección → acciones priorizadas

**Para verificar tendencia de calidad:**
`[[estado/proyecto]]` → historial de baselines → métricas por BC

**Para investigar una inconsistencia específica:**
`[[salud/lint-actual]]` → hallazgo específico → páginas de BC o decisión
afectadas → fuente original en docs/

## Páginas hub de esta vista

- `wiki/salud/lint-actual` — resultado del último lint (alias al último lint-NNN)
- [[estado/proyecto]] — estado consolidado como única fuente de verdad
- `wiki/salud/` — historial de todos los lints

---
*Vista pendiente de poblarse — requiere Fase 4 (primer lint)*
*Los problemas D-02 y D-03 ya están identificados y serán los primeros hallazgos del lint*
