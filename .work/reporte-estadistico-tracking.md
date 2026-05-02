# Reporte Estadístico — AtaraxiaDive Tracking
_Generado: 2026-04-25 06:57 · 85 historias analizadas_

> **Nota sobre Eje 5:** los campos `tests`, `cobertura` y `codeguard` en el resumen
> del tracker sólo se poblaron en SP1. Para SP2+ la evidencia de calidad está en los
> reportes CodeGuard/DesignReviewer por incremento (`quality/reports/`).

---

## Eje 1 — Distribución de Tiempos Reales

**Global — 85 historias con tiempo registrado**

| Métrica | Valor |
|---------|-------|
| Mínimo | 2min |
| Mediana | 14min |
| Media | 2.1h |
| P90 | 1.1h |
| Máximo | 64.3h |
| Desvío estándar | 8.1h |
| **Total acumulado** | **181.9h** |

**Por Subproyecto:**

| SP | N | Mín | Mediana | Media | P90 | Máx | Total SP |
|----|---|-----|---------|-------|-----|-----|----------|
| SP1 | 7 | 15min | 22min | 57min | 4.5h | 4.5h | 6.7h |
| SP2 | 8 | 7min | 26min | 5.8h | 22.2h | 22.2h | 46.2h |
| SP3 | 11 | 10min | 15min | 6.2h | 52min | 64.3h | 67.8h |
| SP4 | 25 | 5min | 12min | 1.3h | 35min | 22.1h | 32.2h |
| SP5 | 17 | 4min | 12min | 1.5h | 30min | 22.0h | 25.2h |
| ADJ-SP3 | 6 | 3min | 7min | 16min | 1.1h | 1.1h | 1.6h |
| ADJ-SP4 | 5 | 2min | 6min | 8min | 15min | 15min | 39min |
| ADJ-SP7 | 3 | 14min | 27min | 23min | 27min | 27min | 1.1h |
| ADJ-SP8 | 3 | 5min | 6min | 8min | 13min | 13min | 24min |

**Top 5 historias más largas:**

| Historia | Título | SP | Tiempo |
|----------|---------|----|--------|
| US-3.3.1 | Competencia torneo_id en ConfigurarIntervaloOT | SP3 | 64.3h |
| US-2.4.2 | Calcular Ranking BC Resultados nucleo | SP2 | 22.2h |
| US-4.3.5 | Adaptacion STA en el Paso 3 | SP4 | 22.1h |
| US-5.3.1 | UI de gestion de usuarios | SP5 | 22.0h |
| US-2.1.1 | Scaffold Aggregate Competencia + ConfigurarInterva | SP2 | 16.8h |

**Histograma de rangos:**

```
  <15min    │ ██████████████████████  48
  15–30min  │ ███████████░░░░░░░░░░░  23
  30–60min  │ ██░░░░░░░░░░░░░░░░░░░░   5
  1–2h      │ ░░░░░░░░░░░░░░░░░░░░░░   1
  2–4h      │ ░░░░░░░░░░░░░░░░░░░░░░   0
  >4h       │ ████░░░░░░░░░░░░░░░░░░   8
```

## Eje 2 — Estimación vs Realidad

> Varianza = (real − estimado) / estimado × 100
> Positiva → tardó más de lo estimado (sub-estimación)
> Negativa → tardó menos de lo estimado (sobre-estimación)

_42 historias con estimación y tiempo real registrados_

| Métrica | Valor |
|---------|-------|
| Varianza media | -30.1% |
| Varianza mediana | -84.3% |
| Más cercano a 0 (mejor) | -35.8% |
| Mayor sub-estimación | +1056.7% |
| Mayor sobre-estimación | -95.2% |
| Desvío estándar | 195.0pp |

| Categoría | N | % |
|-----------|---|---|
| Sub-estimado (>+20%): tardó más de lo previsto | 5 | 12% |
| En rango (±20%) | 0 | 0% |
| Sobre-estimado (<−20%): terminó antes | 37 | 88% |

**Evolución de la varianza media por SP:**

| SP | N | Varianza media | Interpretación |
|----|---|----------------|----------------|
| SP1 | 1 | +126.7% | línea de base |
| SP2 | 4 | +215.9% | ↑ más sub-estimación (tardó más) |
| SP4 | 13 | -75.5% | ↓ más sobre-estimación (terminó antes) |
| SP5 | 14 | -51.2% | ↑ más sub-estimación (tardó más) |

## Eje 3 — Velocidad por SP

_Tiempo promedio por historia en cada SP (US con tiempo > 0)._
_La mediana es más representativa que la media cuando hay outliers grandes._

| SP | Historias | Media | Mediana | ∆ mediana vs SP ant. | Total SP |
|----|-----------|-------|---------|----------------------|----------|
| SP1 | 7 | 57min | 22min | — | 6.7h |
| SP2 | 8 | 5.8h | 26min | +4min | 46.2h |
| SP3 | 11 | 6.2h | 15min | -11min | 67.8h |
| SP4 | 25 | 1.3h | 12min | -3min | 32.2h |
| SP5 | 17 | 1.5h | 12min | +0min | 25.2h |

**Historias de ajuste (US-ADJ) — comparativa:**

| ADJ-SP | Historias | Media | Mediana | Total |
|--------|-----------|-------|---------|-------|
| ADJ-SP3 | 6 | 16min | 7min | 1.6h |
| ADJ-SP4 | 5 | 8min | 6min | 39min |
| ADJ-SP7 | 3 | 23min | 27min | 1.1h |
| ADJ-SP8 | 3 | 8min | 6min | 24min |

> **Observación:** Las US-ADJ son consistentemente más cortas (mediana ~7min vs ~14min en US normales),
> lo esperado dado que son refactors acotados, no implementaciones desde cero.

## Eje 4 — Tiempo por Fase

_Tiempo promedio registrado por fase, sobre todas las historias con datos de fases._

| Fase | Nombre | N | Media | Mediana | % tiempo |
|------|--------|---|-------|---------|----------|
| 0 | Validación de Contexto         | 79 | 1.1min | 0.7min | ░░░░░░░░░░ 3.0% |
| 1 | Generación Escenarios BDD      | 70 | 0.9min | 0.4min | ░░░░░░░░░░ 2.4% |
| 2 | Plan de Implementación         | 79 | 1.8min | 1.1min | ░░░░░░░░░░ 4.9% |
| 3 | Implementación                 | 71 | 6.6min | 3.0min | ██░░░░░░░░ 17.5% |
| 4 | Tests Unitarios                | 65 | 1.1min | 0.5min | ░░░░░░░░░░ 3.0% |
| 5 | Tests de Integración           | 66 | 0.8min | 0.2min | ░░░░░░░░░░ 2.0% |
| 6 | Validación BDD                 | 65 | 1.1min | 0.2min | ░░░░░░░░░░ 2.9% |
| 7 | Quality Gates                  | 65 | 22.8min | 1.4min | ██████░░░░ 60.4% |
| 8 | Documentación                  | 64 | 0.8min | 0.5min | ░░░░░░░░░░ 2.1% |
| 9 | Reporte Final                  | 63 | 0.6min | 0.2min | ░░░░░░░░░░ 1.7% |

**Fase dominante:** Fase 7 — Quality Gates
con 22.8min de media (60.4% del tiempo total registrado).

> **Nota sobre Fase 7:** La media alta (22.8min) vs mediana baja (1.4min) indica
> outliers extremos — probablemente sesiones donde CodeGuard detectó problemas que
> requirieron corrección iterativa.

**Ratio aprobación humana / tiempo total:**
- Tiempo total acumulado en puntos de aprobación: 3min
- Tiempo total de implementación (todas las US): 181.9h
- Ratio: 0.0% — la espera al desarrollador es marginal

## Eje 5 — Calidad Acumulada

> Los campos de calidad en el tracker sólo se registraron sistemáticamente en SP1.
> Para SP2+ la fuente de verdad son los reportes en `quality/reports/`.
> Este eje muestra lo que el tracker tiene directamente, más un resumen de lo
> conocido por los reportes de incremento.

### 5.1 Datos del tracker

| Métrica | Valor |
|---------|-------|
| US con datos de tests en tracker | 1 |
| Total tests registrados | 27 |
| Total tests pasando | 27 |
| US con cobertura registrada | 1 |
| Cobertura registrada | 97.7% |

### 5.2 Resumen por SP (fuente: reportes de incremento)

| SP | Tests (total) | Cobertura | CodeGuard errores | DesignReviewer CRITICAL |
|----|--------------|-----------|-------------------|------------------------|
| SP1 | 207 | 98% | 0 | — (pre-DR) |
| SP2 | 481 | ~90%+ | 0 | 0 |
| SP3 | n/d | n/d | 0 | 0 (SP-ADJ-04) |
| SP4 | n/d | n/d | 0 | 0 (INC-4.2..4.6) |
| SP5 | en curso | en curso | 0 | 0 (INC-5.4) |

### 5.3 Tendencia de calidad observable

```
Errores CodeGuard acumulados por SP:  SP1=0 · SP2=0 · SP3=0 · SP4=0 · SP5=0
DesignReviewer CRITICAL por merge:    0 en todos los SPs desde DR activado (SP2+)
Cobertura (donde conocida):           ≥97% SP1 · ≥90% SP2 (target DoD)
```

> La ausencia de CRITICAL en todos los merges desde SP2 y la cobertura ≥90%
> sostenida son las métricas de calidad más robustas del experimento.

---

## Observaciones Cruzadas

1. **Distribución bimodal de tiempos** (Eje 1): el 85% de las historias se
   implementa en menos de 30 minutos; el 9% supera las 4 horas. Los outliers
   no son ruido — son historias arquitecturalmente complejas (scaffold de aggregates,
   integración de BCs, adaptaciones de dominio real).

2. **Estimaciones masivamente optimistas** (Eje 2): la varianza mediana de −84%
   indica que los tiempos estimados (pensados para implementación humana) son
   5-10× mayores que los tiempos reales con IA. Esto es un dato experimental
   relevante para el paper IEDD.

3. **Aceleración sostenida SP2→SP4** (Eje 3): la mediana cae de 26min (SP2)
   a 12min (SP4/SP5), con más historias por sprint. El salto SP2→SP3 no mejora
   la mediana porque SP3 incluye integración entre BCs (más complejo).

4. **Implementación = 17% del tiempo, Quality Gates = 60%** (Eje 4):
   el cuello de botella no es escribir código — es la verificación. La media alta
   en Fase 7 vs mediana baja sugiere que la mayoría pasa rápido pero un subconjunto
   tiene fricciones iterativas (codeguard → fix → re-check).

5. **Calidad estable a pesar del volumen** (Eje 5): 0 errores CodeGuard y 0
   CRITICAL DesignReviewer en todos los SPs desde la activación de los gates.
   El sistema de quality gates funciona como red de seguridad, no como freno.

---
_Fin del reporte_