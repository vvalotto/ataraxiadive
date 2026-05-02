# Mapa documental — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: navegación documental y jerarquía de lectura
> Última actualización: 2026-04-27

## 1. Propósito

Este documento corresponde a la Fase 3 del plan de adecuación documental. Su objetivo es ofrecer una guía mínima para saber qué documento consultar según la necesidad de lectura o trabajo.

---

## 2. Lectura rápida recomendada

| Orden | Documento | Para qué leerlo |
|---|---|---|
| 1 | `README.md` | Entender rápidamente qué es AtaraxiaDive, su stack y estado resumido. |
| 2 | `CLAUDE.md` | Conocer el estado operativo actual y las reglas de trabajo con IA. |
| 3 | `docs/design/architecture.md` | Revisar la arquitectura técnica vigente y sus vistas principales. |
| 4 | `docs/traceability/matrix.md` | Consultar trazabilidad entre RF, BC, incrementos y US-IEDD. |
| 5 | `.cm/baselines/` | Ver evidencia formal de cierres y baselines. |

---

## 3. Fuentes de verdad por tema

| Tema | Fuente principal | Uso |
|---|---|---|
| Presentación breve | `README.md` | Entrada rápida; no contiene detalle completo. |
| Estado operativo actual | `CLAUDE.md` | Memoria operativa para desarrollo asistido por IA. |
| Workflow de desarrollo | `docs/plans/WORKFLOW-DESARROLLO.md` | Procedimiento vigente para US, incrementos y subproyectos. |
| Arquitectura vigente | `docs/design/architecture.md` | Vista técnica principal. |
| Decisiones arquitectónicas | `docs/adr/` | Registro de decisiones y trade-offs. |
| Dominio del problema | `docs/dominio/01-dominio_torneos_apnea.md` | Descripción narrativa del dominio de apnea. |
| Requerimientos funcionales | `docs/dominio/05-requerimientos_funcionales.md` | Catálogo base de RF. |
| Trazabilidad | `docs/traceability/matrix.md` | Relación RF → BC → incremento → US → estado. |
| Especificaciones US-IEDD | `docs/specs/` | Especificaciones detalladas por historia. |
| Baselines | `.cm/baselines/` | Evidencia formal de cierre. |
| Cambios de configuración | `.cm/changes/` | Registro de cambios. |
| Aprendizajes metodológicos | `docs/contexto/HITO-*.md` | Evidencia y capitalización del experimento. |
| Reportes de calidad | `quality/reports/` | Evidencia técnica de calidad. |

---

## 4. Documentos de inventario y adecuación documental

| Documento | Rol |
|---|---|
| `docs/PLAN-ADECUACION-DOCUMENTAL.md` | Plan general de depuración documental. |
| `docs/inventario/INVENTARIO-DOCUMENTAL.md` | Inventario inicial y clasificación documental. |
| `docs/inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md` | Jerarquía documental y fuentes de verdad. |
| `docs/DOCUMENTATION-MAP.md` | Mapa mínimo de navegación documental. |

---

## 5. Documentos históricos

Los documentos históricos se conservan como evidencia del camino recorrido. No deben usarse como fuente principal para el estado actual.

| Documento / carpeta | Observación |
|---|---|
| `docs/dominio/04-estrategia_desarrollo.md` | Planificación inicial. Ya declara que contiene decisiones superadas, como PostgreSQL y Docker. |
| `docs/contexto/ANALISIS-*.md` | Análisis metodológicos o técnicos. Útiles como evidencia y contexto. |
| Planes cerrados en `docs/plans/` | Deben leerse como planificación o evidencia del momento en que fueron creados. |

---

## 6. Documentos de evidencia

| Documento / carpeta | Tipo de evidencia |
|---|---|
| `.cm/baselines/` | Cierre formal de baselines. |
| `.cm/changes/` | Registros de cambio. |
| `docs/contexto/HITO-*.md` | Aprendizajes y decisiones emergentes del experimento. |
| `quality/reports/` | Reportes de CodeGuard, DesignReviewer y ArchitectAnalyst. |
| `tests/` | Evidencia ejecutable de validación técnica. |

---

## 7. Regla editorial básica

No duplicar el estado detallado del proyecto en varios documentos.

- El README resume.
- CLAUDE.md orienta el trabajo operativo.
- La matriz documenta trazabilidad.
- Las baselines evidencian cierres.
- Los ADRs registran decisiones.
- Los HITOs preservan aprendizajes.

Ante contradicción, consultar `docs/inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md`.
