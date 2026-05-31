# Fuentes de verdad documental — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: jerarquía documental y autoridad por tema
> Última actualización: 2026-05-30

## 1. Propósito

Este documento corresponde a la Fase 2 del plan de adecuación documental. Define qué documento debe considerarse autoridad para cada tipo de información del proyecto y establece convenciones mínimas para distinguir documentación vigente, histórica, operativa, derivada y de evidencia.

---

## 2. Principio rector

Cada tipo de información debe tener una fuente principal. Otros documentos pueden resumirla o enlazarla, pero no deberían duplicarla en detalle.

Cuando exista contradicción entre documentos, se aplicará este orden general:

1. Código y tests para estado implementado y validado.
2. Baselines para cierres formales.
3. ADRs para decisiones arquitectónicas.
4. Matriz de trazabilidad para cobertura RF → BC → US → estado.
5. CLAUDE.md para estado operativo de trabajo.
6. README.md solo como síntesis de entrada.

---

## 3. Fuentes de verdad por tema

| Tema | Fuente de verdad | Documentos secundarios | Regla de uso |
|---|---|---|---|
| Presentación breve del proyecto | `README.md` | `docs/requirements/vision.md`, `docs/contexto/PLAN-EXPERIMENTO.md` | El README resume. No debe contener detalle extenso. |
| Propósito del producto | `docs/requirements/vision.md` | `README.md`, `CLAUDE.md` | El README solo debe incluir una versión breve. |
| Propósito experimental | `docs/contexto/PLAN-EXPERIMENTO.md` | `CLAUDE.md`, documentos `ANALISIS-*.md` | La explicación completa vive en contexto, no en README. |
| Estado operativo actual | `CLAUDE.md` | `README.md`, `docs/traceability/matrix.md`, `.cm/baselines/` | CLAUDE.md resume y enlaza evidencia. |
| Estado validado por baseline | `.cm/baselines/` | `CLAUDE.md`, `README.md` | Las baselines mandan sobre cierres formales. |
| Workflow vigente de desarrollo | `docs/plans/WORKFLOW-DESARROLLO.md` | `CLAUDE.md` | Si hay diferencia, manda el workflow. |
| Arquitectura vigente | `docs/architecture/` | `docs/adr/`, `docs/design/architecture.md` (histórico) | Vista C4 vigente (16 docs: por BC + transversales). |
| Decisiones arquitectónicas | `docs/adr/` | `docs/architecture/` | Las ADRs registran decisión y trade-offs. |
| Bounded Contexts | `docs/architecture/03-bounded-contexts.md` · `20-context-map-integrations.md` | `docs/design/context-map.md` (modelado DDD), `CLAUDE.md §3` | Deben contrastarse con `src/`. |
| Contrato HTTP / API observable | `src/*/api/router.py` (OpenAPI generado) | `docs/architecture/30-runtime-interactions.md` | El contrato real lo define el código; la doc lo describe. |
| Modelo de dominio | `docs/design/domain-model.md` | `docs/dominio/01-dominio_torneos_apnea.md`, specs US-IEDD | Debe actualizarse con refactorings reales. |
| Dominio del problema | `docs/dominio/01-dominio_torneos_apnea.md` | `docs/design/domain-model.md` | Fuente narrativa principal del dominio. |
| Atributos de calidad | `docs/dominio/03-atributos_calidad.md` | `docs/design/architecture.md`, tests, quality reports | Fuente de atributos no funcionales. |
| Requerimientos funcionales | `docs/dominio/05-requerimientos_funcionales.md` | `docs/traceability/matrix.md` | Catálogo base. |
| Trazabilidad | `docs/traceability/matrix.md` | specs US-IEDD, baselines, tests | Debe distinguir estados de madurez. |
| Especificaciones US-IEDD | `docs/specs/` | `docs/traceability/matrix.md` | Fuente de especificación detallada. |
| Planes de implementación | `docs/plans/` | `CLAUDE.md`, specs US-IEDD | Cada plan debe indicar si está vigente, cerrado o histórico. |
| Aprendizajes metodológicos | `docs/contexto/HITO-*.md` | baselines, análisis metodológicos | Evidencia del experimento. |
| Reportes de calidad | `quality/reports/` | `CLAUDE.md`, baselines | Evidencia técnica. |
| Manual de usuario | `manual/` (MkDocs) | GitHub Pages (<https://vvalotto.github.io/ataraxiadive/>) | Guía de uso por rol (organizador, juez, atleta, público). Debe reflejar la app en producción. |
| Gestión de configuración | `.cm/` | `docs/plans/WORKFLOW-DESARROLLO.md` | Fuente de registros de baseline y cambios. |

---

## 4. Convención de estado documental

| Estado documental | Uso |
|---|---|
| Vigente | Documento activo que debe reflejar el estado actual de su tema. |
| Histórico | Documento conservado como memoria previa. No manda sobre el estado actual. |
| Superseded | Reemplazado por otra fuente explícita; no usar como guía sin verificar el reemplazo. |
| Evidencia | Documento que registra cierre, hito, reporte o baseline. |
| Operativo | Documento usado para guiar el trabajo diario. |
| Derivado | Documento que resume información de otras fuentes. |
| Candidato a simplificación | Documento útil pero con riesgo de duplicación. |

---

## 5. Encabezados documentales recomendados

### Documento vigente

```md
> Estado documental: vigente
> Fuente de verdad para: <tema>
> Última actualización: AAAA-MM-DD
```

### Documento histórico

```md
> Estado documental: histórico
> Conservado como evidencia de planificación o decisión previa.
> No usar como fuente de verdad para el estado actual.
> Fuente vigente relacionada: <archivo>
```

### Documento de evidencia

```md
> Estado documental: evidencia
> Registra un hito, baseline, decisión o aprendizaje del proyecto.
> No reemplaza a las fuentes vigentes.
```

### Documento operativo

```md
> Estado documental: operativo
> Uso principal: guía de trabajo diario / asistencia IA.
> Fuente normativa relacionada: <archivo si aplica>
```

### Documento derivado

```md
> Estado documental: derivado
> Resume información de: <fuentes>
> Ante contradicción, consultar la fuente principal.
```

---

## 6. Reglas de actualización

1. El estado resumido puede aparecer en README.md, pero el detalle debe estar en CLAUDE.md, matriz o baseline.
2. Las decisiones arquitectónicas nuevas deben registrarse como ADR antes de consolidarse en `architecture.md`.
3. Los planes iniciales no deben corregirse para parecer actuales: deben marcarse como históricos.
4. La matriz de trazabilidad debe evitar el uso ambiguo de “definido”.
5. Los documentos de evidencia no deben reescribirse salvo correcciones editoriales menores.
6. Todo documento derivado debe enlazar a su fuente principal.

---

## 7. Decisiones de Fase 2

| ID | Decisión | Resultado |
|---|---|---|
| FDV-001 | `README.md` será entrada breve. | No será fuente de estado detallado. |
| FDV-002 | `CLAUDE.md` será fuente operativa principal. | Debe mantenerse alineado con matriz y baselines. |
| FDV-003 | `.cm/baselines/` manda sobre cierres formales. | Los resúmenes deben enlazar baselines. |
| FDV-004 | `docs/traceability/matrix.md` manda sobre cobertura RF → BC → US → estado. | Requiere normalizar estados. |
| FDV-005 | Los documentos históricos se conservan y se rotulan. | No se moverán inicialmente de carpeta. |
| FDV-006 | Se usará una convención común de encabezados documentales. | Aplicación progresiva. |

---

## 8. Próximo paso

La Fase 3 crea el mapa documental mínimo en `docs/inventario/DOCUMENTATION-MAP.md`, usando esta jerarquía como base.
