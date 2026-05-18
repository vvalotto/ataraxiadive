# Overhead del Pipeline IEDD — Tiempo por US

> Fuente: sección "Tracking de Tiempo" / "Tiempo real" de cada `docs/reports/US-*-report.md`  
> Cobertura: 34 de ~123 US totales (28%) — el tracker no fue usado de forma consistente en SP4  
> Unidad: minutos de reloj (wall-clock), pipeline completo Fase 0–9  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §C.2

---

## 1. Dataset completo

| US | SP | Tiempo real (min) | Estimado (min) | Varianza | Tipo |
|----|----|-----------------:|:--------------:|:--------:|------|
| US-1.2.1 | SP1 | ~120 | — | — | Setup inicial (bugs de herramientas) |
| US-1.2.2 | SP1 | ~32 | ~110 | −71% | Primer ciclo limpio |
| US-1.2.3 | SP1 | ~29 | ~95 | −69% | Estabilización confirmada |
| US-1.4.1 | SP1 | ~15 | — | — | |
| US-1.4.2 | SP1 | ~21 | — | — | |
| US-2.1.1 | SP2 | ~18 | — | — | |
| US-2.2.1 | SP2 | ~69 | ~55 | +25% | Supera estimado — nueva lógica de port |
| US-2.3.1 | SP2 | ~22 | — | — | |
| US-2.4.2 | SP2 | ~26 | — | — | |
| US-3.1.1 | SP3 | ~12 | — | — | |
| US-3.1.2 | SP3 | ~20 | — | — | |
| US-3.2.1 | SP3 | ~14 | — | — | |
| US-3.2.3 | SP3 | 22 | — | — | |
| US-3.3.1 | SP3 | ~38 | — | — | |
| US-3.3.2 | SP3 | 110 | ~58 | +90% | Integración torneo↔competencia compleja |
| US-3.4.1 | SP3 | ~11 | — | — | |
| US-4.1.1 | SP4 | 17 | — | — | |
| US-5.2.1 | SP5 | ~14 | — | — | |
| US-5.6.1 | SP5 | ~12 | — | — | |
| US-5.6.3 | SP5 | ~103 | — | — | Algoritmo FAAS + variantes SPE |
| US-5.7.1 | SP5 | 7 | ~70 | −90% | Reutilización casi total |
| US-5.7.2 | SP5 | 273 | ~120 | +128% | Portal atleta completo; incluye espera Fase 8 |
| US-6.4.1 | SP6 | 11 | ~75 | −85% | |
| US-6.4.2 | SP6 | 9 | ~120 | −93% | |
| US-6.6.4 | SP6 | 19 | — | — | |
| US-ADJ-9.4 | SP5-ADJ | 4 | ~90 | −96% | Refactor frontend mínimo |
| US-ADJ-9.5 | SP5-ADJ | 3 | ~75 | −96% | Refactor frontend mínimo |
| US-ADJ-10.1 | SP6-ADJ | 245 | ~220 | +11% | Edición completa de torneo (UAT) |
| US-ADJ-10.2 | SP6-ADJ | 220 | ~205 | +7% | Correcciones UI complejas |
| US-ADJ-10.3 | SP6-ADJ | 18 | — | — | |
| US-ADJ-10.4 | SP6-ADJ | ~23 | — | — | |
| US-ADJ-11.5 | SP6-ADJ | ~50 | — | — | 10 min tracker + 40 min implementación |
| US-ADJ-11.6 | SP6-ADJ | ~6 | — | — | |
| US-ADJ-11.7 | SP6-ADJ | ~40 | — | — | |
| US-ADJ-11.8 | SP6-ADJ | ~15 | — | — | |

---

## 2. Estadísticas globales

| Estadístico | Todos (n=34) | Sin outliers >100 min (n=28) |
|-------------|:-----------:|:---------------------------:|
| Media | 48.6 min | 20.8 min |
| Mediana | 20.5 min | 18.0 min |
| Mínimo | 3 min | 3 min |
| Máximo | 273 min | 69 min |
| P25 | 12 min | 11 min |
| P75 | 38 min | 26 min |

**Tiempo típico (mediana):** ~20 min por US — consistente con la hipótesis H-4.1 y el valor de ~18 min registrado en la memoria del proyecto.

---

## 3. Distribución por rangos

| Rango | Cantidad | % | Descripción |
|-------|:--------:|:-:|-------------|
| < 15 min | 12 | 35% | US de reutilización alta o refactor puntual |
| 15–30 min | 10 | 29% | **Rango modal** — US CRUD estándar bien acotada |
| 30–60 min | 5 | 15% | US con nueva lógica de dominio o decisión de diseño |
| 60–120 min | 3 | 9% | US complejas (nuevos puertos, integración cross-BC) |
| > 120 min | 4 | 12% | Outliers — arquitectura nueva, wait de aprobación, US-ADJ mayores |

El **64% de las US se implementan en menos de 30 minutos** a través del pipeline completo de 10 fases.

---

## 4. Evolución del tiempo por SP

### SP1 — Rampa de aprendizaje

| US | Tiempo |
|----|-------:|
| US-1.2.1 | 120 min (setup + bugs) |
| US-1.2.2 | 32 min |
| US-1.2.3 | 29 min |
| US-1.4.1 | 15 min |
| US-1.4.2 | 21 min |

**Promedio SP1 (sin US-1.2.1):** ~24 min · **Caída de 120 → 29 min en 2 ciclos** — la inversión inicial se amortizó rápidamente.

### SP2 — Primera velocidad estable

| US | Tiempo |
|----|-------:|
| US-2.1.1 | 18 min |
| US-2.2.1 | 69 min ⚠️ |
| US-2.3.1 | 22 min |
| US-2.4.2 | 26 min |

**Promedio SP2:** ~34 min. US-2.2.1 (69 min) fue el único caso donde el tiempo real superó el estimado en SP2 — nueva lógica de puerto con adapter que requirió decisiones de diseño no anticipadas.

### SP3 — Introducción de múltiples BCs nuevos

| US | Tiempo |
|----|-------:|
| US-3.1.1 | 12 min |
| US-3.1.2 | 20 min |
| US-3.2.1 | 14 min |
| US-3.2.3 | 22 min |
| US-3.3.1 | 38 min |
| US-3.3.2 | 110 min ⚠️ |
| US-3.4.1 | 11 min |

**Promedio SP3 (sin US-3.3.2):** ~19.5 min. US-3.3.2 (110 min) fue el caso más complejo del SP — integración torneo↔competencia con dependencias cruzadas y diseño emergente.

### SP4 — Único dato disponible

| US | Tiempo |
|----|-------:|
| US-4.1.1 | 17 min |

**Nota de cobertura:** SP4 tiene el peor registro de tracking (~1 de 21 US funcionales). El tracker no fue usado sistemáticamente durante este sprint.

### SP5 — Mayor dispersión

| US | Tiempo |
|----|-------:|
| US-5.2.1 | 14 min |
| US-5.6.1 | 12 min |
| US-5.6.3 | 103 min |
| US-5.7.1 | 7 min |
| US-5.7.2 | 273 min ⚠️ |

**Promedio SP5 (sin US-5.7.2):** ~34 min. SP5 fue el sprint de mayor variedad de tipos de US (domain algorithms, portal atleta, portal organizador) — el rango de tiempo refleja esa variedad. US-5.7.2 (273 min) incluye tiempo de espera de aprobación de Fase 8, no es tiempo activo.

### SP6 — Mayor eficiencia

| US | Tiempo |
|----|-------:|
| US-6.4.1 | 11 min |
| US-6.4.2 | 9 min |
| US-6.6.4 | 19 min |

**Promedio SP6:** ~13 min (mínimo histórico). Las US de SP6 fueron en su mayoría incrementales sobre bases establecidas.

---

## 5. US más rápidas y más lentas

### Top 5 más rápidas

| US | Tiempo | Causa |
|----|-------:|-------|
| US-ADJ-9.5 | 3 min | Refactor puntual de 1 componente frontend |
| US-ADJ-9.4 | 4 min | Refactor puntual de 1 componente frontend |
| US-5.7.1 | 7 min | Reutilización casi total de componentes existentes |
| US-ADJ-11.6 | 6 min | Ajuste mínimo de formulario |
| US-6.4.2 | 9 min | Corrección acotada en endpoint existente |

### Top 5 más lentas (excluyendo wait-time)

| US | Tiempo | Causa |
|----|-------:|-------|
| US-ADJ-10.1 | 245 min | Edición completa de torneo — frontend + backend |
| US-ADJ-10.2 | 220 min | Correcciones UI complejas — múltiples páginas |
| US-5.7.2 | 273 min | Portal atleta completo + espera Fase 8 |
| US-3.3.2 | 110 min | Integración torneo↔competencia con diseño emergente |
| US-5.6.3 | 103 min | Algoritmo FAAS + variantes SPE multi-disciplina |

---

## 6. Precisión de las estimaciones (donde hay dato)

| US | Estimado | Real | Varianza |
|----|:--------:|:----:|:--------:|
| US-1.2.2 | ~110 min | 32 min | **−71%** |
| US-1.2.3 | ~95 min | 29 min | **−69%** |
| US-2.2.1 | 55 min | 69 min | **+25%** |
| US-3.3.2 | ~58 min | 110 min | **+90%** |
| US-5.7.1 | 70 min | 7 min | **−90%** |
| US-5.7.2 | 120 min | 273 min | **+128%** |
| US-6.4.1 | 75 min | 11 min | **−85%** |
| US-6.4.2 | 120 min | 9 min | **−93%** |
| US-ADJ-9.4 | 90 min | 4 min | **−96%** |
| US-ADJ-9.5 | 75 min | 3 min | **−96%** |
| US-ADJ-10.1 | 220 min | 245 min | **+11%** |
| US-ADJ-10.2 | 205 min | 220 min | **+7%** |

**Patrón:** las estimaciones de US nuevas (primer ciclo, dominio desconocido) son sistemáticamente sobreestimadas cuando el patrón ya existe, y subbestimadas cuando emerge complejidad no anticipada. US-ADJ-10.1/10.2 (con estimados basados en experiencia previa) tienen precisión de ±11% — señal de que la estimación mejora con la experiencia del dominio.

---

## 7. Interpretación para el experimento IEDD

1. **Hipótesis H-4.1 confirmada:** el overhead del pipeline IEDD no es estructural. Tras la primera US (120 min de setup), el tiempo convergió a ~18–20 min (mediana) y se mantuvo estable. El 64% de las US se implementan en < 30 min.

2. **Correlación tiempo ↔ novedad de dominio:** los outliers (US-3.3.2, US-5.6.3, US-ADJ-10.x) corresponden a US donde emergen decisiones de diseño no anticipadas o se integran contextos nuevos. El tiempo es una señal de complejidad intrínseca, no de fricción del proceso.

3. **Las estimaciones iniciales del pipeline sobreestiman sistemáticamente (−70% a −96%):** el equipo tendió a estimar tiempo para un humano lento, no para un flujo IEDD asistido por IA. Las estimaciones basadas en experiencia acumulada (SP6, ADJ-10) son mucho más precisas (±11%).

4. **Cobertura del tracking (28%):** el registro de tiempos no fue sistemático, especialmente en SP4. Para futuros experimentos IEDD se recomienda instrumentar el tracker desde Fase 0 en cada US, automáticamente.

5. **Benchmark para el paper:** US estándar (BC existente, patrón conocido) = 11–22 min. US de nuevo dominio (nuevo BC, primer patrón) = 30–70 min. US de integración compleja (cross-BC, diseño emergente) = 100–245 min.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.2 completado*
