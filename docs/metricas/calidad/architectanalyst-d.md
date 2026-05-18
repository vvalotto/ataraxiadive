# ArchitectAnalyst — Métrica D por BC y Baseline

> Fuente: `quality/reports/architectanalyst/BL-*.json` + `.cm/baselines/BL-*.md`  
> Métrica: D = distancia a la Main Sequence = |A + I − 1| (Robert C. Martin)  
> Escala: 0 = ideal (sobre la Main Sequence) · 1 = zona de riesgo máximo  
> Umbral configurado: D > 0.30 → WARNING; umbrales CRITICAL por BC  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §B.2

---

## 1. Evolución D por BC a lo largo de las baselines

| BC | Tipo | BL-001 | BL-002 | BL-003 | BL-004 | BL-005 | BL-006 |
|----|------|:------:|:------:|:------:|:------:|:------:|:------:|
| competencia | ES (Core) | 0.466 | 0.448 | 0.616 ↑ | 0.621 = | **0.459 ↓** | 0.459 = |
| resultados | CRUD | — | 0.429 | — | — | — | — |
| registro | CRUD | — | — | 0.563 | 0.563 = | 0.592 ↑ | 0.583 ↓ |
| identidad | CRUD | — | — | 0.870 | 0.870 = | 0.669 ↓ | 0.652 ↓ |
| torneo | CRUD | — | — | 0.474 | 0.641 ↑ | 0.476 ↓ | 0.479 = |
| shared | Shared | 0.500 | 0.500 | 0.611 ↑ | 0.635 ↑ | 0.635 = | 0.635 = |
| notificaciones | ES | — | — | — | — | 0.450 | 0.450 = |

**SP correspondiente:** BL-001=SP1 · BL-002=SP2 · BL-003=SP3 · BL-004=SP4 · BL-005=SP5 · BL-006=SP6

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

`should_block` fue **false en todas las baselines** — el ArchitectAnalyst nunca bloqueó el cierre de un SP. Los issues CRITICAL reflejan BCs en Zone of Pain por diseño arquitectónico deliberado (BCs CRUD con alta estabilidad y baja abstracción).

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
BL-003: 0.870 → BL-004: 0.870 = → BL-005: 0.669 ↓ → BL-006: 0.652 ↓
```

**Zone of Pain persistente:** D muy alto (0.87) durante SP3/SP4. La mejora en BL-005 (0.669) y BL-006 (0.652) se debe al refactoring de SP-ADJ-11 que restructuró domain/ de identidad. Tendencia decreciente sana, aunque sigue por encima del umbral.

**Decisión arquitectónica:** no intervenir en v1.0. BC Identidad es CRUD genérico con alta estabilidad (Ca alto) y baja abstracción (interfaces mínimas) — Zone of Pain esperada y aceptada.

### registro (CRUD Supporting)

```
BL-003: 0.563 → BL-004: 0.563 = → BL-005: 0.592 ↑ → BL-006: 0.583 ↓
```

**Estable con leve variación:** el incremento en BL-005 (0.592) coincide con SP-ADJ-11 que agregó entidades Juez y Organizador (más infraestructura concreta → Ce sube → D sube). La corrección en BL-006 (0.583) refleja estabilización post-refactoring.

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

| BC | Tipo | D BL-006 | Posición |
|----|------|:--------:|----------|
| notificaciones | ES | 0.450 | Mejor D de los ES |
| competencia | ES (Core) | 0.459 | Segundo mejor global |
| torneo | CRUD | 0.479 | |
| registro | CRUD | 0.583 | |
| shared | Shared | 0.635 | |
| identidad | CRUD | 0.652 | Mayor D global |

**Hallazgo:** los BCs ES tienen D sistemáticamente menor que los BCs CRUD en BL-006. El patrón es contraintuitivo — se esperaría que la mayor complejidad de ES generara más D — pero es consistente con el análisis de CC por capa: ES mantiene el dominio limpio y abstracto, lo que reduce A+I→D.

Los BCs CRUD tienden a Zone of Pain (alta estabilidad, baja abstracción) porque tienen pocos puertos y muchas implementaciones concretas.

---

## 5. Interpretación para el experimento IEDD

1. **ArchitectAnalyst como gate de tendencia, no de instancia:** ningún valor puntual de D disparó un bloqueo. El valor está en detectar tendencias: competencia casi llega a 0.70 en BL-004, lo que generó una decisión preventiva de refactoring en SP-ADJ-07.

2. **Los BCs CRUD estructuralmente en Zone of Pain:** identidad, registro, shared tienen D alto por diseño, no por descuido. El ArchitectAnalyst confirma que la decisión deliberada de no abstraer los BCs genéricos es consistente y estable.

3. **SP-ADJ-11 visible en la métrica D:** el delta de D en registro (0.563→0.592) es evidencia cuantitativa del costo arquitectónico de incorporar dos nuevas entidades (Juez + Organizador) en un BC CRUD preexistente. Costo aceptado y controlado.

4. **Umbral efectivo:** el umbral interno de 0.70 funcionó como criterio de decisión claro — se monitoreó, se anticipó el riesgo, se resolvió. Proponer como umbral recomendado en el paper IEDD.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.2 completado*
