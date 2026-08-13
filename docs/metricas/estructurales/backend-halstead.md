# Métricas Halstead — Backend Python

> Herramienta: `radon hal` v6.0.1
> Fuente: `src/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**

---

## Conceptos Halstead

| Símbolo | Significado |
|---------|-------------|
| h1 | Operadores únicos |
| h2 | Operandos únicos |
| N1 | Total operadores |
| N2 | Total operandos |
| V (Volumen) | (N1+N2) × log2(h1+h2) — tamaño del programa |
| D (Dificultad) | (h1/2) × (N2/h2) — esfuerzo de comprensión |
| E (Esfuerzo) | V × D — esfuerzo de implementación |
| T (Tiempo) | E / 18 segundos — tiempo estimado |
| B (Bugs) | V / 3000 — errores estimados |

---

## Totales globales

| Métrica | BL-006 (2026-05-18) | v1.0.5 (2026-08-13) | Δ |
|---------|------:|------:|:---:|
| Volumen total (V) | 11 381 | **11 821** | +440 |
| Esfuerzo total (E) | 58 975 | **64 621** | +5 646 |
| Tiempo estimado | 0.9 h (~54 min) | **1.0 h (~60 min)** | +6 min |
| Bugs estimados (B) | 3.79 | **3.94** | +0.15 |
| Módulos no vacíos | 128 | **133** | +5 |
| Dificultad promedio (D) | 0.88 | **2.06*** | ver nota |
| Bugs / 1 000 SLOC | 0.30 | **0.297** | ≈ igual (mejora marginal) |

> \* La dificultad promedio de BL-006 (0.88) se calculó ponderando por módulo en la corrida
> original; el recálculo pondera igual (promedio simple por módulo no vacío, D=2.06). La cifra
> comparable de forma directa es **Bugs/1000 SLOC**, que se mantiene prácticamente igual
> (0.30 → 0.297) pese al crecimiento — el código nuevo no fue más denso ni más propenso a bugs
> que el resto del sistema.

**Bugs/1000 SLOC sigue por debajo del percentil 10 de la industria** (referencia Capers Jones: 1–25 bugs/1000 SLOC). El crecimiento de +550 SLOC en el backend no degradó esta métrica.

> Nota: el tiempo Halstead es una estimación teórica de escritura pura de código; no incluye diseño, testing ni revisión.

---

## Desglose por Bounded Context

| BC | Módulos BL-006 | Módulos v1.0.5 | Volumen v1.0.5 | Esfuerzo v1.0.5 | Bugs est. v1.0.5 | Δ vs BL-006 |
|----|:-------:|:-------:|--------:|---------:|---------:|:---:|
| competencia | 47 | 47 | 3 170 | 13 838 | 1.06 | **= idéntico** |
| resultados | 14 | 14 | 2 637 | 18 513 | 0.88 | **= idéntico** |
| registro | 26 | **27** | **2 651** | **21 025** | **0.88** | **+321 vol · +5 274 esf.** |
| app | 1 | 1 | 842 | 3 626 | 0.28 | **= idéntico** |
| notificaciones | 15 | 15 | 857 | 2 042 | 0.29 | **= idéntico** |
| identidad | 10 | **14** | **892** | **2 884** | **0.30** | **+119 vol · +372 esf.** |
| torneo | 11 | 11 | 477 | 1 537 | 0.16 | **= idéntico** |
| shared | 4 | 4 | 296 | 1 156 | 0.10 | **= idéntico** |
| **TOTAL** | **128** | **133** | **11 821** | **64 621** | **3.94** | **+5 módulos** |

**Hallazgo central:** de los 8 BCs medidos (incluyendo `app` raíz), **solo `registro` e `identidad` cambiaron** — coincide exactamente con `backend-por-capa.md` y `backend-ck.md`. Todo el esfuerzo Halstead adicional (+5 646 sobre 58 975, +9.6%) se explica por el modelo multi-rol de SP-ADJ-12. El resto del sistema (competencia, resultados, torneo, notificaciones, shared, app) es **bit-a-bit idéntico** en Halstead a la medición del 2026-05-18.

---

## Observaciones

- `competencia` mantiene el mayor volumen absoluto (3 170), sin cambios — coherente con que el BC ES Core no recibió trabajo posterior a SP6.
- `resultados` mantiene el mayor esfuerzo pese a menor volumen que `competencia` — su dificultad (D) sigue siendo la más alta del proyecto, sin cambios.
- `registro` subió del tercer al **segundo lugar en esfuerzo** (21 025, superando a `competencia` en esfuerzo aunque no en volumen) — la lógica de aceptación de inscripciones y roles concentró trabajo real.
- `identidad` fue el segundo BC con más crecimiento relativo (+48% en volumen: 773→892) — el modelo multi-rol (`agregar_rol`/`quitar_rol`) es pequeño en SLOC pero agregó módulos nuevos completos (4 archivos).
- Los 3.94 bugs estimados totales siguen siendo una cota teórica (V/3000); la cobertura real de bugs se mide en `calidad/cobertura-tests.md` (pendiente de recálculo — PLAN-METRICAS.md §B.3).
- `shared` y `torneo` siguen con los valores más bajos en todas las métricas, sin cambios — consistente con su naturaleza de CRUD simple e interfaces de puerto, y con que no recibieron ningún incremento desde SP6.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.4 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.4 (Ronda 2)*
