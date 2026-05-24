# Velocidad por Subproyecto — AtaraxiaDive

> Fuentes: `git log` (commits por tag) · `gh pr list` (PRs mergeados) · PLAN-METRICAS.md §C.1  
> US funcionales y de ajuste: matrix.md + CLAUDE.md §5  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §C.1

---

## 1. Tabla principal de velocidad

| SP | Nombre | Duración | US func. | US ADJ | US total | PRs | Commits |
|----|--------|:--------:|:--------:|:------:|:--------:|:---:|:-------:|
| SP1 | La Performance | 10 días | 9 | 5 | 14 | 13 | 96 |
| SP2 | La Competencia | 4 días | 3 | 3 | 6 | 15 | 36 |
| SP3 | El Torneo | 7 días | 11 | 14 | 25 | 26 | 94 |
| SP4 | La Plataforma | 14 días | 21 | 7 | 28 | 26 | 119 |
| SP5 | La Puesta en Marcha | 13 días | 20 | 7 | 27 | 49 | 143 |
| SP6 | Validación y Despliegue | 15 días | 13 | 10 | 23 | 51 | 205 |
| **Total SP1–SP6** | | **63 días** | **77** | **46** | **123** | **180** | **693** |

**Período:** 2026-03-14 → 2026-05-16 (63 días calendario)

---

## 2. Métricas derivadas por SP

| SP | US func./día | US total/día | PRs/día | Commits/día | Commits/PR |
|----|:------------:|:------------:|:-------:|:-----------:|:----------:|
| SP1 | 0.90 | 1.40 | 1.3 | 9.6 | 7.4 |
| SP2 | 0.75 | 1.50 | 3.75 | 9.0 | 2.4 |
| SP3 | 1.57 | 3.57 | 3.7 | 13.4 | 3.6 |
| SP4 | 1.50 | 2.00 | 1.9 | 8.5 | 4.6 |
| SP5 | 1.54 | 2.08 | 3.8 | 11.0 | 2.9 |
| SP6 | 0.87 | 1.53 | 3.4 | 13.7 | 4.0 |
| **Promedio** | **1.19** | **1.95** | **2.86** | **11.0** | **3.8** |

---

## 3. Análisis de tendencias

### 3.1 Cadencia de US funcionales

```
SP1  ████░░░░░░  0.90 US func./día
SP2  ███░░░░░░░  0.75
SP3  ████████░░  1.57
SP4  ████████░░  1.50
SP5  ████████░░  1.54
SP6  ████░░░░░░  0.87
```

**Patrón:** SP1–SP2 son de rampa (setup de plataforma + infraestructura hexagonal). SP3–SP5 alcanzan la velocidad de crucero (~1.5 US func./día). SP6 baja a 0.87 — el SP de validación tiene más US de ajuste (SP-ADJ-11) y menos US funcionales nuevas por diseño.

### 3.2 Estabilización del sprint

La cadencia de SP se estabilizó sorprendentemente rápido:

| Período | Duración SP | US totales | Patrón |
|---------|:-----------:|:----------:|--------|
| SP1–SP3 | 10, 4, 7 días | 14, 6, 25 US | Rampa + calibración |
| SP4–SP6 | 14, 13, 15 días | 28, 27, 23 US | Estado estable ≈ 14 días / 25 US |

Desde SP4, el equipo entregó entre 23 y 28 US en sprints de 13–15 días. **Variación de duración: ±10%. Variación de throughput: ±10%.** El pipeline IEDD es predecible.

### 3.3 PRs por día — indicador de fragmentación

Los PRs/día reflejan qué tan granular fue el desarrollo:

- **SP1 (1.3 PRs/día):** muchos commits de setup por PR (7.4 commits/PR) — trabajo exploratorio
- **SP2–SP3 (3.7–3.75 PRs/día):** alta cadencia, PRs pequeños (2.4–3.6 commits/PR)
- **SP4 (1.9 PRs/día):** SP más complejo (Identidad + Notificaciones ES + Frontend) — PRs más densos (4.6 commits/PR)
- **SP5–SP6 (3.4–3.8 PRs/día):** máxima cadencia — 1 PR ≈ 1 US es la norma establecida

### 3.4 Commits por día — intensidad de trabajo

Oscila entre 8.5 y 13.7 commits/día sin tendencia clara. La variación refleja el tipo de trabajo más que la velocidad: SP4 (8.5/día) tuvo US complejas de infraestructura; SP6 (13.7/día) tuvo muchas iteraciones de ajuste y corrección.

---

## 4. Distribución total del esfuerzo

```
US funcionales:  77 (63%)  ██████████████████████████░░░░░░░░░░░░░░
US de ajuste:    46 (37%)  ██████████████████░░░░░░░░░░░░░░░░░░░░░░
```

| Artefacto | Total | % sobre US func. |
|-----------|:-----:|:----------------:|
| PRs mergeados (SP1–SP6) | 180 | — |
| Commits (SP1–SP6) | 693 | — |
| US funcionales | 77 | 100% |
| US de ajuste (SP-ADJ) | 46 | 60% |
| US totales | 123 | — |

**El proyecto entregó 77 US funcionales en 63 días a un ritmo promedio de 1.22 US funcionales / día calendario.**

---

## 5. Evolución acumulada

| Punto | US func. acum. | Días acum. | Ritmo acum. (US func./día) |
|-------|:--------------:|:----------:|:--------------------------:|
| Fin SP1 | 9 | 10 | 0.90 |
| Fin SP2 | 12 | 14 | 0.86 |
| Fin SP3 | 23 | 21 | 1.10 |
| Fin SP4 | 44 | 35 | 1.26 |
| Fin SP5 | 64 | 48 | 1.33 |
| Fin SP6 | 77 | 63 | 1.22 |

El ritmo acumulado crece consistentemente hasta SP5 (1.33) y consolida en SP6 (1.22) — la caída en SP6 es esperada por ser un SP de validación/despliegue con más peso en ajuste que en features.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.1 completado*
