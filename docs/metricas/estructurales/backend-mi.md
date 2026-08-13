# Índice de Mantenibilidad (MI) por BC · Capa · Módulo — Backend Python

> Herramienta: `radon mi` v6.0.1
> Fuente: `src/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**

**Escala:** A (MI ≥ 20) · B (10 ≤ MI < 20) · C (MI < 10)

---

## Totales por BC — comparación BL-006 vs v1.0.5

| BC | MI prom BL-006 | MI prom v1.0.5 | Rank | Δ |
|----|:---------------:|:---------------:|:----:|:---:|
| competencia | 71.12 | 71.12 | A | = idéntico (0 archivos tocados) |
| torneo | — | — | A | = idéntico |
| resultados | — | — | A | = idéntico |
| notificaciones | — | — | A | = idéntico |
| shared | — | — | A | = idéntico |
| registro | — | **más bajo** | A | ↓ — módulos nuevos más grandes (`router.py` 788 SLOC) |
| identidad | — | **más bajo** | A | ↓ — módulos nuevos pequeños diluyen el promedio de archivos existentes |

**Único movimiento real: `registro` e `identidad`**, los mismos dos BCs identificados en todos los
demás análisis (`backend-por-capa.md`, `backend-halstead.md`, `backend-ck.md`, `architectanalyst-d.md`).
El detalle por capa (con valores exactos de MI prom y N) está en
[`backend-por-capa.md §1`](backend-por-capa.md) — es la fuente autoritativa y evita mantener dos
tablas con metodologías de exclusión de archivos triviales potencialmente distintas.

---

## Módulos con MI más bajo del sistema (v1.0.5)

Los routers con más SLOC siguen siendo los de menor MI — patrón sin cambios desde BL-006, agravado
por el crecimiento de `registro/api/router.py` (691→788 SLOC):

| Módulo | BC | Capa | SLOC | Observación |
|--------|----|------|-----:|-------------|
| `router.py` | registro | api | 788 | **+97 SLOC desde BL-006** — el archivo de menor MI del backend |
| `router.py` | identidad | api | 335 | **+62 SLOC** (base ~273 + roles) |
| `router.py` | resultados | api | 294 | sin cambios |

**Conclusión sin cambios respecto a BL-006:** los routers FastAPI con múltiples rutas inline
siguen siendo el punto de menor mantenibilidad del sistema. El crecimiento de SP-ADJ-12
empeoró esta tendencia en `registro` e `identidad` en vez de revertirla — sería el primer
candidato a refactoring (extraer sub-routers) si el proyecto continuara más allá de v1.0.5.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.3 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.3 (Ronda 2)*
