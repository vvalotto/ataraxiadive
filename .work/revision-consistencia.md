# Revisión de Consistencia y Coherencia — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Tipo** | Revisión de hito — ajuste de rumbo |
| **Fecha inicio** | 2026-03-28 |
| **Alcance temporal** | SP1 + SP2 + SP-ADJ-01 (todo hasta BL-002 / v0.3.0) |
| **Output** | Detección de gaps/inconsistencias → planificación de correcciones |
| **Estado** | ✅ Análisis completo |

---

## Scope

| Bloque | Contenido | Estado |
|--------|-----------|--------|
| **A** | Docs de producto — coherencia interna | ✅ Analizado |
| **B** | Código vs docs — coherencia implementación | ✅ Analizado |
| **C** | Artefactos de flujo (matrix, baselines, git tags) | ✅ Analizado |
| **D** | Entorno de trabajo (CLAUDE.md, MEMORY.md, skills, hooks) | ✅ Analizado |
| **E** | Artefactos del experimento (HITOs, retrospectivas BL) | ✅ Analizado |

### Niveles de análisis
- **Nivel 1** — Coherencia interna documental: documentos que se contradicen entre sí
- **Nivel 2** — Coherencia doc ↔ implementación: código que no hace lo que los documentos dicen

---

## Severidad y Estado

| Símbolo | Nivel | Criterio |
|---------|-------|----------|
| 🔴 | Crítico | Contradicción que puede llevar a decisiones incorrectas o código incorrecto |
| 🟡 | Moderado | Desincronización que genera confusión o deuda documental visible |
| 🟢 | Menor | Desactualización leve, fácil de corregir |

| Estado | Significado |
|--------|-------------|
| `DETECTADO` | Gap identificado, sin plan de corrección |
| `PLANIFICADO` | Corrección planificada, pendiente de ejecutar |
| `EN CURSO` | Corrección en ejecución |
| `RESUELTO` | Corregido y verificado |
| `ACEPTADO` | Gap conocido, se acepta conscientemente (con razón documentada) |

---

## Bloque A — Coherencia Interna Documental

### A1. Dominio → Diseño estratégico (RFs ↔ context-map ↔ domain-model)

| ID | Sev | Descripción | Artefactos afectados | Estado | Corrección planificada |
|----|-----|-------------|----------------------|--------|------------------------|
| A-01 | 🟡 | `matrix.md` no incluye US-ADJ-1.x. Un sub-sprint completo (5 US, refactors SOLID críticos) no tiene trazabilidad formal. | `docs/traceability/matrix.md` | `RESUELTO` | Sección §7 SP-ADJ-01 agregada en matrix.md |
| A-02 | 🟢 | `matrix.md`: numeración duplicada — dos secciones "## 6" (US candidatas SP1 + Cobertura Total). | `docs/traceability/matrix.md` | `RESUELTO` | Secciones renumeradas: §6 SP1, §7 ADJ, §8 Cobertura, §9..11 resto |
| A-03 | 🟢 | `domain-model.md §5`: nota dice "ES Nivel 2 de Resultados (pendiente para SP2)" — SP2 cerró sin producir ese artefacto. Outdated. | `docs/design/domain-model.md §5` | `RESUELTO` | Actualizado a "pendiente para SP3" |
| A-04 | 🟢 | `domain-model.md §4`: nota dice "ES Nivel 2 de Registro (pendiente para SP2/SP3)" — SP2 cerró. Actualizar. | `docs/design/domain-model.md §4` | `RESUELTO` | Actualizado a "pendiente para SP3" |

### A2. Diseño → Especificaciones (ADRs ↔ architecture ↔ US-IEDD specs)

Nivel 1 sin gaps adicionales. Los ADR (001-013) son consistentes con la architecture doc y las US-IEDD de SP1/SP2.
`Disciplina` como cross-BC type es un gap de implementación (ver B-01), no de documentación estratégica.

---

## Bloque B — Coherencia Doc ↔ Implementación

### B1. Invariantes / reglas de arquitectura en docs vs implementación en src/

| ID | Sev | Descripción | Archivos afectados | Estado | Corrección planificada |
|----|-----|-------------|-------------------|--------|------------------------|
| B-01 | 🔴 | `resultados/domain/` importa de `competencia/domain/`. `ranking_competencia.py` y `resultados_competencia_port.py` importan `Disciplina` y `DisciplinaDescriptor` directamente de `competencia.domain`. Viola la Regla de Oro (CLAUDE.md §6): el dominio de un BC nunca importa de otro BC. **Causa raíz:** `Disciplina` vive en `competencia/domain/` pero es un tipo cross-BC que debería estar en `shared/domain/`. | `resultados/domain/aggregates/ranking_competencia.py:13-14`  `resultados/domain/ports/resultados_competencia_port.py` | `DETECTADO` | Mover `Disciplina` (y `DisciplinaDescriptor` si aplica) a `shared/domain/value_objects/`. Actualizar todos los imports en `competencia/` y `resultados/`. US-IEDD para SP-ADJ-02 o inicio SP3. |
| B-02 | 🔴 | `resultados/application/calcular_ranking.py` importa de `competencia/infrastructure/`. Importa `DisciplinaDescriptorAdapter` desde `competencia.infrastructure.repositories`. Double violation: (1) cross-BC import, (2) application layer → infrastructure de otro BC. | `resultados/application/commands/calcular_ranking.py:10-13` | `DETECTADO` | Resolver B-01 primero. Una vez `Disciplina` esté en `shared/`, `DisciplinaDescriptorAdapter` puede permanecer en `competencia/infra/` y ser inyectado como puerto, sin importarlo directamente. |
| B-03 | 🟡 | `competencia/api/router.py` importa de `resultados/application/` y `resultados/infrastructure/`. El composition root de la política P-08 (CalcularRanking) vive en el router de un BC. El lugar correcto es `app.py` (el ensamblador central). | `competencia/api/router.py:70-75` | `DETECTADO` | Mover el wiring de `CalcularRankingHandler` a `src/app.py` o a un módulo de composition root. Requiere US-IEDD propia (refactor de dependencias). |
| B-04 | 🟡 | `resultados/api/router.py` importa `SQLiteEventStore` directamente de `competencia/infrastructure/event_store/`. API layer de Resultados importando infra concreta de Competencia. | `resultados/api/router.py:12` | `DETECTADO` | Al resolver B-01/B-03, este import debería desaparecer (el store de Competencia se inyecta, no se importa). |
| B-05 | 🔴 | DIP violation persiste en `competencia/api/router.py`. `EventStoreDep = Annotated[SQLiteEventStore, ...]` (línea 147) sigue usando el tipo concreto en lugar del puerto. `get_event_store()` (línea 115) retorna `SQLiteEventStore`, no `EventStorePort`. **US-ADJ-1.4 está marcada ✅ Done en BL-002 pero el código contradice ese estado.** Regresión o spec no ejecutada correctamente. | `competencia/api/router.py:115, 147` | `DETECTADO` | Verificar qué se hizo en US-ADJ-1.4. Completar la corrección: `get_event_store() -> EventStorePort` + `EventStoreDep = Annotated[EventStorePort, ...]`. |

### B2. Tests vs criterios de aceptación

Sin gaps críticos detectados. Los 481 tests de BL-002 pasan. El análisis de cobertura (98%) está alineado con los criterios de las US-IEDD de SP1/SP2.

### B3. Estructura de BCs en código vs diseño estratégico

Los 5 BCs scaffoldeados (identidad, notificaciones, registro, torneo + resultados parcial) son coherentes con el plan SP3/SP4. Los gaps B-01..B-04 son el único desvío real.

---

## Bloque C — Artefactos de Flujo

### C1. Trazabilidad (matrix.md) vs US-IEDD specs vs código

| ID | Sev | Descripción | Sección matrix.md | Estado | Corrección planificada |
|----|-----|-------------|-------------------|--------|------------------------|
| C-01 | 🟡 | SP-ADJ-01 no tiene ninguna entrada en matrix.md. Las 5 US-ADJ-1.x existen en `docs/specs/sp-adj-01/` pero no tienen fila en la matriz. | Ninguna — falta la sección | `RESUELTO` | Sección §7 agregada. |
| C-02 | 🟢 | matrix.md tiene numeración de secciones duplicada (dos "## 6"). | `matrix.md §6 (duplicado)` | `RESUELTO` | Secciones renumeradas. |

### C2. Baselines y git tags

| ID | Sev | Descripción | Artefacto | Estado | Corrección planificada |
|----|-----|-------------|-----------|--------|------------------------|
| C-03 | 🔴 | **Inconsistencia de tags:** `BL-002.md` dice `Git tag: v0.2.0` pero en git `v0.2.0` apunta a BL-001/SP1 (commit `9402d73`, "SP1 — La Performance"). BL-002 está efectivamente taggeado como `v0.3.0`. El commit de cierre de BL-002 incluso dice "tag v0.2.0" en su mensaje, lo que agrava la confusión. El esquema real de tags es: v0.0.0=BL-000, v0.1.0=Fase-0, **v0.2.0=BL-001**, **v0.3.0=BL-002**. | `BL-002.md`, `competencia/api/router.py` commit msg, `CLAUDE.md §10` | `RESUELTO` | BL-002.md actualizado: `Git tag: v0.3.0`. CLAUDE.md §9 tabla actualizada. |
| C-04 | 🟡 | `BL-001.md` tiene `Fecha cierre: — (en curso)` y `Git tag cierre: — (se asigna v0.2.0 al cerrar)`. SP1 cerró el 2026-03-24 con tag v0.2.0. El campo de cierre nunca se actualizó. | `.cm/baselines/BL-001-sp1-la-performance.md` | `RESUELTO` | BL-001.md actualizado: fecha cierre 2026-03-24, tag v0.2.0. |

---

## Bloque D — Entorno de Trabajo

### D1. CLAUDE.md vs estado actual del proyecto

| ID | Sev | Descripción | Sección CLAUDE.md | Estado | Corrección planificada |
|----|-----|-------------|-------------------|--------|------------------------|
| D-01 | 🔴 | **§14 "Estado Actual" completamente desactualizado.** Dice "Próximo paso: crear branch feature/US-1.1 desde develop → implementar Inc 1.1" — ese era el próximo paso *antes de SP1*. El estado real es: BL-002/v0.3.0 cerrado, SP2+SP-ADJ-01 completos, SP3 es el siguiente. La tabla de artefactos no refleja nada de SP1 ni SP2. | `CLAUDE.md §14` | `RESUELTO` | §14 reescrito: SP1, SP2, SP-ADJ-01, SP-ADJ-02 en curso, próximo paso SP3. |
| D-02 | 🟡 | **§9 "Jerarquía de Trabajo"** no refleja el patrón SP-ADJ emergente. La tabla de baselines solo lista SP1-SP5 y sus BLs, pero SP-ADJ-01 demostró que existe un nivel intermedio de sub-sprint de ajuste técnico. Sin lugar formal en la jerarquía. | `CLAUDE.md §9` | `RESUELTO` | §9 actualizado: jerarquía con SP-ADJ, tabla con tags y estados reales. |
| D-03 | 🟡 | **§5 estructura del repositorio** no menciona que los HITOs viven en `docs/contexto/`. Un usuario nuevo no sabe dónde buscarlos. La tabla dice `docs/contexto/ ← Documentos fundacionales del experimento ✅` pero no diferencia entre docs fundacionales e HITOs. | `CLAUDE.md §5` | `RESUELTO` | §5 actualizado: `docs/contexto/ ← Documentos fundacionales + HITO-N-*.md`. |

### D2. MEMORY.md, skills, hooks, pyproject.toml

| ID | Sev | Descripción | Artefacto | Estado | Corrección planificada |
|----|-----|-------------|-----------|--------|------------------------|
| D-04 | 🟡 | `memory/project_solid_deuda_sp2.md` documenta la DIP en `router.py` como deuda pendiente de SP1→SP2. BL-002 marca US-ADJ-1.4 como ✅ Done. El código actual contradice ambos (la corrección no se aplicó — ver B-05). La memoria está obsoleta en su estado pero correcta en identificar el problema. | `memory/project_solid_deuda_sp2.md` | `DETECTADO` | Una vez resuelto B-05, actualizar o eliminar esta entrada de memoria. Si persiste como deuda, mantenerla vigente. |

---

## Bloque E — Artefactos del Experimento

### E1. HITOs y retrospectivas BL vs hipótesis del experimento

| ID | Sev | Descripción | HITO/BL afectado | Estado | Corrección planificada |
|----|-----|-------------|------------------|--------|------------------------|
| E-01 | 🟢 | `BL-001.md` describe HITO-8 como "artefactos físicos por fase eliminaron el problema de fases fantasmas". El archivo es `HITO-8-ARTEFACTOS-FALTANTES-COMPRESION-CONTEXTO.md` — el título sugiere una problemática diferente (compresión de contexto). Descripción inconsistente. | `BL-001.md`, `HITO-8` | `DETECTADO` | Revisar HITO-8 y alinear su descripción en BL-001 con el contenido real del artefacto. |
| E-02 | 🟢 | Los 13 HITOs viven en `docs/contexto/` pero no hay un índice centralizado ni referencia cruzada entre HITOs y baselines (salvo los mencionados en cada BL). Para el paper IEDD, la falta de índice dificulta la navegación del material. | `docs/contexto/`, `BL-001.md`, `BL-002.md` | `RESUELTO` | `docs/contexto/INDICE-HITOS.md` creado con los 13 HITOs, SP, hipótesis y distribución. |

---

## Resumen Ejecutivo

| Bloque | 🔴 Críticos | 🟡 Moderados | 🟢 Menores | Total |
|--------|:-----------:|:------------:|:----------:|:-----:|
| A — Docs producto | 0 | 1 | 3 | 4 |
| B — Código vs docs | 3 | 2 | 0 | 5 |
| C — Flujo | 1 | 2 | 1 | 4 |
| D — Entorno | 1 | 2 | 1 | 4 |
| E — Experimento | 0 | 0 | 2 | 2 |
| **Total** | **5** | **7** | **7** | **19** |

### Los 5 críticos — impacto en SP3

| ID | Impacto directo en SP3 |
|----|------------------------|
| B-01 | `Disciplina` cross-BC bloqueará el primer BC CRUD (Torneo) si también necesita el tipo |
| B-02 | Derivado de B-01 — se resuelve junto |
| B-05 | DIP violation activa en el router — DesignReviewer puede bloquear PRs de SP3 si el umbral sube |
| C-03 | Tag v0.3.0 de BL-002 no documentado — confusión en el historial antes de empezar SP3 |
| D-01 | CLAUDE.md §14 desactualizado — sesiones nuevas arrancan con contexto incorrecto |

---

## Plan de Correcciones

| Prioridad | ID | Descripción corta | Esfuerzo | Momento sugerido |
|-----------|----|--------------------|----------|-----------------|
| 1 | D-01 | Actualizar CLAUDE.md §14 | 15 min | **Inmediato** — esta sesión |
| 2 | C-03 | Corregir tag en BL-002.md (v0.2.0 → v0.3.0) | 5 min | **Inmediato** — esta sesión |
| 3 | C-04 | Completar fecha cierre BL-001.md | 5 min | **Inmediato** — esta sesión |
| 4 | B-05 | Verificar y completar DIP fix en router.py | 30 min | **Inmediato** — antes de primer PR SP3 |
| 5 | B-01 | Mover `Disciplina` a `shared/domain/` | 1-2h | **Antes de INC-3.1** — BC Torneo necesitará `Disciplina` |
| 6 | B-02 | Derivado de B-01 — se resuelve junto | — | Junto con B-01 |
| 7 | B-03 | Mover composition root P-08 a `app.py` | 1h | US-IEDD en SP-ADJ-02 o inicio SP3 |
| 8 | B-04 | Derivado de B-03 | — | Junto con B-03 |
| 9 | A-01, C-01 | Agregar SP-ADJ-01 en matrix.md | 30 min | Antes de iniciar SP3 |
| 10 | A-02, C-02 | Renumerar secciones matrix.md | 10 min | Junto con anterior |
| 11 | D-02 | Agregar patrón SP-ADJ en CLAUDE.md §9 | 10 min | Junto con D-01 |
| 12 | D-03 | Mencionar HITOs en CLAUDE.md §5 | 5 min | Junto con D-01 |
| 13 | D-04 | Actualizar memory/ post-resolución B-05 | 5 min | Tras resolver B-05 |
| 14 | A-03, A-04 | Actualizar notas domain-model.md | 10 min | Antes de SP3 |
| 15 | E-02 | Crear INDICE-HITOS.md | 20 min | Antes de SP3 |
| 16 | E-01 | Alinear descripción HITO-8 en BL-001 | 10 min | Baja prioridad |

---

*Creado: 2026-03-28 — Revisión de hito BL-002*
*Análisis ejecutado por: Claude Code + Victor Valotto*
