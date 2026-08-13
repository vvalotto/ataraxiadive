# Reporte de Métricas — AtaraxiaDive

> Síntesis ejecutiva de todas las categorías de métricas
> Medición original: rama doc/metricas · 2026-05-18 (BL-006, tag v1.0.0)
> **Recálculo (Ronda 2): 2026-08-13 · HEAD `main` post SP7 + SP-ADJ-12 + SP-ADJ-13 · tag v1.0.5**
> Fuente: `docs/metricas/**/*.md` — 17 documentos de detalle, todos recalculados
> Experimento: IEDD (Iterative Evidence-Driven Development)

---

## 0. Por qué se recalculó

La medición original (2026-05-18) cerraba en **BL-006 / v1.0.0** (fin de SP6). El proyecto
completo cerró 14 días después con **SP7** (despliegue en Fly.io + manual de usuario),
**SP-ADJ-12** (correcciones post-producción) y **SP-ADJ-13** (ejecución real del torneo Puerto
Madryn 2026 + fixes de UI), alcanzando el tag **v1.0.5**. Esta ronda recalcula las 17 métricas
contra el estado final del proyecto, con foco en **qué cambió y qué no** entre BL-006 y v1.0.5.

**Resultado más importante de la Ronda 2:** el crecimiento del proyecto en esos 77 días
adicionales fue mínimo y **quirúrgicamente localizado**. Cuatro métricas independientes —
SLOC, Halstead, cobertura de tests y endpoints REST — señalan **exactamente los mismos dos BCs**
(`registro`, `identidad`) como el único lugar del sistema que cambió. Los otros 6 BCs
(`competencia`, `torneo`, `resultados`, `notificaciones`, `shared`, `app`) son bit-a-bit
idénticos a la medición del 2026-05-18.

---

## Resumen Ejecutivo

| Categoría | Métrica clave | Valor BL-006 | Valor v1.0.5 | Evaluación |
|-----------|--------------|:-----:|:-----:|:----------:|
| Tamaño backend | SLOC total src | 12 961 | **13 219** (+2.0%, post-limpieza) | — |
| Tamaño frontend | SLOC TypeScript | 15 637 | **15 768** (+0.8%) | — |
| Cobertura de tests | Global (pytest-cov) | 95.3% | **95.35%** (post-limpieza de código muerto — ver §5.3) | ✅ |
| Ratio test/código | Unit+integration / src | 1.55 | **1.55** (sin cambio) | ✅ |
| Complejidad | CC domain/ promedio | 1.89 | **1.86** | ✅ |
| Mantenibilidad | MI domain/ promedio | 90.07 / 100 | **88.02 / 100** | ✅ |
| Cohesión OO | Clases LCOM > 1 | 10 / 303 (3.3%) | **10 / 309 (3.2%)** | ✅ |
| Acoplamiento | I gradiente domain→api | 0.26 → 0.91 | **0.273 → 0.903** | ✅ |
| Diseño evolutivo | DesignReviewer CRITICAL | 0 en toda la historia | **0 — se mantiene** | ✅ |
| Deuda técnica | D ArchitectAnalyst | should_block=false | **should_block=false — se mantiene** | ✅ |
| Tamaño funcional | US funcionales entregadas | 77 en 63 días | **77 en 77 días** (SP7 aportó 0 US func.) | ✅ |
| Velocidad | Ritmo promedio | 1.22 US func./día | **1.00** (77d) / **1.22** (SP1-6, sin cambio) | ✅ |
| Overhead pipeline | Mediana por US | ~20 min | **~20 min** (sin datos nuevos, ver §7.3) | ✅ |
| Ratio ajuste | SP-ADJ / US func. | 0.60 (60%) | **0.60** (SP1-6) · **indefinido** en SP7 | ℹ️ |
| REST Endpoints | Total | 68 | **74** (+6, 100% en registro/identidad) | ℹ️ |
| BDD Scenarios | Total | 636 | **647** (+11) | ℹ️ |

---

## 1. Tamaño Estructural

### 1.1 Backend Python

| Módulo | SLOC BL-006 | SLOC v1.0.5 | Δ | Archivos | % |
|--------|:----:|:----:|:---:|:--------:|:-:|
| competencia | 5 305 | 5 305 | = | 103 | 40% |
| registro | 1 907 | **2 042** | **+135** | 52 | 15% |
| resultados | 1 801 | 1 801 | = | 34 | 14% |
| identidad | 979 | **1 102** | **+123** | 31 | 8% |
| notificaciones | 1 036 | 1 036 | = | 39 | 8% |
| torneo | 1 056 | 1 056 | = | 31 | 8% |
| shared | 306 | 306 | = | 17 | 2% |
| app (raíz) | 571 | 571 | = | 1 | 4% |
| **Total** | **12 961** | **13 219** | **+258** | **307** | 100% |

**Confirmación cruzada #1 (estructura):** el delta total (+258 SLOC, post-limpieza) coincide
exactamente con la suma de `registro` (+135) e `identidad` (+123). Ver
[`backend-raw.md`](estructurales/backend-raw.md). *(Valores post commit `b832d25` — eliminación
de 2 archivos de código muerto en `identidad`, 40 SLOC; antes de la limpieza identidad mostraba
+163 y el total +298, ver §5.3.)*

**Distribución por capa (todos los BCs):**

| Capa | SLOC BL-006 | SLOC v1.0.5 | CC prom v1.0.5 | MI prom v1.0.5 |
|------|:----:|:----:|:-----------:|:-----------:|
| domain/ | 4 158 | 4 192 | **1.86** | **88.02** |
| infrastructure/ | 1 927 | 1 935 | 2.17 | 76.12 |
| application/ | 3 402 | 3 499 | 2.12 | 73.70 |
| api/ | 2 901 | 3 062 | 1.95 | 68.69 |

**`domain/` sigue teniendo la menor complejidad ciclomática y mayor mantenibilidad del sistema**,
sin cambios en el patrón — la arquitectura hexagonal siguió protegiendo el núcleo de negocio
durante los 77 días adicionales. Ver [`backend-por-capa.md`](estructurales/backend-por-capa.md).

### 1.2 Frontend TypeScript

| Artefacto | Archivos | SLOC v1.0.5 | Δ vs BL-006 |
|-----------|:--------:|:----:|:---:|
| Páginas (pages/) | 37 | 8 134 | ver nota metodológica en `frontend-raw.md` |
| Componentes (components/) | 48 | 4 375 | conteo de archivos idéntico (~50) |
| Hooks (hooks/) | 9 | 1 133 | mismo conteo de archivos |
| API clients | 8 | 1 329 | mismo conteo de archivos |
| **Total** | **117** | **15 768** | **+131 (+0.8%)** |

**Duplicación (jscpd):** 54 clones / 932 líneas / **4.05%** (antes 55/875/3.8%) — sigue **dentro
del umbral aceptable** (< 5%). Ver [`frontend-duplicacion.md`](estructurales/frontend-duplicacion.md).

**Bundle de producción:** 673.7 kB JS (gzip 181 kB) — **prácticamente idéntico** al build previo
a SP-ADJ-13 (674.8 kB). El crecimiento de código no impactó el peso de la aplicación.

### 1.3 Tests

| Suite | Archivos BL-006 | SLOC BL-006 | Archivos v1.0.5 | SLOC v1.0.5 | Δ |
|-------|:--------:|:----:|:--------:|:----:|:---:|
| Unit + Integration | 147 | 19 721 | **149** | **20 109** | +388 |
| BDD (Python step defs) | 62 | 11 461 | **64** | **11 675** | +214 |
| BDD (Gherkin .feature) | 125 | 3 751 | **127** | **3 798** | +47 |
| **Total Python tests** | **209** | **31 182** | **213** | **31 784** | **+602** |

**Ratio test/código:** 1.55 (unit+integration) — **sin cambio**. Los tests crecieron
proporcionalmente igual o más que la producción (+388 SLOC de tests vs +258 SLOC de código de
producción, post-limpieza). Ver [`test-to-code-ratio.md`](calidad/test-to-code-ratio.md).

---

## 2. Complejidad y Mantenibilidad Backend

### 2.1 Complejidad Ciclomática (CC) por BC × capa (v1.0.5)

| BC | Tipo | domain/ CC | application/ CC | infra/ CC | api/ CC | Δ desde BL-006 |
|----|------|:----------:|:---------------:|:---------:|:-------:|:---:|
| competencia | ES | 1.74 | 1.92 | 2.16 | 1.60 | = idéntico |
| notificaciones | ES | 1.84 | 2.04 | 2.45 | — | = idéntico |
| identidad | CRUD | 1.53 | **2.52** | 2.00 | 2.64 | application bajó (3.00→2.52) |
| torneo | CRUD | 1.55 | 1.68 | 1.81 | 1.80 | = idéntico |
| registro | CRUD | 2.09 | 1.96 | 2.18 | 2.20 | ≈ estable (2.11→2.09 domain) |
| resultados | CRUD | 2.53 | 2.90 | 2.24 | 2.33 | = idéntico |
| **Global** | | **1.86** | **2.12** | **2.17** | **1.95** | ver §2.2 |

**Gradiente CC(domain) < CC(api) ≈ CC(infra) < CC(application) se mantiene** — la complejidad
legítima sigue concentrada en application/, no en domain/ ni api/.

**Hallazgo nuevo:** el CC de `identidad/application/` **bajó** de 3.00 a 2.52 pese a crecer +78
SLOC — los métodos nuevos de SP-ADJ-12 (`agregar_rol_usuario`... con el hallazgo de código muerto
en §5.3, y los efectivamente usados `agregar_rol`/`quitar_rol`) son handlers simples de baja
complejidad, no lógica densa. El crecimiento diluyó el promedio en vez de elevarlo.

**Hipótesis ES > CRUD en CC de domain/: sigue NO confirmada**, sin cambios en la conclusión desde
BL-006 (ver [`backend-por-capa.md §3`](estructurales/backend-por-capa.md)).

### 2.2 Índice de Mantenibilidad (MI) por BC × capa

| Capa | MI prom BL-006 | MI prom v1.0.5 | Interpretación |
|------|:----------:|:----------:|-----|
| domain/ | 90.07 | **88.02** | Sigue siendo la capa más mantenible del sistema |
| application/ | 77.15 | **73.70** | Baja explicada por `registro`/`identidad` (crecimiento real) |
| infrastructure/ | 82.32 | **76.12** | Ver nota metodológica de exclusión de archivos triviales |
| api/ | 73.21 | **68.69** | Sigue siendo la capa con menor mantenibilidad — routers voluminosos |

**MI > 85 se considera "altamente mantenible".** `domain/` sigue superando ese umbral (88.02).
Ver nota metodológica sobre exclusión de archivos triviales en
[`backend-por-capa.md §2`](estructurales/backend-por-capa.md) — los deltas de MI son
parcialmente sensibles al criterio de exclusión de `__init__.py` vacíos entre corridas.

### 2.3 Halstead — Métricas de Esfuerzo

| Métrica | BL-006 | v1.0.5 | Δ |
|---------|:-----------:|:-----------:|:---:|
| Volumen total (V) | 11 381 | **11 811** | +430 |
| Esfuerzo total (E) | 58 975 | **64 616** | +5 641 |
| Dificultad promedio (D) | 0.88 | ver nota¹ | — |
| **Bugs estimados (B)** | **3.79** | **3.94** | +0.15 |
| Bugs / 1 000 SLOC | 0.30 | **0.298** | ≈ igual |

¹ Metodología de ponderación distinta entre corridas — la cifra comparable directamente es
Bugs/1 000 SLOC, que se mantiene prácticamente igual pese al crecimiento.

**Confirmación cruzada #2 (Halstead):** de 8 BCs medidos, **solo `registro` e `identidad`
cambiaron** — `registro` +321 volumen/+5 274 esfuerzo, `identidad` +110 volumen/+367 esfuerzo
(post-limpieza). Los otros 6 son bit-a-bit idénticos. **3.94 bugs estimados en 13 219 SLOC →
0.298 bugs/1 000 SLOC** sigue por debajo del percentil 10 de la industria (Capers Jones: 1–25).
Ver [`backend-halstead.md`](estructurales/backend-halstead.md).

---

## 3. Métricas OO — Suite Chidamber / Kemerer

### 3.1 LCOM — Falta de Cohesión de Métodos

| BC | Tipo | Clases LCOM > 1 BL-006 | LCOM máx BL-006 | LCOM máx v1.0.5 | Patrón |
|----|------|:---------------:|:--------:|:--------:|--------|
| registro | CRUD | 2 | 4 | **5** ↑ | `Inscripcion` extendida con `estado_aceptacion` (SP-ADJ-12) |
| torneo | CRUD | 2 | 3 | 3 = | Sin cambios |
| competencia | ES | 4 | 2 | 2 = | Sin cambios |
| resultados | CRUD | 1 | 2 | 2 = | Sin cambios |
| notificaciones | ES | 1 | 2 | 2 = | Sin cambios |
| identidad | CRUD | 0 | — | — = | Mejor cohesión, sin cambios |
| shared | Shared | 0 | — | — = | Mejor cohesión, sin cambios |
| **Total** | | **10 / 303 (3.3%)** | **4** | **10 / 309 (3.2%), máx 5** | |

**Único movimiento: `Inscripcion` (registro) subió de LCOM=4 a LCOM=5.** Todas las demás clases
con LCOM > 1 son idénticas a BL-006. Ver [`backend-ck.md §1`](estructurales/backend-ck.md).

### 3.2 CBO / FanOut — Acoplamiento Eferente

| BC | Capa | Módulo | FanOut BL-006 | FanOut v1.0.5 |
|----|------|--------|:------:|:------:|
| — | raíz | `app.py` | 13 | 13 = |
| competencia | api | `router.py` | 12 | 12 = |
| resultados | api | `router.py` | 12 | 12 = |
| **registro** | **api** | **`router.py`** | **11** | **12 ↑** |
| resultados | application | `exportar_resultados.py` | 10 | 10 = |

**Único movimiento: `registro/api/router.py` subió de FanOut=11 a 12** — nuevos endpoints de
aceptación de inscripción y adjuntos. Todo lo demás, idéntico.

### 3.3 WMC proxy — Métodos con Complejidad Elevada

| BC | Métodos sobre umbral BL-006 | Métodos sobre umbral v1.0.5 | Δ |
|----|:--------------------:|:---:|:---:|
| competencia | 74 | **74** | = |
| resultados | 27 | **27** | = |
| registro | 18 | **21** | +3 |
| notificaciones | 10 | **10** | = |
| identidad | 8 | **9** | +1 |
| shared | 5 | **5** | = |
| torneo | 2 | **2** | = |
| **Total** | **144** | **148** | **+4** |

**`competencia` sigue con 74 métodos sobre el umbral, sin crecer desde SP6** — es más código
estable, no menos complejo relativamente. El crecimiento (+4) se concentró en `registro`/`identidad`.

### 3.4 Issues DesignReviewer por BC (todos los analizadores, v1.0.5 — nuevo)

| BC | Total issues | % del proyecto | Issues / 1 000 SLOC |
|----|:---:|:---:|:---:|
| competencia | 130 | 43.9% | 24.5 |
| registro | 42 | 14.2% | 20.6 |
| resultados | 40 | 13.5% | 22.2 |
| identidad | 25 | 8.4% | 22.7 |
| notificaciones | 18 | 6.1% | 17.4 |
| app (raíz) | 21 | 7.1% | — |
| torneo | 15 | 5.1% | **14.2 (mínimo)** |
| shared | 5 | 1.7% | 16.3 |

*Post-limpieza (commit `b832d25`): identidad bajó de 27 a 25 issues (2 de FeatureEnvy
correspondían a código muerto ya eliminado). Total del proyecto: 296 (antes 298).*

La densidad de issues por SLOC está en un rango razonablemente estrecho (14–25) sin outliers —
`competencia` tiene más issues en términos absolutos simplemente porque es 2.5–5× más grande que
el resto, no porque tenga peor calidad relativa. Ver [`backend-ck.md §5`](estructurales/backend-ck.md).

---

## 4. Cohesión y Acoplamiento — Ca / Ce / I / D

### 4.1 Inestabilidad I — Gradiente por capa

| Capa | I promedio BL-006 | I promedio v1.0.5 | Interpretación |
|------|:----------:|:----------:|----------------|
| domain/ | 0.26 | **0.273** | Estable — sin cambios de fondo |
| infrastructure/ | 0.59 | **0.613** | Moderado — sin cambios de fondo |
| application/ | 0.73 | **0.721** | Inestable — sin cambios de fondo |
| api/ | 0.91 | **0.903** | Hoja del grafo — sin cambios de fondo |

**El gradiente I(domain) < I(infra) < I(application) < I(api) se mantiene** — verificado de nuevo
con Ca/Ce recalculados desde cero sobre HEAD v1.0.5. Las variaciones (±0.02) son ruido de
crecimiento normal (309 vs 246 módulos analizados por ArchitectAnalyst), no señal de degradación.

### 4.2 Distancia Main Sequence (D) por BC

| BC | Tipo | D BL-006 | D v1.0.5 | Zona v1.0.5 |
|----|------|:----------:|:----------:|------|
| resultados | CRUD | ≤ 0.30 | **≤ 0.30** = | ✅ Main Sequence |
| notificaciones | ES | 0.450 | **0.450** = | Alejado |
| competencia | ES (Core) | 0.459 | **0.459** = | Alejado |
| torneo | CRUD | 0.479 | **0.479** = | Alejado |
| registro | CRUD | 0.583 | **0.589** ↑ | CRITICAL |
| shared | Shared | 0.635 | **0.635** = | Zone of Pain |
| identidad | CRUD | 0.652 | **0.673** ↑ (máximo) | Zone of Pain |

**Confirmación cruzada #3 (arquitectura):** los únicos dos BCs que se movieron en la métrica D
son, de nuevo, `registro` e `identidad` — mismo patrón que en SLOC, Halstead y LCOM. `identidad`
es ahora el BC con mayor D del proyecto (0.673, antes 0.652). Causa: SP-ADJ-12 agregó comandos
concretos (`agregar_rol`/`quitar_rol`) sin nuevas abstracciones — A bajó de 0.10 a 0.08. Ver
[`architectanalyst-d.md`](calidad/architectanalyst-d.md).

**should_block sigue en `false`** en todas las mediciones, incluida v1.0.5 (3 CRITICAL, 64
WARNING — ArchitectAnalyst nunca bloqueó el cierre de un SP ni del proyecto).

---

## 5. Calidad Evolutiva

### 5.1 DesignReviewer — Evolución de issues

| SP | Issues totales | CRITICAL | Tendencia |
|----|:--------------:|:--------:|:---------:|
| SP2 | 35 | 0 | Línea base |
| SP3 | 72 | 0 | ↓ Mejora |
| SP4 | 145 | 0 | = Estable |
| SP5 | 240 | 0 | ↑ (nuevo código ES) |
| SP6 (SP-ADJ-11) | 287 | 0 | ↓↓ Mínimo histórico relativo |
| SP7 + SP-ADJ-12 + SP-ADJ-13 (antes de la limpieza) | 298 | 0 | ↑ +11 |
| **SP7 + SP-ADJ-12 + SP-ADJ-13 (post-limpieza, v1.0.5 actual)** | **296** | **0** | **↑ +9 — el salto más chico de toda la serie** |

**0 CRITICAL se mantiene en toda la historia del proyecto, sin excepción, hasta el cierre.** El
crecimiento de +9 issues netos en los últimos 77 días es el incremento absoluto más pequeño de
toda la serie histórica — consistente con que fue un período de estabilización, no de construcción.

### 5.2 Cobertura de tests

| Capa | Cobertura BL-006 | Cobertura v1.0.5 (post-limpieza) | Δ |
|------|:---------:|:---------:|:---:|
| domain/ | 97.3% | **97.3%** | = |
| infrastructure/ | 94.0% | **94.0%** | = |
| application/ | 93.6% | **93.7%** | ≈ = (ver §5.3) |
| **Global** | **95.3%** | **95.35%** | ≈ = (ver §5.3) |

### 5.3 Hallazgo y corrección — código muerto detectado y eliminado en identidad

**Hallazgo (Ronda 2, antes de la limpieza):**
`src/identidad/application/commands/agregar_rol_usuario.py` y `.../quitar_rol_usuario.py` tenían
**0% de cobertura (40 sentencias, 0 cubiertas)**. Verificado con grep: **nunca estuvieron
importados** en `router.py`, `app.py` ni en ningún test — el router usaba en su lugar
`agregar_rol.py`/`quitar_rol.py`, que sí están 100% cubiertos. Era un residuo de iteración de
SP-ADJ-12 (una primera versión reemplazada sin eliminar el archivo original), no un gap real de
testing. La cobertura global había caído aparentemente a 94.7% por esta causa.

**Corrección aplicada (commit `b832d25`, 2026-08-13):** se eliminaron ambos archivos. Verificado
antes de borrar (grep confirmó cero referencias externas) y después de borrar: 1049 tests
passed sin cambios, DesignReviewer 0 CRITICAL/296 WARNING (sin regresiones), cobertura global
**95.35%** — prácticamente idéntica a BL-006 (95.3%), confirmando numéricamente que el resto del
sistema nunca perdió cobertura real. Ver [`cobertura-tests.md §3`](calidad/cobertura-tests.md).

---

## 6. Tamaño Funcional

### 6.1 Proxies de tamaño funcional — v1.0.5

| BC | Endpoints BL-006 | Endpoints v1.0.5 | Δ |
|----|:-------------:|:-------------:|:---:|
| competencia | 24 | 24 | = |
| **registro** | 20 | **23** | **+3** |
| torneo | 15 | 15 | = |
| **identidad** | 6 | **9** | **+3** |
| resultados | 3 | 3 | = |
| notificaciones | 0 | 0 | = |
| **Total** | **68** | **74** | **+6** |

**Confirmación cruzada #4 (superficie API):** los +6 endpoints nuevos están 100% en `registro`
(+3, aceptación de inscripción + adjuntos) e `identidad` (+3, `POST/DELETE /auth/me/roles`) —
cuarta métrica independiente (junto con SLOC, Halstead, D arquitectónico) que apunta exactamente
al mismo par de BCs como el único lugar donde el sistema cambió. Ver
[`tamano-funcional.md §3`](productividad/tamano-funcional.md).

### 6.2 Distribución de endpoints por método HTTP

| GET | POST | PUT | PATCH | DELETE |
|:---:|:----:|:---:|:-----:|:------:|
| 30 (41%) | 26 (35%) | 12 (16%) | 4 (5%) | 2 (3%) |

**Sistema sigue orientado a comandos (GET+POST = 76%, antes 77%)** — sin cambio de patrón. Los
nuevos PATCH/DELETE corresponden a aceptación de inscripción y a quitar rol, respectivamente.

### 6.3 BDD Scenarios

Total: **647** (antes 636, +11) sobre **127 feature files** (antes 125, +2). El desglose por BC
usa un método de conteo aproximado (coincidencia de texto, no de propiedad real) ya señalado como
impreciso en la medición original — ver nota metodológica en
[`tamano-funcional.md §2.2`](productividad/tamano-funcional.md).

---

## 7. Productividad

### 7.1 Velocidad por SP

| SP | Duración | US func. | US ADJ | Ritmo func./día |
|----|:--------:|:--------:|:------:|:---------------:|
| SP1 | 10 días | 9 | 5 | 0.90 |
| SP2 | 4 días | 3 | 3 | 0.75 |
| SP3 | 7 días | 11 | 14 | 1.57 |
| SP4 | 14 días | 21 | 7 | 1.50 |
| SP5 | 13 días | 20 | 7 | 1.54 |
| SP6 | 15 días | 13 | 10 | 0.87 |
| **SP1–SP6** | **63 días** | **77** | **46** | **1.22** |
| SP7+ADJ-12+ADJ-13 | 14 días | **0*** | 8 | **N/A** |
| **Proyecto completo** | **77 días** | **77** | **54** | **1.00 (acumulado)** |

\* **Hallazgo metodológico nuevo:** SP7 no generó US funcionales porque sus dos incrementos
(despliegue en Fly.io, manual de usuario MkDocs) no son US-IEDD de dominio con
precondición/postcondición formal. El ritmo acumulado cae de 1.22 a 1.00 US func./día no porque
el equipo se hizo más lento, sino porque los últimos 14 días fueron 100% estabilización/cierre,
sin nuevo dominio. Ver [`velocidad-sp.md §5-6`](productividad/velocidad-sp.md).

### 7.2 Ratio SP-ADJ / US funcionales

Sin cambios en SP1–SP6 (60% global). **El ratio queda indefinido para SP7** (8 US de ajuste / 0
US funcionales) — no por ineficiencia, sino porque la métrica fue diseñada para sprints de
construcción activa, no para fases de cierre. Ver
[`sp-adj-ratio.md §1`](productividad/sp-adj-ratio.md).

### 7.3 Overhead del pipeline IEDD

**Sin datos nuevos.** Se buscó en `docs/reports/`, `.cm/` y los planes de SP-ADJ-12/13 — ninguna
de las 10 US/incrementos del período de cierre tiene registro de tiempo real. El dataset sigue
siendo n=34 (mediana ~20 min), y la cobertura relativa de tracking **empeoró** de 28% (34/123) a
26% (34/131) porque el denominador de US totales creció sin que el tracker se usara. Es la señal
más clara de que la disciplina de tracking manual no se sostiene sin automatización — ver
[`overhead-pipeline.md §7.4`](productividad/overhead-pipeline.md).

---

## 8. Conclusiones para el Paper IEDD

### 8.1 La arquitectura hexagonal se sostuvo, verificada dos veces con 3 meses de diferencia

El gradiente I(domain=0.273) < I(infra=0.613) < I(app=0.721) < I(api=0.903) se recalculó
completamente desde cero (no se copió el resultado anterior) y reprodujo el mismo patrón que
BL-006 con variaciones de ±0.02. Esta es una verificación independiente más fuerte que la
original: no solo el diseño *fue* correcto al momento de medirlo, sino que **se mantuvo correcto**
77 días y 429 SLOC adicionales después, sin intervención dedicada de arquitectura.

### 8.2 El crecimiento post-construcción fue quirúrgico, con cuádruple confirmación

Cuatro métricas completamente independientes — SLOC (§1.1), Halstead (§2.3), métrica D
arquitectónica (§4.2) y endpoints REST (§6.1) — señalan **exactamente los mismos dos BCs**
(`registro`, `identidad`) como el único lugar donde el sistema cambió entre BL-006 y v1.0.5. Los
otros 6 BCs no cambiaron ni un archivo, ni una línea, ni un endpoint. Esto es evidencia fuerte de
que SP7 + SP-ADJ-12 + SP-ADJ-13 fueron un cierre acotado, no una segunda fase de construcción —
y de que el pipeline IEDD, incluso fuera de su fase de mayor disciplina, no generó dispersión de
cambios no relacionados ("scope creep") en el resto del sistema.

### 8.3 ES vs CRUD sigue sin diferenciar en métricas de calidad

Todas las hipótesis re-verificadas en la Ronda 2 (CC domain/, LCOM, I domain/) mantienen
exactamente las mismas conclusiones que en BL-006 — no confirmadas. El paradigma ES vs CRUD no es
lo que las métricas de calidad diferencian; la complejidad intrínseca del BC sí.

### 8.4 El pipeline IEDD no fue el problema — el tracking manual sí

La mediana de 20 min/US de BL-006 sigue siendo el único dato disponible al cierre del proyecto:
**cero de las 10 US/incrementos de la fase de cierre tienen registro de tiempo.** Esto no
contradice la hipótesis H-4.1 original (el overhead de pipeline no es estructural) — la refuerza
con un dato adicional: incluso al final de un proyecto de 77 días con el método completamente
interiorizado, la disciplina de tracking manual se abandonó. La recomendación original de
instrumentar el tracker automáticamente desde Fase 0 queda más justificada, no menos.

### 8.5 La deuda técnica siguió siendo medible, decreciente en tasa, y con un límite metodológico nuevo

- Issues/US: la serie 17.7→2.4 (SP2→SP6) no tiene continuación limpia en SP7 porque el
  denominador (US funcionales) fue 0 — **el ratio SP-ADJ como métrica no está definido fuera de
  fases de construcción activa**, un hallazgo metodológico nuevo para el paper.
- should_block: false en todas las baselines, incluida la medición final v1.0.5.
- LCOM > 1: 3.2% de clases (antes 3.3%) — el único cambio es `Inscripcion` (registro), que
  siguió creciendo en la misma dirección deliberada ya documentada en BL-006.
- Bugs estimados Halstead: 3.94 (antes 3.79) — 0.298 bugs/1 000 SLOC (percentil < 10 industria,
  sin cambio de categoría).

**El sistema de quality gates funcionó como monitor de deuda hasta el último commit del
proyecto** — nunca bloqueó, nunca acumuló CRITICAL, y el único gap real encontrado (código muerto
en `identidad`, §5.3, ya eliminado en commit `b832d25`) fue detectado precisamente *por* este
ejercicio de recálculo de métricas, no por el pipeline de desarrollo — una limitación honesta a
documentar: las métricas agregadas (cobertura global) pueden ocultar hallazgos puntuales (archivos
huérfanos) que solo aparecen al mirar el desglose por archivo. El hecho de que se haya detectado
*y corregido* dentro del mismo ciclo de trabajo es, en sí mismo, evidencia a favor del proceso.

---

## Comparación contra Benchmarks de Industria

Ver [`BENCHMARK-INDUSTRIA.md`](BENCHMARK-INDUSTRIA.md) — clasifica primero el tipo de aplicación
(MIS/vertical SaaS, riesgo bajo-medio, proyecto pequeño, equipo atípico de 1 desarrollador + IA) y
compara calidad y productividad contra benchmarks de industria específicos a ese contexto (ISBSG,
Capers Jones, encuestas de cobertura de tests, McCabe, SonarQube, estudios de Copilot 2025).

---

## Índice de Documentos de Detalle

| Categoría | Documento | Contenido | Estado Ronda 2 |
|-----------|-----------|-----------|:---:|
| Estructural | [backend-raw.md](estructurales/backend-raw.md) | LOC/SLOC por BC y capa | ✅ recalculado |
| Estructural | [backend-cc.md](estructurales/backend-cc.md) | CC radon por BC × función | ✅ recalculado |
| Estructural | [backend-mi.md](estructurales/backend-mi.md) | MI radon por BC × módulo | ✅ recalculado |
| Estructural | [backend-halstead.md](estructurales/backend-halstead.md) | V, E, D, B por BC | ✅ recalculado |
| Estructural | [backend-por-capa.md](estructurales/backend-por-capa.md) | CC + MI + SLOC agregados | ✅ recalculado |
| Estructural | [backend-ck.md](estructurales/backend-ck.md) | LCOM, CBO/FanOut, WMC proxy + issues por BC | ✅ recalculado |
| Estructural | [backend-acoplamiento.md](estructurales/backend-acoplamiento.md) | Ca, Ce, I, A, D por BC × capa | ✅ recalculado |
| Estructural | [frontend-raw.md](estructurales/frontend-raw.md) | SLOC TypeScript por artefacto + bundle | ✅ recalculado |
| Estructural | [frontend-duplicacion.md](estructurales/frontend-duplicacion.md) | jscpd — clones y duplicación | ✅ recalculado |
| Calidad | [cobertura-tests.md](calidad/cobertura-tests.md) | pytest-cov por BC × capa + hallazgo código muerto | ✅ recalculado |
| Calidad | [test-to-code-ratio.md](calidad/test-to-code-ratio.md) | Ratio SLOC tests / SLOC src | ✅ recalculado |
| Calidad | [designreviewer-evolucion.md](calidad/designreviewer-evolucion.md) | Serie temporal issues INC→SP | ⏳ no recalculado — sin nuevos hitos INC individuales en el período |
| Calidad | [architectanalyst-d.md](calidad/architectanalyst-d.md) | D por BC en BL-001→v1.0.5 | ✅ recalculado |
| Productividad | [velocidad-sp.md](productividad/velocidad-sp.md) | US/día por SP + cierre de proyecto | ✅ recalculado |
| Productividad | [sp-adj-ratio.md](productividad/sp-adj-ratio.md) | Ratio ADJ / funcionales | ✅ recalculado |
| Productividad | [overhead-pipeline.md](productividad/overhead-pipeline.md) | Tiempo real por US (n=34, sin datos nuevos) | ✅ revisado |
| Productividad | [tamano-funcional.md](productividad/tamano-funcional.md) | US, BDD scenarios, endpoints | ✅ recalculado |

---

*Generado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §7 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §6 Ronda 2 completa*
*Actualizado post-limpieza: 2026-08-13 — commit `b832d25` (eliminación de código muerto en identidad, hallado durante la Ronda 2)*
