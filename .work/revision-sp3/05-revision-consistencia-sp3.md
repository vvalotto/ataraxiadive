# Revisión de Consistencia y Coherencia — SP3

| Campo | Valor |
|-------|-------|
| **Tipo** | Revisión de hito — cierre SP3 |
| **Fecha inicio** | 2026-04-02 |
| **Alcance temporal** | SP3 completo (INC-3.1 → INC-3.5, 13 US implementadas) |
| **Output** | Detección de gaps → formalización SP-ADJ-03 |
| **Estado** | ✅ Análisis completo |

---

## Scope

| Bloque | Contenido | Estado |
|--------|-----------|--------|
| **A** | Docs de producto — coherencia interna | ✅ Analizado |
| **B** | Código vs docs — coherencia implementación | ✅ Analizado |
| **C** | Artefactos de flujo (matrix, baselines, git tags) | ✅ Analizado |
| **D** | Entorno de trabajo (CLAUDE.md, MEMORY.md) | ✅ Analizado |
| **E** | Artefactos del experimento (HITOs, retrospectivas BL) | ✅ Analizado |

---

## Bloque A — Coherencia Interna Documental

### A1. Dominio → Diseño estratégico

| ID | Sev | Descripción | Artefactos afectados | Estado |
|----|-----|-------------|----------------------|--------|
| A-01 | 🟢 | `domain-model.md §5 y §4`: notas sobre ES de Resultados y Registro actualizadas a "pendiente SP3" en SP-ADJ-02. SP3 cerró con CRUD en Resultados/Registro (sin ES). Las notas deben actualizarse a "pendiente SP4/descartado". | `docs/design/domain-model.md §4, §5` | `DETECTADO` |
| A-02 | 🟢 | `context-map.md`: describe BC Torneo con `Sede` y `EntidadOrganizadora` como conceptos del aggregate. SP3 implementó Torneo sin esos tipos explícitos (US-3.1.1 creó el aggregate básico). El context-map está desactualizado en el detalle. | `docs/design/context-map.md` | `DETECTADO` |

### A2. Diseño → Especificaciones

Sin gaps críticos. Los ADR (001-013) no requieren actualización para SP3 — las decisiones siguen vigentes.

---

## Bloque B — Coherencia Doc ↔ Implementación

| ID | Sev | Descripción | Archivos afectados | Estado |
|----|-----|-------------|-------------------|--------|
| B-01 | 🟡 | **Cross-BC: routers importan `identidad.api.dependencies`** directamente. `competencia/api/router.py:67`, `registro/api/router.py:9`, `torneo/api/router.py:10` importan `OrganizadorDep/AtletaDep` desde `identidad.api.dependencies`. Viola la regla "no imports directos entre BCs" (CLAUDE.md §6). Severidad moderada: funciona, pero acopla los routers de 3 BCs a la API de Identidad. | `competencia/api/router.py:67`  `registro/api/router.py:9`  `torneo/api/router.py:10` | `DETECTADO` |
| B-02 | 🟡 | **`resultados_competencia_adapter.py` importa `Performance` aggregate** de `competencia.domain.aggregates`. Es un ACL documentado, pero importar el aggregate concreto (no solo VOs o events) es agresivo. Funciona y está testeado. | `resultados/infrastructure/repositories/resultados_competencia_adapter.py:7-8` | `ACEPTADO` — deuda D-07 para SP4 |
| B-03 | 🟢 | `competencia/domain/ports/disciplina_descriptor_port.py` importa desde `competencia.domain.value_objects.disciplina` (re-export de shared/). Debería importar directamente de `shared.domain.value_objects`. Cosmético pero mejora la trazabilidad. | `competencia/domain/ports/disciplina_descriptor_port.py:7-8` | `DETECTADO` |

---

## Bloque C — Artefactos de Flujo

### C1. Trazabilidad (matrix.md)

| ID | Sev | Descripción | Sección matrix.md | Estado |
|----|-----|-------------|-------------------|--------|
| C-01 | 🟡 | **13 RFs de SP3 marcados como `✅ definido` en lugar de `✅ implementado`**. SP3 cerró con 13 US implementadas (US-3.1.1 a US-3.5.3). La matrix refleja solo 9 RFs como implementados. Los 13 restantes deben actualizarse. | `docs/traceability/matrix.md §SP3` | `DETECTADO` |
| C-02 | 🟡 | **SP-ADJ-03 no tiene entrada en matrix.md**. Al igual que SP-ADJ-01 y SP-ADJ-02 en su momento, el SP-ADJ-03 aún no está representado. Debe agregarse antes de ejecutarlo. | `docs/traceability/matrix.md` | `DETECTADO` |

### C2. Baselines y git tags

| ID | Sev | Descripción | Artefacto | Estado |
|----|-----|-------------|-----------|--------|
| C-03 | 🔴 | **BL-003 no existe**. El cierre formal de SP3 requiere crear `.cm/baselines/BL-003.md`. Sin este artefacto no hay evidencia formal de cierre del SP. | `.cm/baselines/BL-003.md` | `PLANIFICADO` — parte del cierre formal |
| C-04 | 🟡 | **INDICE-HITOS.md no tiene entrada para HITOs de SP3 más allá de HITO-16**. Si SP3 generó aprendizajes adicionales (hipótesis human-in-the-loop, arquitectura), deben registrarse. | `docs/contexto/INDICE-HITOS.md` | `DETECTADO` |

---

## Bloque D — Entorno de Trabajo

### D1. CLAUDE.md

| ID | Sev | Descripción | Sección CLAUDE.md | Estado |
|----|-----|-------------|-------------------|--------|
| D-01 | 🔴 | **§14 "Estado Actual" desactualizado**. SP3 cerró con implementación funcional completa pero CLAUDE.md §14 sigue mostrando el estado anterior (sin la tabla SP3 completa, sin mencionar los nuevos BCs, sin el estado de BL-003). | `CLAUDE.md §14` | `PLANIFICADO` — parte del cierre formal |
| D-02 | 🟡 | **§9 tabla de baselines: SP3 sigue en "⏳ Pendiente"** cuando la implementación funcional está completa. Actualizar a estado actual antes del tag. | `CLAUDE.md §9` | `PLANIFICADO` — parte del cierre formal |
| D-03 | 🟢 | **pyproject.toml comentarios de thresholds** no actualizados para SP3. Los comentarios mencionan INC-3.3 como el último ajuste pero SP3 terminó sin cambiar umbrales. Agregar nota de confirmación. | `pyproject.toml [tool.designreviewer]` | `DETECTADO` |

### D2. MEMORY.md

| ID | Sev | Descripción | Artefacto | Estado |
|----|-----|-------------|-----------|--------|
| D-04 | 🟢 | `memory/project_sp_adj_03_pendiente.md` tiene la lista de acciones del SP-ADJ-03, pero deberá actualizarse con los items nuevos identificados en esta revisión (B-01, D-07). | `memory/project_sp_adj_03_pendiente.md` | `DETECTADO` |

---

## Bloque E — Artefactos del Experimento

### E1. HITOs y retrospectivas

| ID | Sev | Descripción | HITO/BL afectado | Estado |
|----|-----|-------------|------------------|--------|
| E-01 | 🟢 | **HITO-16 registrado** (secuencialidad del pipeline). La hipótesis human-in-the-loop fue documentada como doc separado pero sin HITO formal. Si el experimento lo requiere, registrar como HITO-17. | `docs/iedd/04-Hipotesis_Ensayo_IA_Ingenieria_Human_In_The_Loop.md` | `DETECTADO` |
| E-02 | 🟢 | **BL-003 retrospectiva**: al crear BL-003, incluir retrospectiva del experimento para SP3 (métricas, aprendizajes, overhead del Dev Kit). Patrón establecido en BL-001 y BL-002. | `BL-003.md (pendiente)` | `PLANIFICADO` |

---

## Resumen Ejecutivo

| Bloque | 🔴 Críticos | 🟡 Moderados | 🟢 Menores | Total |
|--------|:-----------:|:------------:|:----------:|:-----:|
| A — Docs producto | 0 | 0 | 2 | 2 |
| B — Código vs docs | 0 | 2 | 1 | 3 |
| C — Flujo | 1 | 2 | 1 | 4 |
| D — Entorno | 1 | 2 | 1 | 4 |
| E — Experimento | 0 | 0 | 2 | 2 |
| **Total** | **2** | **6** | **7** | **15** |

**Los 2 críticos son documentales** (BL-003 faltante + CLAUDE.md §14 desactualizado) — no hay críticos de código.
Esto contrasta favorablemente con SP2 (5 críticos, 3 de código). SP3 mantuvo mejor coherencia documental.

---

*Creado: 2026-04-02 — Revisión de hito pre-BL-003*
*Análisis ejecutado por: Claude Code + Victor Valotto*
