# Inventario documental — AtaraxiaDive

## 1. Propósito

Este inventario corresponde a la Fase 1 del plan de adecuación documental. Su objetivo es identificar los documentos principales del repositorio, clasificarlos según su función y vigencia, y registrar inconsistencias o duplicaciones iniciales que deberán resolverse en fases posteriores.

---

## 2. Criterios de clasificación

| Categoría | Significado |
|---|---|
| Vigente | Documento que debe reflejar el estado actual del proyecto o una decisión activa. |
| Histórico | Documento conservado como memoria de planificación, análisis o decisión previa. Puede contener información superada. |
| Evidencia | Documento que registra hitos, baselines, reportes, cierres o aprendizajes del experimento. |
| Operativo | Documento usado para guiar el trabajo diario, especialmente con herramientas de IA o flujo de desarrollo. |
| Derivado | Documento que resume, conecta o reorganiza información cuya fuente principal está en otro lugar. |
| Candidato a simplificación | Documento útil, pero con riesgo de duplicación, exceso de narrativa o mezcla de propósitos. |

---

## 3. Inventario inicial

| Documento / carpeta | Clasificación | Función principal | Observación inicial |
|---|---|---|---|
| `README.md` | Vigente / candidato a simplificación | Entrada rápida al proyecto. | Debe mantenerse breve y alineado con `CLAUDE.md` y la matriz. |
| `CLAUDE.md` | Operativo / vigente / candidato a simplificación | Memoria operativa para trabajo con IA y desarrollo. | Debe dar contexto suficiente sin duplicar detalles históricos de SPs. |
| `docs/DOCUMENTATION-MAP.md` | Vigente | Mapa de navegación documental. | Fuente para saber qué leer y qué documento manda. |
| `docs/design/architecture.md` | Vigente | Arquitectura actual y objetivo técnico. | Debe verificarse contra implementación real. |
| `docs/design/context-map.md` | Vigente | Mapa de bounded contexts. | Debe mantenerse alineado con los BC reales en `src/`. |
| `docs/design/domain-model.md` | Vigente | Modelo de dominio. | Debe revisarse contra refactorings posteriores y cambios de dominio real. |
| `docs/adr/` | Vigente / evidencia | Registro de decisiones arquitectónicas. | Debe preservarse. Puede requerir nuevas ADRs si se detectan decisiones no registradas. |
| `docs/dominio/01-dominio_torneos_apnea.md` | Vigente | Descripción del dominio de torneos de apnea. | Fuente narrativa principal del dominio. |
| `docs/dominio/02-arquitectura_referencia.md` | Histórico / derivado | Arquitectura de referencia inicial. | Debe verificarse si fue superado por `docs/design/architecture.md` y ADRs. |
| `docs/dominio/03-atributos_calidad.md` | Vigente | Atributos de calidad. | Fuente de requisitos no funcionales. |
| `docs/dominio/04-estrategia_desarrollo.md` | Histórico | Planificación inicial de subproyectos e incrementos. | Contiene referencias superadas y debe leerse como planificación inicial. |
| `docs/dominio/05-requerimientos_funcionales.md` | Vigente | Catálogo base de requerimientos funcionales. | Debe coordinarse con la matriz de trazabilidad. |
| `docs/traceability/matrix.md` | Vigente / candidato a simplificación | Trazabilidad RF → BC → incremento → US → estado. | Debe distinguir planificado, especificado, implementado y validado. |
| `docs/plans/WORKFLOW-DESARROLLO.md` | Operativo / vigente | Flujo vigente de trabajo por US, incremento y subproyecto. | Fuente autoritativa del workflow. |
| `docs/plans/` | Mixto | Planes de implementación por subproyecto, incremento o ajuste. | Requiere clasificación interna: algunos planes son vigentes, otros históricos o evidencia. |
| `docs/specs/` | Vigente / evidencia | US-IEDD por subproyecto. | Fuente de especificación. Requiere revisión de estados y cobertura. |
| `docs/requirements/vision.md` | Vigente | Visión del producto. | Fuente del propósito de producto. |
| `docs/iedd/` | Vigente / metodológico | Marco conceptual IEDD. | Debe separarse de documentación estrictamente operativa del producto. |
| `docs/contexto/PLAN-EXPERIMENTO.md` | Vigente / evidencia | Marco del experimento. | Fuente del propósito metodológico. |
| `docs/contexto/ANALISIS-*.md` | Histórico / evidencia | Análisis metodológicos y técnicos. | Deben conservarse como evidencia, no como guía operativa principal. |
| `docs/contexto/HITO-*.md` | Evidencia | Aprendizajes y decisiones emergentes del experimento. | Requieren índice para navegación, no reescritura completa. |
| `.cm/baselines/` | Evidencia / vigente para cierres | Registro formal de baselines. | Fuente de verdad para cierres de SP y estado validado por baseline. |
| `.cm/changes/` | Evidencia / operativo | Solicitudes o registros de cambio. | Debe mantenerse vinculado al flujo de CM. |
| `quality/reports/` | Evidencia | Reportes de calidad. | Fuente de evidencia técnica. |
| `frontend/` | Implementación | Código frontend. | Evidencia para validar estado real del frontend y offline-first. |
| `src/` | Implementación | Código backend y bounded contexts. | Fuente primaria para contrastar arquitectura y estado implementado. |
| `tests/` | Evidencia técnica | Tests unitarios, integración y BDD. | Fuente primaria de validación. |

---

## 4. Duplicaciones iniciales detectadas

| Tema duplicado | Documentos involucrados | Riesgo |
|---|---|---|
| Estado de subproyectos | `README.md`, `CLAUDE.md`, `docs/traceability/matrix.md`, `.cm/baselines/` | Estados divergentes o desactualizados. |
| Stack y arquitectura | `README.md`, `CLAUDE.md`, `docs/design/architecture.md`, ADRs | Repetición de decisiones técnicas con distintos niveles de actualización. |
| Estrategia de desarrollo | `docs/dominio/04-estrategia_desarrollo.md`, `CLAUDE.md`, `docs/plans/WORKFLOW-DESARROLLO.md` | Mezcla de planificación histórica con workflow vigente. |
| Propósito experimental | `README.md`, `CLAUDE.md`, `docs/contexto/PLAN-EXPERIMENTO.md`, análisis metodológicos | Riesgo de sobreexplicar el experimento en documentos de entrada. |
| Trazabilidad y estado de RF | `docs/dominio/05-requerimientos_funcionales.md`, `docs/traceability/matrix.md`, specs US-IEDD | Confusión entre requerimiento, especificación, implementación y validación. |

---

## 5. Inconsistencias iniciales a resolver

| ID | Inconsistencia | Evidencia documental | Acción sugerida |
|---|---|---|---|
| INV-001 | Estado de proyecto no siempre unificado. | Diferencias históricas entre `README.md`, `CLAUDE.md` y `matrix.md`. | Definir fuente de verdad y actualizar documentos de entrada. |
| INV-002 | Documentos históricos pueden confundirse con vigentes. | Planes iniciales y documentos de dominio previos. | Mantener como históricos y aplicar convención de encabezado. |
| INV-003 | Mezcla de estados “definido”, “implementado” y “validado”. | Principalmente en `docs/traceability/matrix.md`. | Normalizar estados de madurez documental y técnica. |
| INV-004 | Arquitectura documentada puede contener elementos objetivo o candidatos. | `architecture.md` y documentos de diseño. | Separar arquitectura vigente, objetivo y candidata. |
| INV-005 | El propósito experimental se repite en varios puntos. | `README.md`, `CLAUDE.md`, `docs/contexto/PLAN-EXPERIMENTO.md`. | Centralizar explicación completa en documento de contexto y resumir en documentos de entrada. |

---

## 6. Documentos candidatos a revisión prioritaria

| Prioridad | Documento | Motivo |
|---|---|---|
| Alta | `README.md` | Entrada principal; debe ser simple y actual. |
| Alta | `CLAUDE.md` | Fuente operativa principal; debe contener contexto útil sin exceso histórico. |
| Alta | `docs/traceability/matrix.md` | Instrumento clave para distinguir cobertura y estado real. |
| Alta | `docs/design/architecture.md` | Debe reflejar lo implementado y separar objetivo/candidato. |
| Media | `docs/dominio/04-estrategia_desarrollo.md` | Histórico; conviene usarlo como modelo de marcado documental. |
| Media | `docs/plans/` | Contiene planes con distintos grados de vigencia. |
| Media | `docs/contexto/HITO-*.md` | Requiere índice para capitalización del aprendizaje. |

---

## 7. Resultado de la Fase 1

La Fase 1 deja establecido un inventario inicial y una primera lista de inconsistencias y duplicaciones. La siguiente fase define formalmente las fuentes de verdad por tema y las convenciones de encabezado documental.
