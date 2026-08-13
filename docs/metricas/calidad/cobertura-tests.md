# Cobertura de Tests — AtaraxiaDive

> Fuente: `pytest-cov` sobre `tests/unit/` + `tests/integration/`
> Herramienta: pytest-cov · cobertura de sentencias (`--cov=src`)
> Fecha de ejecución original: 2026-05-18 · **Recálculo Ronda 2: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> **Actualizado post-limpieza: 2026-08-13 — commit `b832d25`, eliminación de código muerto (ver §3)**
> Referencia: PLAN-METRICAS.md §B.3

---

## 1. Resumen global

| Métrica | BL-006 (2026-05-18) | v1.0.5 antes de la limpieza | **v1.0.5 actual (post-limpieza)** | Δ vs BL-006 |
|---------|------:|------:|------:|:---:|
| Tests ejecutados | 1 019 | 1 049 | **1 049** | +30 |
| Tests fallidos | 0 | 0 | **0** | = |
| Sentencias totales | 5 835 | 5 959 | **5 919** | +84 |
| Sentencias sin cubrir | 274 | 315 | **275** | +1 |
| **Cobertura total** | **95.3%** | 94.7% | **95.35%** | **+0.05 pp — prácticamente idéntica** |

Umbral mínimo del proyecto (CLAUDE.md §6): **90% en `domain/` y `application/`** — **cumplido con
margen amplio en ambas capas**.

**La caída a 94.7% detectada en la Ronda 2 fue código muerto, no un gap de testing — y ya se
corrigió.** Ver §3 para el detalle del hallazgo y la corrección aplicada.

---

## 2. Cobertura por BC

| BC | Tipo | Sentencias BL-006 | Sin cubrir BL-006 | Cobertura BL-006 | **Sentencias v1.0.5** | **Sin cubrir v1.0.5** | **Cobertura v1.0.5** |
|----|------|:----------:|:----------:|:---------:|:----------:|:----------:|:---------:|
| shared | Shared | 186 | 1 | 99.5% | 186 | 1 | **99.5%** = |
| torneo | CRUD | 463 | 3 | 99.4% | 463 | 3 | **99.4%** = |
| identidad | CRUD | 434 | 5 | 98.8% | **488** | **6** | **98.8%** = |
| registro | CRUD | 849 | 30 | 96.5% | 879 | 30 | **96.6%** = |
| notificaciones | ES | 606 | 22 | 96.4% | 606 | 22 | **96.4%** = |
| competencia | ES (Core) | 2 317 | 85 | 96.3% | 2 317 | 85 | **96.3%** = |
| resultados | CRUD | 980 | 128 | 86.9% | 980 | 128 | **86.9%** = |

**Los 7 BCs mantienen la misma cobertura porcentual que BL-006** (`identidad` creció en volumen
neto por SP-ADJ-12 — roles reales, `estado_aceptacion` — pero su % de cobertura no cambió: 98.8%
en ambas mediciones). Con la limpieza, `identidad` deja de ser un punto de atención.

---

## 3. Hallazgo (Ronda 2) y corrección aplicada — código muerto en identidad

**Hallazgo original (2026-08-13, antes de la limpieza):**
`src/identidad/application/commands/agregar_rol_usuario.py` y `.../quitar_rol_usuario.py`
(`AgregarRolUsuarioHandler`/`QuitarRolUsuarioHandler`) tenían **40 sentencias, 0 cubiertas (0%)**.
Verificado con grep: nunca estuvieron importados en `router.py`, `app.py` ni en ningún test — el
router usaba en su lugar `AgregarRolCommand`/`QuitarRolCommand` (de `agregar_rol.py`/
`quitar_rol.py`), completamente cubiertos por `tests/unit/identidad/application/test_handlers.py`.
Era un residuo de SP-ADJ-12: una primera versión de los comandos de roles reemplazada por la
versión final sin eliminar el archivo original.

**Corrección aplicada (commit `b832d25`, 2026-08-13):** se eliminaron ambos archivos. Verificado
antes de borrar (grep confirmó cero referencias externas) y después de borrar:

| Verificación | Resultado |
|---|---|
| Suite de tests | 1049 passed, 0 fallos — sin cambios |
| DesignReviewer | 0 CRITICAL · 296 WARNING (antes 298) · should_block=false |
| Cobertura global | **94.7% → 95.35%** — exactamente el valor proyectado en la Ronda 2 |

**El resto del backend nunca perdió cobertura real** — el hallazgo confirmó que la caída aparente
de la Ronda 2 era 100% atribuible a estos dos archivos, y la corrección lo demuestra
numéricamente: la cobertura global quedó a 0.05 pp de BL-006 (95.35% vs 95.3%), dentro del margen
de crecimiento normal del proyecto.

---

## 4. Cobertura por BC × capa (v1.0.5, post-limpieza)

| Capa | BL-006 | v1.0.5 antes de la limpieza | **v1.0.5 actual** |
|------|:---------:|:---------:|:---------:|
| domain/ | 97.3% | 97.3% | **97.3%** = |
| application/ | 93.6% | 92.1% | **93.7%** ≈ igual |
| infrastructure/ | 94.0% | 94.0% | **94.0%** = |
| api/ | — (cubierta por BDD) | — | — |

**`application/` vuelve a estar en línea con BL-006** (93.7% vs 93.6%) una vez removido el código
muerto — confirma que la capa nunca tuvo una regresión real de testing.

---

## 5. Gap histórico — resultados/application/ (sigue en 76.9%, sin cambios)

Sin cambios respecto a BL-006: **111 sentencias sin cubrir** en la capa application del BC
Resultados, por la lógica de ranking con múltiples variantes SPE. `resultados` no tuvo ningún
cambio de código en todo el período BL-006→v1.0.5.

**Evaluación de riesgo:** sin cambios — bajo.

---

## 6. Suite de features BDD (referencia)

| Tipo | Archivos BL-006 | SLOC BL-006 | Archivos v1.0.5 | SLOC v1.0.5 | Δ |
|------|:--------:|-----:|:--------:|-----:|:---:|
| Python (step definitions) | 62 | 11 461 | **64** | **11 675** | +2 archivos / +214 SLOC |
| Gherkin (.feature) | 125 | 3 751 | **127** | **3 798** | +2 archivos / +47 líneas |
| **Total BDD** | **187** | **15 212** | **191** | **15 473** | +4 / +261 |

Sin cambios por la limpieza (los archivos eliminados no tenían tests BDD asociados, consistente
con ser código muerto). Los features BDD cubren principalmente las capas `api/` y flujos
end-to-end.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.3 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §B.3 (Ronda 2). Snapshot: `docs/metricas/calidad/coverage.json`.*
*Actualizado post-limpieza: 2026-08-13 — commit `b832d25` (eliminación de código muerto en identidad)*
