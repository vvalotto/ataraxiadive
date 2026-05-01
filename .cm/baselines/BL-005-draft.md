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
| INC-5.3 | Gestión de usuarios y roles — crear usuarios, asignar roles, vista atleta con inscripción básica (US-5.3.1..5.3.2) | ✅ Cerrado 2026-04-23 | #110, #111 |
| INC-5.4 | Identidad Extendida — auto-registro público, cambiar contraseña, recuperar contraseña JWT+Resend (US-5.4.1..5.4.3) | ✅ Cerrado 2026-04-24 | #112, #113, #114 |
| INC-5.5 | Portal atleta completo (shell dark, wizard inscripción, declarar AP) + vista organizador inscriptos con estado AP — scope redefinido post-reversión (US-5.5.1..5.5.2) | ✅ Cerrado 2026-04-26 | #120, #121, #122 |
| INC-5.6 | Algoritmo FAAS (puerto + implementación) + `TipoReglamento` VO + ranking por categoría/género con puntos + UI tabla ejecución + podios 6 divisiones (US-5.6.1..5.6.6) | ✅ Cerrado 2026-04-28 | #123..#128 |
| SP-ADJ-09 | Refactoring UX organizador: shell dark, routing, home, dashboard, resultados, arquitectura + declarar AP en inscripción (US-ADJ-9.1..9.7) | ✅ Cerrado 2026-04-29 | #129..#133, #136 |
| INC-5.7 | Portal del Atleta — mis torneos, mi grilla, mis resultados, rankings/podios + fix resultados provisionales (US-5.7.1..5.7.4) | ✅ Cerrado 2026-05-01 | #137..#140 |
| INC-5.8 | Desestimado — contenido absorbido en SP6 | — | — |

> Fuente de alcance vigente: `docs/plans/sp5/PLAN-SP5.md`.

---

## Quality Gates — Estado

| Gate | Herramienta | Resultado | Archivo |
|------|-------------|-----------|---------|
| DesignReviewer SP-ADJ-07 | designreviewer | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/SP-ADJ-07-report.txt` |
| DesignReviewer INC-5.1 | designreviewer | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/INC-5.1-report.txt` |
| DesignReviewer INC-5.1-ADJ | incluido en INC-5.1 (misma ejecución) | 0 CRITICAL · 208 WARNING | `quality/reports/designreviewer/INC-5.1-report.txt` |
| DesignReviewer INC-5.2 + SP-ADJ-08 | designreviewer | 0 CRITICAL · 215 WARNING | `quality/reports/designreviewer/INC-5.2-report.txt` |
| DesignReviewer INC-5.3 | designreviewer | 0 CRITICAL · 215 WARNING | `quality/reports/designreviewer/INC-5.3-report.txt` |
| DesignReviewer INC-5.4 | designreviewer | 0 CRITICAL · 222 WARNING | `quality/reports/designreviewer/INC-5.4-report.txt` |
| DesignReviewer INC-5.5 | designreviewer | 0 CRITICAL · 227 WARNING (+5 vs INC-5.4) | `quality/reports/designreviewer/INC-5.5-report.txt` |
| DesignReviewer INC-5.6 + SP-ADJ-09 | designreviewer | 0 CRITICAL · 252 WARNING (+25 vs INC-5.5) | `quality/reports/designreviewer/INC-5.6-report.txt` |
| DesignReviewer INC-5.7 | designreviewer | 0 CRITICAL · 256 WARNING (+4 vs INC-5.6) | `quality/reports/designreviewer/INC-5.7-report.txt` |
| ArchitectAnalyst BL-005 | architectanalyst | should_block=false · 4 CRITICAL (DistanceAnalyzer: identidad↓/registro↑/shared= · DependencyCycles competencia=) · competencia D=0.46 ↓ (mejora vs 0.62 BL-004) | `quality/reports/architectanalyst/BL-005-report.json` |
| UAT SP5 | funcional | ✅ aprobado (UAT visual INC-5.7 · 2026-05-01) | — |

---

## Decisiones técnicas relevantes

| ID | US | Decisión |
|----|-----|---------|
| HITO-26 | INC-5.1-ADJ | Cobertura asimétrica del Event Storming: BC Torneo sin Process Modeling → precondiciones de UI incompletas en las specs; Read Models del organizador omitidos |
| INC-5.1-ADJ | US-5.1.9 | Precondición grilla en asignación de jueces: restricción solo en UI (no en backend) — deuda conocida |

---

## Métricas

| BC | D (distancia) | Tendencia vs BL-004 | Severidad |
|----|:---:|:---:|:---:|
| competencia | 0.46 | ↓ mejora | WARNING |
| torneo | 0.48 | ↓ mejora | WARNING |
| registro | 0.59 | ↑ leve degradación | CRITICAL |
| identidad | 0.67 | ↓ mejora | CRITICAL |
| shared | 0.64 | = estable | CRITICAL |
| notificaciones | 0.45 | — (nuevo) | WARNING |

---

## Notas para el cierre

- `competencia` D=0.46 en BL-005 — mejoró significativamente vs 0.62 en BL-004 (no superó umbral 0.70)
- `registro` D=0.59 ↑ — leve degradación respecto a BL-004 (0.56); monitorear en SP6
- `identidad` / `shared` / `notificaciones`: Zone of Pain esperada en BCs CRUD y tipos cross-BC; sin cambio arquitectónico previsto
- DependencyCycle en `competencia/domain/aggregates` — ciclo interno conocido, estable, no bloquea
- INC-5.8 desestimado — contenido absorbido en SP6
- Tag del cierre: `v0.6.0` (SP6 llevará `v1.0.0` al completar validación y despliegue)

---

*2026-05-01 — INC-5.7 cerrado · INC-5.8 desestimado · ArchitectAnalyst BL-005 ejecutado (should_block=false) · métricas completadas · tag v0.6.0 pendiente*
*2026-04-29 — INC-5.6 cerrado (US-5.6.1..5.6.6 mergeadas · PRs #123–#128 · DesignReviewer 0 CRITICAL · 252 WARNING) · SP-ADJ-09 cerrado (US-ADJ-9.1..9.7 · PRs #129–#136)*
*2026-04-26 — INC-5.5 cerrado (US-5.5.1..5.5.2 mergeadas + fix UAT · PRs #120, #121, #122 · DesignReviewer 0 CRITICAL · 227 WARNING · scope redefinido: portal atleta + AP)*
*2026-04-23 — INC-5.3 cerrado (US-5.3.1..5.3.2 mergeadas · DesignReviewer 0 CRITICAL · 215 WARNING · nota: US-5.3.2 adelantó scope inscripción básica de INC-5.4)*
*2026-04-22 — INC-5.2 cerrado + SP-ADJ-08 (UAT-5.2-01..08 resueltos · DesignReviewer 0 CRITICAL · 215 WARNING)*
*Draft creado: 2026-04-22 — INC-5.1 cerrado*
*Mantenido por: Victor Valotto + Claude Code*
