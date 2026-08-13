# Test-to-Code Ratio — AtaraxiaDive

> Fuente: `cloc` sobre `src/` y `tests/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo Ronda 2: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> **Actualizado post-limpieza: 2026-08-13 — commit `b832d25`, eliminación de código muerto**
> Referencia: PLAN-METRICAS.md §B.4
> Hipótesis: ratio > 1.0 en `domain/` (dominio más testeado que infraestructura)

---

## 1. Resumen global

| Cuerpo | Archivos BL-006 | SLOC BL-006 | Archivos v1.0.5 | SLOC v1.0.5 | Δ SLOC |
|--------|:---------------:|-----:|:---------------:|-----:|:---:|
| Producción (`src/`) | 254 | 12 708 | **258** | **12 964** | **+256** |
| Tests unit + integration | 147 | 19 721 | **149** | **20 109** | **+388** |
| Tests features BDD (Python) | 62 | 11 461 | **64** | **11 675** | +214 |
| Tests features BDD (Gherkin) | 125 | 3 751 | **127** | **3 798** | +47 |
| **Total tests (Python)** | **209** | **31 182** | **213** | **31 784** | +602 |

| Ratio | BL-006 | v1.0.5 | Δ |
|-------|------:|------:|:---:|
| Unit + integration / src | 1.55 | **1.55** | = |
| Tests totales Python / src | 2.45 | **2.45** | = |
| Tests totales (Python + Gherkin) / src | 2.75 | **2.75** | = |

**Los tests crecieron proporcionalmente igual o más que la producción** (+388 SLOC de tests vs
+256 SLOC de código de producción, neto de la limpieza de código muerto) — el ratio global se
mantuvo **exactamente estable**. La señal de alerta de la Ronda 2 (identidad) ya se resolvió — ver
§2.

---

## 2. Ratio por BC (unit + integration)

| BC | Tipo | SLOC src BL-006 | SLOC tests BL-006 | Ratio BL-006 | SLOC src v1.0.5 | SLOC tests v1.0.5 | Ratio v1.0.5 |
|----|------|:--------:|:----------:|:-----:|:--------:|:----------:|:-----:|
| competencia | ES (Core) | 5 281 | 9 851 | 1.87 | 5 281 | 9 851 | **1.87** = |
| torneo | CRUD | 1 030 | 1 754 | 1.70 | 1 030 | 1 754 | **1.70** = |
| identidad | CRUD | 939 | 1 521 | 1.62 | **1 062** | **1 626** | **1.53** ≈ |
| resultados | CRUD | 1 797 | 2 334 | 1.30 | 1 797 | 2 334 | **1.30** = |
| notificaciones | ES | 1 006 | 1 033 | 1.03 | 1 006 | 1 033 | **1.03** = |
| registro | CRUD | 1 815 | 1 632 | 0.90 ⚠️ | **1 948** | **1 915** | **0.98** ↑ |

**4 de 6 BCs sin cambios** (competencia, torneo, resultados, notificaciones). De los dos que se
movieron:

- **`registro` mejoró** (0.90→0.98): el código de producción creció (+133 SLOC, aceptación de
  inscripciones) pero los tests crecieron más rápido en proporción (+283 SLOC) — SP-ADJ-12 sí
  invirtió en tests para esta parte.
- **`identidad` — resuelto tras la limpieza (0.90→0.98→1.53):** la Ronda 2 había detectado una
  caída a 1.48 por los 40 SLOC de código muerto (`agregar_rol_usuario.py`/`quitar_rol_usuario.py`,
  eliminados en commit `b832d25`). Con el código real de producción (+123 SLOC netos vs BL-006,
  no +163), el ratio queda en **1.53** — prácticamente en línea con el resto del sistema, tal
  como se había proyectado.

---

## 3. Hipótesis §B.4 — ratio > 1.0 en domain/ (revalidación)

No se puede calcular directamente el SLOC de tests *por capa* (los tests están organizados por
BC, no por capa). La cobertura por capa (§4 de `cobertura-tests.md`) sigue siendo la evidencia
proxy, y no cambió:

| Capa | Cobertura BL-006 | Cobertura v1.0.5 (post-limpieza) | Interpretación |
|------|:---------:|:---------:|----------------|
| domain/ | 97.3% | **97.3%** = | Mayor cobertura → más tests relativos al código, sin cambios |
| application/ | 93.6% | **93.7%** ≈ | Resuelto — la caída a 92.1% de la Ronda 2 era código muerto, ya eliminado |
| infrastructure/ | 94.0% | **94.0%** = | Sin cambios |
| api/ | — | — | Cubierta por BDD, no por unit/integration |

**Hipótesis confirmada cualitativamente, sin cambios reales:** `domain/` mantiene la cobertura más
alta del sistema, y `application/` quedó a la par de BL-006 una vez removido el código muerto
(ver `cobertura-tests.md §3`).

---

## 4. Distribución del esfuerzo de testing (v1.0.5)

```
Tests unit+integration:  20 109 SLOC  (63%)  ██████████████████████████░░░░░░░░░░░░░░
Tests BDD Python:        11 675 SLOC  (37%)  █████████████████░░░░░░░░░░░░░░░░░░░░░░
Tests BDD Gherkin:        3 798 líneas adicionales (especificación ejecutable)
```

Distribución porcentual idéntica a BL-006 (63%/37%) — la estrategia IEDD de testing (unitario
para dominio + application, BDD para aceptación end-to-end) se mantuvo consistente durante
SP7/SP-ADJ-12/13.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.4 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §B.4 (Ronda 2)*
*Actualizado post-limpieza: 2026-08-13 — commit `b832d25` (eliminación de código muerto en identidad)*
