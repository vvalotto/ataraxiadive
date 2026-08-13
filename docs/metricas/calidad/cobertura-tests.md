# Cobertura de Tests — AtaraxiaDive

> Fuente: `pytest-cov` sobre `tests/unit/` + `tests/integration/`
> Herramienta: pytest-cov · cobertura de sentencias (`--cov=src`)
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> Referencia: PLAN-METRICAS.md §B.3

---

## 1. Resumen global

| Métrica | BL-006 (2026-05-18) | v1.0.5 (2026-08-13) | Δ |
|---------|------:|------:|:---:|
| Tests ejecutados | 1 019 | **1 049** | +30 |
| Tests fallidos | 0 | **0** | = |
| Sentencias totales | 5 835 | **5 959** | +124 |
| Sentencias sin cubrir | 274 | **315** | +41 |
| **Cobertura total** | **95.3%** | **94.7% (display 95%)** | −0.6 pp |

Umbral mínimo del proyecto (CLAUDE.md §6): **90% en `domain/` y `application/`** — **sigue cumplido**.

**El total de sentencias sin cubrir subió +41 (274→315). Ese número no está distribuido: coincide
exactamente con dos archivos de 0% de cobertura en `identidad` (ver §5) — sin ellos, la cobertura
del proyecto se hubiera mantenido igual o mejorado.**

---

## 2. Cobertura por BC

| BC | Tipo | Sentencias BL-006 | Sin cubrir BL-006 | Cobertura BL-006 | Sentencias v1.0.5 | Sin cubrir v1.0.5 | Cobertura v1.0.5 |
|----|------|:----------:|:----------:|:---------:|:----------:|:----------:|:---------:|
| shared | Shared | 186 | 1 | 99.5% | 186 | 1 | **99.5%** = |
| torneo | CRUD | 463 | 3 | 99.4% | 463 | 3 | **99.4%** = |
| identidad | CRUD | 434 | 5 | 98.8% | **528** | **46** | **91.3%** ↓↓ |
| registro | CRUD | 849 | 30 | 96.5% | 879 | 30 | **96.6%** = |
| notificaciones | ES | 606 | 22 | 96.4% | 606 | 22 | **96.4%** = |
| competencia | ES (Core) | 2 317 | 85 | 96.3% | 2 317 | 85 | **96.3%** = |
| resultados | CRUD | 980 | 128 | 86.9% | 980 | 128 | **86.9%** = |

**5 de 7 BCs son bit-a-bit idénticos** a BL-006 — coherente con `backend-por-capa.md` (solo
registro/identidad recibieron cambios de producción). `registro` mejoró levemente. **`identidad`
es el único punto de atención nuevo**, y reemplaza a `resultados` como el BC con el gap más
grande en términos absolutos de sentencias sin cubrir agregadas en esta ronda (+41).

---

## 3. Hallazgo — identidad: 0% de cobertura en dos comandos huérfanos

`src/identidad/application/commands/agregar_rol_usuario.py` y `.../quitar_rol_usuario.py`
(`AgregarRolUsuarioHandler`/`QuitarRolUsuarioHandler`) tienen **40 sentencias, 0 cubiertas (0%)**.

**No es un gap de testing real — es código muerto.** Verificado con grep sobre `src/`: estos dos
archivos **no están importados en ningún lugar** (ni en `router.py`, ni en `app.py`, ni en tests).
El router (`identidad/api/router.py:299-321`) usa en su lugar `AgregarRolCommand`/`QuitarRolCommand`
(de `agregar_rol.py`/`quitar_rol.py`), que sí están completamente cubiertos por
`tests/unit/identidad/application/test_handlers.py`.

**Hipótesis:** SP-ADJ-12 dejó una primera versión de los comandos de roles (`*_usuario.py`) sin
eliminar tras reemplazarla por la versión final (`agregar_rol.py`/`quitar_rol.py`) — un residuo de
iteración, no una decisión de diseño. Se flaggeó como tarea de limpieza aparte (código muerto,
fuera del alcance de esta actualización de métricas).

**Efecto sobre la métrica:** sin estos 40 líneas huérfanas, la cobertura de `identidad` sería
(482/488) = **98.8%** — idéntica a BL-006 — y la cobertura global del proyecto sería
(5 644/5 919) = **95.35%**, prácticamente igual a BL-006 (95.3%) en vez de 94.7%. **El resto del
backend no perdió cobertura real; el número global está distorsionado por dos archivos que nunca
debieron mergearse tal cual.**

---

## 4. Cobertura por BC × capa (v1.0.5)

### domain/

| Capa global | BL-006 | v1.0.5 | Δ |
|------|:---------:|:---------:|:---:|
| domain/ | 97.3% | **97.3%** | = |
| application/ | 93.6% | **92.1%** | −1.5 pp (100% explicado por los 2 archivos huérfanos de identidad) |
| infrastructure/ | 94.0% | **94.0%** | = |
| api/ | — (cubierta por BDD) | — | = |

**`domain/` e `infrastructure/` no se movieron ni un punto porcentual.** La única capa que bajó es
`application/`, y el §3 explica por qué: los dos comandos huérfanos son ambos de `application/`.

---

## 5. Gap histórico — resultados/application/ (sigue en 76.9%, sin cambios)

Sin cambios respecto a BL-006: **111 sentencias sin cubrir** en la capa application del BC
Resultados, por la lógica de ranking con múltiples variantes SPE. Ver análisis original — sigue
vigente sin modificación, ya que `resultados` no tuvo ningún cambio de código desde el 2026-05-18.

**Evaluación de riesgo:** sin cambios — bajo.

---

## 6. Suite de features BDD (referencia)

| Tipo | Archivos BL-006 | SLOC BL-006 | Archivos v1.0.5 | SLOC v1.0.5 | Δ |
|------|:--------:|-----:|:--------:|-----:|:---:|
| Python (step definitions) | 62 | 11 461 | **64** | **11 675** | +2 archivos / +214 SLOC |
| Gherkin (.feature) | 125 | 3 751 | **127** | **3 798** | +2 archivos / +47 líneas |
| **Total BDD** | **187** | **15 212** | **191** | **15 473** | +4 / +261 |

Los features BDD cubren principalmente las capas `api/` y flujos end-to-end. El crecimiento
(+2 archivos Python, +2 Gherkin) es consistente con SP-ADJ-13 (fixes de UI verificados en
producción) y con la extensión de escenarios de aceptación de inscripciones de SP-ADJ-12.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.3 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §B.3 (Ronda 2). Snapshot: `docs/metricas/calidad/coverage.json`.*
