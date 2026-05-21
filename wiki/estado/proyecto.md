---
title: "Estado del Proyecto — AtaraxiaDive"
type: estado-proyecto
last_updated: "2026-05-21"
baseline_vigente: BL-006
tag_vigente: v1.0.0
sp_activo: SP7
sources:
  - .cm/baselines/BL-000-pre-codigo.md
  - .cm/baselines/BL-001-sp1-la-performance.md
  - .cm/baselines/BL-002.md
  - .cm/baselines/BL-003.md
  - .cm/baselines/BL-004.md
  - .cm/baselines/BL-005-draft.md
  - .cm/baselines/BL-006.md
---

# Estado del Proyecto — AtaraxiaDive

> **Fuente de verdad única para el estado del proyecto.**
> Esta página sintetiza los baselines de cierre de cada SP.
> Para estado de implementación por US → [[trazabilidad]].
> Para decisiones técnicas → [[decisiones]].

---

## Situación actual (2026-05-21)

| Campo | Valor |
|-------|-------|
| **Baseline vigente** | BL-006 · `v1.0.0` · 2026-05-16 |
| **SP activo** | SP7 — Despliegue y Documentación |
| **Próximo tag objetivo** | `v1.0.1` (BL-007) |
| **Estado del sistema** | Validado E2E (UAT 10/10 flows); pendiente despliegue en producción |
| **URL producción** | `https://ataraxiadive.fly.dev/` (pendiente US-7.1.2 — `fly deploy`) |

### SP7 — progreso

| Incremento | US | Estado |
|------------|----|--------|
| INC-7.1 — Despliegue Fly.io | US-7.1.1 Dockerfile + fly.toml + FastAPI estáticos | ✅ Completada 2026-05-17 · PR #194 |
| INC-7.1 — Despliegue Fly.io | US-7.1.2 `fly deploy` + verificación + tag v1.0.1 | ⏳ Pendiente |
| INC-7.2 — Manual de Usuario | US-7.2.1 Manual organizador | ⏳ Pendiente |
| INC-7.2 — Manual de Usuario | US-7.2.2 Manual juez | ⏳ Pendiente |
| INC-7.2 — Manual de Usuario | US-7.2.3 Manual atleta | ⏳ Pendiente |

---

## Historia de Baselines

| BL | SP | Nombre | Tag | Fecha cierre | Tests | DesignReviewer | ArchitectAnalyst |
|----|----|--------|-----|--------------|-------|----------------|-----------------|
| BL-000 | Fase 0 | Pre-Código | `v0.1.0` | 2026-03-19 | — | — | — |
| BL-001 | SP1 | La Performance | `v0.2.0` | 2026-03-24 | 207 | 0 CRITICAL | — |
| BL-002 | SP2 + SP-ADJ-01 | La Competencia | `v0.3.0` | 2026-03-28 | 481 | 0 CRITICAL · 78 W | 0 C · 26 W · no-block |
| BL-003 | SP3 + SP-ADJ-03/04 | El Torneo | `v0.4.0` | 2026-04-04 | 785 | 0 CRITICAL · 119 W | 4 C · 44 W · no-block |
| BL-004 | SP4 + SP-ADJ-06 | La Plataforma | `v0.5.0` | 2026-04-18 | 952 | 0 CRITICAL · 197 W | 0 C · — · no-block |
| BL-005 | SP5 + SP-ADJ-07/08/09 | La Puesta en Marcha | `v0.6.0` | 2026-05-01 | — | 0 CRITICAL · 256 W | 4 C · — · no-block |
| BL-006 | SP6 + SP-ADJ-10/11 | Validación y Ajustes | `v1.0.0` | 2026-05-16 | — | 0 CRITICAL · 287 W | 3 C · 62 W · no-block |
| BL-007 | SP7 | Despliegue y Documentación | `v1.0.1` | ⏳ | — | — | — |

---

## Estado de Bounded Contexts (BL-006)

| BC | Tipo DDD | D (distancia) | Tendencia vs BL-005 | Severidad AA | Nota |
|----|----------|:---:|:---:|:---:|---|
| [[competencia]] | Core Domain · Event Sourcing | 0.459 | = | WARNING | estable |
| [[notificaciones]] | Generic · Event Sourcing | 0.450 | = | WARNING | estable |
| [[torneo]] | Supporting · CRUD | 0.479 | ↑ leve | WARNING | estable |
| [[registro]] | Supporting · CRUD | 0.583 | ↑ | **CRITICAL** | SP-ADJ-11 agregó Juez+Organizador (infra nueva) |
| [[identidad]] | Generic · CRUD | 0.652 | ↓ mejora | **CRITICAL** | SP-ADJ-11 refactorizó domain; mejora de 0.87→0.67→0.65 |
| [[shared]] | Cross-cutting | 0.635 | = | **CRITICAL** | diferido post-v1.0 — fan-out estructural |

**`should_block=false` en todos los BCs.** Los CRITICAL de `registro`, `identidad` y `shared` son conocidos y aceptados para v1.0.0. Ver decisiones AA-02, AA-04 en BL-006.

---

## Evolución DesignReviewer

| Baseline | CRITICAL | WARNING | Nota |
|----------|----------|---------|------|
| BL-001 (SP1) | 0 | — | Walking skeleton |
| BL-002 (SP2) | 0 | 78 | +78 BC Resultados + BC Competencia ampliado |
| BL-003 (SP3) | 0 | 119 | +41 BC Torneo + Identidad + Registro |
| BL-004 (SP4) | 0 | 197 | +78 Frontend + BC Notificaciones + Event Sourcing |
| BL-005 (SP5) | 0 | 256 | +59 Portales + FAAS + Rankings |
| BL-006 post-INC-6.4 | 0 | 253 | −3 refactoring deuda técnica |
| BL-006 post-SP-ADJ-11 | 0 | 287 | +34 complejidad modelo multi-rol |

**0 CRITICAL en todos los SPs.** La tendencia WARNING es esperada y monitoreable; los incrementos correlacionan con nuevos BCs y patrones Event Sourcing.

---

## UAT por SP

| SP | Método | Resultado | Fecha |
|----|--------|-----------|-------|
| SP1 | pytest E2E (seed script) | ✅ DoD verificado — 5 performances, traza completa | 2026-03-24 |
| SP2 | pytest E2E | ✅ 481 tests pass | 2026-03-28 |
| SP3 | pytest + HTTP con seed · dataset BA 2025 | ✅ 28/28 (14 pytest + 14 HTTP) · 6 RPs coinciden con resultados oficiales BA 2025 | 2026-04-04 |
| SP4 | UAT funcional en dispositivos físicos (iPhone/iPad/Mac) | ✅ APROBADO con condición · 2 bugs resueltos · 2 diferidos SP5 | 2026-04-18 |
| SP5 | UAT visual INC-5.7 (BDD waiver frontend puro) | ✅ Aprobado | 2026-05-01 |
| SP6 | UAT E2E 10 flows (seed BA 2025) | ✅ 10/10 flows · F-09/F-10 con waiver | 2026-05-16 |

---

## Cobertura de Requerimientos Funcionales

| Área RF | BCs involucrados | Estado |
|---------|------------------|--------|
| RF-GT (Gestión Torneo) | Torneo, Competencia | ✅ completado SP3/SP4 |
| RF-PR (Performance y Resultado) | Competencia, Resultados | ✅ completado SP1/SP2/SP4 |
| RF-EJ (Ejecución) | Competencia, Frontend | ✅ completado SP2/SP4/SP6 |
| RF-IN (Inscripción) | Registro, Frontend | ✅ completado SP3/SP5/SP6 · RF-IN-05/06 SP6 |
| RF-PM (Puntuación) | Resultados, Torneo | ✅ completado SP5 (FAAS + rankings + podios) |
| RF-US (Usuarios y Roles) | Identidad, Registro | ✅ completado SP3/SP-ADJ-11 (multi-rol) |
| RF-NT (Notificaciones) | Notificaciones | 🟡 email ✅ · push — fuera de alcance v1 |
| RF-IG (Integración externa) | — | — fuera de alcance v1 |

---

## Deuda técnica conocida (post-v1.0.0)

| ID | Descripción | BC | Severidad | Estado |
|----|-------------|-----|-----------|--------|
| AA-02 | `identidad` D=0.652 (Zone of Pain — CRUD genérico) | identidad | CRITICAL (DistanceAnalyzer) | Diferido post-v1.0 |
| AA-04 | `shared` D=0.635 (fan-out estructural) | shared | CRITICAL (DistanceAnalyzer) | Diferido post-despliegue |
| DR-01 | `RankingCompetencia` LCOM=2 — falso positivo Event Sourcing | competencia | WARNING (DesignReviewer) | Cerrado como aceptado |
| ARCH-03 | ACL en `resultados/infrastructure/` — coupling temporal por string literals | resultados | WARNING | Cerrado como ACL aceptable |

---

## Subproyectos — resumen

| SP | Nombre | Tag | Fecha | US-IEDD | SP-ADJ | BCs activos |
|----|--------|-----|-------|---------|--------|-------------|
| Fase 0 | Pre-Código | v0.1.0 | 2026-03-19 | — | — | Diseño + ADRs |
| SP1 | La Performance | v0.2.0 | 2026-03-24 | 8 | SP-ADJ-01/02 | Competencia |
| SP2 | La Competencia | v0.3.0 | 2026-03-28 | 10 | SP-ADJ-01 | Competencia + Resultados |
| SP3 | El Torneo | v0.4.0 | 2026-04-04 | 12 | SP-ADJ-03/04/05 | Torneo + Registro + Identidad |
| SP4 | La Plataforma | v0.5.0 | 2026-04-18 | 20 | SP-ADJ-06/07 | Frontend + Notificaciones |
| SP5 | La Puesta en Marcha | v0.6.0 | 2026-05-01 | 28 | SP-ADJ-08/09 | Todos · Portales + FAAS |
| SP6 | Validación y Ajustes | v1.0.0 | 2026-05-16 | 23 + INC-6.6 | SP-ADJ-10/11 | Todos · UAT + deuda técnica |
| SP7 | Despliegue y Documentación | v1.0.1 | ⏳ | 5 | — | Infra + Docs |
