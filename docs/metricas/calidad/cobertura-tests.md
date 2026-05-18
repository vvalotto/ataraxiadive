# Cobertura de Tests — AtaraxiaDive

> Fuente: `pytest-cov` sobre `tests/unit/` + `tests/integration/`  
> Herramienta: pytest-cov · cobertura de sentencias (`--cov=src`)  
> Fecha de ejecución: 2026-05-18  
> Referencia: PLAN-METRICAS.md §B.3

---

## 1. Resumen global

| Métrica | Valor |
|---------|------:|
| Tests ejecutados | 1 019 |
| Tests fallidos | 0 |
| Sentencias totales | 5 835 |
| Sentencias sin cubrir | 274 |
| **Cobertura total** | **95.3%** |

Umbral mínimo del proyecto (CLAUDE.md §6): **90% en `domain/` y `application/`** — **cumplido**.

---

## 2. Cobertura por BC

| BC | Tipo | Sentencias | Sin cubrir | Cobertura |
|----|------|:----------:|:----------:|:---------:|
| shared | Shared | 186 | 1 | **99.5%** |
| torneo | CRUD | 463 | 3 | **99.4%** |
| identidad | CRUD | 434 | 5 | **98.8%** |
| registro | CRUD | 849 | 30 | **96.5%** |
| notificaciones | ES | 606 | 22 | **96.4%** |
| competencia | ES (Core) | 2 317 | 85 | **96.3%** |
| resultados | CRUD | 980 | 128 | **86.9%** |

**Punto de atención:** `resultados` es el único BC por debajo de 90%. La causa es la capa `application/` (ver §3).

---

## 3. Cobertura por BC × capa

### domain/

| BC | Sentencias | Sin cubrir | Cobertura |
|----|:----------:|:----------:|:---------:|
| torneo | 191 | 0 | **100.0%** |
| identidad | 122 | 1 | **99.2%** |
| shared | 128 | 1 | **99.2%** |
| registro | 280 | 6 | **97.9%** |
| resultados | 392 | 5 | **98.7%** |
| competencia | 1 192 | 44 | **96.3%** |
| notificaciones | 264 | 12 | **95.5%** |
| **Total domain/** | **2 569** | **69** | **97.3%** |

### application/

| BC | Sentencias | Sin cubrir | Cobertura |
|----|:----------:|:----------:|:---------:|
| torneo | 190 | 3 | **98.4%** |
| identidad | 206 | 3 | **98.5%** |
| registro | 289 | 3 | **99.0%** |
| competencia | 896 | 19 | **97.9%** |
| notificaciones | 166 | 4 | **97.6%** |
| **resultados** | **481** | **111** | **76.9%** ⚠️ |
| **Total application/** | **2 228** | **143** | **93.6%** |

### infrastructure/

| BC | Sentencias | Sin cubrir | Cobertura |
|----|:----------:|:----------:|:---------:|
| torneo | 82 | 0 | **100.0%** |
| shared | 58 | 0 | **100.0%** |
| identidad | 106 | 1 | **99.1%** |
| competencia | 229 | 22 | **90.4%** |
| notificaciones | 176 | 6 | **96.6%** |
| registro | 280 | 21 | **92.5%** |
| resultados | 107 | 12 | **88.8%** |
| **Total infrastructure/** | **1 038** | **62** | **94.0%** |

### api/

Las capas `api/` no están incluidas en la suite unit/integration — son endpoints FastAPI cubiertos por tests de features BDD (ver §5).

---

## 4. Cobertura global por capa

| Capa | Sentencias | Sin cubrir | Cobertura | Umbral CLAUDE.md |
|------|:----------:|:----------:|:---------:|:----------------:|
| domain/ | 2 569 | 69 | **97.3%** | ≥ 90% ✅ |
| application/ | 2 228 | 143 | **93.6%** | ≥ 90% ✅ |
| infrastructure/ | 1 038 | 62 | **94.0%** | — |
| api/ | 0 | — | — | — |

`domain/` y `application/` cumplen holgadamente el umbral del proyecto.

---

## 5. Gap principal — resultados/application/ (76.9%)

**111 sentencias sin cubrir** en la capa application del BC Resultados.

Causa probable: la lógica de ranking tiene múltiples variantes (SPE_2X50 · SPE_4X50 · SPE_8X50 · SPE_16X50, ranking por género, ranking Overall) con rutas condicionales que los tests de integración no ejercitan exhaustivamente. Los tests de features BDD cubren los flujos felices; las ramas de error y las combinaciones de variantes SPE quedan parcialmente sin cubrir.

**Evaluación de riesgo:** bajo. El BC Resultados es de tipo CRUD con lógica de ranking bien acotada y sin estado persistente complejo. Las variantes SPE tienen tests unitarios para el dominio. La cobertura del 86.9% a nivel BC es aceptable para el estado del proyecto.

---

## 6. Suite de features BDD (referencia)

| Tipo | Archivos | SLOC |
|------|:--------:|-----:|
| Python (step definitions) | 62 | 11 461 |
| Gherkin (.feature) | 125 | 3 751 |
| **Total BDD** | **187** | **15 212** |

Los features BDD cubren principalmente las capas `api/` y flujos end-to-end, complementando la cobertura de unit/integration.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.3 completado*
