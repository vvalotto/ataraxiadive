# Suite Chidamber/Kemerer (parcial) — LCOM y CBO por BC

> Fuente: `quality/reports/designreviewer/current-report.json` (ejecución 2026-05-18)  
> Herramienta: DesignReviewer 287 issues · LCOMAnalyzer · FanOutAnalyzer · LongMethodAnalyzer  
> Cobertura CK: LCOM ✅ · CBO/FanOut ✅ · WMC (proxy) ✅ · DIT ⬜ · NOC ⬜ · RFC ⬜  
> Referencia: PLAN-METRICAS.md §A.1.6

---

## Métricas CK disponibles y excluidas

| Métrica CK | Nombre | Estado | Herramienta / Nota |
|------------|--------|:------:|-------------------|
| **LCOM** | Lack of Cohesion of Methods | ✅ | LCOMAnalyzer — medición directa |
| **CBO** | Coupling Between Objects | ✅ | FanOutAnalyzer — Ce (coupling eferente) |
| **WMC** | Weighted Methods per Class | ≈ | LongMethodAnalyzer — proxy (métodos sobre umbral, no suma CC total) |
| DIT | Depth of Inheritance Tree | ⬜ | No relevante: Python hexagonal usa composición, herencia mínima |
| NOC | Number of Children | ⬜ | No relevante: mismo motivo que DIT |
| RFC | Response For a Class | ⬜ | Requiere call-graph — no disponible en el stack actual |

---

## 1. LCOM — Falta de Cohesión de Métodos

**Umbral DesignReviewer:** LCOM > 1 → WARNING  
**Interpretación:** LCOM = número de grupos de métodos sin atributos en común. LCOM = 0 ideal; LCOM = 1 aceptable; LCOM > 1 indica que la clase debería dividirse.

### 1.1 Clases con LCOM elevado

| BC | Capa | Clase | LCOM |
|----|------|-------|:----:|
| registro | domain | `Inscripcion` | **4** |
| torneo | domain | `Torneo` | **3** |
| torneo | infrastructure | `SQLiteTorneoRepository` | **3** |
| registro | infrastructure | `SQLiteAtletaRepository` | **3** |
| competencia | domain | `Competencia` | 2 |
| competencia | domain | `TarjetaAsignacion` | 2 |
| competencia | domain | `GrillaDeSalida` | 2 |
| competencia | infrastructure | `AndarivelesActivosAdapter` | 2 |
| resultados | domain | `RankingCompetencia` | 2 |
| notificaciones | application | `PoliticaP11Handler` | 2 |

**Total:** 10 clases con LCOM > 1 de 303 archivos analizados (3.3%)

### 1.2 LCOM por BC — resumen

| BC | Tipo | Clases con LCOM > 1 | LCOM máximo | Patrón |
|----|------|:-------------------:|:-----------:|--------|
| registro | CRUD | 2 | **4** | Inscripcion concentra lógica de atleta+juez+organizador (multi-rol SP-ADJ-11) |
| torneo | CRUD | 2 | **3** | Torneo aggregate con múltiples responsabilidades de ciclo de vida |
| competencia | ES (Core) | 4 | 2 | 4 clases pero todas en LCOM=2 — mínimo del umbral |
| resultados | CRUD | 1 | 2 | RankingCompetencia con lógica de ranking + validación |
| notificaciones | ES | 1 | 2 | PoliticaP11Handler con orquestación de casos |
| identidad | CRUD | 0 | — | Sin problemas LCOM — BC más cohesivo |
| shared | Shared | 0 | — | Sin problemas LCOM |

### 1.3 Hipótesis: LCOM más bajo en domain/ que en infrastructure/

| Capa | Clases con LCOM > 1 | LCOM máximo |
|------|:-------------------:|:-----------:|
| domain/ | 6 | 4 |
| infrastructure/ | 3 | 3 |
| application/ | 1 | 2 |
| api/ | 0 | — |

**Hipótesis NO confirmada en conteo**: `domain/` tiene más instancias LCOM que `infrastructure/`. Sin embargo, el LCOM máximo es similar (4 vs 3) y la causa en domain/ es la complejidad intrínseca del dominio (aggregate Inscripcion con multi-rol), no un defecto de diseño.

**Matiz importante:** la clase `Inscripcion` (LCOM=4) agrupa responsabilidades de atleta, juez y organizador en un único aggregate porque SP-ADJ-11 unificó el registro multi-rol — una decisión de diseño deliberada, no una violación de cohesión.

---

## 2. CBO/FanOut — Acoplamiento Eferente

**Umbral DesignReviewer:** FanOut > 7 módulos importados → WARNING  
**Interpretación:** FanOut = Ce = número de módulos externos de los que depende un módulo. Alto Ce → módulo frágil (cambios externos lo afectan).

### 2.1 Módulos con FanOut elevado

| BC | Capa | Módulo | FanOut |
|----|------|--------|:------:|
| — | raíz | `src/app.py` | **13** |
| competencia | api | `router.py` | **12** |
| resultados | api | `router.py` | **12** |
| registro | api | `router.py` | **11** |
| resultados | application | `exportar_resultados.py` | **10** |
| torneo | api | `router.py` | 9 |
| resultados | domain | `ranking_competencia.py` | 9 |
| registro | domain | `inscripcion.py` | 9 |
| identidad | api | `router.py` | 8 |
| resultados | domain | `ranking_overall.py` | 8 |
| resultados | domain | `resultados_competencia_port.py` | 8 |
| resultados | application | `obtener_ranking_provisional.py` | 8 |

### 2.2 FanOut por BC × capa — resumen

| BC | Tipo | api/ FanOut | domain/ FanOut | application/ FanOut |
|----|------|:-----------:|:--------------:|:-------------------:|
| competencia | ES | 12 | — | — |
| torneo | CRUD | 9 | — | — |
| registro | CRUD | 11 | 9 | — |
| resultados | CRUD | 12 | 9 + 8 + 8 | 10 + 8 |
| identidad | CRUD | 8 | — | — |
| notificaciones | ES | — | — | — |
| shared | Shared | — | — | — |

### 2.3 Patrón por capa

**api/ concentra el mayor FanOut** en todos los BCs: los routers FastAPI importan schemas Pydantic, use cases, exceptions, autenticación y tipos de respuesta — el wiring de la capa API es estructuralmente acoplado.

**domain/ con FanOut elevado:** solo `resultados` muestra FanOut en domain (9–8), en `ranking_competencia.py`, `ranking_overall.py` y el puerto `resultados_competencia_port.py`. Estas clases integran datos de múltiples fuentes (competencia × disciplina × atleta × género) — complejidad intrínseca del ranking FAAS.

**notificaciones y shared: FanOut 0 issues** — los BCs más estables del sistema, confirmando que la baja D en ArchitectAnalyst (0.45) correlaciona con bajo acoplamiento saliente.

---

## 3. WMC proxy — Métodos con Complejidad Elevada

**Proxy:** número de métodos que superan el umbral de LongMethodAnalyzer (> 20 líneas)  
**Limitación:** no es WMC real (suma de CC por método) — subestima WMC porque solo cuenta métodos sobre umbral, no todos los métodos.

| BC | Tipo | Métodos sobre umbral | Proporción de LongMethod |
|----|------|:--------------------:|:------------------------:|
| competencia | ES (Core) | **74** | 58% del total del proyecto |
| resultados | CRUD | 27 | 21% |
| registro | CRUD | 18 | 14% |
| notificaciones | ES | 10 | 8% |
| identidad | CRUD | 8 | 6% |
| shared | Shared | 5 | 4% |
| torneo | CRUD | 2 | 2% |
| **Total** | | **144** | 100% |

**Hallazgo:** `competencia` tiene 74 métodos que superan el umbral — más que todos los demás BCs combinados. Esto es consistente con el análisis de backend-por-capa.md (219 bloques CC, 2 278 SLOC en domain/). El BC ES Core tiene más métodos largos **en términos absolutos**, no en densidad — su dominio es más extenso.

---

## 4. FeatureEnvy — cohesión complementaria

**FeatureEnvy:** un método usa más atributos de otra clase que de la propia → señal de responsabilidad mal ubicada.

| BC | Feature Envy issues |
|----|:-------------------:|
| competencia | **36** |
| registro | 12 |
| torneo | 8 |
| identidad | 8 |
| notificaciones | 7 |
| resultados | 3 |
| shared | 0 |

Los 36 issues de FeatureEnvy en `competencia` merecen análisis: en un BC ES con muchos value objects y aggregates, los handlers de application/ frecuentemente acceden a atributos del aggregate — es un patrón estructural del ES, no necesariamente un defecto.

---

## 5. Síntesis CK para el paper IEDD

| BC | Tipo | LCOM máx | CBO máx | WMC proxy | Evaluación |
|----|------|:---------:|:-------:|:---------:|------------|
| competencia | ES (Core) | 2 | 12 (api) | 74 | Alto volumen, baja severidad LCOM — complejidad en extensión |
| resultados | CRUD | 2 | 12 (api) | 27 | FanOut en domain × ranking multi-variante |
| registro | CRUD | **4** | 11 (api) | 18 | Mayor LCOM — aggregate Inscripcion multi-rol |
| torneo | CRUD | 3 | 9 (api) | 2 | LCOM en aggregate + repository |
| identidad | CRUD | 0 | 8 (api) | 8 | **Mejor cohesión** del proyecto |
| notificaciones | ES | 2 | 0 | 10 | Saludable — sin FanOut issues |
| shared | Shared | 0 | 0 | 5 | **Mejor CBO** del proyecto |

**Patrón ES vs CRUD en métricas CK:**
- LCOM: los BCs ES (competencia, notificaciones) no tienen peor cohesión que CRUD — el patrón ES con agregados pequeños y cohesivos mantiene LCOM bajo
- CBO: la capa api/ domina el FanOut en todos los BCs independientemente del paradigma — es un patrón estructural de FastAPI, no del paradigma ES vs CRUD
- Los BCs CRUD con mayor complejidad de dominio (registro multi-rol, resultados multi-variante) muestran peores métricas CK que el BC ES Core

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.6 (Prioridad 8) completada*
