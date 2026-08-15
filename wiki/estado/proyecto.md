---
title: "Estado del Proyecto — AtaraxiaDive"
type: estado-proyecto
last_updated: "2026-05-30"
baseline_vigente: BL-007
tag_vigente: v1.0.5
sp_activo: ninguno — proyecto cerrado
sources:
  - .cm/baselines/BL-000-pre-codigo.md
  - .cm/baselines/BL-001-sp1-la-performance.md
  - .cm/baselines/BL-002.md
  - .cm/baselines/BL-003.md
  - .cm/baselines/BL-004.md
  - .cm/baselines/BL-005-draft.md
  - .cm/baselines/BL-006.md
  - .cm/baselines/BL-007.md
---

# Estado del Proyecto — AtaraxiaDive

> **Fuente de verdad única para el estado del proyecto.**
> Esta página sintetiza los baselines de cierre de cada SP.
> Para estado de implementación por US → [[trazabilidad]].
> Para decisiones técnicas → [[decisiones]].

---

## Situación actual (2026-05-30)

> Proyecto cerrado. SP7 completo, más SP-ADJ-12 y el addendum SP-ADJ-13 posteriores al tag `v1.0.0`.

| Campo | Valor |
|-------|-------|
| **Baseline vigente** | BL-007 · tag `v1.0.2` (extendido a `v1.0.5` por addendum SP-ADJ-13, sin baseline nueva) · cerrado 2026-05-30 |
| **SP activo** | Ninguno — SP7 fue el último subproyecto planificado, cerrado |
| **Estado del sistema** | Validado E2E (UAT 10/10 flows) y desplegado en producción |
| **URL producción** | `https://ataraxiadive.fly.dev/` — verificada end-to-end (US-7.1.2) |

### SP7 — cierre

| Incremento | US | Estado |
|------------|----|--------|
| INC-7.1 — Despliegue Fly.io | US-7.1.1 Dockerfile + fly.toml + FastAPI estáticos | ✅ Completada 2026-05-17 · PR #194 |
| INC-7.1 — Despliegue Fly.io | US-7.1.2 `fly deploy` + verificación + tag v1.0.1 | ✅ Completada 2026-05-30 |
| INC-7.2 — Manual de Usuario | US-7.2.1 Manual organizador | ✅ Completada 2026-05-30 · PR #212 |
| INC-7.2 — Manual de Usuario | US-7.2.2 Manual juez | ✅ Completada 2026-05-30 · PR #212 |
| INC-7.2 — Manual de Usuario | US-7.2.3 Manual atleta | ✅ Completada 2026-05-30 · PR #212 |

### Posteriores a SP7 (sin baseline nueva)

| Ajuste | Alcance | Estado |
|--------|---------|--------|
| SP-ADJ-12 | Correcciones de producción post-SP7 — issues #198–#204 · 6 US + 3 fixes | ✅ Cerrado 2026-05-24 · PR #205–#210 |
| SP-ADJ-13 (addendum a BL-007) | Fixes UI #213–#216 (tag `v1.0.4`) + manual revisado contra producción (tag `v1.0.5`) | ✅ Cerrado 2026-05-30 · PR #217, #218 |

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
| BL-007 | SP7 + SP-ADJ-12 | Despliegue y Documentación | `v1.0.2` | 2026-05-30 | 1049 | 0 CRITICAL · 296 W | 3 C · 62 W · no-block |

---

## Estado de Bounded Contexts (BL-007)

| BC | Tipo DDD | D (distancia) | Tendencia vs BL-006 | Severidad AA | Nota |
|----|----------|:---:|:---:|:---:|---|
| [[competencia]] | Core Domain · Event Sourcing | 0.459 | = | WARNING | sin cambios en SP-ADJ-12 |
| [[notificaciones]] | Generic · Event Sourcing | 0.450 | = | WARNING | sin cambios en SP-ADJ-12 |
| [[bc-torneo]] | Supporting · CRUD | 0.479 | = | WARNING | sin cambios en SP-ADJ-12 |
| [[registro]] | Supporting · CRUD | 0.59 | ↑ | **CRITICAL** | SP-ADJ-12 agregó `estado_aceptacion` (stack completo) — aceptado (AA-06) |
| [[identidad]] | Generic · CRUD | 0.66 | ↑ | **CRITICAL** | SP-ADJ-12 agregó handlers agregar/quitar rol — aceptado (AA-05) |
| [[shared]] | Cross-cutting | 0.63 | = | **CRITICAL** | estable, diferido post-v1.1 (AA-07) |

**`should_block=false` en todos los BCs.** Los CRITICAL de `registro`, `identidad` y `shared` son conocidos y aceptados para el cierre v1.0.2. Ver decisiones AA-05, AA-06, AA-07 en BL-007.

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
| BL-007 (SP7 + SP-ADJ-12) | 0 | 296 | +9 handlers agregar/quitar rol + estado_aceptacion |

**0 CRITICAL en todos los SPs.** La tendencia WARNING es esperada y monitoreable; los incrementos correlacionan con nuevos BCs y patrones Event Sourcing. Ver [[calidad-BL-007]] para el detalle completo del cierre.

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

## Deuda técnica conocida (al cierre v1.0.2)

| ID | Descripción | BC | Severidad | Estado |
|----|-------------|-----|-----------|--------|
| AA-05 | `identidad` D=0.66 ↑ (SP-ADJ-12 agregó handlers agregar/quitar rol) | identidad | CRITICAL (DistanceAnalyzer) | Aceptado — intervenir si D > 0.70 en BL-008 |
| AA-06 | `registro` D=0.59 ↑ (SP-ADJ-12 agregó `estado_aceptacion`) | registro | CRITICAL (DistanceAnalyzer) | Aceptado — intervenir si D > 0.65 en BL-008 |
| AA-07 | `shared` D=0.63 (fan-out estructural, estable) | shared | CRITICAL (DistanceAnalyzer) | Diferido post-v1.1 |
| DR-01 | `RankingCompetencia` LCOM=2 — falso positivo Event Sourcing | competencia | WARNING (DesignReviewer) | Cerrado como aceptado |
| ARCH-03 | ACL en `resultados/infrastructure/` — coupling temporal por string literals | resultados | WARNING | Cerrado como ACL aceptable |

> AA-02 y AA-04 (BL-006) quedan supersedidas por AA-05 y AA-07 respectivamente — mismo hallazgo, valores actualizados a BL-007.

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
| SP7 | Despliegue y Documentación | v1.0.2 (→v1.0.5) | 2026-05-30 | 5 | SP-ADJ-12/13 | Infra + Docs |
