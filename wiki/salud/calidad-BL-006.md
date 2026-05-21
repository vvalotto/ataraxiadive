---
title: "Snapshot de Calidad — BL-006 / v1.0.0"
type: salud
last_updated: "2026-05-21"
sources:
  - quality/reports/designreviewer/current-report.json
  - .cm/baselines/BL-006-report.json
  - quality/reports/architectanalyst/BL-005-report.json
  - quality/reports/uat/SP6/
---

# Snapshot de Calidad — BL-006 / v1.0.0

> Síntesis de los tres quality gates al cierre de SP6 (2026-05-16, tag `v1.0.0`).
> Para métricas por BC → sección `## Salud` en cada página de [[arquitectura]].
> Para lint del wiki → [[lint-001]] (pendiente Fase 4).

---

## Veredicto global

| Gate | Resultado | should_block |
|------|-----------|:---:|
| DesignReviewer | 0 CRITICAL · 287 WARNING | false |
| ArchitectAnalyst | 3 CRITICAL (DistanceAnalyzer) · 62 WARNING | false |
| UAT SP6 | 10/10 flows ✅ (F-09/F-10 con waiver) | — |

**0 CRITICAL de DesignReviewer en todos los SPs.** `should_block=false` en todos los gates al cierre del proyecto.

---

## DesignReviewer — current-report.json (2026-05-18)

> Ejecutado post SP-ADJ-11. 303 archivos analizados. Herramienta: `software_limpio`.

### Por BC

| BC | WARNING | Top smells |
|----|:-------:|------------|
| [[arquitectura/competencia]] | **130** | LongMethod (74) · FeatureEnvy (36) · DataClumps (9) |
| [[arquitectura/resultados]] | **40** | LongMethod (27) · FeatureEnvy (3) |
| [[arquitectura/registro]] | **37** | LongMethod (18) · FeatureEnvy (12) |
| `app.py` (cross-cutting) | **21** | LongMethod (14) · DataClumps (5) |
| [[arquitectura/identidad]] | **21** | LongMethod (8) · FeatureEnvy (8) · DataClumps (2) |
| [[arquitectura/notificaciones]] | **18** | LongMethod (10) · FeatureEnvy (7) |
| [[arquitectura/torneo]] | **15** | FeatureEnvy (8) · LongMethod (2) |
| `shared/` | **5** | LongMethod (5) |
| **Total** | **287** | |

### Por tipo de smell

| Smell | Count | Interpretación arquitectónica |
|-------|:-----:|-------------------------------|
| LongMethod | 158 | Handlers hexagonales con múltiples invariantes — patrón inherente a DDD/CQRS |
| FeatureEnvy | 74 | Handlers que orquestan aggregate + puertos + proyecciones — patrón CQRS |
| DataClumps | 20 | Parámetros coordinados (competencia_id + disciplina + store) — candidatos a Value Object |
| LongParameterList | 13 | Constructores de aggregates y DTOs con múltiples campos |
| FanOut | 12 | Módulos de aplicación con muchas dependencias — esperado en composition root |
| LCOM | 10 | Aggregates Event Sourcing con grupos comando/reconstitución — falso positivo (ver DR-01) |

### Evolución histórica

| Baseline | CRITICAL | WARNING | Δ | Evento |
|----------|:---:|:---:|:---:|--------|
| BL-002 (SP2) | 0 | 78 | +78 | BC Resultados + Competencia ampliado |
| BL-003 (SP3) | 0 | 119 | +41 | BC Torneo + Identidad + Registro |
| BL-004 (SP4) | 0 | 197 | +78 | Frontend + BC Notificaciones + Event Sourcing |
| BL-005 (SP5) | 0 | 256 | +59 | Portales completos + FAAS + rankings |
| BL-006 post-INC-6.4 | 0 | 253 | −3 | Refactoring deuda técnica SP6 |
| BL-006 post-SP-ADJ-11 | 0 | **287** | +34 | Modelo multi-rol (complejidad nueva) |

**Tasa de crecimiento:** ~+30W por incremento mayor. Correlaciona con BCs y patrones nuevos, no con degradación del código existente.

---

## ArchitectAnalyst — BL-006-report.json (2026-05-16)

> 303 archivos · 6 métricas · 1.85s.

### Resumen

| Métrica | Valor |
|---------|-------|
| Total resultados | 505 |
| CRITICAL (DistanceAnalyzer) | 3 |
| WARNING (InstabilityAnalyzer) | 62 |
| INFO | 440 |
| should_block | **false** |

### DistanceAnalyzer — D por BC

| BC | D (BL-006) | D (BL-005) | Δ | Severidad | Decisión |
|----|:---:|:---:|:---:|:---:|---------|
| [[arquitectura/notificaciones]] | 0.450 | 0.450 | = | WARNING | Aceptado |
| [[arquitectura/competencia]] | 0.459 | 0.459 | = | WARNING | Aceptado |
| [[arquitectura/torneo]] | 0.479 | 0.476 | ↑ leve | WARNING | Aceptado |
| [[arquitectura/resultados]] | < umbral | < umbral | = | INFO | ✅ Saludable |
| [[arquitectura/registro]] | 0.583 | 0.592 | ↑ | **CRITICAL** | Diferido post-v1.0 |
| `shared/` | 0.635 | 0.635 | = | **CRITICAL** | Diferido post-v1.0 (AA-04) |
| [[arquitectura/identidad]] | 0.652 | 0.669 | ↓ | **CRITICAL** | Diferido post-v1.0 (AA-02) |

> **Zone of Pain** (D > 0.5): BCs CRUD con alta abstracción y baja inestabilidad. Es la zona esperada para BC genéricos estables por diseño DDD. Los tres CRITICAL son knowns y no bloquean.

### InstabilityAnalyzer — 62 WARNINGs

Los 62 warnings de InstabilityAnalyzer son **falsos positivos estructurales de la arquitectura hexagonal**:

- Las capas `application/` y `api/` siempre tienen I ≈ 1.0 porque dependen del dominio (Ca=0 o bajo, Ce=alto).
- Las capas `domain/value_objects`, `domain/events`, `domain/ports` tienen I=1.0 porque no las importa nadie dentro del propio BC — son hojas del grafo.
- Este es el comportamiento correcto de la arquitectura hexagonal: las capas externas dependen de las internas, no al revés.

**Acción:** ninguna. Patrón documentado y aceptado.

### DependencyCycle — competencia/domain/aggregates

`competencia.domain.aggregates` ↔ `competencia.domain.aggregates.performance`

Auditado en INC-6.4 (US-6.4.1). El ciclo es interno al módulo de aggregates y no cruza capas. Clasificado como **aceptable** — la refactorización para eliminarlo implicaría separar Performance del aggregate de Competencia, rompiendo la cohesión del dominio. Decisión documentada en BL-006.

---

## UAT — SP6 (2026-05-16)

### Resultados por flow

| Flow | Descripción | Resultado |
|------|-------------|-----------|
| F-01 | Setup inicial y configuración | ✅ PASS |
| F-02 | Creación de torneo | ✅ PASS |
| F-03 | Seed dataset BA 2025 | ✅ PASS |
| F-04 | Inscripción abierta | ✅ PASS |
| F-05 | Preparación de competencia | ✅ PASS |
| F-06 | Inicio de ejecución | ✅ PASS |
| F-07 | Ejecución normal | ✅ PASS |
| F-08 | Flujos de excepción | ✅ PASS |
| F-09 | Resultados y premiación | ✅ PASS (waiver) |
| F-10 | Cierre de torneo | ✅ PASS (waiver) |

**10/10 flows aprobados.** F-09 y F-10 tienen waiver documentado (validación con dataset parcial BA 2025 — los cálculos de puntuación fueron verificados en SP3 contra resultados oficiales).

### Dataset de prueba

Seed basado en torneo Buenos Aires 2025. 6 RPs verificados contra resultados oficiales del evento (HITO-17). El dataset es el oráculo empírico del dominio — establece la fuente de verdad para los cálculos de ranking.

---

## Decisiones de aceptación de deuda

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| DR-01 | `RankingCompetencia` LCOM=2 | Falso positivo Event Sourcing | Ninguna — patrón aceptado |
| AA-02 | `identidad` D=0.652 | Zone of Pain esperada — CRUD genérico | Diferir evaluación post-v1.0 |
| AA-04 | `shared` D=0.635 | Fan-out estructural cross-BC | Diferir — riesgo regresión sistémica |
| ARCH-03 | ACL en `resultados/infrastructure` | ACL legítimo en capa infra | Ninguna — patrón DDD aceptado |
| ADP-01 | Ciclo `domain/aggregates` ↔ `performance` | Ciclo interno al módulo | Ninguna — cohesión domain mantenida |

---

## Próximos pasos de calidad

1. **Fase 4 — Primer lint:** ejecutar `/wiki-lint` → `wiki/salud/lint-001.md`
2. **Post-v1.0:** evaluar D(registro) = 0.583 tras SP-ADJ-11 (Juez+Organizador)
3. **Post-v1.0:** evaluar separación de `shared/domain/` en submódulos para reducir D(shared)
4. **DataClumps (20):** candidatos a Value Object — `(competencia_id, disciplina, store)` en `app.py`
