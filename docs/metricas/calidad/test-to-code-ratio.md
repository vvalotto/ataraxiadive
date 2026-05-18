# Test-to-Code Ratio — AtaraxiaDive

> Fuente: `cloc` sobre `src/` y `tests/`  
> Fecha de ejecución: 2026-05-18  
> Referencia: PLAN-METRICAS.md §B.4  
> Hipótesis: ratio > 1.0 en `domain/` (dominio más testeado que infraestructura)

---

## 1. Resumen global

| Cuerpo | Archivos Python | SLOC |
|--------|:---------------:|-----:|
| Producción (`src/`) | 254 | 12 708 |
| Tests unit + integration | 147 | 19 721 |
| Tests features BDD (Python) | 62 | 11 461 |
| Tests features BDD (Gherkin) | 125 | 3 751 |
| **Total tests (Python)** | **209** | **31 182** |

| Ratio | Valor |
|-------|------:|
| Unit + integration / src | **1.55** |
| Tests totales Python / src | **2.45** |
| Tests totales (Python + Gherkin) / src | **2.75** |

El proyecto tiene **2.45 líneas de test Python por cada línea de código de producción** — señal de una suite robusta. Con BDD incluido, el ratio sube a 2.75.

---

## 2. Ratio por BC (unit + integration)

| BC | Tipo | SLOC src | SLOC tests | Ratio |
|----|------|:--------:|:----------:|:-----:|
| competencia | ES (Core) | 5 281 | 9 851 | **1.87** |
| torneo | CRUD | 1 030 | 1 754 | **1.70** |
| identidad | CRUD | 939 | 1 521 | **1.62** |
| resultados | CRUD | 1 797 | 2 334 | **1.30** |
| notificaciones | ES | 1 006 | 1 033 | **1.03** |
| registro | CRUD | 1 815 | 1 632 | **0.90** ⚠️ |

### Observaciones

**Competencia (1.87)** — el ratio más alto. Esperado: BC con mayor lógica de dominio (Event Sourcing, estados de performance, cálculo de tarjetas) y la suite de tests más extensa del proyecto.

**Registro (0.90)** — único BC por debajo de 1.0. Causa: el BC Registro creció significativamente en SP-ADJ-11 con la incorporación de entidades Juez y Organizador (multi-rol). El código de producción creció más rápido que los tests en esa iteración. No es un riesgo inmediato — la cobertura de sentencias es 96.5% — pero indica menor inversión en tests de escenario para Registro.

**Notificaciones (1.03)** — ratio bajo para un BC con Event Sourcing. El dominio de notificaciones tiene más lógica de infraestructura (Email/Push, idempotencia) que de dominio puro, lo que reduce el volumen de tests unitarios de dominio.

---

## 3. Hipótesis §B.4 — ratio > 1.0 en domain/

La hipótesis del plan era verificar si `domain/` tiene ratio de tests superior a infraestructura.

No se puede calcular directamente el SLOC de tests *por capa* (los tests están organizados por BC, no por capa). Sin embargo, la cobertura por capa (§4 de cobertura-tests.md) es evidencia proxy:

| Capa | Cobertura | Interpretación |
|------|:---------:|----------------|
| domain/ | **97.3%** | Mayor cobertura → más tests relativos al código |
| application/ | 93.6% | Cobertura alta, algunos gaps en resultados |
| infrastructure/ | 94.0% | Cobertura sólida |
| api/ | — | Cubierta por BDD, no por unit/integration |

**Hipótesis confirmada cualitativamente:** `domain/` tiene la cobertura más alta (97.3%) y es el foco principal de los tests unitarios. La inversión en tests de dominio es proporcionalmente mayor que en infraestructura.

---

## 4. Distribución del esfuerzo de testing

```
Tests unit+integration:  19 721 SLOC  (63%)  ██████████████████████████░░░░░░░░░░░░░░
Tests BDD Python:        11 461 SLOC  (37%)  █████████████████░░░░░░░░░░░░░░░░░░░░░░
Tests BDD Gherkin:        3 751 líneas adicionales (especificación ejecutable)
```

La distribución refleja la estrategia IEDD: tests unitarios para dominio + application, BDD para verificación end-to-end de criterios de aceptación.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.4 completado*
