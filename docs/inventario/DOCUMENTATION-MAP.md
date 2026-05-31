# Mapa documental — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: navegación documental y jerarquía de lectura
> Última actualización: 2026-05-30

## 1. Propósito

Este documento corresponde a la Fase 3 del plan de adecuación documental. Su objetivo es ofrecer una guía mínima para saber qué documento consultar según la necesidad de lectura o trabajo.

---

## 2. Lectura rápida recomendada (orden pedagógico)

| Orden | Documento | Para qué leerlo |
|---|---|---|
| 1 | `README.md` | Entender rápidamente qué es AtaraxiaDive, su stack y estado resumido. |
| 2 | `CLAUDE.md` | Conocer el estado operativo actual y las reglas de trabajo con IA. |
| 3 | `docs/architecture/` | Revisar la arquitectura técnica vigente (C4) y sus vistas principales. |
| 4 | `docs/traceability/matrix.md` | Consultar trazabilidad entre RF, BC, incrementos y US-IEDD. |
| 5 | `.cm/baselines/` | Ver evidencia formal de cierres y baselines. |

> **Nota:** Este es un orden *pedagógico* — recomendado para un primer acercamiento al proyecto. **No es un orden de autoridad**. Ver sección 2.1 para resolver conflictos de información.

---

## 2.1 Precedencia en caso de conflicto (resolver divergencias)

Cuando exista **contradicción entre documentos** sobre un hecho, estado o decisión, la jerarquía de **precedencia de autoridad** está definida —de forma única— en [`FUENTES-DE-VERDAD-DOCUMENTAL.md §2`](./FUENTES-DE-VERDAD-DOCUMENTAL.md).

En síntesis: **código y tests › baselines › ADRs › matriz de trazabilidad › CLAUDE.md › README.md.**

---

## 3. Fuentes de verdad por tema (entradas frecuentes)

> La **tabla completa y autoritativa** de fuente de verdad por tema vive —de forma única— en [`FUENTES-DE-VERDAD-DOCUMENTAL.md §3`](./FUENTES-DE-VERDAD-DOCUMENTAL.md). Lo de abajo es solo un atajo de navegación para los temas más consultados.

| Tema | Fuente principal | Uso |
|---|---|---|
| Presentación breve | `README.md` | Entrada rápida; no contiene detalle completo. |
| Estado operativo actual | `CLAUDE.md` | Memoria operativa para desarrollo asistido por IA. |
| Manual de usuario (final) | [GitHub Pages](https://vvalotto.github.io/ataraxiadive/) · `manual/` (MkDocs) | Guía de uso de los portales público/organizador/juez/atleta. |
| Arquitectura vigente | `docs/architecture/` | Vista técnica principal (C4). `docs/design/architecture.md` es histórico. |
| Trazabilidad | `docs/traceability/matrix.md` | Relación RF → BC → incremento → US → estado. |
| Workflow de desarrollo | `docs/plans/WORKFLOW-DESARROLLO.md` | Procedimiento vigente para US, incrementos y subproyectos. |

> Para cualquier otro tema (ADRs, dominio, specs, baselines, calidad, etc.), ver la tabla completa en FUENTES §3.

---

## 4. Documentos de inventario y adecuación documental

| Documento | Rol |
|---|---|
| `docs/PLAN-ADECUACION-DOCUMENTAL.md` | Plan general de depuración documental. |
| `docs/inventario/INVENTARIO-DOCUMENTAL.md` | Inventario inicial y clasificación documental. |
| `docs/inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md` | Jerarquía documental y fuentes de verdad. |
| `docs/inventario/DOCUMENTATION-MAP.md` | Mapa mínimo de navegación documental (este documento). |

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
