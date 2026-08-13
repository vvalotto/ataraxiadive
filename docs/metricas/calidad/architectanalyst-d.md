# ArchitectAnalyst — Métrica D por BC y Baseline

> Fuente: `quality/reports/architectanalyst/BL-*.json` + `.cm/baselines/BL-*.md` + `quality/reports/architectanalyst/v1.0.5-report.json`  
> Métrica: D = distancia a la Main Sequence = |A + I − 1| (Robert C. Martin)  
> Escala: 0 = ideal (sobre la Main Sequence) · 1 = zona de riesgo máximo  
> Umbral configurado: D > 0.30 → WARNING; umbrales CRITICAL por BC  
> Fecha de extracción original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP-ADJ-13, tag v1.0.5)**  
> Referencia: PLAN-METRICAS.md §B.2

---

## 1. Evolución D por BC a lo largo de las baselines

| BC | Tipo | BL-001 | BL-002 | BL-003 | BL-004 | BL-005 | BL-006 | **v1.0.5 (HEAD)** |
|----|------|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| competencia | ES (Core) | 0.466 | 0.448 | 0.616 ↑ | 0.621 = | **0.459 ↓** | 0.459 = | 0.459 = |
| resultados | CRUD | — | 0.429 | — | — | — | — | **≤ 0.30** (Main Sequence, sin cambios) |
| registro | CRUD | — | — | 0.563 | 0.563 = | 0.592 ↑ | 0.583 ↓ | **0.589 ↑** |
| identidad | CRUD | — | — | 0.870 | 0.870 = | 0.669 ↓ | 0.652 ↓ | **0.673 ↑** |
| torneo | CRUD | — | — | 0.474 | 0.641 ↑ | 0.476 ↓ | 0.479 = | 0.479 = |
| shared | Shared | 0.500 | 0.500 | 0.611 ↑ | 0.635 ↑ | 0.635 = | 0.635 = | 0.635 = |
| notificaciones | ES | — | — | — | — | 0.450 | 0.450 = | 0.450 = |

**SP correspondiente:** BL-001=SP1 · BL-002=SP2 · BL-003=SP3 · BL-004=SP4 · BL-005=SP5 · BL-006=SP6 · v1.0.5=SP7+SP-ADJ-12+SP-ADJ-13 (sin baseline formal propia — medido directo sobre HEAD)

**Movimiento post-SP6:** solo `registro` (0.583→0.589) e `identidad` (0.652→0.673) subieron — ambos coinciden con el BC que recibió el modelo multi-rol extendido en SP-ADJ-12 (roles, aceptación de inscripciones). El resto del sistema (competencia, torneo, shared, notificaciones, resultados) **no se movió**, consistente con que SP7/SP-ADJ-13 fueron incrementos de infraestructura/documentación/UI, no de dominio.

---

## 2. should_block por baseline

| Baseline | SP | CRITICAL | WARNING | should_block |
|----------|----|---------:|--------:|:------------:|
| BL-001 | SP1 | 0 | 2 | **false** |
| BL-002 | SP2 | 0 | 3 | **false** |
| BL-003 | SP3 | 4 | 1 | **false** |
| BL-004 | SP4 | 5 | 0 | **false** |
| BL-005 | SP5 | 4 | 2 | **false** |
| BL-006 | SP6 | 3 | 3 | **false** |
| BL-007 | SP7+ADJ-12 | 3 | 62 | **false** |
| v1.0.5 (HEAD) | +SP-ADJ-13 | 3 | 64 | **false** |

`should_block` fue **false en todas las mediciones, incluyendo la más reciente (v1.0.5)** — el ArchitectAnalyst nunca bloqueó el cierre de un SP. Los issues CRITICAL se mantienen en 3 desde BL-007 (identidad, shared, registro — los mismos BCs Zone of Pain de siempre). El salto de WARNING de 2-3 (BL-001→BL-006) a 62-64 (BL-007→v1.0.5) refleja un cambio de umbral/cobertura del analizador entre esas mediciones, no una regresión repentina — ambas corridas BL-007 y v1.0.5 son consistentes entre sí (62→64, +2).

---

## 3. Análisis por BC

### competencia (ES Core Domain)

```
BL-001: 0.466  →  BL-002: 0.448 ↓  →  BL-003: 0.616 ↑  →  BL-004: 0.621 =  →  BL-005: 0.459 ↓  →  BL-006: 0.459 =
```

**Patrón en U:** degradación fuerte en BL-003/BL-004 (SP3 agregó muchos aggregates y value objects al dominio ES — alta Ce), recuperación significativa en BL-005 (SP5: refactoring SP-ADJ-07 y callback unification).

**Umbral de alerta interno:** se fijó 0.70 en BL-003 ("si supera 0.70, evaluar nuevas abstracciones"). El BC nunca superó ese umbral. BL-005/BL-006 en 0.459 — zona de advertencia, no de crisis.

**Interpretación:** un BC ES con alta lógica de dominio tiende a crecer en Ce (coupling eferente) conforme se agregan events y handlers. El D no es necesariamente un defecto — refleja que el dominio ES tiene dependencias hacia tipos base (value objects, aggregate root).

### identidad (CRUD Generic)

```
BL-003: 0.870 → BL-004: 0.870 = → BL-005: 0.669 ↓ → BL-006: 0.652 ↓ → v1.0.5: 0.673 ↑
```

**Zone of Pain persistente:** D muy alto (0.87) durante SP3/SP4. La mejora en BL-005 (0.669) y BL-006 (0.652) se debe al refactoring de SP-ADJ-11 que restructuró domain/ de identidad. La tendencia decreciente se revierte levemente en v1.0.5 (0.673): SP-ADJ-12 agregó `agregar_rol()`/`quitar_rol()` al aggregate (más concreción, sin nuevas abstracciones) — consistente con el aumento paralelo de FeatureEnvy en identidad detectado en `backend-ck.md` (8→12 issues).

**Decisión arquitectónica:** no intervenir en v1.0. BC Identidad es CRUD genérico con alta estabilidad (Ca alto) y baja abstracción (interfaces mínimas) — Zone of Pain esperada y aceptada. El leve repunte post-SP-ADJ-12 no cambia esa decisión, pero es la señal más clara de "costo arquitectónico" que dejó el modelo multi-rol extendido.

### registro (CRUD Supporting)

```
BL-003: 0.563 → BL-004: 0.563 = → BL-005: 0.592 ↑ → BL-006: 0.583 ↓ → v1.0.5: 0.589 ↑
```

**Estable con leve variación:** el incremento en BL-005 (0.592) coincide con SP-ADJ-11 que agregó entidades Juez y Organizador (más infraestructura concreta → Ce sube → D sube). La corrección en BL-006 (0.583) refleja estabilización post-refactoring, y el pequeño repunte en v1.0.5 (0.589) coincide con `Inscripcion.estado_aceptacion` de SP-ADJ-12 — mismo patrón que en BL-005: nueva funcionalidad concreta sobre un aggregate ya grande, sin agregar abstracción nueva.

### torneo (CRUD Supporting)

```
BL-003: 0.474 → BL-004: 0.641 ↑ → BL-005: 0.476 ↓ → BL-006: 0.479 =
```

**Anomalía en BL-004:** el salto 0.474 → 0.641 en BL-004 es el movimiento más brusco de todo el dataset. SP4 agregó dependencias cruzadas de torneo con los nuevos BCs (Identidad, Notificaciones). La recuperación en BL-005 (0.476) fue inmediata — el refactoring de SP-ADJ-07 desacoplé esas dependencias.

### shared (Dominio Compartido)

```
BL-001: 0.500 → BL-002: 0.500 = → BL-003: 0.611 ↑ → BL-004: 0.635 ↑ → BL-005: 0.635 = → BL-006: 0.635 =
```

**Crecimiento temprano, luego estable:** shared creció en D a medida que los BCs lo importaron (Ce de shared es alto — todos lo usan). Se estabilizó en 0.635 desde BL-004. Reducir D en shared requeriría reestructurar el módulo base — costo/beneficio desfavorable; diferido post-v1.0.

### notificaciones (ES Generic)

```
BL-005: 0.450 → BL-006: 0.450 =
```

**Estable desde introducción.** BC con Event Sourcing exactly-once. D=0.45 refleja balance entre abstracción (puertos de notificación) y concreción (adaptadores Email/Push).

---

## 4. Comparativa ES vs CRUD en la métrica D

| BC | Tipo | D BL-006 | D v1.0.5 (HEAD) | Posición (v1.0.5) |
|----|------|:--------:|:---------------:|----------|
| notificaciones | ES | 0.450 | 0.450 = | Mejor D de los ES |
| competencia | ES (Core) | 0.459 | 0.459 = | Segundo mejor global |
| torneo | CRUD | 0.479 | 0.479 = | |
| registro | CRUD | 0.583 | 0.589 ↑ | |
| shared | Shared | 0.635 | 0.635 = | |
| identidad | CRUD | 0.652 | 0.673 ↑ | Mayor D global |

**Hallazgo (se mantiene tras SP7/SP-ADJ-12/13):** los BCs ES siguen con D sistemáticamente menor que los BCs CRUD. El patrón es contraintuitivo — se esperaría que la mayor complejidad de ES generara más D — pero es consistente con el análisis de CC por capa: ES mantiene el dominio limpio y abstracto, lo que reduce A+I→D. Los únicos dos BCs que se movieron desde BL-006 (registro, identidad) son ambos CRUD y ambos recibieron el modelo multi-rol de SP-ADJ-12 — el gap ES vs CRUD se **amplió levemente**, no se cerró.

Los BCs CRUD tienden a Zone of Pain (alta estabilidad, baja abstracción) porque tienen pocos puertos y muchas implementaciones concretas.

---

## 5. Interpretación para el experimento IEDD

1. **ArchitectAnalyst como gate de tendencia, no de instancia:** ningún valor puntual de D disparó un bloqueo. El valor está en detectar tendencias: competencia casi llega a 0.70 en BL-004, lo que generó una decisión preventiva de refactoring en SP-ADJ-07.

2. **Los BCs CRUD estructuralmente en Zone of Pain:** identidad, registro, shared tienen D alto por diseño, no por descuido. El ArchitectAnalyst confirma que la decisión deliberada de no abstraer los BCs genéricos es consistente y estable.

3. **SP-ADJ-11 visible en la métrica D:** el delta de D en registro (0.563→0.592) es evidencia cuantitativa del costo arquitectónico de incorporar dos nuevas entidades (Juez + Organizador) en un BC CRUD preexistente. Costo aceptado y controlado.

4. **Umbral efectivo:** el umbral interno de 0.70 funcionó como criterio de decisión claro — se monitoreó, se anticipó el riesgo, se resolvió. Proponer como umbral recomendado en el paper IEDD.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.2 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — `quality/reports/architectanalyst/v1.0.5-report.json` — PLAN-METRICAS.md §B.2 (Ronda 2)*
