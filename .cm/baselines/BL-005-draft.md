# BL-005 — Baseline La Puesta en Marcha (SP5) [DRAFT]

| Campo | Valor |
|-------|-------|
| **Tipo** | Incremento mayor |
| **Subproyecto** | SP5 — La Puesta en Marcha |
| **Fecha apertura** | 2026-04-19 (post-tag v0.5.0) |
| **Fecha cierre** | pendiente |
| **Git tag** | pendiente — `v1.0.0` (planificado) |
| **Branch base** | `develop` |
| **Estado** | 🔄 En construcción |

---

## Descripción

Baseline al cierre de SP5. Objetivo: MVP Demo operativo — ciclo completo de torneo
gestionable desde el panel del organizador, con ejecución por disciplina y resultados.

---

## Inventario de Incrementos

### SP-ADJ-07 — Deuda técnica post-SP4 (pre-SP5)

| Incremento | Descripción | Estado | PRs |
|-----------|-------------|--------|-----|
| SP-ADJ-07 | BUG-SP4-003 (`CorregirResultadoTrasDNS`) + BUG-SP4-004 (`tarjeta_asignada` en grilla) + SCOPE-SP4-001 (P-11 wiring `CompetenciaFinalizada` → email) | ✅ Cerrado 2026-04-19 | #92, #93, #94 |

> DesignReviewer SP-ADJ-07: 0 CRITICAL · 208 WARNING (`quality/reports/designreviewer/SP-ADJ-07-report.txt`)

---

### SP5 — La Puesta en Marcha

| Incremento | Descripción | Estado | PRs |
|-----------|-------------|--------|-----|
| INC-5.1 | Panel del Organizador — CrearTorneo, gestión de fases, inscriptos, grilla, jueces, monitor de ejecución (US-5.1.1..5.1.6) | ✅ Cerrado 2026-04-22 | #95..#100 |
| INC-5.1-ADJ | Ajuste post-UAT panel organizador — política de tabs, composición disciplinas/competencias, precondición grilla en jueces, normalización estado (US-5.1.7..5.1.10) | ✅ Cerrado 2026-04-22 | #101..#104 |
| INC-5.2 | Ejecución por Disciplina — vista maestro-detalle, habilitar disciplina, cierre manual (US-5.2.1..5.2.2) | ✅ Cerrado 2026-04-22 | #105, #106 |
| SP-ADJ-08 | Ajuste post-UAT INC-5.2 — reglas operativas, UX/lenguaje, cancelación fuerte (US-ADJ-8.1..8.3) | ✅ Cerrado 2026-04-22 | #107, #108, #109 |
| INC-5.3 | Gestión de usuarios y roles — crear usuarios, asignar roles, vistas por rol (US-5.3.1..5.3.2) | ⏳ Pendiente | — |
| INC-5.4 | Inscripción completa — auto-registro, APs por disciplina, vista de inscriptos (US-5.4.1..5.4.3) | ⏳ Pendiente | — |
| INC-5.5 | Algoritmo de puntaje y rankings por categoría/género — FAAS, tabla OT, podios y overall (US-5.5.1..5.5.6) | ⏳ Pendiente | — |
| INC-5.6 | Portal del Atleta — mis torneos, mi grilla, mis resultados, rankings/podios (US-5.6.1..5.6.4) | ⏳ Pendiente | — |
| INC-5.7 | Polish y demo-readiness — seed BA 2025, verificación contra resultados oficiales, UX fixes (US-5.7.1..5.7.3) | ⏳ Pendiente | — |

> Fuente de alcance vigente: `docs/plans/sp5/PLAN-SP5.md`.

---

## Quality Gates — Estado

| Gate | Herramienta | Resultado | Archivo |
|------|-------------|-----------|---------|
| DesignReviewer SP-ADJ-07 | designreviewer | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/SP-ADJ-07-report.txt` |
| DesignReviewer INC-5.1 | designreviewer | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/INC-5.1-report.txt` |
| DesignReviewer INC-5.1-ADJ | incluido en INC-5.1 (misma ejecución) | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/INC-5.1-report.txt` |
| DesignReviewer INC-5.2 + SP-ADJ-08 | designreviewer | 0 CRITICAL · 215 WARNING | `quality/reports/designreviewer/INC-5.2-report.txt` |
| ArchitectAnalyst BL-005 | architectanalyst | ⏳ pendiente (al cerrar SP5) | — |
| UAT SP5 | funcional | ⏳ pendiente (INC-5.7 / cierre BL-005) | — |

---

## Decisiones técnicas relevantes

| ID | US | Decisión |
|----|-----|---------|
| HITO-26 | INC-5.1-ADJ | Cobertura asimétrica del Event Storming: BC Torneo sin Process Modeling → precondiciones de UI incompletas en las specs; Read Models del organizador omitidos |
| INC-5.1-ADJ | US-5.1.9 | Precondición grilla en asignación de jueces: restricción solo en UI (no en backend) — deuda conocida |

---

## Métricas

*(a completar al cerrar SP5 con ArchitectAnalyst)*

| BC | D (distancia) | Tendencia vs BL-004 |
|----|:---:|:---:|
| competencia | — | — |
| torneo | — | — |
| registro | — | — |
| identidad | — | — |
| shared | — | — |

---

## Notas para el cierre

- `competencia` D=0.62 en BL-004 — monitorear si supera 0.70 con INC-5.2 (nuevo frontend)
- UAT SP5 debe cubrir ciclo completo: crear torneo → inscribir → grilla → ejecución → resultados
- Integración FAAS / importación CSV queda fuera de alcance SP5; el MVP usa formulario manual.
- Antes del tag `v1.0.0`: merge develop→main, ArchitectAnalyst, retrospectiva SP5

---

*2026-04-22 — INC-5.2 cerrado + SP-ADJ-08 (UAT-5.2-01..08 resueltos · DesignReviewer 0 CRITICAL · 215 WARNING)*
*Draft creado: 2026-04-22 — INC-5.1 cerrado*
*Mantenido por: Victor Valotto + Claude Code*
