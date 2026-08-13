# Suite Chidamber/Kemerer (parcial) — LCOM y CBO por BC

> Fuente: `quality/reports/designreviewer/v1.0.5-report.json` (ejecución 2026-08-13, HEAD `main` post SP-ADJ-13)
> Herramienta: DesignReviewer 298 issues · LCOMAnalyzer · FanOutAnalyzer · LongMethodAnalyzer · FeatureEnvyAnalyzer
> Cobertura CK: LCOM ✅ · CBO/FanOut ✅ · WMC (proxy) ✅ · DIT ⬜ · NOC ⬜ · RFC ⬜
> Referencia: PLAN-METRICAS.md §A.1.6
>
> **Medición anterior:** 2026-05-18 (SP-ADJ-11, `current-report.json`, 287 issues, 303 archivos).
> Esta medición cubre además SP7, SP-ADJ-12 y SP-ADJ-13 (309 archivos analizados).

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

| BC | Capa | Clase | LCOM | Δ vs 2026-05-18 |
|----|------|-------|:----:|:---:|
| registro | domain | `Inscripcion` | **5** | +1 |
| torneo | domain | `Torneo` | **3** | = |
| torneo | infrastructure | `SQLiteTorneoRepository` | **3** | = |
| registro | infrastructure | `SQLiteAtletaRepository` | **3** | = |
| competencia | domain | `Competencia` | 2 | = |
| competencia | domain | `TarjetaAsignacion` | 2 | = |
| competencia | domain | `GrillaDeSalida` | 2 | = |
| competencia | infrastructure | `AndarivelesActivosAdapter` | 2 | = |
| resultados | domain | `RankingCompetencia` | 2 | = |
| notificaciones | application | `PoliticaP11Handler` | 2 | = |

**Total:** 10 clases con LCOM > 1 de 309 archivos analizados (3.2%, antes 3.3% / 303 archivos)

**Único cambio real:** `Inscripcion` (registro/domain) subió de LCOM=4 a LCOM=5 — consistente con SP-ADJ-12/13 (roles adicionales: `agregar_rol`/`quitar_rol`, `estado_aceptacion`). El resto de las clases con LCOM > 1 no cambiaron.

### 1.2 LCOM por BC — resumen

| BC | Tipo | Clases con LCOM > 1 | LCOM máximo | Patrón |
|----|------|:-------------------:|:-----------:|--------|
| registro | CRUD | 2 | **5** | Inscripcion concentra lógica de atleta+juez+organizador+roles (SP-ADJ-11/12/13) |
| torneo | CRUD | 2 | **3** | Torneo aggregate con múltiples responsabilidades de ciclo de vida |
| competencia | ES (Core) | 4 | 2 | 4 clases pero todas en LCOM=2 — mínimo del umbral |
| resultados | CRUD | 1 | 2 | RankingCompetencia con lógica de ranking + validación |
| notificaciones | ES | 1 | 2 | PoliticaP11Handler con orquestación de casos |
| identidad | CRUD | 0 | — | Sin problemas LCOM — BC más cohesivo |
| shared | Shared | 0 | — | Sin problemas LCOM |

### 1.3 Hipótesis: LCOM más bajo en domain/ que en infrastructure/

| Capa | Clases con LCOM > 1 | LCOM máximo |
|------|:-------------------:|:-----------:|
| domain/ | 6 | 5 |
| infrastructure/ | 3 | 3 |
| application/ | 1 | 2 |
| api/ | 0 | — |

**Hipótesis NO confirmada en conteo** (igual que en la medición anterior): `domain/` tiene más instancias LCOM que `infrastructure/`, y ahora también el LCOM máximo es mayor (5 vs 3). La causa sigue siendo la complejidad intrínseca del dominio (aggregate Inscripcion multi-rol, ampliado en SP-ADJ-12/13), no un defecto de diseño.

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
| registro | api | `router.py` | **12** |
| resultados | application | `exportar_resultados.py` | **10** |
| torneo | api | `router.py` | 9 |
| resultados | domain | `ranking_competencia.py` | 9 |
| registro | domain | `inscripcion.py` | 9 |
| identidad | api | `router.py` | 8 |
| resultados | domain | `ranking_overall.py` | 8 |
| resultados | domain | `resultados_competencia_port.py` | 8 |
| resultados | application | `obtener_ranking_provisional.py` | 8 |

**Δ vs 2026-05-18:** `registro/api/router.py` subió de FanOut=11 a **12** (nuevos endpoints de aceptación/adjuntos de SP-ADJ-12). El resto se mantiene igual — la superficie de FanOut ya estaba estabilizada.

### 2.2 FanOut por BC × capa — resumen (máximo por capa)

| BC | Tipo | api/ FanOut | domain/ FanOut | application/ FanOut |
|----|------|:-----------:|:--------------:|:-------------------:|
| competencia | ES | 12 | — | — |
| torneo | CRUD | 9 | — | — |
| registro | CRUD | 12 | 9 | — |
| resultados | CRUD | 12 | 9 | 10 |
| identidad | CRUD | 8 | — | — |
| notificaciones | ES | — | — | — |
| shared | Shared | — | — | — |

### 2.3 Patrón por capa

**api/ concentra el mayor FanOut** en todos los BCs: los routers FastAPI importan schemas Pydantic, use cases, exceptions, autenticación y tipos de respuesta — el wiring de la capa API sigue siendo estructuralmente acoplado, sin cambios de patrón respecto a la medición anterior.

**domain/ con FanOut elevado:** solo `resultados` muestra FanOut en domain (9–8), en `ranking_competencia.py`, `ranking_overall.py` y el puerto `resultados_competencia_port.py` — sin cambios.

**notificaciones y shared: FanOut 0 issues** — se mantienen como los BCs más estables del sistema.

---

## 3. WMC proxy — Métodos con Complejidad Elevada

**Proxy:** número de métodos que superan el umbral de LongMethodAnalyzer (> 20 líneas)
**Limitación:** no es WMC real (suma de CC por método) — subestima WMC porque solo cuenta métodos sobre umbral, no todos los métodos.

| BC | Tipo | Métodos sobre umbral | Proporción | Δ vs 2026-05-18 |
|----|------|:--------------------:|:----------:|:---:|
| competencia | ES (Core) | **74** | 50% del total | = |
| resultados | CRUD | 27 | 18% | = |
| registro | CRUD | 21 | 14% | +3 |
| notificaciones | ES | 10 | 7% | = |
| identidad | CRUD | 9 | 6% | +1 |
| shared | Shared | 5 | 3% | = |
| torneo | CRUD | 2 | 1% | = |
| **Total** | | **148** | 100% | +4 |

**Hallazgo:** `competencia` se mantiene con 74 métodos sobre el umbral — más que todos los demás BCs combinados — sin crecer desde SP6. El crecimiento post-SP6 se concentró en `registro` (+3, roles y aceptación de SP-ADJ-12) e `identidad` (+1, `agregar_rol`/`quitar_rol`).

---

## 4. FeatureEnvy — cohesión complementaria

**FeatureEnvy:** un método usa más atributos de otra clase que de la propia → señal de responsabilidad mal ubicada.

| BC | Feature Envy issues | Δ vs 2026-05-18 |
|----|:-------------------:|:---:|
| competencia | **36** | = |
| registro | 13 | +1 |
| identidad | **12** | +4 |
| torneo | 8 | = |
| notificaciones | 7 | = |
| resultados | 3 | = |
| shared | 0 | = |

**Cambio a observar:** `identidad` pasó de 8 a 12 issues de FeatureEnvy — el mayor incremento relativo de la nueva medición, consistente con la extensión del modelo multi-rol (`agregar_rol`/`quitar_rol` en SP-ADJ-12) accediendo a atributos de `Usuario` desde application/.

---

## 5. Síntesis CK para el paper IEDD

| BC | Tipo | LCOM máx | CBO máx | WMC proxy | Evaluación |
|----|------|:---------:|:-------:|:---------:|------------|
| competencia | ES (Core) | 2 | 12 (api) | 74 | Alto volumen, baja severidad LCOM — complejidad en extensión, estable desde SP6 |
| resultados | CRUD | 2 | 12 (api) | 27 | FanOut en domain × ranking multi-variante — estable |
| registro | CRUD | **5** | 12 (api) | 21 | Mayor LCOM, sigue creciendo — aggregate Inscripcion multi-rol extendido en SP-ADJ-12/13 |
| torneo | CRUD | 3 | 9 (api) | 2 | LCOM en aggregate + repository — sin cambios |
| identidad | CRUD | 0 | 8 (api) | 9 | Cohesión LCOM intacta, pero FeatureEnvy en alza (modelo multi-rol) |
| notificaciones | ES | 2 | 0 | 10 | Saludable — sin FanOut issues |
| shared | Shared | 0 | 0 | 5 | **Mejor CBO** del proyecto |

**Patrón ES vs CRUD en métricas CK (se mantiene tras SP7/SP-ADJ-12/13):**
- LCOM: los BCs ES (competencia, notificaciones) siguen sin peor cohesión que CRUD
- CBO: la capa api/ sigue dominando el FanOut en todos los BCs — patrón estructural de FastAPI, no de paradigma
- El crecimiento post-SP6 se concentró en `registro` e `identidad` — exactamente los BCs que recibieron el modelo multi-rol extendido en SP-ADJ-12 (issues #198–#204) y SP-ADJ-13, no en el BC ES Core

---

*Ejecutado: 2026-08-13 — recálculo contra HEAD `main` (post SP-ADJ-13, tag v1.0.5) — PLAN-METRICAS.md §A.1.6 (Ronda 2, Prioridad 8)*
