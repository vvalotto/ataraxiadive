# Velocidad por Subproyecto — AtaraxiaDive

> Fuentes: `git log` (commits por tag) · `gh pr list` (PRs mergeados) · PLAN-METRICAS.md §C.1  
> US funcionales y de ajuste: matrix.md + CLAUDE.md §5  
> Fecha de extracción original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, tags hasta v1.0.5)**  
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
| **SP7 + SP-ADJ-12 + SP-ADJ-13** | Despliegue, manual y producción real | **14 días** | **0*** | **8** | **8** | **13** | **100** |
| **Total SP1–SP7+ADJ** | | **77 días** | **77** | **54** | **131** | **193** | **793** |

**Período SP1–SP6:** 2026-03-14 → 2026-05-16 (63 días calendario)
**Período SP7+SP-ADJ-12+SP-ADJ-13:** 2026-05-16 → 2026-05-30 (14 días calendario, tags v1.0.0→v1.0.5)

\* **Nota metodológica (nueva en esta ronda):** SP7 no generó US funcionales en el sentido
clásico de IEDD (dominio nuevo con precondición/postcondición). Sus dos incrementos fueron
**infraestructura** (INC-7.1 — despliegue en Fly.io, ADR-021, PR #194) y **documentación**
(INC-7.2 — manual de usuario MkDocs, PR #212), ninguno de los cuales es una "US funcional"
comparable a las de SP1–SP6. Las 8 US contadas como "ADJ" en esta fila son:
SP-ADJ-12 (6 US, PRs #205–#210, issues #198–#204) + SP-ADJ-13 (2 entradas de matrix.md §35,
PRs #217–#218). Los PRs #195/#196 (adecuación documental + plan de métricas) no se cuentan como
US — son trabajo de documentación paralelo, no incrementos de producto.

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
| **Fin SP7+ADJ-12+ADJ-13** | **77** | **77** | **1.00** |

El ritmo acumulado crece consistentemente hasta SP5 (1.33) y consolida en SP6 (1.22) — la caída en SP6 es esperada por ser un SP de validación/despliegue con más peso en ajuste que en features. **El ritmo acumulado sigue cayendo hasta 1.00 US func./día al cierre de SP7+ADJ-12+ADJ-13** — no porque el equipo se hizo más lento, sino porque el denominador (días) siguió sumando mientras el numerador (US funcionales) se congeló en 77: los últimos 14 días del proyecto fueron 100% despliegue, corrección post-producción y documentación, sin nuevas US funcionales de dominio. Es el patrón esperado del cierre de un proyecto: la curva de "ritmo funcional" se aplana cuando el foco pasa de construir producto a llevarlo a producción y sostenerlo.

---

## 6. Cierre del proyecto — interpretación (2026-08-13)

**El proyecto completo (SP1 → SP-ADJ-13) tomó 77 días calendario y entregó 77 US funcionales +
54 US de ajuste (131 US totales), con 193 PRs y 793 commits.** El último 18% del calendario
(14 de 77 días) no agregó ni una sola US funcional nueva — se dedicó íntegramente a:

1. Poner el sistema en producción real (Fly.io, ADR-021)
2. Corregir los primeros bugs de uso real (SP-ADJ-12, issues #198–#204)
3. Documentar el sistema para usuarios finales (manual MkDocs)
4. Validarlo en una ejecución real de torneo (SP-ADJ-13, Puerto Madryn 2026) y corregir lo que
   esa ejecución reveló

**Esto es evidencia a favor de una fase de proyecto distinta, no de una desaceleración del
método IEDD.** El ritmo de 1.5 US func./día de SP3–SP5 (velocidad de crucero de *construcción*)
no es comparable con el ritmo de *estabilización post-producción* — son dos tipos de trabajo
distintos y sería un error metodológico promediarlos en una sola cifra de "velocidad IEDD" para
el paper sin esta distinción.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.1 completado*
*Recalculado: 2026-08-13 — HEAD `main` (tags v1.0.0→v1.0.5) — PLAN-METRICAS.md §C.1 (Ronda 2)*
