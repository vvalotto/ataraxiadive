# Plan de adecuación documental — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: estrategia de adecuación documental
> Última actualización: 2026-05-17

## 1. Propósito del plan

Este plan propone una estrategia de depuración documental para AtaraxiaDive, orientada a resolver inconsistencias entre lo documentado y lo implementado, reducir duplicaciones, aclarar el estado real del proyecto y presentar la información de la forma más simple posible.

La intención no es reescribir toda la documentación. El objetivo es ordenar el ecosistema documental para que cada documento tenga una función clara, una autoridad definida y un nivel de detalle adecuado.

---

## 2. Diagnóstico de partida

El proyecto cuenta con documentación abundante y valiosa, pero actualmente conviven varios tipos de documentos con distintos grados de vigencia:

1. Documentos vivos, que deberían reflejar el estado actual del producto.
2. Documentos históricos, que explican decisiones o planes iniciales ya modificados.
3. Documentos de evidencia, que registran baselines, hitos, decisiones y aprendizajes del experimento.
4. Documentos operativos, pensados para guiar a Claude Code, Claude Cowork o al desarrollador durante el trabajo diario.

El principal riesgo no es la falta de documentación, sino la superposición de documentos que intentan explicar lo mismo desde momentos distintos del proyecto.

### 2.1 Problemas detectados inicialmente

| Problema | Descripción | Impacto |
|---|---|---|
| Estados divergentes del proyecto | Algunos documentos presentan estados diferentes para los mismos subproyectos o incrementos. | Confunde la lectura inicial y debilita la confianza en la documentación. |
| Duplicación del estado | El avance del proyecto aparece en README, CLAUDE.md, matriz de trazabilidad, planes y baselines. | Cada actualización exige tocar varios lugares; aumenta el riesgo de inconsistencia. |
| Mezcla de plan, especificación e implementación | En algunos casos no queda claro si algo está planificado, especificado, implementado o validado. | Se puede confundir intención con evidencia real. |
| Documentos históricos con lenguaje normativo | Algunos planes iniciales conservan definiciones ya superadas, aunque sean útiles como memoria. | Pueden ser leídos como vigentes si no están rotulados con claridad. |
| Exceso de narrativa en documentos técnicos | Algunos documentos explican más contexto del necesario para su función específica. | Dificulta encontrar rápidamente la información operativa. |
| Ausencia de mapa documental explícito | No había una guía breve que indique qué documento leer para cada propósito. | El lector debe reconstruir la arquitectura documental por ensayo y error. |

---

## 3. Principios de adecuación

### 3.1 Una fuente de verdad por tema

Cada tipo de información debe tener un documento principal responsable. Otros documentos pueden enlazarlo o resumirlo, pero no duplicarlo en detalle.

### 3.2 Separar lo vigente de lo histórico

Los documentos históricos no deben borrarse ni reescribirse como si fueran actuales. Deben conservarse como evidencia del camino recorrido, pero rotulados con claridad.

### 3.3 Distinguir estados de madurez

Toda funcionalidad, requerimiento, incremento o US relevante debería usar una taxonomía simple de estados:

| Estado | Significado |
|---|---|
| Planificado | Existe intención de abordarlo. |
| Especificado | Tiene US, criterios o definición suficientemente clara. |
| Implementado | Existe código integrado. |
| Validado | Tiene tests, UAT, baseline o evidencia de validación. |
| Diferido | Se decidió postergarlo. |
| Fuera de alcance | No forma parte del alcance actual. |

### 3.4 Mantener simple la entrada al proyecto

El README debe ser breve, claro y orientador. No debe explicar todo el experimento ni repetir la historia completa del desarrollo.

### 3.5 Conservar evidencia sin convertirla en guía principal

HITOs, baselines, ADRs y reportes son valiosos, pero no deberían competir con los documentos vivos como explicación principal del estado actual.

### 3.6 Corregir contra la implementación real

Cuando haya contradicción entre documentación y código, debe revisarse el código como evidencia primaria. Si el código contradice una decisión documentada, se debe decidir si se actualiza la documentación, se crea una nueva ADR, o se registra una desviación.

---

## 4. Jerarquía documental propuesta

| Tema | Fuente principal propuesta | Rol |
|---|---|---|
| Presentación breve del proyecto | `README.md` | Entrada rápida al proyecto. |
| Estado operativo actual | `CLAUDE.md` | Memoria operativa para trabajo con IA y desarrollo. |
| Mapa de documentación | `docs/DOCUMENTATION-MAP.md` | Guía de lectura y autoridad documental. |
| Workflow de desarrollo | `docs/plans/WORKFLOW-DESARROLLO.md` | Procedimiento vigente para trabajar por US, incremento y baseline. |
| Arquitectura actual | `docs/design/architecture.md` | Vista técnica vigente del sistema. |
| Decisiones arquitectónicas | `docs/adr/` | Registro de decisiones, contexto y trade-offs. |
| Dominio del problema | `docs/dominio/01-dominio_torneos_apnea.md` | Explicación del dominio de torneos de apnea. |
| Requerimientos funcionales | `docs/dominio/05-requerimientos_funcionales.md` | Catálogo base de RF. |
| Trazabilidad | `docs/traceability/matrix.md` | Relación RF → BC → incremento → US → estado. |
| Evidencia de cierre | `.cm/baselines/` | Registro formal de baselines cerradas. |
| Aprendizajes del experimento | `docs/contexto/HITO-*.md` | Evidencia metodológica y lecciones aprendidas. |
| Planes iniciales superados | Documentos rotulados como históricos | Memoria del diseño original, no fuente vigente. |

---

## 5. Alcance de la adecuación

### 5.1 Incluido

- Clasificación de documentos por tipo y vigencia.
- Actualización de documentos de entrada.
- Resolución de inconsistencias de estado.
- Revisión de la matriz de trazabilidad.
- Revisión de arquitectura contra implementación real.
- Marcado explícito de documentos históricos.
- Creación de un mapa documental.
- Reducción de duplicaciones innecesarias.
- Definición de reglas editoriales para futuras actualizaciones.
- Resolución de ADRs supersedidos y numeración duplicada.
- Clasificación y limpieza de `.work/` y `memory/` operativa.

### 5.2 No incluido en esta primera etapa

- Reescribir todos los HITOs.
- Reestructurar por completo la carpeta `docs/`.
- Cambiar decisiones de arquitectura.
- Refactorizar código.
- Eliminar documentación histórica valiosa.
- Convertir todos los documentos a un estilo homogéneo perfecto.

---

## 6. Fases del plan

| Fase | Nombre | Resultado esperado | Estado |
|---|---|---|---|
| 1 | Inventario y clasificación documental | Tabla de inventario inicial y lista de inconsistencias. | ✅ Completada 2026-05-02 |
| 2 | Definición de fuentes de verdad | Jerarquía documental y reglas de autoridad. | ✅ Completada 2026-05-02 |
| 3 | Mapa documental mínimo | `docs/DOCUMENTATION-MAP.md`. | ✅ Completada 2026-04-27 |
| 4 | Limpieza de documentos de entrada | README y CLAUDE.md alineados y simplificados. | ⏳ Parcial (50%) — README desactualizado |
| 5 | Auditoría de estado y trazabilidad | Matriz con estados claros y evidencia mínima. | ⏳ Parcial (60%) — RF-IN-05/06 pendientes |
| 6 | Auditoría arquitectura contra implementación | Arquitectura documentada alineada con el sistema real. | ⏳ Parcial (40%) — architecture.md desfasado (Cloud Run vs Fly.io) |
| 7 | Marcado de documentos históricos | Documentos históricos rotulados y enlazados. | ⏳ Parcial (20%) — encabezados no aplicados |
| 8 | Índice de evidencia experimental | HITOs y baselines más navegables. | ⏳ Parcial (70%) — HITO-30/31/32 sin indexar |
| 9 | Limpieza operativa | `.work/`, `memory/` y ADRs saneados. | ⏳ Pendiente |

---

## 7. Backlog de adecuación

| Prioridad | Tarea | Archivo(s) | Estado |
|---|---|---|---|
| ✅ | Crear inventario documental inicial | `docs/inventario/INVENTARIO-DOCUMENTAL.md` | Completado 2026-05-02 |
| ✅ | Crear fuentes de verdad documental | `docs/inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md` | Completado 2026-05-02 |
| ✅ | Crear mapa documental | `docs/inventario/DOCUMENTATION-MAP.md` | Completado 2026-04-27 |
| Alta | Actualizar README | `README.md` | SP6 aparece como "⏳ En definición" — debe marcarse ✅ y agregar SP7 |
| Alta | Corregir inconsistencia arquitectura producción | `docs/design/architecture.md` | Reemplazar Cloud Run por Fly.io; referenciar ADR-021 |
| Alta | Marcar ADR-010 como supersedido | `docs/adr/ADR-010-*.md` | Agregar encabezado "Supersedido por ADR-021" |
| Alta | Resolver ADR-015 duplicado | `docs/adr/ADR-015-*.md` (dos archivos) | Renombrar uno a ADR-022 |
| Alta | Actualizar matrix.md §RF-IN-05/06 | `docs/traceability/matrix.md` | Cambiar "⏳ Deuda técnica" → "✅ Implementado (SP-ADJ-10.3)" |
| Media | Marcar documentos históricos con encabezado | `docs/dominio/02, 04`, `docs/contexto/ANALISIS-*.md` | Aplicar convención definida en Fase 2 |
| Media | Actualizar INDICE-HITOS con HITO-30/31/32 | `docs/contexto/INDICE-HITOS.md` | Cubrir aprendizajes de SP6 |
| Media | Clasificar y limpiar `.work/` | `.work/` (38 archivos) | Archivar evidencia útil, eliminar temporales, mover `formacion/` fuera del alcance de producto |
| Media | Limpiar `memory/` obsoleto | `memory/project_faz_faas_pendiente.md`, `memory/project_sp_adj_05_pendiente.md` | Eliminar entradas de tracking ya completadas |
| Baja | Crear índice de especificaciones | `docs/specs/README.md` | Tabla navegable de US-IEDD por SP/INC |
| Baja | Crear índice de arquitectura BC | `docs/architecture/INDEX.md` | Tabla BC → archivo → responsabilidades |
| Baja | Homogeneizar encabezados documentales | varios | Convención editorial consistente en toda la documentación |

---

## 8. Orden recomendado de ejecución

### Iteración 1 — Entrada y estado ✅ Completada

1. ✅ Crear inventario documental.
2. ✅ Crear fuentes de verdad documental.
3. ✅ Crear mapa documental.
4. ✅ CLAUDE.md actualizado; README pendiente → ver Iteración 2.

### Iteración 2 — Correcciones críticas ⏳ En curso

1. Actualizar README: tabla de SPs, referencia a SP7, enlace a CLAUDE.md como fuente operativa.
2. Actualizar `docs/design/architecture.md`: producción = Fly.io, referenciar ADR-021.
3. Marcar `ADR-010` como supersedido por ADR-021.
4. Renombrar ADR-015 duplicado a ADR-022.
5. Corregir `matrix.md` §RF-IN-05/06: cambiar estado a implementado.

### Iteración 3 — Trazabilidad

1. Revisar `docs/traceability/matrix.md` completo.
2. Normalizar estados (Planificado / Especificado / Implementado / Validado / Diferido).
3. Verificar cobertura SP7 (INC-7.1, INC-7.2).
4. Resolver inconsistencias restantes de RFs.

### Iteración 4 — Arquitectura

1. Revisar estructura real de `src/`.
2. Revisar estructura real de `frontend/`.
3. Verificar `architecture.md` y `context-map.md` contra implementación.
4. Separar arquitectura vigente de arquitectura objetivo.
5. Crear ADR si aparece una decisión no documentada.

### Iteración 5 — Historia y evidencia

1. Marcar documentos históricos con encabezado de Fase 2.
2. Actualizar `INDICE-HITOS.md` con HITO-30/31/32.
3. Revisar baselines como evidencia de cierre.
4. Enlazar fuentes vigentes desde documentos históricos.

### Iteración 6 — Limpieza operativa

1. Clasificar `.work/`: archivar evidencia útil en `docs/contexto/`, eliminar temporales, mover `formacion/` fuera del repo de producto.
2. Eliminar entradas obsoletas de `memory/`.
3. Crear índices navegables para `docs/specs/` y `docs/architecture/`.

---

## 9. Criterios de aceptación

El plan se considera cumplido cuando:

1. ✅ Existe un mapa documental claro.
2. README y CLAUDE.md no se contradicen.
3. La matriz de trazabilidad distingue estado documental, implementación y validación.
4. Los documentos históricos están rotulados con la convención de encabezado definida en Fase 2.
5. La arquitectura documentada coincide con la implementación real (Fly.io, no Cloud Run).
6. ✅ Las fuentes de verdad están definidas.
7. Las duplicaciones críticas de estado fueron eliminadas o reducidas.
8. Un lector nuevo puede entender el proyecto sin recorrer documentos en círculo.
9. `.work/` no contiene archivos temporales ni material fuera del scope del producto.
10. Los ADRs supersedidos están marcados y la numeración no tiene duplicados.

---

## 10. Síntesis ejecutiva

La adecuación documental de AtaraxiaDive debe enfocarse en ordenar, no en producir más texto.

La clave es:

- una fuente de verdad por tema,
- documentos históricos claramente marcados,
- README breve,
- CLAUDE.md operativo,
- matriz honesta sobre estados,
- arquitectura alineada con código,
- HITOs preservados como evidencia del experimento.
