# Auditoría docs/ — Post-SP5

> Fecha: 2026-05-01 · Branch: docs/ajuste-documental-post-sp5
> Alcance: todos los `.md` en `docs/` excepto `docs/reports/` y `docs/plans/` (artefactos de implementación)
> ~100 documentos analizados

---

## Resumen Ejecutivo

| Categoría | Cantidad |
|-----------|:--------:|
| CRÍTICO — acción requerida | 6 |
| MODERADO — mejora recomendada | 8 |
| OK — sin cambios necesarios | 25+ |

---

## Hallazgos CRÍTICOS

### C-01 · `docs/design/architecture.md` — Supersedido + ubicación errónea

| Campo | Valor |
|-------|-------|
| **Motivo** | Desactualización técnica + duplicidad |
| **Estado del archivo** | Marcado como "Histórico / superseded" en su propio header |
| **Problema** | El documento describe la arquitectura C4 de Semana 0. Coexiste con `docs/architecture/` (12 archivos vigentes). Su presencia en `docs/design/` confunde la navegación. |
| **Referencia duplicada** | `docs/architecture/01-system-context.md`, `02-container-view.md`, `03-bounded-contexts.md` |
| **Acción recomendada** | Eliminar o mover a `docs/contexto/` como artefacto histórico. Agregar nota en `docs/design/README.md`. |

---

### C-02 · `docs/dominio/02-arquitectura_referencia.md` — Propuesta inicial supersedida

| Campo | Valor |
|-------|-------|
| **Motivo** | Desactualización técnica |
| **Estado del archivo** | Ya tiene nota de estado histórico, pero no está cross-referenciado con ADRs que lo reemplazan |
| **Problema** | Describe una arquitectura con PostgreSQL, Docker multi-contenedor, y sin distinción por BC — todo reemplazado por ADR-007, ADR-009, ADR-010. |
| **Acción recomendada** | Completar la nota histórica con lista explícita de ADRs que reemplazaron cada sección. |

---

### C-03 · Límite ambiguo `docs/design/` vs `docs/architecture/`

| Campo | Valor |
|-------|-------|
| **Motivo** | Duplicidad estructural |
| **Problema** | `docs/design/` contiene: Event Storming, Context Map, Domain Model, architecture.md, offline-first.md — algunos vigentes, algunos históricos. `docs/architecture/` tiene el contenido vigente. Sin política clara de qué va en cada carpeta. |
| **Documentos en conflicto** | `docs/design/context-map.md` (vigente) vs `docs/architecture/20-context-map-integrations.md` (también vigente, más detallado) |
| **Acción recomendada** | Definir en `docs/design/README.md`: "artefactos de diseño y decisiones estratégicas DDD" vs `docs/architecture/`: "descripción viva de la arquitectura en ejecución". |

---

### C-04 · `docs/design/ux/wireframes-*.md` — Posiblemente desactualizados vs SP5

| Campo | Valor |
|-------|-------|
| **Motivo** | Desactualización funcional (riesgo) |
| **Archivos** | `wireframes-organizador.md`, `wireframes-atleta.md`, `wireframes-juez.md`, `wireframes-registro-roles.md`, `wireframes-setup-torneo.md` |
| **Problema** | Todos fechados en SP4 (2026-04-05/08). SP5 implementó SP-ADJ-09 (refactoring UX organizador completo: shell dark, routing, home, dashboard) y portal atleta completo (INC-5.5..5.7). Los wireframes pueden no reflejar la UX actual. |
| **Acción recomendada** | Revisar sección por sección contra la implementación. Marcar secciones desactualizadas o actualizar al estado SP5. |

---

### C-05 · `docs/iedd/01`, `02`, `03` — Solapamiento entre los tres archivos

| Campo | Valor |
|-------|-------|
| **Motivo** | Redundancia + documentación excesiva |
| **Archivos** | `01-Ingenieria_Especificaciones_DDD_IA.md`, `02-Marco_Conceptual_5_Capas.md`, `03-Diagrama_Conceptual.md` |
| **Problema** | Los tres tratan el mismo marco conceptual IEDD con distinto nivel de detalle. `03` es el diagrama textual de lo que `02` describe en prosa. `01` repite el planteo del problema que `02` también introduce. Audiencia y propósito solapados. |
| **Acción recomendada** | Consolidar `01` + `02` + `03` en un único `01-Marco-IEDD.md`. `04-Hipotesis-Ensayo` queda separado (propósito distinto: hipótesis del experimento). |

---

### C-06 · `docs/contexto/` — 29 archivos HITO sin política de archivo

| Campo | Valor |
|-------|-------|
| **Motivo** | Documentación excesiva + riesgo de confusión operativa |
| **Archivos** | HITO-1 a HITO-29, INDICE-HITOS.md, PLAN-EXPERIMENTO.md, ARTEFACTOS-WORKFLOW.md, ANALISIS-*.md, DECISION-*.md, IMPLEMENT-US-DISCREPANCIAS.md |
| **Problema** | 29 HITOs más archivos de análisis en la misma carpeta, sin separación entre "vigente" y "completado". Un desarrollador nuevo no sabe qué leer primero. `CLAUDE.md` ya referencia lo operativo. |
| **Nota** | Por diseño del experimento, los HITOs son artefactos valiosos para el paper/libro — no se deben eliminar. El problema es la ausencia de una política de navegación. |
| **Acción recomendada** | Agregar/actualizar `docs/contexto/README.md` con: (a) propósito de la carpeta, (b) índice por audiencia — "si sos nuevo, empezá por X", (c) señalar que INDICE-HITOS.md es la puerta de entrada. |

---

## Hallazgos MODERADOS

### M-01 · `docs/design/auditoria.md` — Estado desconocido

| Motivo | Desactualización funcional (por verificar) |
|--------|------------------------------------------|
| Problema | No fue auditado en detalle. Nombre genérico, sin header de estado. Probablemente describe el modelo de auditoría de BC Competencia (ADR-018). Si está vigente, debería tener nota de estado; si es histórico, marcarlo. |
| Acción | Verificar contenido y agregar header de estado. |

---

### M-02 · `docs/design/context-map.md` ↔ `docs/architecture/20-context-map-integrations.md` — Dos context maps vigentes

| Motivo | Duplicidad moderada |
|--------|---------------------|
| Problema | `docs/design/context-map.md` (v1.2, nivel estratégico DDD) y `docs/architecture/20-context-map-integrations.md` (nivel operativo, integraciones). Ambos vigentes pero con distinto propósito. Sin cross-reference entre ellos. |
| Acción | Agregar `Ver también:` en cada uno apuntando al otro. |

---

### M-03 · `docs/design/offline-first.md` ↔ `docs/architecture/50-offline-sync.md` — Sin cross-link

| Motivo | Duplicidad moderada |
|--------|---------------------|
| Problema | `docs/design/offline-first.md` es el diseño conceptual; `docs/architecture/50-offline-sync.md` es la especificación técnica. Mismo tema, distinto nivel. ADR-003 no apunta a ninguno de los dos. |
| Acción | Cross-link entre los tres: design/offline-first ↔ architecture/50-offline-sync ↔ ADR-003. |

---

### M-04 · `docs/design/estrategia-desarrollo-bc.md` — Relación con `docs/dominio/04` no declarada

| Motivo | Duplicidad / ambigüedad |
|--------|------------------------|
| Problema | Ambos documentos tratan la estrategia de desarrollo por BC. `dominio/04` ya tiene nota histórica. `design/estrategia-desarrollo-bc.md` no especifica si está vigente o supersedido. |
| Acción | Verificar vigencia y agregar header de estado. |

---

### M-05 · `docs/design/ux/mejoras-ux.md` — Registro de pendientes sin estado de cierre

| Motivo | Desactualización funcional |
|--------|---------------------------|
| Problema | Contiene `MUX-01` y otros ítems de mejora UX. Sin indicación de cuáles fueron resueltos en SP4/SP5. Puede llevar a re-trabajo o confusión con defectos de SP6. |
| Acción | Revisar cada ítem contra implementación SP5. Marcar como Resuelto / Pendiente / En SP6. |

---

### M-06 · `docs/design/ux/flujos-por-rol.md` — Fechado en SP4, portal atleta no incluido

| Motivo | Desactualización funcional |
|--------|---------------------------|
| Problema | Describe flujos de Juez y Organizador (SP4). Portal del Atleta implementado en INC-5.5..5.7 no está documentado. |
| Acción | Agregar sección "Rol: Atleta" con flujos SP5. |

---

### M-07 · `docs/dominio/05-requerimientos_funcionales.md` — Sin indicación de trazabilidad hacia matrix.md

| Motivo | Documentación incompleta |
|--------|--------------------------|
| Problema | Es el documento de origen de los RF. `docs/traceability/matrix.md` traza RF→US, pero `05-requerimientos_funcionales.md` no referencia la matrix. Navegación unidireccional. |
| Acción | Agregar al pie: "Trazabilidad RF→US: `docs/traceability/matrix.md`". |

---

### M-08 · `docs/requirements/vision.md` — Ubicación aislada, sin referencias entrantes

| Motivo | Estructura documental |
|--------|----------------------|
| Problema | Único archivo en `docs/requirements/`. No es referenciado desde CLAUDE.md, README, ni docs/dominio/. Puede estar duplicando el propósito de `docs/dominio/01-dominio_torneos_apnea.md`. |
| Acción | Verificar relación con `docs/dominio/01`. Si es complementario, agregar cross-link desde CLAUDE.md o README. Si es redundante, consolidar. |

---

## Documentos en buen estado (sin cambios)

| Documento | Estado |
|-----------|--------|
| `docs/architecture/` (todos — 12 archivos) | ✅ Vigentes, bien estructurados, STATUS.md actualizado |
| `docs/adr/ADR-001..019` | ✅ Vigentes, inmutables por convención |
| `docs/design/event-storming-big-picture.md` | ✅ Artefacto de diseño, histórico por naturaleza |
| `docs/design/event-storming-competencia.md` | ✅ Ídem |
| `docs/design/domain-model.md` | ✅ Modelo DDD vigente |
| `docs/design/notificaciones.md` | ✅ Diseño vigente BC Notificaciones |
| `docs/iedd/04-Hipotesis-Ensayo.md` | ✅ Hipótesis del experimento, vigente |
| `docs/iedd/US-IEDD-template.md` | ✅ Template operativo |
| `docs/contexto/HITO-1..29` | ✅ Artefactos del experimento — no modificar |
| `docs/contexto/INDICE-HITOS.md` | ✅ Vigente como índice |
| `docs/contexto/PLAN-EXPERIMENTO.md` | ✅ Ya tiene nota histórica |
| `docs/dominio/01-dominio_torneos_apnea.md` | ✅ Dominio del problema, estable |
| `docs/dominio/03-atributos_calidad.md` | ✅ Atributos de calidad, estable |
| `docs/dominio/06-brechas-reglamento.md` | ✅ Vigente |
| `docs/traceability/matrix.md` | ✅ Actualizado v1.30 en esta sesión |
| `docs/WBS-ATARAXIADIVE.md` | ✅ Actualizado en esta sesión |
| `docs/CANONICAL-SOURCES.md` | ✅ Vigente |
| `docs/specs/` (todos) | ✅ Artefactos de especificación — no modificar |

---

## Plan de Acción Sugerido para SP6

| Prioridad | Hallazgo | Esfuerzo estimado |
|-----------|----------|:-----------------:|
| ALTA | C-03 Política docs/design/ vs architecture/ — `docs/design/README.md` | S |
| ALTA | C-06 `docs/contexto/README.md` — política de navegación | S |
| ALTA | M-02 Cross-link context-map ↔ architecture/20 | XS |
| ALTA | M-03 Cross-link offline-first ↔ architecture/50 ↔ ADR-003 | XS |
| MEDIA | C-01 Mover `docs/design/architecture.md` a `docs/contexto/` | S |
| MEDIA | C-04 Revisar wireframes UX vs SP5 | M |
| MEDIA | C-05 Consolidar docs/iedd/01+02+03 | S |
| MEDIA | M-01 Verificar y marcar `docs/design/auditoria.md` | XS |
| MEDIA | M-04 Verificar `docs/design/estrategia-desarrollo-bc.md` | XS |
| MEDIA | M-05 Actualizar `mejoras-ux.md` con estado SP5 | S |
| MEDIA | M-06 Agregar flujos Atleta en `flujos-por-rol.md` | S |
| BAJA | C-02 Completar nota en `dominio/02` con lista ADRs | XS |
| BAJA | M-07 Cross-link `dominio/05` → `matrix.md` | XS |
| BAJA | M-08 Verificar `requirements/vision.md` vs `dominio/01` | XS |

> XS = minutos · S = < 1h · M = 1-2h

---

*Generado: 2026-05-01 · Auditor: Claude Code + Victor Valotto*
